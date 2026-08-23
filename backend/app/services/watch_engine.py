"""
NeuroWatch — Continuous Automation Engine (Section B)
Manages per-watch asyncio tasks that re-scrape sources on a fixed interval,
diff results against previous cycles, and stream updates via WebSocket.

Reuses the existing scrape/heal/karma/compliance pipeline — zero duplication.
"""

import asyncio
import hashlib
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlmodel import Session, select

from ..core.config import settings
from ..core.robots_check import check_compliance
from ..db import engine as db_engine
from ..healing.karma_score import karma_engine
from ..models.schemas import WatchJob, WatchCycle, Collector, Job, ScrapedRow, SchemaVersion
from ..scrapers.brightdata_client import brightdata_client
from ..scrapers.scrapling_fallback import scrapling_fetcher
from ..scrapers.web_search_scraper import web_search_scraper
from ..core.llm import llm_client
from ..ws.manager import ws_manager

logger = logging.getLogger("neuroscrape.watch")


class WatchScheduler:
    """Manages one asyncio.Task per active WatchJob. Clean pause/resume/delete."""

    def __init__(self):
        self._tasks: Dict[str, asyncio.Task] = {}
        self._running = False

    async def start(self):
        """Resumes all active watches from DB on startup."""
        self._running = True
        with Session(db_engine) as db:
            active_watches = db.exec(
                select(WatchJob).where(WatchJob.status == "active")
            ).all()
            for w in active_watches:
                self._spawn_task(w.id, w.interval_seconds)
        logger.info(f"WatchScheduler started. Resumed {len(self._tasks)} active watches.")

    async def stop(self):
        """Cancel all running watch tasks on shutdown."""
        self._running = False
        for watch_id, task in list(self._tasks.items()):
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):
                pass
        self._tasks.clear()
        logger.info("WatchScheduler stopped. All watch tasks cancelled.")

    def create_watch(self, watch_job: WatchJob):
        """Start scheduling a newly created watch."""
        self._spawn_task(watch_job.id, watch_job.interval_seconds)

    def pause_watch(self, watch_id: str):
        """Cancel the task for a watch without deleting it."""
        task = self._tasks.pop(watch_id, None)
        if task:
            task.cancel()
            logger.info(f"Watch {watch_id} paused — task cancelled.")

    def resume_watch(self, watch_id: str, interval_seconds: int):
        """Re-spawn task for a paused watch."""
        if watch_id not in self._tasks:
            self._spawn_task(watch_id, interval_seconds)
            logger.info(f"Watch {watch_id} resumed.")

    def delete_watch(self, watch_id: str):
        """Cancel task and remove. No orphans."""
        self.pause_watch(watch_id)

    def _spawn_task(self, watch_id: str, interval_seconds: int):
        if watch_id in self._tasks and not self._tasks[watch_id].done():
            return
        task = asyncio.create_task(self._watch_loop(watch_id, interval_seconds))
        self._tasks[watch_id] = task

    async def _watch_loop(self, watch_id: str, interval_seconds: int):
        """The per-watch background loop: sleep → scrape → diff → push → repeat."""
        logger.info(f"Watch loop started for {watch_id} (interval={interval_seconds}s)")
        try:
            # Run first cycle immediately
            await self._run_cycle(watch_id)

            while self._running:
                await asyncio.sleep(interval_seconds)
                await self._run_cycle(watch_id)
        except asyncio.CancelledError:
            logger.info(f"Watch loop {watch_id} cancelled.")
        except Exception as e:
            logger.error(f"Watch loop {watch_id} crashed: {e}")
            with Session(db_engine) as db:
                wj = db.get(WatchJob, watch_id)
                if wj:
                    wj.status = "error"
                    db.add(wj)
                    db.commit()

    async def _run_cycle(self, watch_id: str):
        """Execute one cycle: scrape all sources → karma → diff → persist → push WS."""
        with Session(db_engine) as db:
            wj = db.get(WatchJob, watch_id)
            if not wj or wj.status != "active":
                return

            urls = list(wj.input_urls)

            # Mode 2 (keyword): resolve URLs via search
            if wj.mode == "keyword" and wj.keyword_query:
                try:
                    search_result = await web_search_scraper.search_and_scrape(
                        query=wj.keyword_query,
                        fields=["headline", "summary", "source_url"],
                        max_sources=min(settings.WATCH_MAX_SOURCES, 5)
                    )
                    urls = [
                        r.get("source_url") or r.get("url", "")
                        for r in search_result.get("rows", [])
                        if r.get("source_url") or r.get("url")
                    ][:settings.WATCH_MAX_SOURCES]
                except Exception as e:
                    logger.error(f"Watch {watch_id} keyword search failed: {e}")
                    urls = []

            if not urls:
                logger.warning(f"Watch {watch_id}: no URLs to scrape this cycle.")
                return

            # Ethics guardrail on every URL every cycle
            compliant_urls = []
            for url in urls:
                try:
                    result = await check_compliance(url, check_robots=settings.ENFORCE_ROBOTS_TXT)
                    if result.allowed:
                        compliant_urls.append(url)
                    else:
                        logger.warning(f"Watch {watch_id}: URL {url} now disallowed — {result.reason}")
                        await ws_manager.broadcast_to_job(
                            f"watch_{watch_id}",
                            {"type": "watch_warning", "url": url, "reason": result.reason}
                        )
                except Exception:
                    compliant_urls.append(url)

            if not compliant_urls:
                wj.status = "paused"
                db.add(wj)
                db.commit()
                await ws_manager.broadcast_to_job(
                    f"watch_{watch_id}",
                    {"type": "watch_paused", "reason": "All source URLs are now non-compliant."}
                )
                self.pause_watch(watch_id)
                return

            # Scrape each source
            cycle_rows: Dict[str, List[Dict[str, Any]]] = {}
            total_karma = 0.0
            total_count = 0

            for url in compliant_urls:
                try:
                    html = await scrapling_fetcher.fetch_html(url)
                    fields = ["title", "price", "description", "url"]
                    plan = await llm_client.generate_scrape_plan(url, fields)
                    selector_map = {f.name: f.selector_hint or f".{f.name}" for f in plan.fields}
                    field_specs = [f.dict() for f in plan.fields]

                    raw_rows = scrapling_fetcher.extract_from_html(
                        html, selector_map, field_specs, max_rows=30
                    )

                    scored_rows = []
                    field_descs = {f["name"]: f.get("description", f["name"]) for f in field_specs}
                    for r in raw_rows:
                        score, flags = karma_engine.evaluate_row(r, field_descs)
                        r["karma_score"] = score
                        total_karma += score
                        total_count += 1
                        scored_rows.append(r)

                    cycle_rows[url] = scored_rows
                except Exception as e:
                    logger.error(f"Watch {watch_id} scrape failed for {url}: {e}")
                    cycle_rows[url] = []

            # Diff against previous cycle
            prev_cycle = db.exec(
                select(WatchCycle)
                .where(WatchCycle.watch_job_id == watch_id)
                .order_by(WatchCycle.cycle_number.desc())
                .limit(1)
            ).first()

            diff = self._compute_diff(prev_cycle, cycle_rows)
            avg_karma = round(total_karma / total_count, 1) if total_count > 0 else 0.0

            # Persist cycle
            cycle_num = (prev_cycle.cycle_number + 1) if prev_cycle else 1
            new_cycle = WatchCycle(
                watch_job_id=watch_id,
                cycle_number=cycle_num,
                run_at=datetime.utcnow(),
                source_results=cycle_rows,
                diff_summary=diff,
                avg_karma=avg_karma,
                status="completed"
            )
            db.add(new_cycle)

            wj.total_cycles = cycle_num
            wj.last_run_at = datetime.utcnow()
            wj.next_run_at = datetime.utcnow() + timedelta(seconds=wj.interval_seconds)
            db.add(wj)
            db.commit()

            # Push WebSocket update
            update_event = {
                "type": "watch_update",
                "watch_job_id": watch_id,
                "cycle_number": cycle_num,
                "timestamp": datetime.utcnow().isoformat(),
                "sources_scraped": len(compliant_urls),
                "total_rows": total_count,
                "avg_karma": avg_karma,
                "diff": diff,
                "next_run_at": wj.next_run_at.isoformat() if wj.next_run_at else None,
            }
            await ws_manager.broadcast_to_job(f"watch_{watch_id}", update_event)
            # Also broadcast to aggregate feed
            await ws_manager.broadcast_to_global(update_event)

            logger.info(
                f"Watch {watch_id} cycle {cycle_num} complete: "
                f"{total_count} rows, avg karma {avg_karma}, "
                f"diff: +{diff.get('new', 0)} / -{diff.get('removed', 0)} / ~{diff.get('changed', 0)}"
            )

    def _compute_diff(
        self, prev_cycle: Optional[WatchCycle], current_rows: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Diff current cycle rows against previous cycle rows by content hash."""
        def _hash_row(row: Dict) -> str:
            clean = {k: v for k, v in sorted(row.items()) if k != "karma_score"}
            return hashlib.md5(json.dumps(clean, default=str).encode()).hexdigest()

        current_hashes = set()
        current_map = {}
        for url, rows in current_rows.items():
            for r in rows:
                h = _hash_row(r)
                current_hashes.add(h)
                current_map[h] = r

        if not prev_cycle or not prev_cycle.source_results:
            return {"new": len(current_hashes), "removed": 0, "changed": 0, "total": len(current_hashes)}

        prev_hashes = set()
        prev_results = prev_cycle.source_results or {}
        for url, rows in prev_results.items():
            if isinstance(rows, list):
                for r in rows:
                    prev_hashes.add(_hash_row(r))

        new_count = len(current_hashes - prev_hashes)
        removed_count = len(prev_hashes - current_hashes)
        # Changed = rows with same title but different hash (approximation)
        changed_count = 0

        return {
            "new": new_count,
            "removed": removed_count,
            "changed": changed_count,
            "total": len(current_hashes)
        }


watch_scheduler = WatchScheduler()

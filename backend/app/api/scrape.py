"""
NeuroScrape - Scrape API Router (Sections 5.1, 5.3, 5.4, 5.8)
Handles plan generation, collector creation/run, status polling,
teach-by-example learning, and agentic multi-step crawling.
"""

import uuid
import time
import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select

from ..db import get_session
from ..core.config import settings
from ..core.robots_check import check_compliance
from ..core.llm import llm_client
from ..models.schemas import (
    Job, Collector, ScrapedRow, SchemaVersion,
    ScrapePlanRequest, ScrapeRunRequest, TeachScrapeRequest, AgenticScrapeRequest
)
from ..scrapers.brightdata_client import brightdata_client
from ..scrapers.teach_by_example import teach_learner
from ..scrapers.agentic_crawler import agentic_crawler
from ..healing.karma_score import karma_engine
from ..ws.manager import ws_manager

logger = logging.getLogger("neuroscrape.api.scrape")
router = APIRouter(prefix="/api/scrape", tags=["Scrape Engine"])


@router.post("/plan")
async def generate_plan(req: ScrapePlanRequest):
    """
    Generates a structured Scraper Studio schema plan from a URL and plain-English field descriptions.
    """
    compliance = await check_compliance(req.url, check_robots=settings.ENFORCE_ROBOTS_TXT)
    if not compliance.allowed:
        raise HTTPException(status_code=400, detail=compliance.reason)

    plan = await llm_client.generate_scrape_plan(req.url, req.fields)
    return {
        "url": req.url,
        "compliance": compliance.model_dump(),
        "plan": plan.model_dump()
    }


@router.post("/run")
async def run_scrape(
    req: ScrapeRunRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session)
):
    """
    Creates and initiates a scrape job. Returns immediately with job_id and streams live events via WebSocket.
    """
    # 1. Pre-flight ethics check (Section 5.8)
    compliance = await check_compliance(req.url, check_robots=settings.ENFORCE_ROBOTS_TXT)
    if not compliance.allowed:
        raise HTTPException(status_code=400, detail=f"Compliance check rejected: {compliance.reason}")

    job_id = f"job_{uuid.uuid4().hex[:10]}"
    
    # 2. Resolve or create Collector
    collector = None
    if req.collector_id:
        collector = db.get(Collector, req.collector_id)
        if not collector:
            raise HTTPException(status_code=404, detail="Collector not found")

    if not collector:
        collector_id = f"col_{uuid.uuid4().hex[:8]}"
        field_descriptions = req.fields or ["product_name", "price", "stock_status"]
        plan = await llm_client.generate_scrape_plan(req.url, field_descriptions)
        
        field_specs = [f.dict() for f in plan.fields]
        selector_map = {
            f.name: f.selector_hint or f".{f.name}, [data-{f.name}]"
            for f in plan.fields
        }

        bd_id = await brightdata_client.create_collector(
            name=f"Collector-{req.url.split('//')[-1][:20]}",
            target_url=req.url,
            field_specs=field_specs
        )

        collector = Collector(
            id=collector_id,
            name=f"Collector for {req.url}",
            target_url=req.url,
            schema_version=1,
            brightdata_collector_id=bd_id,
            active_selector_map=selector_map,
            field_specs=field_specs,
            status="active"
        )
        db.add(collector)

        schema_v = SchemaVersion(
            collector_id=collector_id,
            version_num=1,
            field_specs=field_specs,
            selector_map=selector_map,
            commit_message="Initial schema created"
        )
        db.add(schema_v)
        db.commit()
        db.refresh(collector)

    # 3. Create Job record
    job = Job(
        id=job_id,
        collector_id=collector.id,
        url=req.url,
        mode=req.mode,
        status="running",
        plan=collector.active_selector_map
    )
    db.add(job)
    db.commit()

    # 4. Dispatch async execution
    background_tasks.add_task(
        _execute_scrape_job,
        job_id=job_id,
        collector_id=collector.id,
        url=req.url,
        max_rows=req.max_rows,
        simulate_drift=req.simulate_drift
    )

    return {
        "job_id": job_id,
        "collector_id": collector.id,
        "status": "running",
        "ws_url": f"/ws/jobs/{job_id}"
    }


@router.post("/teach")
async def teach_by_example(
    req: TeachScrapeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session)
):
    """
    Teach by Example (Section 5.3): Locates sample text on the page, derives generalized selectors,
    creates a collector, and executes the scrape.
    """
    rule = await teach_learner.learn_rule(req.url, req.label, req.example)
    field_name = rule["field_name"]
    selector = rule["selector"]

    collector_id = f"col_teach_{uuid.uuid4().hex[:8]}"
    selector_map = {field_name: selector}
    field_specs = [{"name": field_name, "description": req.label, "selector_hint": selector}]

    collector = Collector(
        id=collector_id,
        name=f"Teach-by-example for {req.url}",
        target_url=req.url,
        schema_version=1,
        active_selector_map=selector_map,
        field_specs=field_specs,
        status="active"
    )
    db.add(collector)

    job_id = f"job_teach_{uuid.uuid4().hex[:10]}"
    job = Job(
        id=job_id,
        collector_id=collector.id,
        url=req.url,
        mode="teach_by_example",
        status="running",
        plan=selector_map
    )
    db.add(job)
    db.commit()

    background_tasks.add_task(
        _execute_scrape_job,
        job_id=job_id,
        collector_id=collector.id,
        url=req.url,
        max_rows=20,
        simulate_drift=False
    )

    return {
        "job_id": job_id,
        "collector_id": collector.id,
        "learned_rule": rule,
        "status": "running",
        "ws_url": f"/ws/jobs/{job_id}"
    }


@router.post("/agentic")
async def agentic_scrape(
    req: AgenticScrapeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session)
):
    """
    Agentic Crawl (Section 5.4): Performs bounded multi-step autonomous navigation
    and schedules extraction for discovered endpoints.
    """
    result = await agentic_crawler.run_agentic_plan(
        start_url=req.url,
        goal=req.goal,
        max_steps=req.max_steps,
        timeout_seconds=req.timeout_seconds
    )

    target_url = result["discovered_urls"][0] if result["discovered_urls"] else req.url
    field_descriptions = ["title", "price", "description"]
    plan = await llm_client.generate_scrape_plan(target_url, field_descriptions)
    
    collector_id = f"col_agentic_{uuid.uuid4().hex[:8]}"
    selector_map = {f.name: f.selector_hint or f".{f.name}" for f in plan.fields}
    field_specs = [f.dict() for f in plan.fields]

    collector = Collector(
        id=collector_id,
        name=f"Agentic Collector: {req.goal[:30]}",
        target_url=target_url,
        schema_version=1,
        active_selector_map=selector_map,
        field_specs=field_specs
    )
    db.add(collector)

    job_id = f"job_agentic_{uuid.uuid4().hex[:10]}"
    job = Job(
        id=job_id,
        collector_id=collector.id,
        url=target_url,
        mode="agentic",
        status="running",
        plan={"goal": req.goal, "steps": result["step_logs"], "selectors": selector_map}
    )
    db.add(job)
    db.commit()

    background_tasks.add_task(
        _execute_scrape_job,
        job_id=job_id,
        collector_id=collector.id,
        url=target_url,
        max_rows=20,
        simulate_drift=False
    )

    return {
        "job_id": job_id,
        "collector_id": collector.id,
        "navigation": result,
        "status": "running",
        "ws_url": f"/ws/jobs/{job_id}"
    }


@router.get("/{job_id}")
async def get_job(job_id: str, db: Session = Depends(get_session)):
    """
    Polls status and structured records for a given job_id.
    """
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    rows = db.exec(select(ScrapedRow).where(ScrapedRow.job_id == job_id).order_by(ScrapedRow.row_index)).all()
    rows_data = [
        {**r.data, "karma_score": r.karma_score, "karma_flags": r.karma_flags}
        for r in rows
    ]

    return {
        "job_id": job.id,
        "collector_id": job.collector_id,
        "url": job.url,
        "status": job.status,
        "mode": job.mode,
        "row_count": len(rows_data),
        "avg_karma_score": job.avg_karma_score,
        "rows": rows_data,
        "error": job.error,
        "created_at": job.created_at,
        "completed_at": job.completed_at
    }


@router.get("/jobs")
async def list_jobs(limit: int = 20, db: Session = Depends(get_session)):
    jobs = db.exec(select(Job).order_by(Job.created_at.desc()).limit(limit)).all()
    return jobs


# ==========================================
# Background Execution Worker
# ==========================================

async def _execute_scrape_job(job_id: str, collector_id: str, url: str, max_rows: int, simulate_drift: bool = False):
    """
    Background worker that runs Bright Data Scraper Studio collector, calculates Scrape Karma,
    and updates DB / streams WebSocket updates.
    """
    from ..db import engine
    start_time = time.time()

    await ws_manager.send_log(job_id, f"Initializing Bright Data Scraper Studio collector for {url}...")
    await ws_manager.send_progress(job_id, 15, "Connecting to extraction gateway...")
    await asyncio.sleep(0.4)

    with Session(engine) as db:
        collector = db.get(Collector, collector_id)
        job = db.get(Job, job_id)
        if not collector or not job:
            return

        selectors = dict(collector.active_selector_map)
        if simulate_drift:
            # Purposefully introduce drift on the first selector
            first_key = list(selectors.keys())[0]
            selectors[first_key] = ".obsolete-legacy-broken-selector"

        await ws_manager.send_log(job_id, f"Dispatching active selectors: {list(selectors.keys())}")
        await ws_manager.send_progress(job_id, 45, "Extracting DOM records...")

        try:
            raw_rows = await brightdata_client.run_collector(
                collector_id=collector.brightdata_collector_id or collector.id,
                target_url=url,
                active_selectors=selectors,
                field_specs=collector.field_specs,
                max_rows=max_rows
            )

            await ws_manager.send_progress(job_id, 75, "Computing Scrape Karma scores & validation...")

            # Scrape Karma Scoring (Section 5.7)
            field_descs = {f["name"]: f.get("description", f["name"]) for f in (collector.field_specs or [])}
            evaluated_rows = []
            karma_sum = 0

            for idx, r in enumerate(raw_rows):
                score, flags = karma_engine.evaluate_row(r, field_descs)
                karma_sum += score
                r["karma_score"] = score
                
                scraped_row = ScrapedRow(
                    job_id=job_id,
                    collector_id=collector.id,
                    row_index=idx,
                    data=r,
                    karma_score=score,
                    karma_flags=flags
                )
                db.add(scraped_row)
                evaluated_rows.append(r)

            avg_karma = round(karma_sum / len(evaluated_rows), 1) if evaluated_rows else 0.0

            # Update Job & Collector
            job.status = "completed"
            job.row_count = len(evaluated_rows)
            job.avg_karma_score = avg_karma
            job.execution_time_ms = int((time.time() - start_time) * 1000)
            job.completed_at = datetime.utcnow()

            collector.total_runs += 1
            collector.updated_at = datetime.utcnow()
            db.add(job)
            db.add(collector)
            db.commit()

            await ws_manager.send_progress(job_id, 100, f"Extraction complete: {len(evaluated_rows)} rows (Avg Karma: {avg_karma})")
            await ws_manager.send_done(job_id, evaluated_rows, collector_id=collector.id)
            logger.info(f"Job {job_id} completed successfully with {len(evaluated_rows)} rows.")

        except Exception as e:
            logger.error(f"Job execution failed: {e}")
            job.status = "failed"
            job.error = str(e)
            db.add(job)
            db.commit()
            await ws_manager.send_error(job_id, f"Execution failed: {str(e)}")

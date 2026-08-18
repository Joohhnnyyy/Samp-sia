"""
NeuroScrape - Developer & Demo Utilities API (Sections 5.2.4, 5.9, 6.3)
Houses the live 'Simulate Site Change' trigger, preset connector gallery, and debug endpoints.
"""

import time
import uuid
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from bs4 import BeautifulSoup

from ..db import get_session
from ..models.schemas import Job, Collector, HealEvent, ScrapedRow
from ..connectors.registry import connector_registry
from ..scrapers.scrapling_fallback import scrapling_fetcher
from ..healing.heal_engine import heal_engine
from ..healing.neuroanchor import neuroanchor_engine
from ..healing.karma_score import karma_engine
from ..ws.manager import ws_manager

logger = logging.getLogger("neuroscrape.api.dev")
router = APIRouter(tags=["Dev & Demo Utilities"])


@router.post("/api/dev/simulate-site-change/{job_id}")
async def simulate_site_change(
    job_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session)
):
    """
    Demo Hero Feature (Section 5.2.4):
    1. Fetches current HTML for job's collector.
    2. Programmatically mutates class names/IDs/structure to break legacy selectors.
    3. Re-runs collector, detects broken fields, and triggers Two-Layer Self-Healing live.
    4. Streams real-time before/after diffs and resolution events over WebSocket.
    """
    job = db.get(Job, job_id)
    if not job or not job.collector_id:
        raise HTTPException(status_code=404, detail="Job or associated collector not found.")

    collector = db.get(Collector, job.collector_id)
    if not collector:
        raise HTTPException(status_code=404, detail="Collector not found")

    new_job_id = f"job_healed_{uuid.uuid4().hex[:8]}"
    new_job = Job(
        id=new_job_id,
        collector_id=collector.id,
        url=job.url,
        mode="self_heal_simulation",
        status="healing",
        plan=collector.active_selector_map
    )
    db.add(new_job)
    db.commit()

    background_tasks.add_task(
        _execute_simulated_heal_flow,
        target_job_id=job_id,
        new_job_id=new_job_id,
        collector_id=collector.id,
        url=job.url
    )

    return {
        "status": "healing_initiated",
        "job_id": new_job_id,
        "collector_id": collector.id,
        "message": "Site change simulation initiated. Self-heal replay streaming live.",
        "ws_url": f"/ws/jobs/{job_id}"  # stream to existing console listener
    }


@router.get("/api/connectors")
async def list_connectors():
    """Returns preset site connectors for the idea gallery."""
    return {"connectors": connector_registry.list_all()}


@router.get("/api/debug/embed")
async def debug_embed(text: str = "product price"):
    """Dev debug endpoint to inspect NeuroAnchor 384-dim embeddings."""
    emb = neuroanchor_engine.embed([text])[0]
    return {
        "text": text,
        "dimensions": len(emb),
        "sample_vector": [round(float(v), 4) for v in emb[:8]],
        "norm": round(float(sum(emb**2)**0.5), 4)
    }


# ==========================================
# Simulated Heal Worker
# ==========================================

async def _execute_simulated_heal_flow(target_job_id: str, new_job_id: str, collector_id: str, url: str):
    from ..db import engine
    
    await ws_manager.send_log(target_job_id, "⚠️ Target website update detected: DOM restructuring in progress...", "warn")
    await ws_manager.send_progress(target_job_id, 20, "Detecting broken selectors on mutated DOM...")
    await asyncio.sleep(0.5)

    # 1. Fetch HTML and mutate classes to simulate a real breaking website redesign
    original_html = await scrapling_fetcher.fetch_html(url)
    soup = BeautifulSoup(original_html, "html.parser")

    # Mutation: change .price -> .cost-amount-v2, .product-title -> .item-heading-v2
    for el in soup.find_all(class_=True):
        new_classes = []
        for c in el["class"]:
            if "price" in c:
                new_classes.append("cost-amount-v2")
            elif "title" in c:
                new_classes.append("item-heading-v2")
            elif "stock" in c:
                new_classes.append("inventory-badge-v2")
            else:
                new_classes.append(c)
        el["class"] = new_classes

    mutated_html = str(soup)

    with Session(engine) as db:
        collector = db.get(Collector, collector_id)
        job = db.get(Job, new_job_id)
        if not collector:
            return

        active_selectors = dict(collector.active_selector_map)
        healed_count = 0

        for field_spec in (collector.field_specs or []):
            f_name = field_spec["name"]
            f_desc = field_spec.get("description", f_name)
            old_selector = active_selectors.get(f_name, f".{f_name}")

            # Test selector on mutated HTML
            matches = soup.select(old_selector)
            if not matches:
                await ws_manager.send_log(target_job_id, f"❌ Selector broke for '{f_name}': '{old_selector}' returned 0 matches.", "error")
                await ws_manager.send_progress(target_job_id, 45, f"Re-anchoring '{f_name}' via Layer 1 NeuroAnchor model...")
                await asyncio.sleep(0.3)

                # Attempt Layer 1 NeuroAnchor healing
                healed, heal_evt = await heal_engine.attempt_healing(
                    db=db,
                    collector=collector,
                    job_id=new_job_id,
                    broken_field_name=f_name,
                    field_description=f_desc,
                    old_selector=old_selector,
                    current_html=mutated_html
                )

                if healed and heal_evt:
                    healed_count += 1
                    await ws_manager.send_heal_event(target_job_id, {
                        "field_name": f_name,
                        "method": heal_evt.method,
                        "before_selector": heal_evt.before_selector,
                        "after_selector": heal_evt.after_selector,
                        "confidence": heal_evt.confidence,
                        "latency_ms": heal_evt.latency_ms
                    })
                    await ws_manager.send_log(
                        target_job_id,
                        f"✨ Successfully healed '{f_name}' ({heal_evt.method}) in {heal_evt.latency_ms}ms with confidence {heal_evt.confidence:.2f}!",
                        "heal"
                    )

        # Re-extract rows with updated healed selectors
        updated_collector = db.get(Collector, collector_id)
        healed_selectors = updated_collector.active_selector_map if updated_collector else active_selectors
        
        extracted_rows = scrapling_fetcher.extract_from_html(
            html=mutated_html,
            selectors=healed_selectors,
            field_specs=collector.field_specs,
            max_rows=20
        )

        evaluated_rows = []
        field_descs = {f["name"]: f.get("description", f["name"]) for f in (collector.field_specs or [])}
        for idx, r in enumerate(extracted_rows):
            score, flags = karma_engine.evaluate_row(r, field_descs)
            r["karma_score"] = score
            evaluated_rows.append(r)
            db.add(ScrapedRow(
                job_id=new_job_id,
                collector_id=collector.id,
                row_index=idx,
                data=r,
                karma_score=score,
                karma_flags=flags
            ))

        if job:
            job.status = "completed"
            job.row_count = len(evaluated_rows)
            job.completed_at = datetime.utcnow()
            db.add(job)
        db.commit()

        await ws_manager.send_progress(target_job_id, 100, f"Self-healing verified: {healed_count} selectors repaired.")
        await ws_manager.send_done(target_job_id, evaluated_rows, collector_id=collector.id)

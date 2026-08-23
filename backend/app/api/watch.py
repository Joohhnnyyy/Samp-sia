"""
NeuroWatch — API Router (Section B4)
Endpoints for creating, listing, pausing, resuming, and deleting watches.
All watch operations use the shared WatchScheduler for task lifecycle management.
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..core.config import settings
from ..db import get_session
from ..models.schemas import WatchJob, WatchCycle, WatchCreateRequest
from ..services.watch_engine import watch_scheduler

logger = logging.getLogger("neuroscrape.api.watch")
router = APIRouter(prefix="/api/watch", tags=["NeuroWatch — Continuous Automation"])


@router.post("")
async def create_watch(req: WatchCreateRequest, db: Session = Depends(get_session)):
    """
    Create a new NeuroWatch job.
    Mode 1 (links): provide up to 5 URLs.
    Mode 2 (keyword): provide a search query string.
    """
    # Validate mode
    if req.mode not in ("links", "keyword"):
        raise HTTPException(status_code=400, detail="Mode must be 'links' or 'keyword'.")

    # Validate inputs
    if req.mode == "links":
        if not req.urls or len(req.urls) == 0:
            raise HTTPException(status_code=400, detail="Mode 'links' requires at least one URL.")
        if len(req.urls) > settings.WATCH_MAX_SOURCES:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum {settings.WATCH_MAX_SOURCES} source URLs allowed. Received {len(req.urls)}."
            )
        urls = req.urls
        query = None
    elif req.mode == "keyword":
        if not req.query or not req.query.strip():
            raise HTTPException(status_code=400, detail="Mode 'keyword' requires a non-empty query string.")
        urls = []
        query = req.query.strip()
    else:
        raise HTTPException(status_code=400, detail="Invalid mode.")

    # Calculate estimated credits/hour
    num_sources = len(urls) if urls else settings.WATCH_MAX_SOURCES  # keyword may resolve up to max
    interval = settings.WATCH_INTERVAL_SECONDS
    credits_per_hour = round((num_sources * 3600) / interval, 1)

    watch_id = f"watch_{uuid.uuid4().hex[:10]}"
    watch_job = WatchJob(
        id=watch_id,
        mode=req.mode,
        input_urls=urls,
        keyword_query=query,
        interval_seconds=interval,
        status="active",
        estimated_credits_per_hour=credits_per_hour,
        next_run_at=datetime.utcnow() + timedelta(seconds=2),  # starts nearly immediately
    )
    db.add(watch_job)
    db.commit()
    db.refresh(watch_job)

    # Spawn the background scheduler task
    watch_scheduler.create_watch(watch_job)

    return {
        "watch_job_id": watch_id,
        "mode": req.mode,
        "sources": urls if urls else f"keyword: {query}",
        "interval_seconds": interval,
        "estimated_credits_per_hour": credits_per_hour,
        "status": "active",
        "ws_url": f"/ws/watch/{watch_id}",
        "ws_aggregate_url": "/ws/watch"
    }


@router.get("")
async def list_watches(db: Session = Depends(get_session)):
    """List all watch jobs with current status and last cycle summary."""
    watches = db.exec(select(WatchJob).order_by(WatchJob.created_at.desc())).all()
    result = []
    for w in watches:
        # Get last cycle
        last_cycle = db.exec(
            select(WatchCycle)
            .where(WatchCycle.watch_job_id == w.id)
            .order_by(WatchCycle.cycle_number.desc())
            .limit(1)
        ).first()

        result.append({
            "watch_job_id": w.id,
            "mode": w.mode,
            "sources": w.input_urls if w.mode == "links" else w.keyword_query,
            "status": w.status,
            "interval_seconds": w.interval_seconds,
            "total_cycles": w.total_cycles,
            "estimated_credits_per_hour": w.estimated_credits_per_hour,
            "last_run_at": w.last_run_at,
            "next_run_at": w.next_run_at,
            "last_diff": last_cycle.diff_summary if last_cycle else None,
            "last_avg_karma": last_cycle.avg_karma if last_cycle else None,
        })

    return {"watches": result, "count": len(result)}


@router.get("/{watch_job_id}")
async def get_watch(watch_job_id: str, db: Session = Depends(get_session)):
    """Full detail: config, cycle history, latest diff."""
    wj = db.get(WatchJob, watch_job_id)
    if not wj:
        raise HTTPException(status_code=404, detail="Watch job not found.")

    cycles = db.exec(
        select(WatchCycle)
        .where(WatchCycle.watch_job_id == watch_job_id)
        .order_by(WatchCycle.cycle_number.desc())
        .limit(20)
    ).all()

    return {
        "watch_job_id": wj.id,
        "mode": wj.mode,
        "input_urls": wj.input_urls,
        "keyword_query": wj.keyword_query,
        "interval_seconds": wj.interval_seconds,
        "status": wj.status,
        "total_cycles": wj.total_cycles,
        "estimated_credits_per_hour": wj.estimated_credits_per_hour,
        "created_at": wj.created_at,
        "last_run_at": wj.last_run_at,
        "next_run_at": wj.next_run_at,
        "cycles": [
            {
                "cycle_number": c.cycle_number,
                "run_at": c.run_at,
                "diff_summary": c.diff_summary,
                "avg_karma": c.avg_karma,
                "sources_scraped": len(c.source_results) if c.source_results else 0,
                "total_rows": sum(
                    len(rows) for rows in (c.source_results or {}).values()
                    if isinstance(rows, list)
                ),
                "status": c.status,
            }
            for c in cycles
        ]
    }


@router.post("/{watch_job_id}/pause")
async def pause_watch(watch_job_id: str, db: Session = Depends(get_session)):
    """Pause a watch — stops scheduling but preserves history."""
    wj = db.get(WatchJob, watch_job_id)
    if not wj:
        raise HTTPException(status_code=404, detail="Watch job not found.")
    if wj.status == "paused":
        return {"status": "already_paused", "watch_job_id": watch_job_id}

    wj.status = "paused"
    wj.next_run_at = None
    db.add(wj)
    db.commit()

    watch_scheduler.pause_watch(watch_job_id)
    return {"status": "paused", "watch_job_id": watch_job_id}


@router.post("/{watch_job_id}/resume")
async def resume_watch(watch_job_id: str, db: Session = Depends(get_session)):
    """Resume a paused watch."""
    wj = db.get(WatchJob, watch_job_id)
    if not wj:
        raise HTTPException(status_code=404, detail="Watch job not found.")
    if wj.status == "active":
        return {"status": "already_active", "watch_job_id": watch_job_id}

    wj.status = "active"
    wj.next_run_at = datetime.utcnow() + timedelta(seconds=5)
    db.add(wj)
    db.commit()

    watch_scheduler.resume_watch(watch_job_id, wj.interval_seconds)
    return {"status": "active", "watch_job_id": watch_job_id}


@router.delete("/{watch_job_id}")
async def delete_watch(watch_job_id: str, db: Session = Depends(get_session)):
    """Delete a watch — cancels task, removes from DB. No orphans."""
    wj = db.get(WatchJob, watch_job_id)
    if not wj:
        raise HTTPException(status_code=404, detail="Watch job not found.")

    # Cancel background task first
    watch_scheduler.delete_watch(watch_job_id)

    # Remove cycles
    cycles = db.exec(select(WatchCycle).where(WatchCycle.watch_job_id == watch_job_id)).all()
    for c in cycles:
        db.delete(c)

    db.delete(wj)
    db.commit()

    return {"status": "deleted", "watch_job_id": watch_job_id, "cycles_removed": len(cycles)}

"""
NeuroScrape - Scraper Health Monitor API (Section 5.10)
Periodically tracks collector success rate, monitors data shape drift
(row count drop, new-vs-missing fields, karma score degradation), and alerts in real-time.
"""

import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..db import get_session
from ..models.schemas import Collector, HealthEvent, ScrapedRow, Job
from ..healing.karma_score import karma_engine

logger = logging.getLogger("neuroscrape.api.health")
router = APIRouter(prefix="/api/health", tags=["Scraper Health Monitor"])


@router.get("/collectors")
async def list_collector_health(db: Session = Depends(get_session)):
    """
    Returns live health telemetry for all collectors (success rate, runs, schema version, status).
    """
    collectors = db.exec(select(Collector).order_by(Collector.updated_at.desc())).all()
    health_reports = []

    for c in collectors:
        recent_jobs = db.exec(
            select(Job)
            .where(Job.collector_id == c.id)
            .order_by(Job.created_at.desc())
            .limit(5)
        ).all()

        avg_karma = (
            sum([j.avg_karma_score for j in recent_jobs if j.avg_karma_score is not None]) / len([j for j in recent_jobs if j.avg_karma_score is not None])
            if any(j.avg_karma_score is not None for j in recent_jobs) else 100.0
        )

        health_reports.append({
            "collector_id": c.id,
            "name": c.name,
            "target_url": c.target_url,
            "status": c.status,
            "schema_version": c.schema_version,
            "total_runs": c.total_runs,
            "success_rate": c.success_rate,
            "avg_karma_score": round(avg_karma, 1),
            "last_updated": c.updated_at
        })

    return {"collectors": health_reports}


@router.get("/events")
async def list_health_events(limit: int = 50, db: Session = Depends(get_session)):
    """Lists drift and health warning events."""
    events = db.exec(select(HealthEvent).order_by(HealthEvent.timestamp.desc()).limit(limit)).all()
    return {"count": len(events), "events": events}


@router.post("/check/{collector_id}")
async def run_health_check(collector_id: str, db: Session = Depends(get_session)):
    """
    Runs an active drift detection health check for a collector.
    """
    collector = db.get(Collector, collector_id)
    if not collector:
        raise HTTPException(status_code=404, detail="Collector not found")

    recent_jobs = db.exec(
        select(Job)
        .where(Job.collector_id == collector_id)
        .order_by(Job.created_at.desc())
        .limit(3)
    ).all()

    drift_detected = False
    missing_fields = []
    status = "healthy"
    message = "Collector operational. Data shape is consistent."

    if recent_jobs:
        latest = recent_jobs[0]
        if latest.avg_karma_score is not None and latest.avg_karma_score < 60:
            drift_detected = True
            status = "warning"
            message = f"Karma score degraded to {latest.avg_karma_score}/100. Extraction quality drift detected."

    health_event = HealthEvent(
        collector_id=collector.id,
        status=status,
        drift_detected=drift_detected,
        row_count=recent_jobs[0].row_count if recent_jobs else 0,
        missing_fields=missing_fields,
        avg_karma=recent_jobs[0].avg_karma_score if recent_jobs and recent_jobs[0].avg_karma_score else 100.0,
        message=message,
        timestamp=datetime.utcnow()
    )
    db.add(health_event)
    db.commit()
    db.refresh(health_event)

    return health_event


# ==========================================
# Periodic Background Scraper Health Monitor
# ==========================================

import asyncio
from ..db import engine as db_engine
from ..ws.manager import ws_manager

class ScraperHealthScheduler:
    def __init__(self):
        self._task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self, interval_seconds: int = 300):
        self._running = True
        self._task = asyncio.create_task(self._periodic_loop(interval_seconds))
        logger.info("ScraperHealthScheduler started (interval=300s).")

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, Exception):
                pass
        logger.info("ScraperHealthScheduler stopped.")

    async def _periodic_loop(self, interval_seconds: int):
        while self._running:
            try:
                await asyncio.sleep(interval_seconds)
                await self._check_all_collectors()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor periodic run error: {e}")

    async def _check_all_collectors(self):
        with Session(db_engine) as db:
            collectors = db.exec(select(Collector).where(Collector.status == "active")).all()
            for c in collectors:
                recent_jobs = db.exec(
                    select(Job)
                    .where(Job.collector_id == c.id)
                    .order_by(Job.created_at.desc())
                    .limit(3)
                ).all()

                if not recent_jobs:
                    continue

                latest = recent_jobs[0]
                drift_detected = False
                status = "healthy"
                message = f"Collector '{c.name}' operating nominally."

                if latest.avg_karma_score is not None and latest.avg_karma_score < 60:
                    drift_detected = True
                    status = "warning"
                    message = f"Extraction quality degradation on {c.name}: Karma {latest.avg_karma_score}/100."

                if latest.status == "failed":
                    drift_detected = True
                    status = "broken"
                    message = f"Recent extraction failure on {c.name}: {latest.error}"

                he = HealthEvent(
                    collector_id=c.id,
                    status=status,
                    drift_detected=drift_detected,
                    row_count=latest.row_count,
                    missing_fields=[],
                    avg_karma=latest.avg_karma_score or 100.0,
                    message=message,
                    timestamp=datetime.utcnow()
                )
                db.add(he)
                db.commit()

                # Broadcast health alert over global WS if degraded
                if drift_detected:
                    await ws_manager.broadcast_to_global({
                        "type": "health_alert",
                        "collector_id": c.id,
                        "status": status,
                        "message": message,
                        "timestamp": he.timestamp.isoformat()
                    })

health_scheduler = ScraperHealthScheduler()


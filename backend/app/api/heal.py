"""
NeuroScrape - Self-Healing API Router (Section 5.2)
Feeds the "Self-Healing Replay" visualization screen: timeline of heal events,
before/after selector diffs, confidence scores, layer resolution metrics,
and Git-like schema version commits.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..db import get_session
from ..models.schemas import Collector, HealEvent, SchemaVersion

logger = logging.getLogger("neuroscrape.api.heal")
router = APIRouter(tags=["Self-Healing Engine"])


@router.get("/api/heal-events/{collector_id}")
async def get_collector_heal_events(collector_id: str, db: Session = Depends(get_session)):
    """
    Returns all heal events for a specific collector ordered by timestamp descending.
    Powers the hero Self-Healing Replay UI visualization.
    """
    collector = db.get(Collector, collector_id)
    if not collector:
        raise HTTPException(status_code=404, detail="Collector not found")

    events = db.exec(
        select(HealEvent)
        .where(HealEvent.collector_id == collector_id)
        .order_by(HealEvent.timestamp.desc())
    ).all()

    return {
        "collector_id": collector_id,
        "total_heals": len(events),
        "current_schema_version": collector.schema_version,
        "active_selectors": collector.active_selector_map,
        "events": events
    }


@router.get("/api/heal-events")
async def list_all_heal_events(limit: int = 50, db: Session = Depends(get_session)):
    """Lists recent heal events across all collectors."""
    events = db.exec(select(HealEvent).order_by(HealEvent.timestamp.desc()).limit(limit)).all()
    return {
        "count": len(events),
        "events": events
    }


@router.get("/api/schema-history/{collector_id}")
async def get_schema_history(collector_id: str, db: Session = Depends(get_session)):
    """
    Returns Git-style commit log for schema versions of a collector.
    """
    versions = db.exec(
        select(SchemaVersion)
        .where(SchemaVersion.collector_id == collector_id)
        .order_by(SchemaVersion.version_num.asc())
    ).all()

    return {
        "collector_id": collector_id,
        "versions": versions
    }

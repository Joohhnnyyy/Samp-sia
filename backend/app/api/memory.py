"""
NeuroScrape / SaMp - NeuroAnchor Collective Memory API Router (Section 3.6)
Exposes explainability endpoints for judges, developer inspection, and live UI dashboards.
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from ..db import get_session
from ..healing.collective_memory import collective_memory
from ..healing.field_normalizer import field_normalizer

logger = logging.getLogger("neuroscrape.api.memory")
router = APIRouter(prefix="/api/memory", tags=["Collective Memory — Immune System"])


@router.get("/stats")
async def get_collective_memory_stats(db: Session = Depends(get_session)):
    """
    Returns headline immune memory metrics:
    - Total cross-site patterns learned
    - First-try resolution rate overall %
    - First-try resolution rate on genuinely new / unseen sites %
    - Average reinforcement count
    - Patterns breakdown by canonical field_type
    - Most reinforced patterns and origin sites
    """
    stats = collective_memory.get_memory_stats(db)
    return stats


@router.get("/taxonomy")
async def get_taxonomy():
    """
    Returns the canonical field taxonomy and synonyms dictionary.
    """
    return {
        "total_categories": len(field_normalizer.taxonomy),
        "taxonomy": field_normalizer.taxonomy
    }


@router.get("/{field_type}")
async def get_patterns_by_field_type(field_type: str):
    """
    Returns all stored immune patterns for a specific canonical field type (e.g. price, title, stock_status).
    """
    patterns = collective_memory.get_field_type_patterns(field_type)
    canonical_type, _ = field_normalizer.normalize(field_type)
    return {
        "field_type_queried": field_type,
        "canonical_field_type": canonical_type,
        "patterns_count": len(patterns),
        "patterns": patterns
    }


@router.post("/prune")
async def prune_degraded_memory(
    min_confidence: float = Query(0.40, ge=0.1, le=0.9),
    max_age_days: int = Query(30, ge=1, le=365)
):
    """
    Prunes degraded memory patterns below the confidence floor or older than max_age_days.
    """
    deleted_count = collective_memory.prune(min_confidence=min_confidence, max_age_days=max_age_days)
    return {
        "status": "success",
        "pruned_patterns_count": deleted_count,
        "active_patterns_remaining": len(collective_memory._memory_store)
    }

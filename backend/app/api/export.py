"""
NeuroScrape - Universal Export Layer (Section 5.5)
Inspired by Firecrawl: One endpoint with query param format=json|csv|markdown|rag_chunks.
"""

import io
import csv
import json
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlmodel import Session, select
from ..db import get_session
from ..models.schemas import Job, ScrapedRow
from ..rag.rag_engine import rag_engine

logger = logging.getLogger("neuroscrape.api.export")
router = APIRouter(prefix="/api/export", tags=["Universal Exporter"])


@router.get("/{job_id}")
async def export_job(
    job_id: str,
    format: str = Query("json", pattern="^(json|csv|markdown|rag_chunks)$"),
    db: Session = Depends(get_session)
):
    """
    Exports scraped data for job_id into requested format: json, csv, markdown, or rag_chunks.
    """
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    rows = db.exec(select(ScrapedRow).where(ScrapedRow.job_id == job_id).order_by(ScrapedRow.row_index)).all()
    if not rows:
        raise HTTPException(status_code=400, detail="Job has no scraped rows to export.")

    data_rows = [{**r.data, "karma_score": r.karma_score} for r in rows]

    # 1. JSON Export
    if format == "json":
        payload = {
            "job_id": job.id,
            "collector_id": job.collector_id,
            "target_url": job.url,
            "total_rows": len(data_rows),
            "avg_karma_score": job.avg_karma_score,
            "exported_at": str(job.completed_at or job.created_at),
            "data": data_rows
        }
        return Response(
            content=json.dumps(payload, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=neuroscrape_{job_id}.json"}
        )

    # 2. CSV Export
    elif format == "csv":
        all_keys = list(data_rows[0].keys())
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=all_keys)
        writer.writeheader()
        for r in data_rows:
            writer.writerow({k: r.get(k, "") for k in all_keys})
        
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=neuroscrape_{job_id}.csv"}
        )

    # 3. Clean Markdown Export
    elif format == "markdown":
        all_keys = list(data_rows[0].keys())
        cols_header = " | ".join(all_keys)
        separator = " | ".join(["---"] * len(all_keys))
        
        md_lines = [
            f"# Scraped Knowledge Report — {job.url}",
            f"**Job ID**: `{job_id}` | **Rows**: {len(data_rows)} | **Karma Trust Score**: {job.avg_karma_score}/100",
            "",
            f"| {cols_header} |",
            f"| {separator} |"
        ]

        for r in data_rows:
            row_str = " | ".join([str(r.get(k, "")).replace("\n", " ").replace("|", "\\|") for k in all_keys])
            md_lines.append(f"| {row_str} |")

        md_content = "\n".join(md_lines)
        return Response(
            content=md_content,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=neuroscrape_{job_id}.md"}
        )

    # 4. RAG Chunks Export (Pre-split with overlap for vector databases)
    elif format == "rag_chunks":
        chunks = rag_engine.chunk_records(data_rows, source_url=job.url, job_id=job.id)
        payload = {
            "job_id": job.id,
            "source_url": job.url,
            "chunk_count": len(chunks),
            "chunks": [c.dict() for c in chunks]
        }
        return Response(
            content=json.dumps(payload, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=neuroscrape_{job_id}_rag_chunks.json"}
        )

"""
NeuroScrape - Scrape to RAG API Router (Section 5.6)
Turns any scraped documentation/catalog into an instant queryable Q&A knowledge base
with source citations.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..db import get_session
from ..models.schemas import Job, ScrapedRow, RAGIndexRequest, RAGAskRequest
from ..rag.rag_engine import rag_engine

logger = logging.getLogger("neuroscrape.api.rag")
router = APIRouter(prefix="/api/rag", tags=["Scrape → RAG Engine"])


@router.post("/index/{job_id}")
async def index_job_to_rag(job_id: str, db: Session = Depends(get_session)):
    """
    Indexes scraped data for job_id into ChromaDB using the local NeuroAnchor model.
    """
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    rows = db.exec(select(ScrapedRow).where(ScrapedRow.job_id == job_id)).all()
    if not rows:
        raise HTTPException(status_code=400, detail="No rows found for this job to index.")

    data_rows = [r.data for r in rows]
    chunks_indexed = await rag_engine.index_job_data(
        job_id=job.id,
        rows=data_rows,
        source_url=job.url
    )

    return {
        "job_id": job.id,
        "collection_name": f"job_{job_id.replace('-', '_')}",
        "chunks_indexed": chunks_indexed,
        "status": "ready"
    }


@router.post("/ask")
async def ask_rag(req: RAGAskRequest):
    """
    Answers questions with citations using the vector-indexed scraped records.
    """
    response = await rag_engine.ask(
        question=req.question,
        collection_name=req.collection_name,
        job_id=req.job_id,
        top_k=req.top_k
    )
    return response.dict()

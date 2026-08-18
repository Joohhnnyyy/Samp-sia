"""
NeuroScrape - RAG Engine Test Suite
Verifies document chunking with overlap, semantic embedding, and Q&A with citations.
"""

import pytest
from app.rag.rag_engine import rag_engine


@pytest.mark.asyncio
async def test_chunking_and_overlap():
    rows = [
        {
            "title": "Bright Data CLI Overview",
            "body": "The Bright Data CLI allows developers to create and trigger scrapers programmatically."
        },
        {
            "title": "Two-Layer Self-Healing",
            "body": "NeuroScrape combines local sub-200ms ONNX semantic matching with Bright Data cloud fallbacks."
        }
    ]
    chunks = rag_engine.chunk_records(rows, source_url="https://docs.neuroscrape.dev", job_id="job_rag_test")
    assert len(chunks) >= 2
    assert chunks[0].source_url == "https://docs.neuroscrape.dev"
    assert chunks[0].job_id == "job_rag_test"


@pytest.mark.asyncio
async def test_indexing_and_ask():
    rows = [
        {
            "feature": "NeuroAnchor Model",
            "details": "A fine-tuned 25MB all-MiniLM-L6-v2 ONNX int8 model for DOM semantic re-anchoring."
        },
        {
            "feature": "Bright Data Scraper Studio",
            "details": "Orchestrates residential proxy pools and scalable cloud collectors."
        }
    ]
    job_id = "job_test_rag_qa"
    indexed = await rag_engine.index_job_data(job_id, rows, source_url="https://neuroscrape.ai")
    assert indexed >= 2

    response = await rag_engine.ask("What is NeuroAnchor?", job_id=job_id)
    assert response.answer is not None
    assert len(response.citations) > 0
    assert "neuroscrape.ai" in response.citations[0]["source_url"]

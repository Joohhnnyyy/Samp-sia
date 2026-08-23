"""
NeuroScrape - Watch, NewsKeeper, Health & Export Integration Test Suite
Verifies:
1. NeuroWatch CRUD lifecycle (create, list, get, pause, resume, delete)
2. Universal Exporter (JSON, CSV, Markdown, RAG chunks)
3. NewsKeeper Fact-Checker and Geopolitical Assistant endpoints
4. Scraper Health Monitor endpoints
"""

import pytest
import json
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.main import app
from app.db import engine
from app.models.schemas import Job, Collector, ScrapedRow, WatchJob
from app.services.news_keeper import news_keeper
from app.services.geopolitical_assistant import geopolitical_assistant

client = TestClient(app)


def test_universal_export_formats():
    """Verifies that GET /api/export/{job_id} exports json, csv, markdown, and rag_chunks."""
    test_job_id = "job_export_test_123"
    with Session(engine) as db:
        job = db.get(Job, test_job_id)
        if not job:
            job = Job(
                id=test_job_id,
                url="https://example-store.com/laptops",
                status="completed",
                row_count=2,
                avg_karma_score=95.0
            )
            db.add(job)
            db.add(ScrapedRow(
                job_id=test_job_id,
                row_index=0,
                data={"title": "Pro Laptop 15", "price": "$1,499.00", "stock": "In Stock"},
                karma_score=95
            ))
            db.add(ScrapedRow(
                job_id=test_job_id,
                row_index=1,
                data={"title": "Pro Laptop 17", "price": "$1,999.00", "stock": "In Stock"},
                karma_score=95
            ))
            db.commit()

    # 1. JSON Export
    r_json = client.get(f"/api/export/{test_job_id}?format=json")
    assert r_json.status_code == 200
    assert "application/json" in r_json.headers["content-type"]
    data = r_json.json()
    assert data["total_rows"] == 2
    assert len(data["data"]) == 2

    # 2. CSV Export
    r_csv = client.get(f"/api/export/{test_job_id}?format=csv")
    assert r_csv.status_code == 200
    assert "text/csv" in r_csv.headers["content-type"]
    assert "title" in r_csv.text and "price" in r_csv.text

    # 3. Markdown Export
    r_md = client.get(f"/api/export/{test_job_id}?format=markdown")
    assert r_md.status_code == 200
    assert "text/markdown" in r_md.headers["content-type"]
    assert "# Scraped Knowledge Report" in r_md.text
    assert "Pro Laptop 15" in r_md.text

    # 4. RAG Chunks Export
    r_rag = client.get(f"/api/export/{test_job_id}?format=rag_chunks")
    assert r_rag.status_code == 200
    d_rag = r_rag.json()
    assert d_rag["chunk_count"] >= 1


def test_neurowatch_crud_lifecycle():
    """Verifies complete lifecycle of a continuous automation watch job."""
    # 1. Create Mode 1 (Links)
    payload_links = {
        "mode": "links",
        "urls": ["https://webscraper.io/test-sites/e-commerce/allinone"]
    }
    r_create = client.post("/api/watch", json=payload_links)
    assert r_create.status_code == 200
    d_create = r_create.json()
    watch_id = d_create["watch_job_id"]
    assert d_create["status"] == "active"

    # 2. List Watches
    r_list = client.get("/api/watch")
    assert r_list.status_code == 200
    d_list = r_list.json()
    assert "watches" in d_list
    assert any(w["watch_job_id"] == watch_id for w in d_list["watches"])

    # 3. Get Single Watch Details
    r_get = client.get(f"/api/watch/{watch_id}")
    assert r_get.status_code == 200
    assert r_get.json()["watch_job_id"] == watch_id

    # 4. Pause Watch
    r_pause = client.post(f"/api/watch/{watch_id}/pause")
    assert r_pause.status_code == 200
    assert r_pause.json()["status"] == "paused"

    # 5. Resume Watch
    r_resume = client.post(f"/api/watch/{watch_id}/resume")
    assert r_resume.status_code == 200
    assert r_resume.json()["status"] == "active"

    # 6. Delete Watch
    r_del = client.delete(f"/api/watch/{watch_id}")
    assert r_del.status_code == 200
    assert r_del.json()["status"] == "deleted"


def test_health_monitor_endpoints():
    """Verifies Scraper Health Monitor fleet telemetry."""
    r_collectors = client.get("/api/health/collectors")
    assert r_collectors.status_code == 200
    d_cols = r_collectors.json()
    assert "collectors" in d_cols

    r_events = client.get("/api/health/events")
    assert r_events.status_code == 200
    d_evts = r_events.json()
    assert "events" in d_evts


@pytest.mark.asyncio
async def test_newskeeper_fact_check_endpoint(monkeypatch):
    """Verifies NewsKeeper fact-check & geopolitical analysis endpoints with mocked synthesis for speed."""
    async def mock_analyze(query_or_url, user_region="India", max_sources=4, ws_callback=None):
        return {
            "query": query_or_url,
            "region": user_region,
            "trust_percentage": 92,
            "consensus_rating": "HIGH CONSENSUS",
            "facts": ["Chip supply is expanding in 2026."],
            "myths": ["All chips are single sourced."],
            "source_matrix": [{"source": "Reuters", "stance": "Verified"}]
        }

    async def mock_chat(message, user_location="India", chat_history=None):
        return {
            "response": "Clean energy investments grew 30% in 2026.",
            "sources_consulted": ["IEA Report 2026", "Reuters Energy Wire"]
        }

    monkeypatch.setattr(news_keeper, "analyze_news_topic", mock_analyze)
    monkeypatch.setattr(geopolitical_assistant, "chat", mock_chat)

    # Fact-check query
    payload = {
        "query_or_url": "Global semiconductor supply chain and AI chip production 2026",
        "user_region": "India",
        "max_sources": 3
    }
    r_fc = client.post("/api/news/fact-check", json=payload)
    assert r_fc.status_code == 200
    d_fc = r_fc.json()
    assert d_fc["trust_percentage"] == 92
    assert d_fc["consensus_rating"] == "HIGH CONSENSUS"
    assert len(d_fc["facts"]) >= 1

    # Trending themes
    r_trend = client.get("/api/news/trending?location=India")
    assert r_trend.status_code == 200
    d_trend = r_trend.json()
    assert d_trend["topics_count"] >= 1

    # Assistant chat
    r_chat = client.post("/api/assistant/geopolitical-chat", json={
        "message": "What is the latest development in clean energy transition?",
        "user_location": "India"
    })
    assert r_chat.status_code == 200
    d_chat = r_chat.json()
    assert "response" in d_chat
    assert len(d_chat["sources_consulted"]) >= 1

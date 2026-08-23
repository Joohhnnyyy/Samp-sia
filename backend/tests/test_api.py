"""
NeuroScrape - API Test Suite
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["neuroanchor_loaded"] is True


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "SaMp" in response.text or "NeuroScrape" in response.text or "text/html" in response.headers.get("content-type", "")


def test_generate_scrape_plan():
    payload = {
        "url": "https://example-store.com/laptops",
        "fields": ["product title", "price in USD", "stock status"]
    }
    response = client.post("/api/scrape/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "plan" in data
    assert len(data["plan"]["fields"]) == 3
    assert data["compliance"]["allowed"] is True


def test_connectors_gallery():
    response = client.get("/api/connectors")
    assert response.status_code == 200
    data = response.json()
    assert len(data["connectors"]) >= 4
    categories = [c["category"] for c in data["connectors"]]
    assert "Price Intelligence" in categories
    assert "Docs-to-RAG" in categories


def test_debug_embed():
    response = client.get("/api/debug/embed?text=product%20price")
    assert response.status_code == 200
    data = response.json()
    assert data["dimensions"] == 384
    assert len(data["sample_vector"]) == 8

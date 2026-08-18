"""
NeuroScrape - Scrapers Test Suite
Verifies Teach by Example, Scrapling Fallback, and Agentic Multi-Step Crawler.
"""

import pytest
from app.scrapers.teach_by_example import teach_learner
from app.scrapers.scrapling_fallback import scrapling_fetcher
from app.scrapers.agentic_crawler import agentic_crawler


@pytest.mark.asyncio
async def test_teach_by_example_learner():
    url = "https://example-store.com/laptops"
    rule = await teach_learner.learn_rule(url=url, label="price", example_text="$2,499.00")
    assert rule is not None
    assert rule["field_name"] == "price"
    assert "selector" in rule
    assert rule["confidence"] >= 0.7


@pytest.mark.asyncio
async def test_scrapling_fallback_extraction():
    url = "https://example-store.com/laptops"
    selectors = {
        "title": ".product-title",
        "price": ".product-price",
        "stock": ".stock-status"
    }
    field_specs = [
        {"name": "title", "description": "product title"},
        {"name": "price", "description": "price"},
        {"name": "stock", "description": "stock status"}
    ]
    rows = await scrapling_fetcher.fetch_and_extract(url, selectors, field_specs, max_rows=5)
    assert len(rows) >= 1
    assert "title" in rows[0]
    assert "price" in rows[0]


@pytest.mark.asyncio
async def test_agentic_crawler_bounded_navigation():
    url = "https://example-store.com"
    res = await agentic_crawler.run_agentic_plan(
        start_url=url,
        goal="discover all product pages",
        max_steps=2,
        timeout_seconds=5
    )
    assert res["status"] == "completed"
    assert res["steps_executed"] <= 2
    assert len(res["discovered_urls"]) >= 1

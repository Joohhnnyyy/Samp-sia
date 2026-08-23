"""
NeuroScrape / SaMp - Cold-Start Collective Memory Seeder (Section 3.5)
Populates initial cross-site immune patterns across representative site archetypes
(e-commerce, docs-to-rag, tech job boards, and github releases) so the model
can pre-heal fields on brand-new unseen sites immediately.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add backend directory to sys.path
backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.healing.collective_memory import collective_memory
from app.healing.field_normalizer import field_normalizer

SEED_PATTERNS = [
    # E-Commerce & Retail Archetypes
    {
        "field": "product price",
        "selector": ".price, .product-price, [data-price], span.a-price-whole, .cost-amount-v2, .amount",
        "site": "amazon.com",
        "method": "teach_by_example",
        "confidence": 0.96,
        "context": {"tag": "span", "classes": "price product-price", "attr_str": "itemprop='price'", "text": "$1,299.00"}
    },
    {
        "field": "product title",
        "selector": "h1.product-title, .title, h1, h2.product-heading-v2, [data-title]",
        "site": "shopify-stores.com",
        "method": "local_model",
        "confidence": 0.94,
        "context": {"tag": "h1", "classes": "product-title heading", "attr_str": "itemprop='name'", "text": "Pro Carbon Pickleball Paddle"}
    },
    {
        "field": "stock status",
        "selector": ".stock, .availability, [data-stock], .inventory-badge-v2, .in-stock",
        "site": "bestbuy.com",
        "method": "local_model",
        "confidence": 0.92,
        "context": {"tag": "span", "classes": "stock availability in-stock", "attr_str": "", "text": "In Stock — Ready to ship"}
    },
    {
        "field": "customer rating",
        "selector": ".ratings, .rating-stars, [data-rating], .review-score, .stars-count",
        "site": "walmart.com",
        "method": "local_model",
        "confidence": 0.91,
        "context": {"tag": "div", "classes": "ratings review-stars", "attr_str": "aria-label='4.8 out of 5 stars'", "text": "4.8 (1,240 reviews)"}
    },
    {
        "field": "product image",
        "selector": "img.product-image, .main-image img, [data-hero-img], .carousel-img",
        "site": "target.com",
        "method": "local_model",
        "confidence": 0.93,
        "context": {"tag": "img", "classes": "product-image primary", "attr_str": "src='https://cdn.store.com/shoe.jpg'", "text": ""}
    },

    # Tech Job Boards & Salary Trackers
    {
        "field": "job title",
        "selector": "h2.job-title, .title a, .position-title, h1.role",
        "site": "news.ycombinator.com",
        "method": "teach_by_example",
        "confidence": 0.95,
        "context": {"tag": "h2", "classes": "job-title role", "attr_str": "", "text": "Senior Distributed Systems Engineer"}
    },
    {
        "field": "company name",
        "selector": ".company, .employer, .company-name, [data-company]",
        "site": "greenhouse.io",
        "method": "local_model",
        "confidence": 0.92,
        "context": {"tag": "span", "classes": "company-name employer", "attr_str": "", "text": "Anthropic AI"}
    },
    {
        "field": "salary compensation",
        "selector": ".salary, .compensation, .pay-range, [data-salary]",
        "site": "levels.fyi",
        "method": "local_model",
        "confidence": 0.94,
        "context": {"tag": "span", "classes": "salary compensation-range", "attr_str": "", "text": "$180,000 - $240,000 / year"}
    },
    {
        "field": "work location",
        "selector": ".location, .remote-badge, [data-location], .workplace-type",
        "site": "lever.co",
        "method": "local_model",
        "confidence": 0.90,
        "context": {"tag": "span", "classes": "location remote-badge", "attr_str": "", "text": "San Francisco, CA (Hybrid / Remote)"}
    },

    # Documentation & RAG Knowledge Repositories
    {
        "field": "section heading",
        "selector": "h2.section-header, h3.subheading, .doc-heading, article h2",
        "site": "docs.brightdata.com",
        "method": "local_model",
        "confidence": 0.95,
        "context": {"tag": "h2", "classes": "section-header doc-heading", "attr_str": "id='overview'", "text": "Getting Started with Scraper Studio"}
    },
    {
        "field": "code snippet",
        "selector": "pre code, .code-block, pre, div.highlight pre",
        "site": "fastapi.tiangolo.com",
        "method": "local_model",
        "confidence": 0.97,
        "context": {"tag": "pre", "classes": "highlight code-block", "attr_str": "", "text": "uvicorn app.main:app --reload"}
    },

    # Developer Changelogs & GitHub OSS Releases
    {
        "field": "release version",
        "selector": ".release-header, .tag, h1 a, .version-tag, [data-version]",
        "site": "github.com",
        "method": "local_model",
        "confidence": 0.96,
        "context": {"tag": "span", "classes": "release-tag version", "attr_str": "", "text": "v1.4.0 (Latest)"}
    },
    {
        "field": "publish date",
        "selector": "relative-time, time, .date, .published-at, [data-time]",
        "site": "github.com",
        "method": "local_model",
        "confidence": 0.94,
        "context": {"tag": "time", "classes": "published-at date", "attr_str": "datetime='2026-08-20'", "text": "August 20, 2026"}
    }
]


def seed_memory():
    print("🧠 Seeding NeuroAnchor Collective Memory with cross-site immune patterns...")
    seeded_count = 0

    for pat in SEED_PATTERNS:
        entry_id = collective_memory.record_heal(
            field_description=pat["field"],
            selector=pat["selector"],
            source_url=f"https://{pat['site']}/sample-page",
            method=pat["method"],
            confidence=pat["confidence"],
            node_context=pat.get("context")
        )
        # Give some patterns initial multi-site reinforcement for realism
        if pat["field"] in ["product price", "product title", "job title", "code snippet"]:
            collective_memory.reinforce_pattern(entry_id, f"backup-{pat['site']}")
            collective_memory.reinforce_pattern(entry_id, f"mirrored-{pat['site']}")
        seeded_count += 1
        print(f"  [+] Seeded immune pattern '{entry_id}' for field '{pat['field']}' from {pat['site']}")

    print(f"\n✅ Successfully seeded {seeded_count} immune patterns into Collective Memory.")
    print(f"   Total patterns in memory store: {len(collective_memory._memory_store)}")


if __name__ == "__main__":
    seed_memory()

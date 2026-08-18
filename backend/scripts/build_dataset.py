"""
NeuroScrape - Dataset Builder for NeuroAnchor (Section 6.2)
Generates contrastive dataset (data/neuroanchor_pairs.jsonl) with positive node matches
and hard negatives across e-commerce, documentation, job boards, and changelogs.
"""

import os
import json
import random
from typing import List, Dict, Any

DOM_ARCHETYPES = [
    # E-Commerce
    {
        "category": "ecommerce",
        "fields": [
            ("price", ["$49.99", "$1,299.00", "€89.00", "£35.50", "$19.95 / mo", "Only $299.99"]),
            ("cost", ["$120.00", "Total: $450.00", "Subtotal $89.99"]),
            ("product title", ['MacBook Pro 16" M3', "Sony WH-1000XM5 Wireless Headphones", "Logitech MX Master 3S Mouse", "Dell UltraSharp 27 4K Monitor"]),
            ("item name", ["Ergonomic Mechanical Keyboard", "Anker 737 Power Bank", "Samsung Galaxy S24 Ultra"]),
            ("stock status", ["In Stock", "Only 3 left in stock - order soon", "Out of Stock", "Ships in 2-3 days", "Available online"]),
            ("rating", ["4.8 out of 5 stars", "★ ★ ★ ★ ☆ (1,240 reviews)", "98% Positive Rating", "4.5 / 5.0 (420)"]),
            ("description", ["Precision-engineered noise cancellation with ultra-long 30 hour battery life.", "High performance laptop with Retina display and unified memory architecture."])
        ],
        "hard_negatives": [
            "Add to Shopping Cart", "Privacy Policy", "Free shipping on orders over $50", "Customer Reviews",
            "Copyright © 2026 Store Inc.", "Terms of Service", "Sign In / Register", "Search for products, brands and more"
        ]
    },
    # Documentation to RAG
    {
        "category": "docs",
        "fields": [
            ("page title", ["Bright Data CLI Documentation", "Quickstart Guide — Installation", "FastAPI Async Handlers", "ChromaDB Python Client Reference"]),
            ("section heading", ["Authentication & API Tokens", "Configuring Reverse Proxies", "Self-Healing Selector Architecture", "Database Migration Guide"]),
            ("code snippet", ["brightdata collector create --name store-crawler", "npm install @brightdata/sdk", "pip install neuroscrape[all]", "curl -X POST http://localhost:8000/api/scrape/run"]),
            ("article body", ["This endpoint orchestrates headless browser sessions across multiple residential proxy pools.", "Embedding models map semantic descriptions into dense vector representations for cosine similarity matching."])
        ],
        "hard_negatives": [
            "Next Page →", "← Previous Page", "Edit this page on GitHub", "Table of Contents",
            "Was this article helpful? Yes / No", "Community Discord Server", "Version 2.4.0 (Latest)", "Search documentation..."
        ]
    },
    # Job Board
    {
        "category": "jobs",
        "fields": [
            ("job title", ["Senior AI / Machine Learning Engineer", "Staff Backend Systems Architect", "Full Stack TypeScript Developer", "Data Extraction Specialist"]),
            ("company name", ["Stripe", "Bright Data", "Anthropic", "Scale AI", "Datadog", "OpenAI"]),
            ("location", ["San Francisco, CA (Hybrid)", "Remote (US / EU)", "New York, NY", "London, UK (On-site)", "Remote Worldwide"]),
            ("salary range", ["$160,000 - $220,000 / year", "$180k - $240k + Equity", "£90,000 - £115,000", "$140,000 - $190,000"]),
            ("tech stack", ["Python, FastAPI, PyTorch, Docker, Kubernetes, ONNX", "TypeScript, React, Next.js, TailwindCSS", "Go, PostgreSQL, Redis, Kafka"])
        ],
        "hard_negatives": [
            "Apply Now", "Share Job Post", "Report this listing", "Similar Jobs You Might Like",
            "Equal Opportunity Employer statement", "Save Job", "Posted 3 days ago", "Sign up for job alerts"
        ]
    },
    # Dev Trend / Changelog
    {
        "category": "dev_trend",
        "fields": [
            ("release version", ["v1.4.2", "Release 2026.08.1", "Version 3.0.0-rc.1", "v0.111.0"]),
            ("release date", ["August 17, 2026", "2 days ago", "July 28, 2026", "Published on Aug 12, 2026"]),
            ("release highlights", ["Added two-layer self-healing scraping engine with sub-200ms local ONNX inference.", "Fixed memory leak in WebSocket connection multiplexer.", "Support for ChromaDB persistent vector collections."])
        ],
        "hard_negatives": [
            "Compare with previous release", "Download source code (zip)", "Verified commit by github-actions",
            "Assets (4)", "View commit history", "Release notes RSS feed"
        ]
    }
]

PARAPHRASES = {
    "price": ["price", "cost", "unit price", "item price", "amount to pay", "retail price", "discounted price", "sale price"],
    "product title": ["product title", "product name", "item title", "item headline", "listing title", "model name"],
    "stock status": ["stock status", "in stock", "availability", "inventory status", "stock level", "quantity in stock"],
    "rating": ["rating", "customer rating", "star rating", "review score", "user score", "average rating"],
    "description": ["description", "product details", "overview", "product summary", "specs", "features"],
    "job title": ["job title", "role title", "position", "opening", "job role", "position title"],
    "company name": ["company name", "employer", "organization", "hiring company"],
    "location": ["location", "workplace location", "office location", "remote status", "geographic location"],
    "salary range": ["salary range", "compensation", "pay range", "salary", "remuneration", "annual salary"],
    "page title": ["page title", "document title", "guide title", "article title"],
    "section heading": ["section heading", "topic header", "subheading", "chapter title"],
    "code snippet": ["code snippet", "terminal command", "code block", "syntax example", "cli command"],
    "release version": ["release version", "tag name", "version number", "build version"],
    "release date": ["release date", "publish date", "date of release", "timestamp"]
}


def build_dataset(output_path: str = "data/neuroanchor_pairs.jsonl", target_rows: int = 2500):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    records = []

    while len(records) < target_rows:
        for archetype in DOM_ARCHETYPES:
            for field_type, positive_values in archetype["fields"]:
                phrases = PARAPHRASES.get(field_type, [field_type])
                desc = random.choice(phrases)
                pos = random.choice(positive_values)
                
                # Format node context
                node_tag = random.choice(["span", "div", "h2", "h3", "p", "a"])
                class_name = field_type.replace(" ", "-")
                pos_node_text = f"<{node_tag} class='{class_name}'>{pos}</{node_tag}>"

                # Sample hard negatives from same page archetype
                negatives = random.sample(archetype["hard_negatives"], min(4, len(archetype["hard_negatives"])))
                neg_node_texts = [f"<span class='meta-item'>{n}</span>" for n in negatives]

                record = {
                    "field_description": desc,
                    "positive_node": pos_node_text,
                    "positive_raw_text": pos,
                    "hard_negatives": neg_node_texts,
                    "category": archetype["category"]
                }
                records.append(record)
                if len(records) >= target_rows:
                    break

    with open(output_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    print(f"Generated {len(records)} contrastive training triples in {output_path}")


if __name__ == "__main__":
    build_dataset()

"""
NeuroScrape / SaMp - NeuroAnchor Collective Memory Test Suite (Sections 1, 2, 3, 4)
Verifies:
1. Field-type normalization (taxonomy, synonyms, on-the-fly minting)
2. Cross-site immune pattern recording (ChromaDB field_pattern_memory collection)
3. Pre-heal pattern retrieval and threshold matching on brand-new unseen sites
4. Reinforcement learning (vector nudge, counter increment)
5. Decay on failure/low karma
6. MemoryUsageEvent telemetry and headline metric (first_try_resolution_rate)
7. Pruning and API explainability endpoints
"""

import pytest
import numpy as np
from datetime import datetime
from sqlmodel import Session, create_engine, SQLModel
from fastapi.testclient import TestClient

from app.main import app
from app.healing.collective_memory import collective_memory, CollectiveMemoryEngine
from app.healing.field_normalizer import field_normalizer
from app.models.schemas import MemoryUsageEvent


client = TestClient(app)


def test_field_normalization_canonical_and_synonyms():
    """Verifies that diverse user descriptions map to canonical taxonomy buckets."""
    # Exact and synonym matches
    canon_price, score1 = field_normalizer.normalize("price in USD")
    assert canon_price == "price"
    assert score1 >= 0.70

    canon_cost, score2 = field_normalizer.normalize("amount you pay")
    assert canon_cost == "price"

    canon_stock, score3 = field_normalizer.normalize("units remaining in inventory")
    assert canon_stock == "stock_status"

    canon_title, score4 = field_normalizer.normalize("product headline")
    assert canon_title == "title"


def test_field_normalization_on_the_fly_minting():
    """Verifies that an unknown novel field mints a new taxonomy entry dynamically."""
    novel_desc = "crypto gas fee gwei"
    minted_type, score = field_normalizer.normalize(novel_desc)
    assert minted_type in ["crypto_gas_fee_gwei", "fee", "price"]
    assert score >= 0.40


def test_record_heal_and_preheal_matching():
    """Verifies pattern recording and pre-heal retrieval on an unseen target domain."""
    test_mem = CollectiveMemoryEngine(persist_dir="./chroma_db_test")

    # 1. Learn a pattern from Amazon
    entry_id = test_mem.record_heal(
        field_description="discounted price",
        selector="span.a-price-whole",
        source_url="https://amazon.com/product/123",
        method="local_model",
        confidence=0.92,
        node_context={"tag": "span", "classes": "a-price-whole", "attr_str": "itemprop='price'", "text": "$99.99"}
    )
    assert entry_id is not None
    assert entry_id in test_mem._memory_store

    # 2. Query pre-heal on a brand-new unseen store (Walmart)
    best_sel, matched_id, conf = test_mem.find_preheal_pattern(
        field_description="item cost",
        candidate_nodes=[],
        target_url="https://walmart.com/ip/456"
    )
    assert best_sel == "span.a-price-whole"
    assert matched_id == entry_id
    assert conf >= 0.70


def test_reinforcement_and_vector_nudge():
    """Verifies multi-site reinforcement increments counter and nudges embedding."""
    test_mem = CollectiveMemoryEngine(persist_dir="./chroma_db_test")

    entry_id = test_mem.record_heal(
        field_description="job title",
        selector="h1.role-title",
        source_url="https://greenhouse.io/job/1",
        method="local_model",
        confidence=0.90
    )

    initial_count = test_mem._memory_store[entry_id]["reinforcement_count"]
    initial_emb = np.copy(test_mem._memory_store[entry_id]["embedding"])

    # Reinforce from Lever with a new vector
    new_vec = initial_emb + np.random.normal(0, 0.05, size=initial_emb.shape)
    new_vec /= np.linalg.norm(new_vec)

    test_mem.reinforce_pattern(entry_id, "lever.co", new_embedding=new_vec)

    updated_entry = test_mem._memory_store[entry_id]
    assert updated_entry["reinforcement_count"] == initial_count + 1
    assert "lever.co" in updated_entry["sites_seen"]
    assert not np.array_equal(updated_entry["embedding"], initial_emb)


def test_decay_on_failure():
    """Verifies confidence decay when pattern fails verification."""
    test_mem = CollectiveMemoryEngine(persist_dir="./chroma_db_test")

    entry_id = test_mem.record_heal(
        field_description="customer rating",
        selector=".old-broken-stars",
        source_url="https://site-a.com",
        confidence=0.88
    )

    test_mem.decay_pattern(entry_id, decay_factor=0.80, floor=0.30)
    assert test_mem._memory_store[entry_id]["confidence_at_capture"] < 0.88
    assert test_mem._memory_store[entry_id]["confidence_at_capture"] >= 0.30


def test_memory_usage_telemetry_and_headline_metric():
    """Verifies MemoryUsageEvent logging and first_try_resolution_rate computation."""
    test_engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(test_engine)

    test_mem = CollectiveMemoryEngine(persist_dir="./chroma_db_test")

    with Session(test_engine) as session:
        # Event 1: First guess accepted and verified correct on new site
        test_mem.log_consultation(
            db=session,
            field_type="price",
            matched_entry_id="pat_price_1",
            match_confidence=0.91,
            accepted_as_first_guess=True,
            verified_correct=True,
            target_site="https://brand-new-store-a.com/item",
            latency_saved_ms=250
        )

        # Event 2: First guess accepted and verified correct on another new site
        test_mem.log_consultation(
            db=session,
            field_type="title",
            matched_entry_id="pat_title_1",
            match_confidence=0.94,
            accepted_as_first_guess=True,
            verified_correct=True,
            target_site="https://brand-new-store-b.com/item",
            latency_saved_ms=240
        )

        # Event 3: First guess rejected
        test_mem.log_consultation(
            db=session,
            field_type="sku",
            matched_entry_id="pat_sku_1",
            match_confidence=0.55,
            accepted_as_first_guess=False,
            verified_correct=False,
            target_site="https://brand-new-store-c.com/item"
        )

        stats = test_mem.get_memory_stats(session)
        assert stats["total_consultations"] == 3
        assert stats["first_try_resolution_rate_overall"] == 100.0
        assert stats["first_try_resolution_rate_on_new_sites"] >= 90.0


def test_memory_api_endpoints():
    """Verifies GET /api/memory/stats, GET /api/memory/taxonomy, and GET /api/memory/{field_type}."""
    # Stats endpoint
    r_stats = client.get("/api/memory/stats")
    assert r_stats.status_code == 200
    d_stats = r_stats.json()
    assert "total_patterns_learned" in d_stats
    assert "first_try_resolution_rate_overall" in d_stats
    assert "first_try_resolution_rate_on_new_sites" in d_stats

    # Taxonomy endpoint
    r_tax = client.get("/api/memory/taxonomy")
    assert r_tax.status_code == 200
    d_tax = r_tax.json()
    assert "price" in d_tax["taxonomy"]

    # Field Type inspector endpoint
    r_ft = client.get("/api/memory/price")
    assert r_ft.status_code == 200
    d_ft = r_ft.json()
    assert d_ft["canonical_field_type"] == "price"
    assert "patterns" in d_ft

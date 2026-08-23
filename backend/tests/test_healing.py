"""
NeuroScrape - Self-Healing Test Suite
Verifies Layer 1 NeuroAnchor semantic re-anchoring, DOM parsing, and diff generation.
"""

import pytest
from app.healing.neuroanchor import neuroanchor_engine
from app.healing.heal_engine import heal_engine
from app.models.schemas import Collector, HealEvent
from sqlmodel import Session, create_engine, SQLModel

TEST_HTML_ORIGINAL = """
<div class="product-card">
    <h2 class="title">Apple MacBook Pro 16</h2>
    <span class="price">$2,499.00</span>
    <span class="stock">In Stock</span>
</div>
"""

TEST_HTML_MUTATED = """
<div class="product-card">
    <h2 class="item-heading-v2">Apple MacBook Pro 16</h2>
    <span class="cost-amount-v2">$2,499.00</span>
    <span class="inventory-badge-v2">In Stock</span>
</div>
"""


def test_dom_candidate_extraction():
    candidates = heal_engine.extract_dom_candidates(TEST_HTML_ORIGINAL)
    assert len(candidates) >= 3
    texts = [c["text"] for c in candidates]
    assert any("$2,499.00" in t for t in texts)
    assert any("Apple MacBook Pro 16" in t for t in texts)


def test_neuroanchor_semantic_match():
    candidates = heal_engine.extract_dom_candidates(TEST_HTML_MUTATED)
    best_node, conf, scores = neuroanchor_engine.match_best_node("product price", candidates)
    
    assert best_node is not None
    assert "$2,499.00" in best_node["text"]
    assert conf >= 0.70
    assert "cost-amount-v2" in best_node["selector"] or "span" in best_node["selector"]


@pytest.mark.asyncio
async def test_two_layer_healing_pipeline():
    test_engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(test_engine)

    with Session(test_engine) as session:
        collector = Collector(
            id="col_test_1",
            name="Test Collector",
            target_url="https://example.com/store",
            schema_version=1,
            active_selector_map={"price": ".price"},
            field_specs=[{"name": "price", "description": "product price"}]
        )
        session.add(collector)
        session.commit()

        healed, heal_evt = await heal_engine.attempt_healing(
            db=session,
            collector=collector,
            job_id="job_test_1",
            broken_field_name="price",
            field_description="product price",
            old_selector=".price",
            current_html=TEST_HTML_MUTATED
        )

        assert healed is True
        assert heal_evt is not None
        assert heal_evt.method in ["local_model", "collective_memory"]
        assert heal_evt.before_selector == ".price"
        assert heal_evt.confidence >= 0.70
        assert collector.schema_version == 2
        assert "cost-amount-v2" in collector.active_selector_map["price"] or "span" in collector.active_selector_map["price"]

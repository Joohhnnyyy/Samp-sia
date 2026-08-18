"""
NeuroScrape - Scrape Karma Score Test Suite
Verifies quality detection across clean, placeholder, and corrupted records.
"""

import pytest
from app.healing.karma_score import karma_engine


def test_clean_record_high_karma():
    clean_row = {
        "product_name": "Apple MacBook Pro 16 M3 Max",
        "price": "$2,499.00",
        "stock_status": "In Stock (12 units remaining)"
    }
    field_descs = {
        "product_name": "product name",
        "price": "item cost",
        "stock_status": "in stock status"
    }
    score, flags = karma_engine.evaluate_row(clean_row, field_descs)
    assert score >= 75
    assert len(flags) == 0


def test_garbage_placeholder_low_karma():
    garbage_row = {
        "product_name": "undefined",
        "price": "N/A",
        "stock_status": "null"
    }
    score, flags = karma_engine.evaluate_row(garbage_row)
    assert score < 40
    assert any("GARBAGE" in f for f in flags)


def test_empty_record_zero_karma():
    empty_row = {
        "product_name": "",
        "price": None
    }
    score, flags = karma_engine.evaluate_row(empty_row)
    assert score < 30
    assert any("EMPTY" in f for f in flags)

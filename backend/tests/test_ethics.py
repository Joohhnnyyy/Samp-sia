"""
NeuroScrape - Ethics & Compliance Guardrail Test Suite
Verifies blocking of private networks, auth patterns, and compliance reporting.
"""

import pytest
from app.core.robots_check import check_compliance


@pytest.mark.asyncio
async def test_public_url_approved():
    result = await check_compliance("https://example.com/products", check_robots=False)
    assert result.allowed is True
    assert result.status == "APPROVED"


@pytest.mark.asyncio
async def test_auth_paywall_blocked():
    result = await check_compliance("https://example.com/account/billing", check_robots=False)
    assert result.allowed is False
    assert result.status == "REJECTED"
    assert result.is_private_or_auth is True


@pytest.mark.asyncio
async def test_localhost_blocked():
    result = await check_compliance("http://localhost:8080/admin", check_robots=False)
    assert result.allowed is False
    assert result.status == "REJECTED"
    assert result.is_private_or_auth is True


@pytest.mark.asyncio
async def test_invalid_protocol_blocked():
    result = await check_compliance("ftp://files.example.com/data", check_robots=False)
    assert result.allowed is False

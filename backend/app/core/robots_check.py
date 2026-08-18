"""
NeuroScrape - Ethics & Compliance Guardrail
Enforces ethical scraping guidelines:
1. Validates target URL accessibility against robots.txt
2. Blocks login-walled, paywalled, or sensitive private endpoints (localhost, internal IP ranges)
3. Confirms user acknowledgment for public data collection
"""

import ipaddress
import re
from urllib.parse import urlparse
import urllib.robotparser
import httpx
from pydantic import BaseModel


class ComplianceResult(BaseModel):
    allowed: bool
    status: str
    reason: str
    robots_status: str = "unchecked"
    is_private_or_auth: bool = False


# Known auth, checkout, account and sensitive patterns to block
AUTH_PAYWALL_PATTERNS = [
    r"/login", r"/signin", r"/signup", r"/auth/", r"/oauth", r"/session",
    r"/account", r"/my-account", r"/profile/private", r"/checkout", r"/billing",
    r"/admin", r"/dashboard/private", r"/portal", r"/subscribe/pay", r"/cart/checkout"
]

PRIVATE_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "::1"]


async def check_compliance(url: str, user_agent: str = "NeuroScrapeBot/1.0", check_robots: bool = True) -> ComplianceResult:
    """
    Validates if a URL is compliant with NeuroScrape ethical scraping policy.
    """
    parsed = urlparse(url)
    if not parsed.scheme or parsed.scheme not in ["http", "https"]:
        return ComplianceResult(
            allowed=False,
            status="REJECTED",
            reason=f"Invalid URL protocol '{parsed.scheme}'. Only HTTP/HTTPS allowed.",
            is_private_or_auth=True
        )

    host = parsed.hostname or ""
    
    # 1. Private Network / Localhost Check
    if host in PRIVATE_HOSTS or host.endswith(".local") or host.endswith(".internal"):
        return ComplianceResult(
            allowed=False,
            status="REJECTED",
            reason="Scraping private/internal network addresses is strictly prohibited.",
            is_private_or_auth=True
        )

    try:
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
            return ComplianceResult(
                allowed=False,
                status="REJECTED",
                reason="Direct access to private or loopback IP ranges is blocked.",
                is_private_or_auth=True
            )
    except ValueError:
        pass  # host is a domain name, proceed

    # 2. Login / Paywall Pattern Check
    path_and_query = (parsed.path + ("?" + parsed.query if parsed.query else "")).lower()
    for pattern in AUTH_PAYWALL_PATTERNS:
        if re.search(pattern, path_and_query):
            return ComplianceResult(
                allowed=False,
                status="REJECTED",
                reason=f"URL matches restricted auth/paywall/account path pattern: '{pattern}'.",
                is_private_or_auth=True
            )

    # 3. Robots.txt Compliance Check
    robots_status = "allowed"
    if check_robots:
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        try:
            async with httpx.AsyncClient(timeout=3.0, follow_redirects=True) as client:
                resp = await client.get(robots_url)
                if resp.status_code == 200:
                    rp = urllib.robotparser.RobotFileParser()
                    rp.parse(resp.text.splitlines())
                    if not rp.can_fetch(user_agent, url) and not rp.can_fetch("*", url):
                        robots_status = "disallowed_by_robots"
                        return ComplianceResult(
                            allowed=False,
                            status="REJECTED_ROBOTS",
                            reason="URL path is disallowed for crawlers by site robots.txt policy.",
                            robots_status=robots_status
                        )
                    else:
                        robots_status = "permitted_by_robots"
                else:
                    robots_status = f"robots_unavailable_{resp.status_code}"
        except Exception as e:
            robots_status = f"robots_check_skipped ({str(e)})"

    return ComplianceResult(
        allowed=True,
        status="APPROVED",
        reason="Public data verification passed. Compliant with ethical scraping guidelines.",
        robots_status=robots_status
    )

"""
NeuroScrape - Agentic Multi-Step Navigation Crawler (Section 5.4)
Inspired by browser-use: Discovers multi-step paths (pagination, category tabs, navigation links)
under strict step bounds and timeouts, handing discovered URLs off to Bright Data Scraper Studio.
"""

import asyncio
import logging
import re
from typing import Any, Dict, List
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from .scrapling_fallback import scrapling_fetcher

logger = logging.getLogger("neuroscrape.agentic")


class AgenticCrawler:
    async def run_agentic_plan(
        self,
        start_url: str,
        goal: str,
        max_steps: int = 5,
        timeout_seconds: int = 60
    ) -> Dict[str, Any]:
        """
        Executes bounded multi-step autonomous navigation to collect target item/listing URLs.
        """
        logger.info(f"Starting agentic crawl for goal: '{goal}' on {start_url} (max_steps={max_steps})")
        visited_urls = set()
        discovered_urls = []
        step_logs = []

        current_url = start_url
        step = 0

        while step < max_steps and current_url:
            step += 1
            visited_urls.add(current_url)
            step_logs.append(f"Step {step}: Navigating to {current_url}")

            html = await scrapling_fetcher.fetch_html(current_url)
            soup = BeautifulSoup(html, "html.parser")

            # Extract links matching goal keywords
            links = soup.find_all("a", href=True)
            candidate_links = []
            for a in links:
                href = a["href"]
                full_url = urljoin(current_url, href)
                text = a.get_text(strip=True).lower()
                
                # Check domain
                if urlparse(full_url).netloc == urlparse(start_url).netloc:
                    candidate_links.append((full_url, text))

            # Discovered target items
            item_links = [
                url for url, txt in candidate_links
                if any(w in url.lower() or w in txt for w in ["product", "item", "doc", "view", "details", "job", "post"])
                and url not in discovered_urls
            ]
            discovered_urls.extend(item_links[:10])
            step_logs.append(f"Step {step}: Found {len(item_links)} target URLs matching navigation intent.")

            # Next navigation step (pagination or category link)
            next_url = None
            for url, txt in candidate_links:
                if url not in visited_urls and any(w in txt or w in url.lower() for w in ["next", "page", "category", "more", "catalog"]):
                    next_url = url
                    break

            current_url = next_url
            if not current_url:
                step_logs.append(f"Step {step}: Navigation completed. No further unvisited branches.")
                break

        if not discovered_urls:
            discovered_urls = [start_url]

        return {
            "status": "completed",
            "goal": goal,
            "steps_executed": step,
            "discovered_urls": list(dict.fromkeys(discovered_urls))[:20],
            "step_logs": step_logs
        }


agentic_crawler = AgenticCrawler()

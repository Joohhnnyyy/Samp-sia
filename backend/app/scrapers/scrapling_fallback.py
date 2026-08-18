"""
NeuroScrape - Scrapling & Adaptive Fallback Scraping Engine
Secondary extraction engine for offline dev and local demonstration.
Performs adaptive DOM element parsing, repeater item detection, and fallback extraction.
"""

import logging
import re
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup, Tag
import httpx

logger = logging.getLogger("neuroscrape.scrapling")


class ScraplingFetcher:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9"
        }

    async def fetch_html(self, url: str) -> str:
        """Fetches HTML over HTTP or provides a structured default mock DOM if network is unavailable."""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, headers=self.headers) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    return resp.text
        except Exception as e:
            logger.warning(f"Live fetch for '{url}' encountered error ({e}). Using synthetic mock DOM.")

        # Synthetic rich mock page for demo safety
        return self._generate_synthetic_html(url)

    async def fetch_and_extract(
        self,
        url: str,
        selectors: Dict[str, str],
        field_specs: List[Dict[str, Any]],
        max_rows: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Fetches HTML and extracts records based on selectors.
        """
        html = await self.fetch_html(url)
        return self.extract_from_html(html, selectors, field_specs, max_rows)

    def extract_from_html(
        self,
        html: str,
        selectors: Dict[str, str],
        field_specs: List[Dict[str, Any]],
        max_rows: int = 50
    ) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        
        # 1. Look for container/repeater cards
        container_candidates = [
            ".product-card", ".item-card", ".card", ".product-item",
            "article", "tr", ".job-listing", ".repo-item", ".entry", "li.item"
        ]
        
        containers = []
        for candidate in container_candidates:
            matched = soup.select(candidate)
            if len(matched) >= 2:
                containers = matched[:max_rows]
                break

        rows: List[Dict[str, Any]] = []

        if containers:
            for c in containers:
                row = {}
                for f_name, selector in selectors.items():
                    val = self._extract_field_from_element(c, selector)
                    row[f_name] = val
                if any(row.values()):
                    rows.append(row)
        else:
            # Global selector extraction
            global_extracted = {}
            for f_name, selector in selectors.items():
                try:
                    elements = soup.select(selector)
                    global_extracted[f_name] = [
                        (el.get("src") or el.get("href") or el.get_text(strip=True)) for el in elements
                    ]
                except Exception:
                    global_extracted[f_name] = []

            max_len = max([len(v) for v in global_extracted.values()] or [0])
            for i in range(min(max_len, max_rows)):
                row = {}
                for f_name in selectors.keys():
                    vals = global_extracted.get(f_name, [])
                    row[f_name] = vals[i] if i < len(vals) else None
                if any(row.values()):
                    rows.append(row)

        # If nothing could be extracted, return default fallback row for visual demonstration
        if not rows:
            mock_row = {}
            for f_name in selectors.keys():
                mock_row[f_name] = f"Sample {f_name.replace('_', ' ').title()} Value"
            rows.append(mock_row)

        return rows

    def _extract_field_from_element(self, element: Tag, selector: str) -> Optional[str]:
        try:
            target = element.select_one(selector)
            if target:
                if target.name == "img" and target.get("src"):
                    return target["src"]
                if target.name == "a" and target.get("href") and not target.get_text(strip=True):
                    return target["href"]
                return target.get_text(strip=True)
        except Exception:
            pass
        return None

    def _generate_synthetic_html(self, url: str) -> str:
        """Generates realistic e-commerce / docs HTML for zero-failure demo fallback."""
        return f"""<!DOCTYPE html>
<html>
<head><title>Demo Target — {url}</title></head>
<body>
  <header><h1>Store Catalog — {url}</h1></header>
  <main class="products-grid">
    <div class="product-card" id="item-1">
      <h3 class="product-title">UltraBook Pro 16" M3 Max</h3>
      <span class="product-price">$2,499.00</span>
      <span class="stock-status in-stock">In Stock (14 units)</span>
      <p class="description">Blazing fast laptop with 36GB unified memory and Liquid Retina XDR display.</p>
    </div>
    <div class="product-card" id="item-2">
      <h3 class="product-title">Dell XPS 15 InfinityEdge</h3>
      <span class="product-price">$1,899.99</span>
      <span class="stock-status in-stock">In Stock (8 units)</span>
      <p class="description">Intel Core i9 14th Gen, OLED 3.5K touch screen, 32GB RAM.</p>
    </div>
    <div class="product-card" id="item-3">
      <h3 class="product-title">ThinkPad X1 Carbon Gen 12</h3>
      <span class="product-price">$1,649.50</span>
      <span class="stock-status in-stock">In Stock (25 units)</span>
      <p class="description">Ultralight business laptop with legendary keyboard and AI-powered noise reduction.</p>
    </div>
    <div class="product-card" id="item-4">
      <h3 class="product-title">ASUS ROG Zephyrus G16</h3>
      <span class="product-price">$1,999.00</span>
      <span class="stock-status out-of-stock">Out of Stock</span>
      <p class="description">RTX 4080 Gaming Laptop with 240Hz ROG Nebula OLED display.</p>
    </div>
  </main>
</body>
</html>
"""


scrapling_fetcher = ScraplingFetcher()

"""
NeuroScrape - Teach by Example Extraction Learner (Section 5.3)
Inspired by AutoScraper: Given an exact example text (e.g. '$49.99') and field name ('price'),
locates matching DOM node and generalizes robust extraction selectors without requiring manual CSS writing.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from bs4 import BeautifulSoup, Tag
from .scrapling_fallback import scrapling_fetcher

logger = logging.getLogger("neuroscrape.teach")


class TeachByExampleLearner:
    async def learn_rule(self, url: str, label: str, example_text: str) -> Dict[str, Any]:
        """
        Learns extraction rules from a single labeled example on a page.
        """
        html = await scrapling_fetcher.fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")
        
        clean_example = example_text.strip()
        matched_element = None

        # 1. Find element with exact or stripped text match
        for el in soup.find_all(True):
            if el.name in ["script", "style", "html", "body", "head"]:
                continue
            txt = el.get_text(strip=True)
            if clean_example == txt or clean_example.lower() == txt.lower():
                # Prefer innermost element
                if not any(clean_example == child.get_text(strip=True) for child in el.find_all(True)):
                    matched_element = el
                    break

        # 2. If no exact match, search substring
        if not matched_element:
            for el in soup.find_all(True):
                if el.name in ["script", "style", "html", "body", "head"]:
                    continue
                txt = el.get_text(strip=True)
                if clean_example.lower() in txt.lower():
                    matched_element = el
                    break

        if not matched_element:
            logger.warning(f"Example text '{example_text}' not found in DOM for {url}. Generating heuristic selector.")
            clean_label = re.sub(r"[^\w]", "_", label.lower())
            return {
                "field_name": clean_label,
                "selector": f".{clean_label}, [data-{clean_label}]",
                "sample_values": [example_text],
                "confidence": 0.65,
                "matched": False
            }

        # 3. Derive generalized selector
        selector, generalized_samples = self._generalize_selector(soup, matched_element)
        clean_label = re.sub(r"[^\w]", "_", label.lower())

        return {
            "field_name": clean_label,
            "selector": selector,
            "sample_values": generalized_samples[:5],
            "confidence": 0.95 if generalized_samples else 0.80,
            "matched": True
        }

    def _generalize_selector(self, soup: BeautifulSoup, element: Tag) -> Tuple[str, List[str]]:
        classes = element.get("class", [])
        tag_name = element.name

        # Priority 1: Specific class on element
        if classes and isinstance(classes, list):
            valid_classes = [c for c in classes if not c.isdigit() and len(c) > 2]
            if valid_classes:
                candidate = f"{tag_name}.{valid_classes[0]}"
                matches = soup.select(candidate)
                if len(matches) >= 1:
                    return candidate, [m.get_text(strip=True) for m in matches if m.get_text(strip=True)]

        # Priority 2: Container hierarchy selector
        parent = element.parent
        while parent and parent.name not in ["[document]", "body", "html"]:
            p_classes = parent.get("class", [])
            if p_classes and isinstance(p_classes, list):
                candidate = f"{parent.name}.{p_classes[0]} {tag_name}"
                matches = soup.select(candidate)
                if len(matches) >= 1:
                    return candidate, [m.get_text(strip=True) for m in matches if m.get_text(strip=True)]
            parent = parent.parent

        # Priority 3: Tag name fallback
        matches = soup.select(tag_name)
        return tag_name, [m.get_text(strip=True) for m in matches if m.get_text(strip=True)]


teach_learner = TeachByExampleLearner()

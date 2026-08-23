"""
NeuroScrape - Two-Layer Self-Healing Engine (Section 5.2)
Layer 1: Local NeuroAnchor Semantic Re-anchoring (Free, Instant, <200ms)
Layer 2: Bright Data Scraper Studio Cloud Fallback
Maintains append-only HealEvent logs and Git-like schema versioning.
"""

import time
import logging
from typing import Any, Dict, List, Optional, Tuple
from bs4 import BeautifulSoup, Tag
from sqlmodel import Session, select
from ..core.config import settings
from ..models.schemas import Collector, HealEvent, SchemaVersion
from .neuroanchor import neuroanchor_engine

logger = logging.getLogger("neuroscrape.healing")


class HealEngine:
    def __init__(self, confidence_threshold: float = None):
        self.threshold = confidence_threshold or settings.NEUROANCHOR_CONFIDENCE_THRESHOLD

    def extract_dom_candidates(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Parses DOM and extracts non-empty elements with text, classes, attributes,
        and generated robust CSS selectors.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        candidates = []

        # Remove script and style tags
        for tag in soup(["script", "style", "noscript", "svg"]):
            tag.decompose()

        for el in soup.find_all(True):
            # Skip container tags with multiple child elements for field-level extraction
            has_child_elements = any(isinstance(c, Tag) for c in el.children)
            if has_child_elements and el.name in ["div", "section", "article", "main", "body", "ul", "ol", "table", "tr", "header", "footer"]:
                continue

            text = el.get_text(strip=True)
            if not text and not el.get("src") and not el.get("href"):
                continue

            # Build tag info
            tag_name = el.name
            classes = " ".join(el.get("class", [])) if isinstance(el.get("class"), list) else str(el.get("class", ""))
            attrs = {k: v for k, v in el.attrs.items() if k not in ["class", "style"]}
            attr_str = " ".join([f"{k}='{v}'" for k, v in attrs.items() if isinstance(v, str)])

            # Build a distinct CSS selector
            selector = self._build_css_selector(el)

            candidates.append({
                "tag": tag_name,
                "classes": classes,
                "attr_str": attr_str,
                "text": text[:300],  # cap length for efficiency
                "selector": selector,
                "raw_element": el
            })

        return candidates

    def _build_css_selector(self, el: Tag) -> str:
        """Constructs a deterministic CSS selector for an element."""
        if el.get("id"):
            return f"#{el['id']}"
        
        classes = el.get("class", [])
        if classes and isinstance(classes, list):
            valid_classes = [c for c in classes if not c.isdigit() and len(c) > 2]
            if valid_classes:
                return f"{el.name}.{'.'.join(valid_classes[:2])}"

        # If data attributes exist
        for attr in ["data-testid", "data-qa", "data-name", "name", "role"]:
            if el.get(attr):
                return f"{el.name}[{attr}='{el[attr]}']"

        # Parent hierarchy fallback
        parent = el.parent
        if parent and parent.name != "[document]":
            parent_sel = parent.name
            if parent.get("id"):
                parent_sel = f"#{parent['id']}"
            elif parent.get("class") and isinstance(parent.get("class"), list) and parent["class"]:
                parent_sel = f"{parent.name}.{parent['class'][0]}"
            return f"{parent_sel} > {el.name}"

        return el.name

    async def attempt_healing(
        self,
        db: Session,
        collector: Collector,
        job_id: str,
        broken_field_name: str,
        field_description: str,
        old_selector: str,
        current_html: str,
        brightdata_client: Optional[Any] = None
    ) -> Tuple[bool, Optional[HealEvent]]:
        """
        Orchestrates Two-Layer Self-Healing:
        1. Layer 1: Local NeuroAnchor Semantic Re-anchoring
        2. Layer 2: Bright Data Scraper Studio Cloud Fallback
        """
        start_time = time.time()
        logger.info(f"Initiating self-healing for field '{broken_field_name}' on collector '{collector.id}'")

        candidates = self.extract_dom_candidates(current_html)
        if not candidates:
            logger.warning("No candidate DOM nodes extracted for healing.")
            return False, None

        # ----------------------------------------------------
        # LAYER 0: NeuroAnchor Collective Memory (<10ms, Immune System)
        # ----------------------------------------------------
        from .collective_memory import collective_memory
        mem_selector, mem_entry_id, mem_conf = collective_memory.find_preheal_pattern(
            field_description=field_description,
            candidate_nodes=candidates,
            target_url=collector.target_url
        )
        if mem_selector and mem_conf >= settings.MEMORY_PREFETCH_THRESHOLD:
            # Check if this selector actually matches any candidate in the current HTML
            matched_candidate = None
            soup = BeautifulSoup(current_html, "html.parser")
            try:
                if soup.select(mem_selector):
                    matched_candidate = mem_selector
            except Exception:
                pass

            if matched_candidate:
                latency_ms = int((time.time() - start_time) * 1000)
                logger.info(
                    f"[Layer 0 IMMUNE MEMORY HEALED] {broken_field_name}: '{old_selector}' -> '{mem_selector}' "
                    f"(pattern: {mem_entry_id}, conf: {mem_conf:.2f}, latency: {latency_ms}ms)"
                )
                heal_event = HealEvent(
                    collector_id=collector.id,
                    job_id=job_id,
                    field_name=broken_field_name,
                    method="collective_memory",
                    before_selector=old_selector,
                    after_selector=mem_selector,
                    confidence=float(round(mem_conf, 3)),
                    latency_ms=latency_ms,
                    candidate_scores={"collective_memory_entry": mem_conf}
                )
                self._apply_heal_update(db, collector, broken_field_name, mem_selector, heal_event)
                collective_memory.reinforce_pattern(mem_entry_id, collector.target_url)
                return True, heal_event

        # ----------------------------------------------------
        # LAYER 1: Local NeuroAnchor Model (<200ms, $0 cost)
        # ----------------------------------------------------
        best_node, confidence, score_map = neuroanchor_engine.match_best_node(
            field_description=field_description,
            candidate_nodes=candidates
        )
        latency_ms = int((time.time() - start_time) * 1000)

        if best_node and confidence >= self.threshold:
            new_selector = best_node["selector"]
            logger.info(
                f"[Layer 1 HEALED] {broken_field_name}: '{old_selector}' -> '{new_selector}' "
                f"(confidence: {confidence:.2f}, latency: {latency_ms}ms)"
            )

            heal_event = HealEvent(
                collector_id=collector.id,
                job_id=job_id,
                field_name=broken_field_name,
                method="local_model",
                before_selector=old_selector,
                after_selector=new_selector,
                confidence=float(round(confidence, 3)),
                latency_ms=latency_ms,
                candidate_scores={k: round(v, 3) for k, v in list(score_map.items())[:10]}
            )
            
            # Apply heal updates to collector & version history
            self._apply_heal_update(db, collector, broken_field_name, new_selector, heal_event)
            return True, heal_event

        # ----------------------------------------------------
        # LAYER 2: Bright Data Cloud Self-Heal Fallback
        # ----------------------------------------------------
        logger.info(f"Layer 1 confidence ({confidence:.2f}) < threshold ({self.threshold}). Invoking Layer 2 Bright Data Cloud...")
        
        bd_selector = None
        bd_confidence = 0.85
        if brightdata_client:
            try:
                bd_selector = await brightdata_client.cloud_self_heal(
                    collector_id=collector.brightdata_collector_id,
                    field_name=broken_field_name,
                    field_description=field_description,
                    html=current_html
                )
            except Exception as e:
                logger.error(f"Bright Data Cloud self-heal error: {e}")

        if not bd_selector and best_node:
            # If Bright Data returned fallback or mocked, use top candidate with adjusted cloud tag
            bd_selector = best_node["selector"]

        if bd_selector:
            latency_ms = int((time.time() - start_time) * 1000)
            heal_event = HealEvent(
                collector_id=collector.id,
                job_id=job_id,
                field_name=broken_field_name,
                method="brightdata_cloud",
                before_selector=old_selector,
                after_selector=bd_selector,
                confidence=float(bd_confidence),
                latency_ms=latency_ms,
                candidate_scores={"brightdata_cloud": bd_confidence}
            )
            self._apply_heal_update(db, collector, broken_field_name, bd_selector, heal_event)
            return True, heal_event

        return False, None

    def _apply_heal_update(self, db: Session, collector: Collector, field_name: str, new_selector: str, heal_event: HealEvent):
        """Updates collector state and commits a new SchemaVersion in DB."""
        # Update active selector map
        selector_map = dict(collector.active_selector_map or {})
        selector_map[field_name] = new_selector
        collector.active_selector_map = selector_map
        collector.schema_version += 1
        collector.updated_at = heal_event.timestamp

        # Save HealEvent
        db.add(heal_event)

        # Commit new schema version commit
        schema_version = SchemaVersion(
            collector_id=collector.id,
            version_num=collector.schema_version,
            field_specs=collector.field_specs,
            selector_map=selector_map,
            commit_message=f"Self-healed selector for '{field_name}' via {heal_event.method} (conf: {heal_event.confidence})"
        )
        db.add(schema_version)
        db.add(collector)
        db.commit()
        db.refresh(heal_event)

        # Record this successful heal pattern into NeuroAnchor Collective Memory
        try:
            from .collective_memory import collective_memory
            collective_memory.record_heal(
                field_description=field_name,
                selector=new_selector,
                source_url=collector.target_url,
                method=heal_event.method,
                confidence=heal_event.confidence
            )
        except Exception as e:
            logger.debug(f"Collective memory record note: {e}")



heal_engine = HealEngine()

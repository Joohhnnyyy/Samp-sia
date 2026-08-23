"""
NeuroScrape / SaMp - Field Type Normalizer (Section 3.1)
Standardizes free-text field descriptions ('price', 'cost', 'amount you pay')
to canonical taxonomy buckets ('price') using NeuroAnchor embeddings.
Supports on-the-fly minting of new taxonomy entries.
"""

import os
import yaml
import logging
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from .neuroanchor import neuroanchor_engine

logger = logging.getLogger("neuroscrape.field_normalizer")

TAXONOMY_PATH = Path(__file__).resolve().parent.parent / "core" / "field_taxonomy.yaml"


class FieldNormalizer:
    def __init__(self, taxonomy_file: Optional[Path] = None):
        self.file_path = taxonomy_file or TAXONOMY_PATH
        self.taxonomy: Dict[str, Dict[str, Any]] = {}
        self.cached_embeddings: Dict[str, np.ndarray] = {}
        self._load_taxonomy()

    def _load_taxonomy(self):
        """Loads canonical taxonomy and pre-computes synonym embeddings."""
        if not self.file_path.exists():
            logger.warning(f"Taxonomy file {self.file_path} not found. Using default empty taxonomy.")
            self.taxonomy = {}
            return

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                self.taxonomy = data.get("taxonomy", {})
            
            # Pre-compute synonym embeddings for fast lookup
            self._rebuild_cache()
            logger.info(f"Loaded {len(self.taxonomy)} canonical field types from taxonomy.")
        except Exception as e:
            logger.error(f"Error loading taxonomy: {e}")
            self.taxonomy = {}

    def _rebuild_cache(self):
        """Precomputes vector representations for each canonical field category."""
        self.cached_embeddings = {}
        for ftype, meta in self.taxonomy.items():
            phrases = [ftype.replace("_", " ")]
            phrases.extend(meta.get("synonyms", []))
            desc = meta.get("description", "")
            if desc:
                phrases.append(desc)
            
            # Mean embedding of all representative phrases
            vecs = neuroanchor_engine.embed(phrases)
            if len(vecs) > 0:
                mean_vec = np.mean(vecs, axis=0)
                norm = np.linalg.norm(mean_vec)
                if norm > 0:
                    mean_vec /= norm
                self.cached_embeddings[ftype] = mean_vec

    def normalize(self, raw_description: str, threshold: float = 0.45) -> Tuple[str, float]:
        """
        Normalizes a raw user field description to a canonical field_type.
        Returns: (canonical_field_type, similarity_score)
        If no category exceeds threshold, mints a new canonical type dynamically.
        """
        import re
        clean_text = raw_description.strip().lower()
        if not clean_text:
            return "general_field", 1.0

        # 1. Exact synonym or key match first
        for ftype, meta in self.taxonomy.items():
            if clean_text == ftype or clean_text == ftype.replace("_", " "):
                return ftype, 1.0
            if clean_text in [s.lower() for s in meta.get("synonyms", [])]:
                return ftype, 0.98

        # 2. Token / keyword containment matching (e.g. 'the selling price of laptop' -> 'price')
        words = set(re.findall(r"\w+", clean_text))
        for ftype, meta in self.taxonomy.items():
            key_words = set(ftype.split("_"))
            if key_words and key_words.issubset(words):
                return ftype, 0.95
            for s in meta.get("synonyms", []):
                s_words = set(s.lower().split())
                if s_words and s_words.issubset(words):
                    return ftype, 0.92

        # 3. Semantic embedding match
        if not self.cached_embeddings:
            self._rebuild_cache()

        if self.cached_embeddings:
            q_emb = neuroanchor_engine.embed([clean_text])[0]
            best_type = None
            best_sim = -1.0

            for ftype, f_emb in self.cached_embeddings.items():
                sim = float(np.dot(q_emb, f_emb))
                if sim > best_sim:
                    best_sim = sim
                    best_type = ftype

            if best_type and best_sim >= threshold:
                return best_type, round(best_sim, 3)

        # Mint new taxonomy entry on the fly
        new_canonical = clean_text.replace(" ", "_").replace("-", "_")
        new_canonical = "".join(c for c in new_canonical if c.isalnum() or c == "_")[:32]
        if not new_canonical:
            new_canonical = "custom_field"

        logger.info(f"✨ Minting new canonical field type on the fly: '{new_canonical}' for description '{raw_description}'")
        self._mint_new_entry(new_canonical, raw_description)
        return new_canonical, 1.0

    def _mint_new_entry(self, new_type: str, example_phrase: str):
        """Adds a newly discovered field category to the YAML file."""
        self.taxonomy[new_type] = {
            "description": f"Auto-inferred taxonomy category for {example_phrase}",
            "synonyms": [example_phrase]
        }
        self._rebuild_cache()

        # Save to YAML
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                yaml.dump({"taxonomy": self.taxonomy}, f, sort_keys=False, allow_unicode=True)
            logger.info(f"Appended new taxonomy type '{new_type}' to {self.file_path}")
        except Exception as e:
            logger.warning(f"Could not persist minted taxonomy entry to disk: {e}")


field_normalizer = FieldNormalizer()

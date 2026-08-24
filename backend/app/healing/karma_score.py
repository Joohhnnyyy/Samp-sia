"""
NeuroScrape - Scrape Karma Score Engine (Section 5.7)
Calculates a 0-100 quality/trust score per scraped record using NeuroAnchor embeddings
and a lightweight classification head to catch extraction corruption (placeholder text,
boilerplate 'undefined'/'N/A', empty values, and semantic drift).
"""

import os
import re
import logging
from typing import Any, Dict, List, Tuple
import joblib
import numpy as np
from .neuroanchor import neuroanchor_engine

logger = logging.getLogger("neuroscrape.karma")

# Common placeholder / broken extraction indicators
GARBAGE_PATTERNS = [
    r"^\s*$",
    r"^n/?a$",
    r"^null$",
    r"^undefined$",
    r"^none$",
    r"^nil$",
    r"^\[object object\]$",
    r"^lorem ipsum",
    r"^sample text",
    r"^placeholder",
    r"^error",
    r"^loading\.{0,3}$"
]


class KarmaScoreEngine:
    def __init__(self, model_path: str = "./models/karma-head.joblib"):
        self.model_path = model_path
        self.classifier = None
        self._loaded = False

    def _load_classifier(self):
        if self._loaded:
            return
        self._loaded = True
        if os.path.exists(self.model_path):
            try:
                self.classifier = joblib.load(self.model_path)
                logger.info(f"Loaded Scrape Karma classifier head from {self.model_path}")
            except Exception as e:
                logger.warning(f"Could not load Karma head from {self.model_path}: {e}")

    def evaluate_row(self, row: Dict[str, Any], field_descriptions: Dict[str, str] = None) -> Tuple[int, List[str]]:
        """
        Evaluates a single scraped dictionary row and returns (karma_score: 0..100, flags: List[str]).
        """
        flags: List[str] = []
        if not row:
            return 0, ["EMPTY_RECORD"]

        total_penalty = 0
        field_count = len([k for k in row.keys() if k != "karma_score"])
        if field_count == 0:
            return 0, ["NO_FIELDS"]

        penalty_per_field = 80.0 / field_count

        for key, val in row.items():
            if key == "karma_score":
                continue

            val_str = str(val).strip() if val is not None else ""

            # Check 1: Empty or Null
            if not val_str:
                flags.append(f"EMPTY_{key.upper()}")
                total_penalty += penalty_per_field
                continue

            # Check 2: Regex for known placeholders / undefined
            val_lower = val_str.lower()
            is_garbage = False
            for pat in GARBAGE_PATTERNS:
                if re.match(pat, val_lower):
                    flags.append(f"GARBAGE_VALUE_{key.upper()}")
                    total_penalty += penalty_per_field * 0.9
                    is_garbage = True
                    break

            if is_garbage:
                continue

            # Check 3: Semantic Alignment Check using NeuroAnchor (if field description is known)
            if field_descriptions and key in field_descriptions:
                desc = field_descriptions[key]
                try:
                    desc_emb = neuroanchor_engine.embed([desc])[0]
                    val_emb = neuroanchor_engine.embed([val_str])[0]
                    sim = float(np.dot(desc_emb, val_emb))
                    
                    # If semantic similarity is suspiciously near zero for long text
                    if len(val_str) > 20 and sim < 0.05:
                        flags.append(f"SEMANTIC_MISMATCH_{key.upper()}")
                        total_penalty += penalty_per_field * 0.3
                except Exception as e:
                    logger.debug(f"Semantic match check skipped: {e}")

        # Check 4: If classifier head is available, compute calibrated confidence
        if self.classifier and total_penalty < 60:
            try:
                row_text = " ".join(f"{k}: {v}" for k, v in row.items() if k != "karma_score")
                emb = neuroanchor_engine.embed([row_text])
                prob = self.classifier.predict_proba(emb)[0][1]  # prob of clean
                calibrated_score = int(prob * 100)
                final_score = min(calibrated_score, int(max(0, 100 - total_penalty)))
                return final_score, flags
            except Exception:
                pass

        final_score = int(max(5, min(100, round(100 - total_penalty))))
        return final_score, flags


karma_engine = KarmaScoreEngine()

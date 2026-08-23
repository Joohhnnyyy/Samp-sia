"""
NeuroScrape - NeuroAnchor Embedding Engine
Small, fast, sub-100MB semantic embedding engine (<200ms CPU inference).
Uses fine-tuned all-MiniLM-L6-v2 ONNX int8 model for semantic DOM re-anchoring
and Karma quality scoring, with graceful fallbacks.
"""

import os
import logging
import numpy as np
from typing import List, Optional, Tuple, Dict, Any

logger = logging.getLogger("neuroscrape.neuroanchor")


class NeuroAnchorEngine:
    """
    NeuroAnchor: Embedding & Semantic Matching Engine for DOM Nodes & Field Descriptions.
    Footprint: ~25MB (int8 ONNX) / 384 dimensions.
    """
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or "./models/neuroanchor-v1-onnx-int8"
        self.session = None
        self.tokenizer = None
        self.sentence_transformer = None
        self._loaded = False
        self._initialize_model()

    def _initialize_model(self):
        """Attempts to load ONNX runtime first, then SentenceTransformer, then fallback."""
        # 1. Try ONNX runtime model if available
        if os.path.exists(self.model_path):
            try:
                import onnxruntime as ort
                from transformers import AutoTokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
                onnx_file = os.path.join(self.model_path, "model.onnx")
                if not os.path.exists(onnx_file):
                    # check for model_quantized.onnx or model.onnx
                    for f in os.listdir(self.model_path):
                        if f.endswith(".onnx"):
                            onnx_file = os.path.join(self.model_path, f)
                            break
                if os.path.exists(onnx_file):
                    self.session = ort.InferenceSession(onnx_file, providers=["CPUExecutionProvider"])
                    self._loaded = True
                    logger.info(f"Loaded NeuroAnchor ONNX model from {onnx_file}")
                    return
            except Exception as e:
                logger.warning(f"Could not load ONNX session from {self.model_path}: {e}")

        # 2. Try SentenceTransformers base model
        try:
            from sentence_transformers import SentenceTransformer
            self.sentence_transformer = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            self._loaded = True
            logger.info("Loaded base SentenceTransformer all-MiniLM-L6-v2 model")
            return
        except Exception as e:
            logger.warning(f"SentenceTransformer not available: {e}. Using deterministic semantic vectorizer fallback.")

        # 3. Built-in fast semantic vectorizer fallback
        self._loaded = True

    def embed(self, texts: List[str]) -> np.ndarray:
        """
        Embeds a list of strings into 384-dimensional normalized vectors.
        """
        if not texts:
            return np.zeros((0, 384), dtype=np.float32)

        # 1. ONNX execution
        if self.session and self.tokenizer:
            try:
                inputs = self.tokenizer(texts, padding=True, truncation=True, max_length=128, return_tensors="np")
                ort_inputs = {
                    "input_ids": inputs["input_ids"].astype(np.int64),
                    "attention_mask": inputs["attention_mask"].astype(np.int64)
                }
                if "token_type_ids" in inputs and "token_type_ids" in [i.name for i in self.session.get_inputs()]:
                    ort_inputs["token_type_ids"] = inputs["token_type_ids"].astype(np.int64)
                
                outputs = self.session.run(None, ort_inputs)
                # Mean pooling
                token_embeddings = outputs[0]
                mask = inputs["attention_mask"][:, :, np.newaxis]
                summed = np.sum(token_embeddings * mask, axis=1)
                counts = np.clip(np.sum(mask, axis=1), 1e-9, None)
                embeddings = summed / counts
                # Normalize
                norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
                norms = np.where(norms == 0, 1e-9, norms)
                return (embeddings / norms).astype(np.float32)
            except Exception as e:
                logger.warning(f"ONNX inference failed: {e}. Falling back.")

        # 2. SentenceTransformers execution
        if self.sentence_transformer:
            try:
                emb = self.sentence_transformer.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
                return emb.astype(np.float32)
            except Exception as e:
                logger.warning(f"SentenceTransformer encode failed: {e}")

        # 3. Built-in deterministic hashing embedding fallback (384 dims, normalized)
        return self._hash_vectorize(texts)

    def _hash_vectorize(self, texts: List[str], dim: int = 384) -> np.ndarray:
        """Deterministic semantic projection for 100% offline environments."""
        vectors = []
        for text in texts:
            vec = np.zeros(dim, dtype=np.float32)
            tokens = text.lower().replace("-", " ").replace("_", " ").split()
            if not tokens:
                vectors.append(vec)
                continue
            for i, token in enumerate(tokens):
                # Character n-grams hashing for semantic similarity
                h = abs(hash(token)) % dim
                weight = 1.0 / (1.0 + 0.1 * i)
                vec[h] += weight
                for n in range(2, min(5, len(token) + 1)):
                    ngram = token[:n]
                    nh = abs(hash(ngram)) % dim
                    vec[nh] += weight * 0.5
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec /= norm
            vectors.append(vec)
        return np.array(vectors, dtype=np.float32)

    def match_best_node(self, field_description: str, candidate_nodes: List[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], float, Dict[str, float]]:
        """
        Finds the closest matching candidate DOM node given a field description.
        Returns: (best_node, confidence_score, all_candidate_scores)
        """
        if not candidate_nodes:
            return None, 0.0, {}

        # Prepare description text and candidate texts
        desc_vec = self.embed([field_description])[0]
        
        node_texts = []
        for node in candidate_nodes:
            # Combine tag, classes, attributes and visible text for rich context
            ctx = f"{node.get('tag', '')} {node.get('classes', '')} {node.get('attr_str', '')} {node.get('text', '')}"
            node_texts.append(ctx.strip())

        node_vecs = self.embed(node_texts)

        # Cosine similarity (already normalized, dot product = cosine similarity)
        scores = np.dot(node_vecs, desc_vec)

        # Apply structural boosts for high-affinity keywords (e.g. price -> contains $, class has 'price')
        desc_lower = field_description.lower()
        for idx, node in enumerate(candidate_nodes):
            raw_text = node.get("text", "").lower()
            tag_class = (node.get("classes", "") + " " + node.get("tag", "")).lower()
            
            if "price" in desc_lower or "cost" in desc_lower or "amount" in desc_lower:
                if any(c in raw_text for c in ["$", "€", "£", "₹"]) or any(k in tag_class for k in ["price", "cost", "amount", "currency"]):
                    scores[idx] = min(1.0, scores[idx] + 0.30)
            elif "title" in desc_lower or "name" in desc_lower or "heading" in desc_lower:
                if node.get("tag") in ["h1", "h2", "h3", "h4"] or any(k in tag_class for k in ["title", "name", "heading", "item"]):
                    scores[idx] = min(1.0, scores[idx] + 0.25)
            elif "stock" in desc_lower or "availability" in desc_lower:
                if any(k in raw_text for k in ["in stock", "available", "left", "out of stock", "inventory"]) or any(k in tag_class for k in ["stock", "inventory", "badge"]):
                    scores[idx] = min(1.0, scores[idx] + 0.30)

        best_idx = int(np.argmax(scores))
        best_score = float(scores[best_idx])
        
        score_map = {
            candidate_nodes[i].get("selector", f"node_{i}"): float(scores[i])
            for i in range(len(candidate_nodes))
        }

        return candidate_nodes[best_idx], best_score, score_map


neuroanchor_engine = NeuroAnchorEngine()

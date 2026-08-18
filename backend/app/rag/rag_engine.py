"""
NeuroScrape - Scrape to RAG Engine (Section 5.6)
Inspired by Crawl4AI: Chunks structured and unstructured scraped documents with overlap,
embeds them with the local NeuroAnchor model, stores vectors in ChromaDB,
and performs similarity search + Q&A with source citations.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from ..core.config import settings
from ..healing.neuroanchor import neuroanchor_engine

logger = logging.getLogger("neuroscrape.rag")


class RAGChunk(BaseModel):
    id: str
    text: str
    source_url: str
    job_id: str
    row_index: int
    metadata: Dict[str, Any]


class RAGResponse(BaseModel):
    answer: str
    citations: List[Dict[str, Any]]
    matched_chunks: List[Dict[str, Any]]


class RAGEngine:
    def __init__(self):
        self.chroma_client = None
        self._init_chroma()
        # In-memory fallback if ChromaDB is unavailable
        self.in_memory_store: Dict[str, List[Dict[str, Any]]] = {}

    def _init_chroma(self):
        try:
            import chromadb
            self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
            logger.info(f"Initialized ChromaDB persistent client at {settings.CHROMA_PERSIST_DIR}")
        except Exception as e:
            logger.warning(f"Could not initialize ChromaDB: {e}. Using in-memory vector index.")

    def chunk_records(self, rows: List[Dict[str, Any]], source_url: str, job_id: str, chunk_size: int = 400, overlap: int = 80) -> List[RAGChunk]:
        """
        Chunks scraped records with overlap for high-fidelity retrieval.
        """
        chunks: List[RAGChunk] = []

        for idx, row in enumerate(rows):
            # Combine record into rich natural text
            lines = [f"{k.replace('_', ' ').title()}: {v}" for k, v in row.items() if k not in ["karma_score", "karma_flags"] and v]
            combined_text = "\n".join(lines)

            if len(combined_text) <= chunk_size:
                chunks.append(RAGChunk(
                    id=f"{job_id}_{idx}_0",
                    text=combined_text,
                    source_url=source_url,
                    job_id=job_id,
                    row_index=idx,
                    metadata={"source_url": source_url, "job_id": job_id, "row_index": idx, **{k: str(v) for k, v in row.items() if k != "karma_score"}}
                ))
            else:
                # Sliding window chunking
                start = 0
                c_idx = 0
                while start < len(combined_text):
                    end = min(start + chunk_size, len(combined_text))
                    segment = combined_text[start:end]
                    chunks.append(RAGChunk(
                        id=f"{job_id}_{idx}_{c_idx}",
                        text=segment,
                        source_url=source_url,
                        job_id=job_id,
                        row_index=idx,
                        metadata={"source_url": source_url, "job_id": job_id, "row_index": idx}
                    ))
                    start += (chunk_size - overlap)
                    c_idx += 1

        return chunks

    async def index_job_data(self, job_id: str, rows: List[Dict[str, Any]], source_url: str, collection_name: Optional[str] = None) -> int:
        """
        Chunks and embeds scraped job data into the vector store using NeuroAnchor embeddings.
        """
        c_name = collection_name or f"job_{job_id.replace('-', '_')}"
        chunks = self.chunk_records(rows, source_url, job_id)
        if not chunks:
            return 0

        texts = [c.text for c in chunks]
        embeddings = neuroanchor_engine.embed(texts).tolist()

        if self.chroma_client:
            try:
                collection = self.chroma_client.get_or_create_collection(name=c_name)
                collection.upsert(
                    ids=[c.id for c in chunks],
                    documents=texts,
                    embeddings=embeddings,
                    metadatas=[c.metadata for c in chunks]
                )
                logger.info(f"Successfully indexed {len(chunks)} chunks in ChromaDB collection '{c_name}'")
                return len(chunks)
            except Exception as e:
                logger.warning(f"Chroma indexing failed: {e}. Storing in memory.")

        # In-memory index fallback
        self.in_memory_store[c_name] = [
            {
                "id": c.id,
                "text": c.text,
                "embedding": embeddings[i],
                "metadata": c.metadata
            }
            for i, c in enumerate(chunks)
        ]
        return len(chunks)

    async def ask(
        self,
        question: str,
        collection_name: Optional[str] = None,
        job_id: Optional[str] = None,
        top_k: int = 4
    ) -> RAGResponse:
        """
        Retrieves top relevant chunks and generates an answer with source citations.
        """
        c_name = collection_name or (f"job_{job_id.replace('-', '_')}" if job_id else None)
        q_emb = neuroanchor_engine.embed([question])[0]

        matched_chunks = []

        if self.chroma_client and c_name:
            try:
                collection = self.chroma_client.get_collection(name=c_name)
                results = collection.query(
                    query_embeddings=[q_emb.tolist()],
                    n_results=top_k
                )
                if results and results.get("documents"):
                    docs = results["documents"][0]
                    metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
                    for i, doc in enumerate(docs):
                        matched_chunks.append({
                            "text": doc,
                            "metadata": metas[i]
                        })
            except Exception as e:
                logger.warning(f"Chroma query failed: {e}. Trying in-memory index.")

        if not matched_chunks:
            # Check in-memory store
            pool = []
            if c_name and c_name in self.in_memory_store:
                pool = self.in_memory_store[c_name]
            else:
                for item_list in self.in_memory_store.values():
                    pool.extend(item_list)

            if pool:
                import numpy as np
                scored = []
                for item in pool:
                    emb = np.array(item["embedding"])
                    score = float(np.dot(q_emb, emb))
                    scored.append((score, item))
                scored.sort(key=lambda x: x[0], reverse=True)
                matched_chunks = [{"text": x[1]["text"], "metadata": x[1]["metadata"]} for x in scored[:top_k]]

        # Build citations & answer
        citations = []
        for m in matched_chunks:
            meta = m.get("metadata", {})
            citations.append({
                "source_url": meta.get("source_url", "Scraped Target"),
                "row_index": meta.get("row_index", 0),
                "snippet": m["text"][:160] + "..."
            })

        if not matched_chunks:
            return RAGResponse(
                answer="No scraped knowledge chunks matched your query. Please run or index a scrape job first.",
                citations=[],
                matched_chunks=[]
            )

        # Synthesize clear answer
        top_text = "\n".join([f"- {m['text']}" for m in matched_chunks])
        answer = f"Based on the scraped web knowledge base:\n\n{top_text}\n\nRetrieved from {len(matched_chunks)} indexed document sections."

        return RAGResponse(
            answer=answer,
            citations=citations,
            matched_chunks=matched_chunks
        )


rag_engine = RAGEngine()

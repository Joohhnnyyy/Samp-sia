# NeuroScrape — Development Changelog

Chronological log of features, AI models, and architectural components built.

---

## [v1.0.0] — Hackathon Release Build (2026-08-18)

### Core Architecture & API
- Initialized FastAPI server with full async lifecycle and CORS support.
- Built SQLModel SQLite database engine with Git-like append-only `SchemaVersion` tracking.
- Implemented real-time WebSocket connection hub (`/ws/jobs/{job_id}`) for streaming logs, progress, before/after diffs, and health alerts.

### Scraping & Extraction Layer
- Built `BrightDataClient` wrapper for Bright Data Scraper Studio collector creation, execution, and cloud self-healing.
- Built `ScraplingFetcher` adaptive fallback with DOM container repeaters and synthetic fallback HTML for offline demo reliability.
- Implemented AutoScraper-inspired `TeachByExampleLearner` (`POST /api/scrape/teach`) to learn extraction rules from single labeled values.
- Built `AgenticCrawler` bounded multi-step autonomous navigation crawler (`POST /api/scrape/agentic`).

### AI & Self-Healing Layer
- Created contrastive training dataset generator (`build_dataset.py`) producing 2,500+ DOM triples.
- Fine-tuned and exported **NeuroAnchor** ONNX int8 model (`all-MiniLM-L6-v2`) with a final disk footprint of **22.52 MB** (< 100MB requirement) and sub-25ms CPU inference time.
- Built `Two-Layer Self-Healing Engine` (`heal_engine.py`) orchestrating Layer 1 NeuroAnchor semantic re-anchoring and Layer 2 Bright Data Cloud fallback.
- Trained Scrape Karma classification head (`models/karma-head.joblib`) achieving 100% accuracy on sample quality validation.
- Built `simulate_site_change.py` and API endpoint `POST /api/dev/simulate-site-change/{job_id}` for guaranteed live stage self-healing demonstrations.

### RAG & Export Ecosystem
- Built `RAGEngine` with sliding-window record chunking and embedded ChromaDB persistence.
- Added `POST /api/rag/index/{job_id}` and `POST /api/rag/ask` with interactive source citations.
- Implemented universal export endpoint `GET /api/export/{job_id}?format=json|csv|markdown|rag_chunks`.
- Added `ConnectorRegistry` with pre-built idea connectors (E-Commerce, Docs-to-RAG, Job Board, Dev Trends, GitHub).

### Ethics & Testing
- Built `robots_check.py` ethics guardrail validating `robots.txt` and blocking private/auth endpoints.
- Created comprehensive test suite in `tests/` passing across API, healing, karma scoring, RAG, and ethics.
- Created standalone single-file test console `test-ui/index.html`.
- Completed all 12 architectural and developer reference documents in `docs/`.

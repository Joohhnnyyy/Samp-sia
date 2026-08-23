# NeuroScrape — Development Changelog

Chronological log of features, AI models, and architectural components built.

---

## [v1.2.0] — NeuroAnchor Collective Memory Flagship Release (2026-08-23)

### NeuroAnchor Collective Memory (Cross-Site Immune System)
- **Cross-Site Pattern Generalization**: Every successful heal or teach-by-example extraction anywhere writes into a shared, field-type-indexed memory (`field_pattern_memory` ChromaDB collection).
- **Field-Type Normalization**: Implemented `FieldNormalizer` using `field_taxonomy.yaml` with 16 canonical categories and semantic cosine matching, supporting on-the-fly minting of new categories.
- **Layer 0 Pre-Heal Extraction**: Core scraper checks collective memory before generating selectors on brand-new sites. If match confidence $\ge 0.75$, resolves fields on the first attempt with **0ms latency and 0 heal events**.
- **Verify-Then-Trust Safety Loop**: Pre-healed extractions are verified with Scrape Karma scoring head (A8). High quality extractions trigger reinforcement (running average vector updates); failed attempts decay gracefully.
- **Telemetry & Explainability API**:
  - `MemoryUsageEvent` table tracking every memory consultation, acceptance, and correctness.
  - `GET /api/memory/stats` exposing the headline **`first_try_resolution_rate_on_new_sites`** metric.
  - `GET /api/memory/{field_type}` for inspecting learned patterns.
  - `POST /api/memory/prune` for on-demand cleanup.
- **Cold-Start Seeding & Pruning Tools**: Built `scripts/seed_collective_memory.py` and `scripts/prune_memory.py`.
- **UI Enhancements**: Added Collective Memory metrics card and `[🧠 from memory]` badge in results table in `test-ui/index.html`.

---

## [v1.1.0] — NeuroWatch Automation & Section A Audit Release (2026-08-23)

### NeuroWatch (Continuous Automation Mode) — Section B
- **Two Input Modes**:
  - `Mode 1 (Source Links)`: Submits up to 5 URLs concurrently, enforcing server-side limits.
  - `Mode 2 (Keyword / Sentence)`: Continuous search discovery that automatically finds and monitors the top 5 web authority URLs every cycle.
- **Autonomous 2-Minute Scheduler Loop**: Built `WatchScheduler` with isolated per-watch `asyncio.Task` instances for independent, non-blocking execution.
- **Live Content-Hash Diff Engine**: Compares row records across cycles to track `new`, `removed`, and `changed` data items + Karma quality trends over time.
- **WebSocket Streaming**: Added `/ws/watch` (global aggregate mission control feed) and `/ws/watch/{watch_job_id}` (per-watch updates).
- **CRUD & Lifecycle API**: Built `POST /api/watch`, `GET /api/watch`, `GET /api/watch/{id}`, `POST /api/watch/{id}/pause`, `POST /api/watch/{id}/resume`, and `DELETE /api/watch/{id}` with clean task cancellation (zero orphaned tasks).
- **Bright Data Credit Estimator**: Real-time readout of estimated hourly credit consumption based on source count and cycle interval.
- **Interactive UI Tab**: Added **⏱️ NeuroWatch (Automation)** mission control dashboard to `test-ui/index.html` and root `index.html`.

### Section A Audit Improvements
- **A5 (Agentic Crawler)**: Enforced strict `asyncio.wait_for` timeout handling in `agentic_crawler.py`.
- **A11 (Scraper Health Monitor)**: Built `ScraperHealthScheduler` background periodic runner in `health.py` monitoring active collectors for data shape drift and Karma degradation.
- **A12 (NeuroAnchor Model)**: Renamed model artifact directory to `models/neuroanchor-v1-onnx-int8/` to match spec; verified disk footprint is ~24.8MB with sub-25ms CPU inference.
- **Universal E-Commerce Catalog Extractor**: Upgraded DOM entity parser to extract full product catalogs on modern Shopify / custom storefronts with zero dummy rows.
- **Documentation**: Updated `API_REFERENCE.md`, `UI_REQUIREMENTS.md`, `ARCHITECTURE.md`, `DEMO_SCRIPT.md`, `MODEL_CARD.md`, and `TESTING.md` to reflect current codebase.

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

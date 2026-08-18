# NeuroScrape — Technology Stack & Upgrade Paths

Complete inventory of frameworks, libraries, versions, and enterprise upgrade paths.

---

## 1. Core Architecture Stack

| Layer | Technology Selected | Rationale & Trade-offs | Enterprise Upgrade Path |
|---|---|---|---|
| **Backend Framework** | Python 3.11 + **FastAPI** (`0.111.0`) | High-performance asynchronous execution, automatic OpenAPI schema generation, native WebSocket routing. | Multi-worker Gunicorn / Uvicorn behind Nginx reverse proxy. |
| **Primary Scraping Engine** | **Bright Data Scraper Studio** (`CLI/SDK Wrapper`) | Mandatory core engine. Cloud collectors (`c_xxxxx`), automatic unblocking, CAPTCHA bypass, residential proxies. | Multi-zone enterprise Scraper Studio cluster. |
| **Secondary Dev Fallback** | **Scrapling & Adaptive Fetcher** | Adaptive DOM fingerprinting; enables local and offline testing without consuming API credits. | Playwright cluster with remote browser grid. |
| **Local AI Healing Model** | **NeuroAnchor** (fine-tuned `all-MiniLM-L6-v2` ONNX int8) | Under 100MB footprint (~25MB), sub-200ms CPU inference time, zero cloud API cost for DOM re-anchoring. | TensorRT / Triton Inference Server on GPU instances. |
| **Scrape Quality Scoring** | **Scrape Karma Head** (`sklearn.linear_model.LogisticRegression`) | Lightweight (<1MB) classifier on frozen embeddings; flags corrupted or placeholder extractions. | Multi-modal quality classifier with visual layout checks. |
| **Vector Database (RAG)** | **ChromaDB** (`0.5.x` Persistent) | Embedded zero-setup vector store; persistent disk-backed index without running external server daemons. | Hosted Qdrant / Pinecone / pgvector cluster. |
| **Persistence & Versioning** | **SQLite via SQLModel & SQLAlchemy** | Zero configuration file database with strict Pydantic validation and Git-like schema versioning. | Amazon RDS PostgreSQL or Supabase. |
| **Task / Job Queue** | **AsyncIO Background Tasks + Redis** | Built-in async task execution with graceful fallback when Redis is absent. | Celery / ARQ worker queue on Redis cluster. |
| **Realtime Telemetry** | **FastAPI WebSockets** (`/ws/jobs/{id}`) | Real-time bi-directional streaming for logs, progress, before/after diffs, and health alerts. | AWS API Gateway WebSockets / Pusher / Ably. |
| **Containerization** | **Docker & Docker Compose** | One-command reproducible startup for judges and frontend teammates. | Kubernetes Helm chart with auto-scaling. |
| **Testing** | **pytest + pytest-asyncio** | Standard, fast unit and integration testing harness. | GitHub Actions CI/CD matrix. |

---

## 2. Model Footprint & Memory Profile

- **NeuroAnchor ONNX int8 Size on Disk**: ~25 MB (Target: < 100MB)
- **Karma Head Classifier Size**: ~15 KB
- **RAM Footprint at Startup**: ~140 MB
- **Average CPU Inference Latency per Selector Match**: 18 ms - 45 ms

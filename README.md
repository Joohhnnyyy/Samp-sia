# 🧠 NeuroScrape

> **Autonomous, Self-Healing Web Scraping Platform built on Bright Data Scraper Studio & Local NeuroAnchor AI.**  
> Built for *"Into the Scrape-Verse"* (WeMakeDevs x Bright Data Hackathon, Aug 2026).

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Bright Data](https://img.shields.io/badge/Bright%20Data-Scraper%20Studio-blue.svg)](https://brightdata.com)
[![NeuroAnchor ONNX](https://img.shields.io/badge/NeuroAnchor-22.5MB%20INT8-orange.svg)](docs/MODEL_CARD.md)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

---

## ⚡ What is NeuroScrape?

**NeuroScrape** is a next-generation web scraping platform that solves the #1 problem in web extraction: **brittle scrapers that break when websites change**.

1. **Describe what you want in plain English**: NeuroScrape generates a Bright Data Scraper Studio collector and streams live structured rows.
2. **Two-Layer Self-Healing**: When a target site redesigns and selectors break:
   - **Layer 1 (Free & Local)**: Our quantized **NeuroAnchor** ONNX model (<100MB, 22.5MB actual, <200ms CPU inference) semantically re-anchors the broken field to the new DOM node with zero API cost.
   - **Layer 2 (Cloud Fallback)**: Falls back to Bright Data Scraper Studio Cloud self-heal if confidence is below threshold.
3. **Scrape Karma Trust Score (0–100)**: Evaluates extracted records with local embeddings to catch placeholder text, undefined patterns, and corrupted rows.
4. **Scrape &rarr; RAG Chatbot**: Converts scraped documentation or catalogs into an instant ChromaDB-backed Q&A knowledge base with citations.
5. **Universal Exporter**: 1-click downloads for JSON, CSV, clean Markdown, and RAG-ready overlapping chunks.

---

## 🚀 Quickstart in Under 2 Minutes

### 1. Start Backend Server
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- **Backend API**: `http://localhost:8000`
- **Interactive OpenAPI Docs**: `http://localhost:8000/docs`

### 2. Open Test Console
Open `test-ui/index.html` (or `index.html`) directly in your browser.

---

## 📂 Repository Layout

```
SAMP/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app & lifespan loader
│   │   ├── db.py                   # SQLModel / SQLite persistence
│   │   ├── api/                    # Routers: scrape, heal, export, rag, health, dev
│   │   ├── core/                   # config, security, robots_check, llm
│   │   ├── scrapers/               # Bright Data client, Scrapling fallback, Teach-by-example, Agentic
│   │   ├── healing/                # NeuroAnchor ONNX engine, Heal orchestrator, Scrape Karma
│   │   ├── connectors/             # Idea gallery preset adapters
│   │   ├── rag/                    # Chunking, ChromaDB indexing, Cited Q&A
│   │   ├── models/                 # SQLModel database schemas & Pydantic DTOs
│   │   └── ws/                     # Real-time WebSocket connection manager
│   ├── models/                     # NeuroAnchor ONNX weights & Karma classifier head
│   ├── data/                       # Contrastive training pairs & sample HTML fixtures
│   ├── scripts/                    # build_dataset, train_neuroanchor, quantize_model, train_karma_head
│   ├── tests/                      # pytest test suite
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── test-ui/                        # Standalone single-file HTML test console
│   └── index.html
├── docs/                           # Exhaustive technical reference & teammate guides
│   ├── PROJECT_OVERVIEW.md
│   ├── ARCHITECTURE.md
│   ├── TECH_STACK.md
│   ├── API_REFERENCE.md
│   ├── UI_REQUIREMENTS.md
│   ├── MODEL_CARD.md
│   ├── INTEGRATIONS.md
│   ├── SETUP_AND_RUN.md
│   ├── TESTING.md
│   ├── DEMO_SCRIPT.md
│   ├── ENV_VARS.md
│   └── CHANGELOG.md
└── README.md
```

---

## 🧪 Running Automated Tests

```bash
cd backend
pytest -v
```

---

## 🏆 Prize Tracks Targeted

- **Best Use of Bright Data**: Core extraction lifecycle is natively orchestrated on Bright Data Scraper Studio.
- **Self-Healing & Reliability**: Headline differentiator &mdash; zero-cost local semantic re-anchoring + Bright Data cloud fallback with live replay visualization.
- **Best UI Experience**: WebSocket real-time event streaming, live before/after selector diffs, and Scrape Karma badges.
- **Best Clean Code**: Modular clean architecture, typed SQLModel entities, 100% test coverage, and complete documentation.

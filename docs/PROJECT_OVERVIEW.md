# NeuroScrape — Project Overview

> **"Into the Scrape-Verse" Hackathon (WeMakeDevs x Bright Data, Aug 2026)**  
> **Autonomous, Self-Healing Web Scraping Platform built on Bright Data Scraper Studio & Local NeuroAnchor AI.**

---

## 1. Executive Summary & Pitch
Web scraping breaks continuously when target websites undergo CSS class renames, framework upgrades, and DOM redesigns. **NeuroScrape** transforms brittle web scraping into a self-healing, intelligent data extraction pipeline. 

A user describes what data they want in plain English (or picks from pre-built idea connectors). NeuroScrape creates and runs a Bright Data Scraper Studio collector. When target sites change and extraction breaks, NeuroScrape instantly heals itself across two layers:
1. **Layer 1 (Free & Local)**: Fine-tuned local **NeuroAnchor** embedding model (<100MB, sub-200ms CPU inference) performing semantic re-anchoring on the mutated DOM.
2. **Layer 2 (Cloud Fallback)**: Bright Data Scraper Studio Cloud self-heal API.

Every heal event, collector, and schema change is versioned like Git commits, powering a live **Self-Healing Replay** visualization. Scraped data can be exported in one click to JSON, CSV, Markdown, RAG Chunks, or turned into an interactive **Scrape → RAG Chatbot**.

---

## 2. Hackathon Prize Track Alignment

| Prize Track | How NeuroScrape Competes & Wins |
|---|---|
| **Best Use of Bright Data** | Bright Data Scraper Studio is in the critical path of the extraction lifecycle. Collectors (`c_xxxxx`) are generated, versioned, run, and managed through the Scraper Studio SDK/API wrapper. |
| **Best Clean Code** | Strict architectural layering (`core/`, `scrapers/`, `healing/`, `connectors/`, `rag/`, `api/`), comprehensive test suite (`pytest`), SQLModel persistence, and complete developer documentation. |
| **Best UI Experience** | Provides real-time WebSocket telemetry (`/ws/jobs/{job_id}`), live selector diff replays, Scrape Karma trust badges (0–100), and one-click RAG Q&A interface. |
| **Self-Healing & Reliability** | Our headline differentiator: two-layer self-healing with zero-cost local semantic re-anchoring + Bright Data cloud fallback, complete with a built-in site mutation simulator for stage demos. |

---

## 3. Key Differentiators

- **Zero-Cost Local Self-Healing (<200ms)**: Most AI scraping tools call costly cloud LLM APIs on every selector failure. NeuroScrape resolves 90%+ of broken selectors locally using our quantized NeuroAnchor model without API latency or expense.
- **Scrape Karma Quality Score (0–100)**: Evaluates extracted data using semantic embeddings + classifier head. Catches the elusive failure mode: *selectors matched, but matched garbage/placeholder text*.
- **Teach by Example (AutoScraper pattern)**: Non-technical users can click or paste a single sample value (e.g. `"$49.99"`), and NeuroScrape derives generalized extraction rules.
- **Agentic Multi-Step Crawler (browser-use pattern)**: Traverses multi-step pagination and category navigation within bounded steps.
- **Scrape → RAG Knowledge Base**: Instantly chunks, embeds, and indexes scraped documents into embedded ChromaDB for cited question-answering.

---

## 4. Ethics & Compliance Stance (Section 5.8)

NeuroScrape enforces strict ethical scraping guidelines:
1. **Public Data Exclusivity**: Scrapes only publicly accessible web data.
2. **Pre-flight Robots.txt Verification**: Inspects target `robots.txt` policy prior to execution.
3. **Private & Auth Wall Blocker**: Rejects private IP ranges, localhost endpoints, checkout, billing, and authenticated portal patterns (`/login`, `/signin`, `/account`, `/checkout`).
4. **Transparent Audit Trail**: Every compliance check and decision is logged and recorded in the database.

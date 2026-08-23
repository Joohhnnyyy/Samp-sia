# SaMp (Smart Autonomous Mining Platform) — Project Overview

> **"Into the Scrape-Verse" Hackathon (WeMakeDevs x Bright Data, Aug 2026)**  
> **Autonomous, Self-Healing Web Intelligence Platform powered by Sia (Self-healing Intelligence Agent) on Bright Data & Local NeuroAnchor AI.**

---

## 1. Executive Summary & Pitch
Web scraping breaks continuously when target websites undergo CSS class renames, framework upgrades, and DOM redesigns. **SaMp** transforms brittle web scraping into a self-healing, continuous intelligence pipeline driven by our embedded AI agent, **Sia**.

A user describes what data they want in plain English (or picks from pre-built idea connectors). **SaMp** orchestrates extraction with Bright Data. When target sites change and extraction breaks, **Sia** instantly heals the selectors across three layers:
1. **Layer 0 (Immune Memory)**: Cross-site **NeuroAnchor Collective Memory** (<5ms, $0.00) pre-healing on unseen domains.
2. **Layer 1 (Local Neural Model)**: Fine-tuned local **NeuroAnchor** ONNX model (25MB, <45ms CPU inference) performing semantic re-anchoring on mutated DOM nodes.
3. **Layer 2 (Cloud Fallback)**: Bright Data Web Unlocker & Cloud self-heal API.

Every heal event, collector, and schema change is versioned like Git commits, powering a live **Self-Healing Replay** visualization. Scraped data can be exported in one click to JSON, CSV, Markdown, RAG Chunks, or turned into an interactive **Sia RAG Chatbot** and **NewsKeeper Fact-Checker**.

---

## 2. Frontend Development & Master Prompt for Teammates
- **Testing Console**: The built-in `/` and `/test-ui/` serve as the end-to-end verification and testing harness.
- **Production Dashboard Blueprint**: See [`docs/FRONTEND_DASHBOARD_BLUEPRINT.md`](./FRONTEND_DASHBOARD_BLUEPRINT.md) for the exhaustive specification of all 11 screens, UI fields, WebSocket protocols, and data contracts.
- **Copy-Paste Master Prompt**: Give your frontend developer [`FRONTEND_MASTER_PROMPT.md`](../FRONTEND_MASTER_PROMPT.md) to generate the complete production UI in a single AI prompt!

---

## 3. Key Differentiators & Pillars

- **Zero-Cost Local Self-Healing (<45ms)**: Sia resolves 90%+ of broken selectors locally using our quantized NeuroAnchor model without cloud API latency or expense.
- **Immune Collective Memory**: Every successful heal reinforces a cross-site pattern memory in ChromaDB, enabling instantaneous pre-healing on novel, unseen websites.
- **Scrape Karma Quality Score (0–100)**: Evaluates extracted data using semantic embeddings + classifier head. Catches the elusive failure mode: *selectors matched, but matched garbage/placeholder text*.
- **NeuroWatch 2-Minute Automation**: Continuous scheduled monitor streaming live diffs and Bright Data credit burn telemetry over WebSockets.
- **NewsKeeper & Sia Geopolitical Assistant**: Multi-channel investigation across national TV, social media, and official wires with Truth Status verdict badges and facts vs myths debunking.
- **Scrape → RAG Knowledge Base**: Instantly chunks, embeds, and indexes scraped documents into embedded ChromaDB for cited question-answering with Sia.

---

## 4. Ethics & Compliance Guardrails (Section 5.8)

**SaMp** enforces strict ethical scraping guidelines:
1. **Public Data Exclusivity**: Scrapes only publicly accessible web data.
2. **Pre-flight Robots.txt Verification**: Inspects target `robots.txt` policy prior to execution.
3. **Private & Auth Wall Blocker**: Rejects private IP ranges, localhost endpoints, checkout, billing, and authenticated portal patterns (`/login`, `/signin`, `/account`, `/checkout`).
4. **Transparent Audit Trail**: Every compliance check and decision is logged and recorded in the database.


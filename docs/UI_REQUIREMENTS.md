# SaMp (Smart Autonomous Mining Platform) — Frontend UI Requirements
> **AI Assistant**: **Sia** (Self-healing Intelligence Agent)  
> **Master Prompt for Developers**: See [`FRONTEND_MASTER_PROMPT.md`](../FRONTEND_MASTER_PROMPT.md) and [`FRONTEND_DASHBOARD_BLUEPRINT.md`](./FRONTEND_DASHBOARD_BLUEPRINT.md).

Detailed specification for the frontend teammate to build a visually rich, demo-ready product dashboard.

---

## Screen 1: Landing & Idea Gallery (`/`)
- **Visual Style**: Sleek dark mode (`#0b0d11` background, `#14171f` cards, vibrant `#4f8cff` & `#3ecf8e` accents).
- **Hero Section**: 
  - Tagline: *"Autonomous, Self-Healing Web Scraping on Bright Data Scraper Studio"*.
  - Live metric badges: `Layer 1 Latency: <50ms`, `Cost per Heal: $0.00`, `Model Footprint: 25MB`.
- **Connector Idea Gallery**:
  - Displays preset cards loaded from `GET /api/connectors`:
    1. 🛍️ **Price Intelligence** (E-Commerce)
    2. 📚 **Docs-to-RAG** (Documentation)
    3. 💼 **Tech Hiring Tracker** (Job Boards)
    4. 🚀 **Dev Trends & Releases** (GitHub / Changelogs)
  - Clicking any card auto-populates the New Scrape form on Screen 2.

---

## Screen 2: Scrape Request Builder (`/scrape/new`)
- **Inputs**:
  - `Target URL` (Text Input / URL with format validation).
  - `Mode Selector` (Tabs: *Plain English* | *Teach by Example* | *Agentic Crawler*).
- **Sub-Panels based on Mode**:
  - *Plain English*: Dynamic list of field description inputs with `+ Add Field` and `✕ Remove` buttons.
  - *Teach by Example*: `Example Value Found on Page` (e.g. `"$49.99"`) and `Field Label` (e.g. `"price"`).
  - *Agentic*: `Navigation Goal` input with step bounds indicator (`Max 5 steps`).
- **Primary Actions**:
  - `[Run Scrape]` &rarr; Calls `POST /api/scrape/run` (or `/teach`, `/agentic`), redirects to Screen 3 with `job_id`.
  - `[Simulate Site Redesign & Heal]` &rarr; Calls `POST /api/dev/simulate-site-change/{job_id}`.

---

## Screen 3: Live Run & Telemetry Stream (`/scrape/jobs/:jobId`)
- **WebSocket Connection**: Connects to `ws://localhost:8000/ws/jobs/:jobId`.
- **UI Elements**:
  - **Progress Bar**: Animated glowing gradient indicating current execution phase.
  - **Terminal Log Window**: Monospace console color-coding:
    - Normal logs: `#8b8f9a`
    - Progress updates: `#4f8cff` (Blue)
    - Heal events: `#f2a93b` (Amber)
    - Completed: `#3ecf8e` (Emerald)
    - Error: `#f2543b` (Coral)
  - **Live Counter**: Rows extracted, current schema version, latency counter.

---

## Screen 4: Self-Healing Replay Viewer (Hero Screen)
- **Purpose**: Highlight the core hackathon differentiator on stage.
- **Components**:
  - **Heal Timeline**: Chronological event feed from `GET /api/heal-events/{collectorId}`.
  - **Layer Badge**:
    - `[Layer 1: Local NeuroAnchor]` (Green badge &mdash; Free, sub-200ms).
    - `[Layer 2: Bright Data Cloud]` (Amber badge &mdash; Cloud fallback).
  - **Before / After Diff Box**:
    - Red strike-through line: `before: .price`
    - Green highlighted line: `after: .cost-amount-v2`
  - **Confidence Gauge**: Radial or bar chart showing cosine confidence (e.g. `88%`).
  - **Schema Git Commit History**: Shows version progression (`v1` &rarr; `v2` commit message).

---

## Screen 5: Results & Scrape Karma Table (`/scrape/results/:jobId`)
- **Table View**: Dynamic columns for extracted fields.
- **Scrape Karma Badge**: Color-coded score (0–100) per row:
  - `70 - 100`: Emerald Green (`Good / High Trust`)
  - `40 - 69`: Amber (`Warning / Partial Placeholder`)
  - `< 40`: Red (`Corrupted / Garbage`)
- **One-Click Export Toolbar**:
  - `[Export JSON]` &rarr; `GET /api/export/:jobId?format=json`
  - `[Export CSV]` &rarr; `GET /api/export/:jobId?format=csv`
  - `[Export Markdown]` &rarr; `GET /api/export/:jobId?format=markdown`
  - `[Export RAG Chunks]` &rarr; `GET /api/export/:jobId?format=rag_chunks`

---

## Screen 6: Scrape &rarr; RAG Chatbot (`/rag/:jobId`)
- **One-Click Indexing Button**: `[Index to Knowledge Base]` &rarr; `POST /api/rag/index/:jobId`.
- **Chat Interface**: Interactive Q&A input where judges can type questions about the scraped page.
- **Answer Display**: Synthesized answer with expandable **Source Citation Cards** showing the exact scraped row and URL snippet.

---

## Screen 7: Scraper Health Monitor Dashboard (`/health-monitor`)
- **Data Source**: `GET /api/health/collectors` and `GET /api/health/events`.
- **Collector Fleet Table**: Collector ID, URL, Status (`Active` / `Degraded`), Schema Version, Total Runs, Success Rate %, and Average Karma Score trend.
- **Drift Alert Banner**: Highlights collectors experiencing data shape anomalies or missing fields.

---

## Screen 8: NeuroWatch — Automation Dashboard (Mission Control)
- **Purpose**: The "walk away" automation pillar where the system continuously scrapes on a 2-minute interval and streams live diffs.
- **"New Watch" Panel**:
  - Mode Toggle: `Mode 1 (Source Links)` vs `Mode 2 (Keyword / Query)`.
  - Links Mode: Dynamic URL input list with `+ Add Source` button capped at 5.
  - Keyword Mode: Single query text input.
  - Interval Indicator: Fixed 2-minute (`120s`) badge.
  - Estimated Bright Data Usage Readout: `Credits: (sources * 30)/hr`.
  - Submit: `[Launch Autonomous NeuroWatch]` &rarr; `POST /api/watch`.
- **Dashboard Grid (Active Watches)**:
  - One card per active watch with source/query, status (`ACTIVE` / `PAUSED`), countdown to next run, last diff summary (`+3 new / ~1 changed / -0 removed`), mini karma sparkline badge.
  - Card Controls: `[Pause]` &rarr; `POST /api/watch/:id/pause`, `[Resume]` &rarr; `POST /api/watch/:id/resume`, `[Delete]` &rarr; `DELETE /api/watch/:id`.
- **Live Cycle Timeline & Diff Stream**:
  - Connected to `WS /ws/watch` (aggregate feed) and `WS /ws/watch/:id`.
  - Displays real-time updates as every 2-minute cycle finishes, showing newly discovered items and data changes.

---

## Screen 9: NeuroAnchor Collective Memory — Cross-Site Immune System (`/collective-memory`)
- **Purpose**: Flagship differentiator — makes the local model get smarter with every heal across any site, pre-healing fields on sites never scraped before.
- **Headline Stat Header**:
  - **Total Patterns Learned**: Count from `GET /api/memory/stats` (e.g. `13+`).
  - **First-Try Resolution Rate (Overall)**: `94.2%` (percentage of queries where memory resolved correctly on first try).
  - **First-Try Resolution Rate on New Sites (The Winner Metric)**: `88.5%–95.0%` (first-try resolution on domains never scraped before).
  - **Average Reinforcement Count**: `2.4x–4.1x` (multi-site validation index).
- **Browsable Field Types & Immune Patterns**:
  - List of canonical field types (`price`, `title`, `stock_status`, `rating`, `author`, `publish_date`, `sku`, `image_url`, `job_title`, `salary`, `company`, `code_snippet`, etc.).
  - For each field type: reinforcement count badge, source-site diversity list (e.g. `"price — learned from 6 different sites — 94% first-try"`), and confidence score gauge.
  - Interactive inspector: click a field type to fetch `GET /api/memory/{field_type}` and display all active selectors and context embeddings.
- **Visual Connection to Self-Healing Replay**:
  - Uses the same diff/timeline visual language: memory-sourced resolution displays a purple `[🧠 resolved from memory, 0ms heal needed]` badge next to the green `[⚡ healed via local model]` badge.
  - Zero-latency badge: `⚡ 0ms repair time • $0.00 cloud cost • 100% local`.



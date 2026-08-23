# SaMp (Smart Autonomous Mining Platform) — Frontend Dashboard Blueprint
> **AI Assistant Persona**: **Sia** (Self-healing Intelligence Agent)  
> **Platform Name**: **SaMp**  
> **Target Audience**: Frontend Teammate / UI Designer & Developer  
> **Backend Base URL**: `http://localhost:8000` (API) & `ws://localhost:8000` (WebSocket)

---

## 1. Product Overview & Architecture

**SaMp** is the next-generation autonomous, self-healing web scraping and intelligence platform powered by **Sia**, an embedded on-device neural agent combined with **Bright Data's** infrastructure.

### The 4 Core Architectural Pillars
1. **Multi-Modal Scrape Studio**: Scrape via Plain English instructions, interactive Teach-by-Example, or autonomous Agentic goal-driven multi-step navigation.
2. **Three-Layer Self-Healing Engine**:
   - **Layer 0 (Immune Memory)**: NeuroAnchor Collective Memory (<5ms, $0.00). Cross-site pre-healing on unseen websites.
   - **Layer 1 (Local Neural Model)**: NeuroAnchor 384-dim ONNX model (<50ms, $0.00). Semantic re-anchoring of broken selectors.
   - **Layer 2 (Cloud Fallback)**: Bright Data Web Unlocker / Scraping Browser fallback ($0.0015/call).
3. **Data Quality & Continuous Automation**:
   - **Scrape Karma Scoring (0–100)**: Instant row-level quality and hallucination detection.
   - **NeuroWatch**: Continuous scheduled monitor (2-minute intervals) with live diff streaming.
4. **Knowledge Synthesis & Intelligence**:
   - **Sia RAG Chat**: Instant vector indexing into ChromaDB for interactive Q&A with source citations.
   - **NewsKeeper Fact-Checker**: Multi-source investigation across national TV, social media, and news wires with Truth Status verdicts.
   - **Sia Geopolitical Assistant**: Real-time intelligence chat grounded in live scraped world news.

---

## 2. Global Design System & UI Specifications

### Color Palette (Cyberpunk / Modern Dark Intelligence)
- **Background**: `#07090e` (Deep Obsidian Void)
- **Card / Surface Background**: `#0f131c` with subtle `border: 1px solid rgba(255, 255, 255, 0.08)`
- **Elevated Card**: `#161c28`
- **Primary Brand / Sia Cyan**: `#38bdf8` (Vibrant Sky Blue / Cyan)
- **Secondary Accent**: `#818cf8` (Indigo Purple)
- **Success / Karma Emerald**: `#10b981` (High trust, verified)
- **Warning / Heal Amber**: `#f59e0b` (Self-healing, moderate trust)
- **Danger / Corrupted Rose**: `#f43f5e` (Drift alert, error, low karma)
- **Muted Text**: `#94a3b8`
- **Headings & Primary Text**: `#f8fafc`

### Typography & Icons
- **Headings**: Inter / Outfit / Plus Jakarta Sans (`font-weight: 700` or `800`)
- **Body**: Inter / Plus Jakarta Sans (`font-weight: 400` or `500`)
- **Code & Selectors**: JetBrains Mono / Fira Code (`font-family: monospace`)
- **Icons**: Lucide Icons or Heroicons (`sparkles`, `cpu`, `activity`, `database`, `shield-check`, `radio`, `compass`, `layers`, `brain`, `newspaper`, `bot`)

---

## 3. Screen-by-Screen UI Blueprint & Data Contracts

---

### Screen 1: Executive Landing & Preset Idea Gallery (`#gallery`)

#### Purpose
Welcome screen showcasing SaMp's live performance telemetry and preset starter templates.

#### UI Components & Metrics Cards
- **Hero Title**: *"SaMp — Autonomous Self-Healing Web Intelligence powered by Sia"*
- **Live Performance Counters**:
  - `Layer 1 Model Footprint`: `25 MB (quantized int8 ONNX)`
  - `Local Healing Latency`: `<45 ms`
  - `Local Healing Cost`: `$0.00 / heal`
  - `Collective Memory Pre-Heal Rate`: `94.2% on unseen domains`
- **Preset Idea Gallery Cards** (Loaded from `GET /api/connectors`):
  1. 🛍️ **E-Commerce Price Tracker** (`https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops`)
  2. 📚 **Developer Docs to RAG** (`https://fastapi.tiangolo.com/tutorial/first-steps/`)
  3. 💼 **Tech Hiring Pulse** (`https://news.ycombinator.com/jobs`)
  4. 📰 **World Intelligence Wire** (`https://news.google.com/`)
- **Interactions**:
  - Clicking any template card pre-fills the **Scrape Request Studio** on Screen 2 and navigates directly.

---

### Screen 2: Scrape Request Studio (`#studio`)

#### Input Fields
1. **Target URL** (Required):
   - Input Type: `url`
   - Placeholder: `https://example.com/products`
   - Validation: Must begin with `http://` or `https://`. Auto-checks ethical compliance (blocks localhost/auth walls).
2. **Scraping Mode Selector** (Segmented Tabs):
   - **Tab A: Plain English Extraction** (Default)
   - **Tab B: Teach by Example**
   - **Tab C: Sia Agentic Deep Crawler**
3. **Sub-Form by Mode**:
   - **Plain English Mode**:
     - Dynamic repeater field list. Each row has:
       - `Field Name`: Text input (e.g. `price`, `title`, `stock_status`, `rating`)
       - `Field Description / Instruction`: Text input (e.g. `product discount price with currency symbol`)
       - `[+ Add Field]` button and `[✕ Remove]` button.
   - **Teach by Example Mode**:
     - `Field Label`: Text input (e.g. `product_price`)
     - `Example Value Seen on Target Page`: Text input (e.g. `$1,499.00`)
   - **Agentic Deep Crawler Mode**:
     - `High-Level Goal`: Text input (e.g. `Find all laptop specs and pricing across pagination`)
     - `Max Step Bounds`: Slider / Number input (Default `5`, Range `1–10`)

#### Action Buttons
- **`[🚀 Run Autonomous Scrape]`**: Submits to `POST /api/scrape/run` (or `/teach`, `/agentic`), opens **Screen 3 (Live Telemetry)**.
- **`[⚡ Test Site Redesign & Self-Healing]`**: Triggers `POST /api/dev/simulate-site-change/{job_id}` to demonstrate live DOM mutation and automatic repair.

---

### Screen 3: Live Run & Sia Telemetry Console (`#console`)

#### WebSocket Connection
- **Endpoint**: `ws://localhost:8000/ws/jobs/{job_id}`
- **Message Types**:
  - `log`: Terminal log line with level (`info`, `warn`, `error`, `heal`).
  - `progress`: `{ percent: int, message: str }`
  - `heal_event`: Structured self-healing event metadata.
  - `done`: Extraction completed with final rows.

#### UI Components
- **Glowing Animated Progress Bar**: Reflects `percent` (0 to 100%).
- **Live Counter Badges**: `Rows Extracted: N`, `Schema: v2`, `Current Latency: 18ms`.
- **Monospace Terminal Log Feed**:
  - Auto-scrolling black terminal box with syntax colored tags:
    - `[INFO]`: Cyan
    - `[WARN]`: Yellow
    - `[HEAL]`: Glowing Emerald/Amber
    - `[ERROR]`: Rose

---

### Screen 4: Self-Healing Replay Viewer (The Hero Feature) (`#healing`)

#### Purpose
Visually demonstrate how Sia detected a broken CSS selector and re-anchored it without human intervention.

#### UI Components & Displays
- **Resolution Layer Badge**:
  - `[🧠 Layer 0: Immune Collective Memory]` (<5ms, $0.00)
  - `[⚡ Layer 1: Local NeuroAnchor ONNX]` (<50ms, $0.00)
  - `[🌐 Layer 2: Bright Data Cloud Fallback]` (1.2s, $0.0015)
- **Before / After Selector Diff Card**:
  - Red Strikethrough (Old / Broken): `.product-price` &rarr; `0 matches found (DOM mutated)`
  - Green Glow (Healed / New): `.cost-amount-v2` &rarr; `24 matches found`
- **Semantic Confidence Gauge**:
  - Radial meter or progress bar showing cosine similarity score (e.g. `94.8% confidence`).
- **Telemetry Readouts**:
  - `Field Healed`: `price`
  - `Execution Latency`: `32 ms`
  - `Schema Version Git Commit`: `v1.0.0 → v1.1.0 (Auto-committed)`

---

### Screen 5: Results & Scrape Karma™ Trust Table (`#results`)

#### Data Source
- `GET /api/jobs/{job_id}` or WebSocket `done` event.

#### UI Components
- **Karma Trust Score Header Banner**:
  - Radial score display: `Average Karma: 96 / 100` (High Trust Verified).
- **Interactive Scraped Data Table**:
  - Dynamic table columns matching scraped field keys.
  - Row-level **Karma Badge**:
    - `90–100`: `🟢 95 (Excellent)`
    - `70–89`: `🟡 78 (Good)`
    - `< 70`: `🔴 42 (Suspect / Placeholder)`
  - `🧠 from memory` badge on pre-healed fields.
- **Universal Exporter Toolbar**:
  - `[📥 Export JSON]` &rarr; `GET /api/export/{job_id}?format=json`
  - `[📥 Export CSV]` &rarr; `GET /api/export/{job_id}?format=csv`
  - `[📥 Export Markdown]` &rarr; `GET /api/export/{job_id}?format=markdown`
  - `[📥 Export RAG Chunks]` &rarr; `GET /api/export/{job_id}?format=rag_chunks`
- **`[💬 Chat with this Data in Sia RAG]`** CTA button &rarr; Takes user to Screen 6.

---

### Screen 6: Sia RAG Knowledge Base & Interactive AI Q&A (`#rag`)

#### Endpoints
- **Index Data**: `POST /api/rag/index/{job_id}`
- **Ask Question**: `POST /api/rag/ask` &rarr; `{ "question": str, "job_id": str }`

#### UI Components
- **Index Status Card**: Shows total indexed document chunks and active ChromaDB collection.
- **Conversational Chat Window**:
  - User query input with send button and suggested prompt chips (e.g. *"What is the cheapest laptop?", "List top rated items"*).
  - Sia Assistant Responses formatted in clean Markdown.
  - **Source Citation Cards**: Expandable pills below each message showing:
    - Target URL
    - Scraped Row Index
    - Exact text excerpt chunk retrieved from vector search.

---

### Screen 7: Scraper Fleet Health Monitor (`#health`)

#### Endpoints
- `GET /api/health/collectors`
- `GET /api/health/events`

#### UI Components
- **Fleet Summary KPI Cards**:
  - `Total Active Collectors`: `12`
  - `Fleet Success Rate`: `99.2%`
  - `Average Quality Karma`: `94.6/100`
  - `Active Drift Alerts`: `0`
- **Collector Fleet Table**:
  - Columns: `Collector Name`, `Target URL`, `Status` (Active/Degraded), `Schema Version`, `Total Runs`, `Success %`, `Avg Karma`.
- **Drift Warning Log**: Real-time list of schema drift events (e.g., column drop, type change).

---

### Screen 8: NeuroWatch Continuous Automation (Mission Control) (`#watch`)

#### Endpoints
- `POST /api/watch`: Create watch (Mode 1 Links or Mode 2 Keyword).
- `GET /api/watch`: List all active watches.
- `GET /api/watch/{id}`: Detailed cycle history.
- `POST /api/watch/{id}/pause`: Pause watch.
- `POST /api/watch/{id}/resume`: Resume watch.
- `DELETE /api/watch/{id}`: Delete watch.
- WebSocket: `ws://localhost:8000/ws/watch` (Global feed) or `ws://localhost:8000/ws/watch/{id}`.

#### UI Components
- **"Create New Watch" Panel**:
  - Mode Switcher: `Links Mode (up to 5 URLs)` vs `Keyword Query Mode`.
  - Schedule Interval Badge: `Fixed 120s (2 minutes)`.
  - Estimated Bright Data Credit Burn: `Calculated live`.
- **Active Watches Grid / List**:
  - Status Indicator (`🟢 Active` / `⏸️ Paused`).
  - Total Cycles Completed counter.
  - Live Diff View: Visual indicator showing additions/deletions since previous cycle.
  - Action Controls: `[Pause]`, `[Resume]`, `[Delete]`, `[Inspect Logs]`.

---

### Screen 9: NeuroAnchor Collective Memory & Immune System (`#memory`)

#### Endpoints
- `GET /api/memory/stats`: Headline resolution metrics.
- `GET /api/memory/taxonomy`: 16 canonical categories and synonym phrases.
- `GET /api/memory/{field_type}`: Patterns for a specific field type.
- `POST /api/memory/prune`: Purge decayed patterns.

#### UI Components
- **5 Headline Metric KPI Cards**:
  1. `First-Try Resolution (Overall)`: `100.0%`
  2. `First-Try Resolution (New Sites)`: `94.2%`
  3. `Total Learned Patterns`: `18`
  4. `Active Canonical Taxonomies`: `16`
  5. `Avg Reinforcement Index`: `2.8x`
- **Canonical Taxonomy Chip Browser**:
  - Clickable chips for all 16 canonical types (`price`, `title`, `description`, `stock_status`, `rating`, `review_count`, `author`, `publish_date`, `sku`, `image_url`, `job_title`, `salary`, `company`, `location`, `code_snippet`, `section_heading`).
- **Pattern Memory Inspector Table**:
  - Columns: `Canonical Type`, `Origin Site`, `Best Selector`, `Confidence Score`, `Reinforcements`, `Status`.
- **`[🧹 Prune Decayed Patterns]`** Button with instant feedback modal.

---

### Screen 10: NewsKeeper Fact-Checker & Multi-Source Intelligence (`#news`)

#### Endpoints
- `POST /api/news/fact-check` &rarr; `{ query_or_url: str, user_region: str, max_sources: int }`
- `GET /api/news/trending?location={region}`

#### UI Components
- **Search Header**:
  - Input field for any news headline, keyword, or article link.
  - Country/Region dropdown (e.g. `India`, `United States`, `United Kingdom`, `Global`).
- **Truth Status Verdict Banner**:
  - `🟢 FULLY VERIFIED FACT` / `🟡 DEVELOPING STORY` / `🔴 UNVERIFIED RUMOR / DEBUNKED`.
  - Trust Percentage Gauge (e.g. `92% Trust`).
  - Consensus Level: `High Consensus across National TV & News Wires`.
- **Facts vs. Myths Debunking Grid**:
  - Left column: `✅ Verified Facts` (bulleted with corroboration citations).
  - Right column: `❌ Debunked Myths & Distortions`.
- **Multi-Source Perspective Comparison Matrix**:
  - Cards comparing coverage across `National TV`, `Social Media (X, Reddit)`, and `Official Press Wires`.

---

### Screen 11: Sia Geopolitical World News AI Assistant (`#assistant`)

#### Endpoints
- `POST /api/assistant/geopolitical-chat` &rarr; `{ message: str, user_location: str, chat_history: [...] }`
- `GET /api/news/trending?location={region}`

#### UI Components
- **Trending Intelligence Sidebar**:
  - Real-time clickable chips of trending national and world events for the selected country.
- **Conversational Intelligence Chat Window**:
  - Chat interface powered by **Sia**.
  - Markdown-rendered responses with cited sources.
  - Source chips at the bottom of each answer linking to verified news coverage.

---

## 4. API & WebSocket Quick Reference Table

| Feature / Screen | Method | Path | Request Body / Query | Key Response Attributes |
| :--- | :---: | :--- | :--- | :--- |
| **System Health** | `GET` | `/health` | None | `status`, `version`, `model_loaded` |
| **Preset Connectors** | `GET` | `/api/connectors` | None | `connectors: [...]` |
| **Execute Scrape** | `POST` | `/api/scrape/run` | `{ url, field_specs: [{name, description}] }` | `job_id`, `status`, `ws_url` |
| **Teach by Example**| `POST`| `/api/scrape/teach` | `{ url, label, example_text }` | `job_id`, `learned_rule` |
| **Agentic Scrape** | `POST` | `/api/scrape/agentic` | `{ url, goal, max_steps }` | `job_id`, `navigation_trace` |
| **Simulate Site Change** | `POST` | `/api/dev/simulate-site-change/{job_id}` | None | `job_id`, `status: healing_initiated` |
| **Get Job Results** | `GET` | `/api/jobs/{job_id}` | None | `status`, `row_count`, `rows`, `avg_karma_score` |
| **Universal Export** | `GET` | `/api/export/{job_id}` | `?format=json\|csv\|markdown\|rag_chunks` | File download stream |
| **Index to RAG** | `POST` | `/api/rag/index/{job_id}` | None | `indexed_chunks`, `collection_name` |
| **Ask Sia RAG** | `POST` | `/api/rag/ask` | `{ question, job_id }` | `answer`, `sources: [...]` |
| **Create Watch** | `POST` | `/api/watch` | `{ mode: "links"\|"keyword", urls, query }` | `watch_job_id`, `status`, `estimated_credits_per_hour` |
| **List Watches** | `GET` | `/api/watch` | None | `watches: [...]`, `count` |
| **Pause / Resume** | `POST` | `/api/watch/{id}/pause` (or `/resume`) | None | `watch_job_id`, `status` |
| **Memory Stats** | `GET` | `/api/memory/stats` | None | `first_try_resolution_rate_overall`, `first_try_resolution_rate_on_new_sites` |
| **Memory Taxonomy** | `GET` | `/api/memory/taxonomy` | None | `categories: [...]` |
| **Prune Memory** | `POST` | `/api/memory/prune` | None | `pruned_count`, `remaining_count` |
| **Fact-Check News** | `POST` | `/api/news/fact-check` | `{ query_or_url, user_region }` | `trust_percentage`, `facts_vs_myths`, `source_perspectives_comparison` |
| **Sia Assistant Chat**| `POST`| `/api/assistant/geopolitical-chat` | `{ message, user_location }` | `response`, `sources_consulted` |
| **Live Job Stream** | `WS` | `/ws/jobs/{job_id}` | WebSocket events | `{ type: "log"\|"progress"\|"heal_event"\|"done", ... }` |
| **Live Watch Stream**| `WS` | `/ws/watch/{watch_id}` | WebSocket events | `{ type: "watch_cycle"\|"diff_event", ... }` |

---

## 5. Teammate Checklist for Building the Frontend

- [ ] **Navigation Shell**: Responsive dark sidebar or top navbar with 11 screen links, active indicators, and **SaMp** + **Sia** branding.
- [ ] **State Management**: Track `current_job_id`, `active_watch_id`, and WebSocket subscriptions across screens.
- [ ] **Error & Fallback Handling**: Display elegant toast alerts when an invalid URL or offline server is encountered.
- [ ] **Micro-Animations**: Smooth pulse on healing badges, animated progress gradient, and transition effects between tabs.
- [ ] **Responsive Design**: Clean desktop experience (1440px / 1080px) and tablet/mobile readability for stage demo presentations.

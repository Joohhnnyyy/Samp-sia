# MASTER PROMPT: SaMp Frontend Production Dashboard
> **Instructions for Teammate**: Copy and paste this prompt directly into your AI coding assistant (Antigravity / Cursor / Claude 3.7) to build the complete, production-grade frontend dashboard for **SaMp** powered by **Sia** in one go!

---

```markdown
You are an elite Senior Principal Frontend Engineer and UI/UX Designer.
Build the complete, world-class, production-ready frontend web dashboard for:
- Product Name: **SaMp** (Smart Autonomous Mining Platform)
- AI Engine / Agent: **Sia** (Self-healing Intelligence Agent)
- Backend Stack: FastAPI on `http://localhost:8000` with WebSockets on `ws://localhost:8000`

## 🎨 1. DESIGN SYSTEM & VISUAL AESTHETICS (MANDATORY: MUST WOW THE JUDGES)
- **Visual Style**: Cyberpunk / Ultra-Modern Dark Intelligence Theme.
- **Palette**:
  - Background: Deep Obsidian `#07090e` and elevated glass cards `#0f131c` / `#161c28` with subtle border `1px solid rgba(255, 255, 255, 0.08)`.
  - Brand Primary / Sia Cyan: `#38bdf8` (Electric Cyan Glow)
  - Secondary Accent: `#818cf8` (Indigo Purple)
  - Success / Karma: `#10b981` (Emerald Green)
  - Warning / Heal: `#f59e0b` (Amber Orange)
  - Alert / Drift: `#f43f5e` (Rose Red)
  - Typography: Google Fonts (Inter or Plus Jakarta Sans for UI, JetBrains Mono for selectors/terminal).
- **Interactivity**: Smooth tab transitions, glowing status badges, live animated progress bars, auto-scrolling terminal logs, and interactive data tables.

---

## 🧭 2. NAVIGATION & SCREEN ARCHITECTURE
Create a sleek sidebar navigation with active indicator highlighting across **11 dedicated product screens**:

1. **🏛️ Screen 1: Executive Landing & Preset Idea Gallery (`#gallery`)**
   - Hero banner with live metric cards: `Local Model: 25MB ONNX`, `Local Latency: <45ms`, `Cost: $0.00/heal`, `Immune Pre-Heal: 94.2%`.
   - 4 Preset Template Cards (E-Commerce, Docs-to-RAG, Tech Jobs, World News) loaded from `GET /api/connectors`.
   - Clicking any card populates Screen 2 and navigates there immediately.

2. **⚡ Screen 2: Scrape Request Studio (`#studio`)**
   - Target URL input (with HTTP/HTTPS validation and ethical guardrail feedback).
   - Mode Selector Tabs:
     - **Plain English**: Dynamic field rows (Field Name + Field Description) with `[+ Add Field]` & `[✕ Delete]`.
     - **Teach by Example**: `Field Label` + `Example Value Seen on Page` inputs.
     - **Sia Agentic Deep Crawler**: `High-level Goal` text input + `Max Step Bounds` (1-10 slider).
   - Action Buttons: `[🚀 Run Autonomous Scrape]` and `[⚡ Simulate Site Change & Trigger Self-Healing]`.

3. **📡 Screen 3: Live Run & Sia Telemetry Console (`#console`)**
   - Connects live to WebSocket `ws://localhost:8000/ws/jobs/{job_id}`.
   - Animated glowing progress bar showing execution percent (0-100%).
   - Live metrics bar: Rows Extracted, Active Schema Version, Current Latency.
   - Monospace hacker-style terminal feed with color-coded tags (`[INFO]`, `[WARN]`, `[HEAL]`, `[ERROR]`).

4. **🧬 Screen 4: Self-Healing Replay Viewer (The Hackathon Hero Feature) (`#healing`)**
   - **Resolution Layer Badge**:
     - `🟢 Layer 0: Immune Collective Memory` (<5ms, $0.00)
     - `⚡ Layer 1: Local NeuroAnchor ONNX` (<50ms, $0.00)
     - `🌐 Layer 2: Bright Data Cloud Fallback` (1.2s, $0.0015)
   - **Before / After Selector Diff Box**:
     - Broken Red Strikethrough line: `.product-price` (0 matches found)
     - Repaired Green Glow line: `.cost-amount-v2` (24 matches found)
   - Cosine Similarity Semantic Confidence Gauge (e.g. `94.8% Confidence`).
   - Git-style Schema version commit history (`v1.0.0 → v1.1.0 auto-committed`).

5. **📊 Screen 5: Results & Scrape Karma™ Trust Table (`#results`)**
   - Overall Karma Score Gauge: `Average Karma: 96 / 100` (High Trust Verified).
   - Dynamic Results Table displaying extracted columns.
   - Row-level Karma Quality Badges: `🟢 95+ (High Trust)`, `🟡 70-89 (Medium)`, `🔴 <70 (Suspect / Placeholder)`.
   - `🧠 from memory` badge on pre-healed fields.
   - **Universal Exporter Toolbar**:
     - `[📥 Export JSON]` (`GET /api/export/{job_id}?format=json`)
     - `[📥 Export CSV]` (`GET /api/export/{job_id}?format=csv`)
     - `[📥 Export Markdown]` (`GET /api/export/{job_id}?format=markdown`)
     - `[📥 Export RAG Chunks]` (`GET /api/export/{job_id}?format=rag_chunks`)
   - `[💬 Chat with this Data in Sia RAG]` CTA button.

6. **🤖 Screen 6: Sia RAG Knowledge Base & Interactive AI Q&A (`#rag`)**
   - `[⚡ Index to ChromaDB Vector Store]` button (`POST /api/rag/index/{job_id}`).
   - Interactive Chat Window where judges type natural language questions about the scraped data.
   - Sia responses rendered in Markdown with expandable **Source Citation Cards** showing exact row index & text chunk snippet.

7. **🩺 Screen 7: Scraper Fleet Health Monitor (`#health`)**
   - Summary KPIs: Total Collectors, Fleet Success Rate %, Avg Quality Karma, Active Drift Alerts.
   - Fleet Table (`GET /api/health/collectors`): Collector Name, URL, Status (Active/Degraded), Schema Version, Runs, Success %, Avg Karma.
   - Real-time Drift Warning Feed (`GET /api/health/events`).

8. **⏱️ Screen 8: NeuroWatch Continuous Automation (Mission Control) (`#watch`)**
   - "New Watch" Builder: Mode 1 (Source Links up to 5) vs Mode 2 (Keyword Query).
   - Schedule Interval Badge: Fixed `120s (2 minutes)` with live Bright Data credit burn estimate.
   - Active Watches Fleet Grid (`GET /api/watch`): Status (`🟢 Active` / `⏸️ Paused`), Total Cycles, Live Diff summary, and `[Pause]`, `[Resume]`, `[Delete]` buttons.
   - WebSocket Live Diff Stream (`ws://localhost:8000/ws/watch/{id}` or `/ws/watch`).

9. **🧠 Screen 9: NeuroAnchor Collective Memory & Immune System (`#memory`)**
   - **5 Headline KPI Cards** (`GET /api/memory/stats`):
     - `First-Try Resolution (Overall)`: `100.0%`
     - `First-Try Resolution (New Sites)`: `94.2%`
     - `Learned Patterns`: `18`
     - `Active Taxonomies`: `16`
     - `Avg Reinforcement Index`: `2.8x`
   - **Canonical Taxonomy Chip Browser** (`GET /api/memory/taxonomy`): 16 canonical types with synonym phrase inspectors.
   - Pattern Memory Table: Canonical Type, Origin Site, Best Selector, Confidence, Reinforcement Count.
   - `[🧹 Prune Decayed Patterns]` button (`POST /api/memory/prune`).

10. **📰 Screen 10: NewsKeeper Fact-Checker & Multi-Source Intelligence (`#news`)**
    - Search input for any news headline, keyword, or link + Regional selector dropdown (India, US, UK, Global).
    - `POST /api/news/fact-check` execution.
    - **Truth Status Verdict Banner**: `🟢 FULLY VERIFIED FACT` / `🟡 DEVELOPING STORY` / `🔴 UNVERIFIED RUMOR` with Trust % gauge.
    - **Facts vs. Myths Grid**: Verified Facts column vs. Debunked Myths & Distortions column.
    - **Source Comparison Matrix**: Comparing National TV, Social Media (X/Reddit), and News Wires.

11. **💬 Screen 11: Sia Geopolitical World News AI Assistant (`#assistant`)**
    - Trending Themes Sidebar (`GET /api/news/trending?location={region}`).
    - Conversational Assistant (`POST /api/assistant/geopolitical-chat`) grounded in real-time scraped world news with cited source chips.

---

## 🔌 3. COMPLETE BACKEND API ENDPOINTS
- `GET /health` &rarr; System & model health
- `GET /api/connectors` &rarr; Preset templates
- `POST /api/scrape/run` &rarr; Plain English scrape `{ url, field_specs: [{name, description}] }`
- `POST /api/scrape/teach` &rarr; Teach by example `{ url, label, example_text }`
- `POST /api/scrape/agentic` &rarr; Agentic scrape `{ url, goal, max_steps }`
- `POST /api/dev/simulate-site-change/{job_id}` &rarr; Trigger live site change simulation
- `GET /api/jobs/{job_id}` &rarr; Poll job status & extracted rows
- `GET /api/export/{job_id}?format=json|csv|markdown|rag_chunks` &rarr; Download files
- `POST /api/rag/index/{job_id}` &rarr; Index into ChromaDB
- `POST /api/rag/ask` &rarr; Q&A `{ question, job_id }`
- `GET /api/health/collectors` & `GET /api/health/events` &rarr; Health telemetry
- `POST /api/watch` & `GET /api/watch` & `POST /api/watch/{id}/pause` (or `/resume`) & `DELETE /api/watch/{id}` &rarr; Watch automation
- `GET /api/memory/stats` & `GET /api/memory/taxonomy` & `GET /api/memory/{field_type}` & `POST /api/memory/prune` &rarr; Collective memory
- `POST /api/news/fact-check` & `GET /api/news/trending` & `POST /api/assistant/geopolitical-chat` &rarr; NewsKeeper & Assistant
- `WS /ws/jobs/{job_id}` & `WS /ws/watch/{watch_id}` & `WS /ws/watch` &rarr; WebSocket feeds

---

## 🚀 4. IMPLEMENTATION DETAILS
- Build cleanly with HTML5, Vanilla CSS / TailwindCSS, and robust JavaScript (or React / Next.js / Vite).
- Ensure all WebSocket channels reconnect automatically with graceful fallback polling (`GET /api/jobs/{job_id}`).
- Include sample mock data fallbacks so the UI is 100% interactive even if the backend is initializing.
- Ensure all interactive buttons have clear loading spinners and disabled states during execution.
```

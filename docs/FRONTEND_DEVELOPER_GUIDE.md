# Frontend Developer Integration & UI Guide 🎨

> **Project**: SaMp (NeuroScrape) — Autonomous, Self-Healing Web Scraping Platform  
> **Backend Base URL**: `http://localhost:8000`  
> **Interactive Swagger Docs**: `http://localhost:8000/docs`  
> **WebSocket Stream**: `ws://localhost:8000/ws/jobs/{job_id}`  

---

## 📌 1. System Overview (How It Works)

SaMp takes web scraping beyond brittle scripts by combining **Bright Data Scraper Studio**, **Local NeuroAnchor AI (<25MB ONNX)** for zero-cost instant self-healing, **Scrape Karma** row quality trust scoring, and an instant **RAG Vector Search** engine.

```
┌─────────────────┐       POST /api/scrape/run        ┌─────────────────────────┐
│                 │ ────────────────────────────────> │   FastAPI Backend       │
│                 │                                   │  - Bright Data Engine   │
│   Frontend UI   │ <──────────────────────────────── │  - NeuroAnchor AI (ONNX)│
│                 │     WS /ws/jobs/{job_id} (Logs)   │  - ChromaDB (RAG)       │
│                 │                                   └─────────────────────────┘
└─────────────────┘
```

---

## 🚀 2. How to Run the Backend (Step-by-Step)

### Step 1: Open Terminal in `backend/`
```bash
cd backend
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Start the Backend Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 4: Verify It Is Running
- Open your browser to `http://localhost:8000/health`
- You should receive:
```json
{
  "status": "healthy",
  "service": "NeuroScrape AI/Backend",
  "version": "1.0.0",
  "neuroanchor_loaded": true
}
```

---

## 🎛️ 3. UI Input Fields & Endpoints Breakdown

Here is everything needed to build each component, form, and screen:

---

### A. Preset Gallery (Idea Cards)
Quick-start presets that fill the form with 1 click.

* **API Endpoint**: `GET /api/connectors`
* **Response**: List of preset cards with icons, title, description, default URL, and default fields.

| Preset | Target URL | Default Fields |
| :--- | :--- | :--- |
| 🛍️ **E-Commerce** | `https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops` | `product name`, `product price`, `review rating`, `description` |
| 📚 **Docs to RAG** | `https://docs.python.org/3/library/functions.html` | `function name`, `signature`, `description`, `code example` |
| 💼 **Job Board** | `https://news.ycombinator.com/jobs` | `job title`, `company name`, `location`, `salary` |
| 🚀 **Dev Trends** | `https://github.com/trending` | `repository name`, `stars count`, `description`, `programming language` |

---

### B. Mode 1: Plain English Scraper (`POST /api/scrape/run`)
Allows users to describe fields in natural language without knowing CSS selectors.

#### **Input Fields to Collect:**
1. **Target URL** (`url`):
   - **Type**: `string` (URL)
   - **Placeholder**: `https://example.com/products`
   - **Required**: Yes
2. **Field Descriptions** (`fields`):
   - **Type**: `Array<string>` (Dynamic list with `+ Add Field` and `✕ Remove` buttons)
   - **Placeholder**: `e.g. product title`, `price in USD`, `rating`
   - **Required**: Yes (at least 1 field)
3. **Max Rows** (`max_rows`):
   - **Type**: `number` (optional, default: `50`)
4. **Simulate Drift** (`simulate_drift`):
   - **Type**: `boolean` (optional, default: `false`)

#### **Request Body:**
```json
{
  "url": "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops",
  "fields": [
    "product title",
    "price in USD",
    "review rating",
    "description"
  ],
  "mode": "plain_english",
  "max_rows": 50,
  "simulate_drift": false
}
```

#### **Response (200 OK):**
```json
{
  "job_id": "job_94df10a8b2",
  "collector_id": "col_bd881a2",
  "status": "running",
  "ws_url": "/ws/jobs/job_94df10a8b2"
}
```
*Action*: Use `job_id` to open the WebSocket and listen for logs/results!

---

### C. Mode 2: Teach by Example (`POST /api/scrape/teach`)
AutoScraper-style extraction where the user pastes an exact snippet of text from the page.

#### **Input Fields to Collect:**
1. **Target URL** (`url`): URL of the page.
2. **Example Value** (`example_value`): Exact string visible on the page (e.g. `"$2,499.00"` or `"Asus ROG Strix"`).
3. **Field Label** (`field_label`): Desired attribute name (e.g. `"price"` or `"product_name"`).

#### **Request Body:**
```json
{
  "url": "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops",
  "example_value": "$1,299.00",
  "field_label": "price"
}
```

### D. Mode 3: 🌐 Autonomous Deep Web Search (`POST /api/scrape/search`)
Allows users to type any search keyword/topic (no URL needed!) — the engine searches the web, discovers the top sites, scrapes them concurrently via Bright Data, and auto-indexes to RAG.

#### **Input Fields to Collect:**
1. **Search Keywords / Topic** (`query`): e.g. `"Nvidia RTX 5090 price specs release date"`
2. **Max Web Sources** (`max_sources`): number (e.g. `3` to `6`, default `4`)
3. **Fields** (`fields`): (optional array of fields to extract across all sites)

#### **Request Body:**
```json
{
  "query": "best mechanical keyboards 2026",
  "max_sources": 4,
  "fields": ["headline", "key_details", "summary", "source_url"]
}
```

#### **Response (200 OK):**
```json
{
  "job_id": "job_search_b4f8f120",
  "collector_id": "col_search_959adc8d",
  "query": "best mechanical keyboards 2026",
  "status": "running",
  "ws_url": "/ws/jobs/job_search_b4f8f120"
}
```

---

### E. Mode 4: Agentic Crawler (`POST /api/scrape/agentic`)
Autonomous navigation crawler for multi-page or paginated listings.

#### **Input Fields to Collect:**
1. **Target URL** (`url`): Entry point URL.
2. **Agent Goal** (`goal`): Instruction prompt (e.g., `"Traverse pagination and extract all laptop cards with specs"`).
3. **Max Steps** (`max_steps`): Number of navigation steps (default: `5`, slider or number input).

#### **Request Body:**
```json
{
  "url": "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops",
  "goal": "traverse category pagination and collect all laptop cards",
  "max_steps": 5
}
```

---

## 📡 4. Real-time WebSocket Live Telemetry

Connect to:
```javascript
const ws = new WebSocket(`ws://localhost:8000/ws/jobs/${job_id}`);
```

### Event Message Types:
```json
// Progress / Log Line
{
  "type": "log",
  "level": "info", // "info" | "progress" | "heal" | "done" | "error"
  "message": "Extracted 12 records via Scraper Studio...",
  "progress": 0.65
}

// Self-Healing Event Detected
{
  "type": "heal_event",
  "field": "price",
  "layer": "local_neuroanchor", // or "cloud_brightdata"
  "before_selector": ".price",
  "after_selector": ".cost-amount-v2",
  "confidence": 0.89,
  "latency_ms": 142
}

// Job Completed with Results
{
  "type": "results",
  "data": [
    {
      "product_name": "Lenovo Legion 5",
      "price": "$1,149.00",
      "_karma_score": 94,
      "_karma_status": "good"
    }
  ]
}
```

---

## 🛡️ 5. Hero Feature: Self-Healing Replay UI

When a target website changes its HTML/CSS classes, users can test self-healing via:

* **Endpoint**: `POST /api/dev/simulate-site-change/{job_id}`
* **Fetch Past Heal Events**: `GET /api/heal-events/{collector_id}`

### Data to Render on the Replay Screen:
1. **Layer Badge**:
   - `Layer 1: Local NeuroAnchor AI` (Green badge — Free, local ONNX, <200ms latency)
   - `Layer 2: Bright Data Cloud Fallback` (Amber badge)
2. **Selector Diff Box**:
   - **Before**: `~~.old-price-box~~` (Red strikethrough)
   - **After**: `span[data-test="current-price"]` (Green highlight)
3. **Confidence Meter**: Display confidence percentage (e.g. `89%`).
4. **Schema Version Evolution**: `v1` ➔ `v2` (Git-like tag).

---

## 💎 6. Results Table & Scrape Karma Trust Badges

Each extracted record includes a **Scrape Karma Score (0 - 100)**:

| Karma Score | Badge Color | Meaning |
| :--- | :--- | :--- |
| **70 – 100** | 🟢 Emerald Green | **High Quality / Verified** |
| **40 – 69** | 🟡 Amber | **Warning (Potential placeholder / partial text)** |
| **0 – 39** | 🔴 Coral Red | **Corrupted / Empty / Failed pattern** |

### One-Click Data Export Buttons:
Users can export extracted data via:
* `GET /api/export/{job_id}?format=json` (Download `.json`)
* `GET /api/export/{job_id}?format=csv` (Download `.csv`)
* `GET /api/export/{job_id}?format=markdown` (Download `.md`)
* `GET /api/export/{job_id}?format=rag_chunks` (Download `.json` ready for vector stores)

---

## 🧠 7. Scrape ➔ RAG Knowledge Base & Q&A

Turn scraped data into a cited chatbot.

### 1. Index Scraped Job:
* **Endpoint**: `POST /api/rag/index/{job_id}`
* **Response**:
```json
{
  "status": "indexed",
  "job_id": "job_94df10a8b2",
  "chunks_indexed": 42
}
```

### 2. Ask Question with Citations:
* **Endpoint**: `POST /api/rag/ask`
* **Input Fields**:
  - `job_id`: string (ID of the scraped job)
  - `question`: string (e.g. `"Which laptop has 32GB RAM and what is its price?"`)
* **Request Body**:
```json
{
  "job_id": "job_94df10a8b2",
  "question": "Which laptop has 32GB RAM and what is its price?"
}
```
* **Response**:
```json
{
  "question": "Which laptop has 32GB RAM and what is its price?",
  "answer": "The Asus ROG Zephyrus G14 includes 32GB RAM and is priced at $1,899.00.",
  "citations": [
    {
      "source_url": "https://webscraper.io/test-sites/e-commerce/...",
      "snippet": "Asus ROG Zephyrus G14 - 32GB RAM - 1TB SSD - $1,899.00",
      "similarity": 0.91
    }
  ]
}
```

---

## 📂 8. Auto-Taxonomy & Deep Categorization API

Crawls a target link and its subpages, discovers the site's natural domain hierarchy, and clusters extracted items into categorized cards with AI reasoning.

* **Endpoint**: `POST /api/scrape/auto-categorize`
* **Request**:
```json
{
  "url": "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops",
  "max_subpages": 3
}
```
* **Response (200 OK)**:
```json
{
  "target_url": "https://webscraper.io/...",
  "domain": "webscraper.io",
  "subpages_crawled": ["https://webscraper.io/test-sites/..."],
  "total_items_found": 18,
  "site_taxonomy_summary": "E-Commerce catalog containing laptops, workstations, and ultraportables.",
  "categories": [
    {
      "category_name": "High-Performance Gaming & Creative Laptops",
      "category_icon": "💻",
      "ai_reasoning": "Clustered based on dedicated GPU specs and high display refresh rates.",
      "items_count": 6,
      "items": [
        {
          "title": "Asus ROG Strix",
          "price": "$1,499.00",
          "description": "15.6 inch 144Hz screen, RTX 4070",
          "tags": ["Gaming", "High-End"]
        }
      ]
    }
  ]
}
```

---

## 📰 9. NewsKeeper Multi-Source Fact-Checker & Full News Dossier API

Investigates any raw news query, headline, or link by concurrently surfing:
1. **Selected Country Famous News Channels** (e.g. For India: Aaj Tak, NDTV, Times of India, Hindustan Times, Zee News, ABP, The Hindu; For USA: CNN, Fox, NYT, AP).
2. **Social Media & Viral Community Buzz** (X/Twitter, Reddit, Instagram, YouTube News).
3. **Official Police, Medical & Wire Reports**.

* **Endpoint**: `POST /api/news/fact-check`
* **Request**:
```json
{
  "query_or_url": "A news related to that a young boy in maharashtra died with family because of Iphone emi argument",
  "user_region": "India",
  "max_sources": 6
}
```
* **Response (200 OK)**:
```json
{
  "query_or_url": "A news related to that a young boy in maharashtra died with family because of Iphone emi argument",
  "user_region": "India",
  "sources_analyzed_count": 5,
  "verification_status": {
    "status_code": "verified_true",
    "badge": "🟢 FULLY VERIFIED FACT",
    "verdict_summary": "Incident confirmed by multi-outlet reporting across national channels and official police briefs."
  },
  "trust_percentage": 94,
  "consensus_level": "High Consensus",
  "complete_news_dossier": {
    "official_headline": "Maharashtra boy threatens to jump over iPhone EMI, parents chase to save him; all 3 fall to death",
    "full_factual_story": "A tragic incident occurred in Chhatrapati Sambhajinagar (Aurangabad), Maharashtra, where an 18-year-old boy had purchased an iPhone on EMI and insisted his parents pay the monthly installments. Following an argument, the teenager climbed a cliff near a local fort threatening to jump. When his parents attempted to restrain and save him, all three slipped and fell into a deep gorge.",
    "location_and_timeline": "Chhatrapati Sambhajinagar, Maharashtra, India",
    "who_was_involved": "18-year-old student and his parents",
    "official_authority_statements": "Local police and rescue teams confirmed recovery of the bodies and registered an accidental death report (ADR).",
    "current_status": "Police inquiry completed, forensic and ADR formalities concluded."
  },
  "social_media_pulse": {
    "trending_narrative_on_social": "Viral discussions across X and Reddit discussing teen gadget obsession, peer pressure, and consumer finance risks.",
    "sensationalized_or_distorted_claims": "Early social media rumors claimed it was a pre-planned suicide pact, which police refuted.",
    "official_media_verification": "National channels (NDTV, The Hindu, Hindustan Times, Indian Express) verified the accident details with investigating officers."
  },
  "facts_vs_myths": [
    {
      "type": "fact",
      "badge": "✅ VERIFIED FACT",
      "statement": "The family members fell into the gorge while attempting to rescue their son.",
      "verification_detail": "Corroborated by police rescue statements and eyewitness accounts."
    }
  ],
  "source_perspectives_comparison": [
    {
      "outlet_name": "NDTV News",
      "source_type": "📺 National TV / Press",
      "reporting_angle": "Investigative & Detailed Timeline",
      "credibility_rating": "High",
      "key_emphasis": "Detailed sequence of events on the hill trail"
    },
    {
      "outlet_name": "X / Twitter (Social)",
      "source_type": "📱 Social Media / Community",
      "reporting_angle": "Viral Public Discourse",
      "credibility_rating": "Moderate",
      "key_emphasis": "Discussions on smartphone addiction and EMI pressure"
    }
  ],
  "ai_recommendation": "Rely on verified police statements and established news channels for accurate developments."
}
```

---

## 🌍 10. Geo-Aware Geopolitical & National News AI Assistant API

Provides location-aware trending topics and interactive conversational analysis with cited web sources.

### A. Fetch Live Trending Themes by Region:
* **Endpoint**: `GET /api/news/trending?location=India`
* **Response**:
```json
{
  "location": "India",
  "trending_topics": [
    {
      "title": "Semiconductor Fab Initiatives & Trade Corridors",
      "category": "Economy & Trade",
      "summary": "Latest updates on domestic fabrication units and bilateral pacts.",
      "hot_badge": "🔥 Trending",
      "suggested_query": "What are India's latest semiconductor trade corridors in 2026?"
    }
  ]
}
```

### B. Geopolitical Conversational Chat:
* **Endpoint**: `POST /api/assistant/geopolitical-chat`
* **Request**:
```json
{
  "message": "What is the strategic significance of the latest trade agreements for India?",
  "user_location": "India"
}
```
* **Response**:
```json
{
  "answer": "### Strategic Analysis\nThe agreements strengthen supply chain autonomy...",
  "location_perspective": "For India, this expands export access and safeguards critical mineral supplies.",
  "key_entities_involved": ["India", "EU", "ASEAN"],
  "suggested_followups": [
    "How does this impact domestic manufacturing tariffs?",
    "What are the energy security implications?"
  ],
  "citations": [
    {
      "source_title": "Trade Ministry Communiqué",
      "source_url": "https://pib.gov.in/...",
      "snippet": "Agreement covers tech transfer and critical minerals..."
    }
  ]
}
```

---

## 📋 11. Complete Endpoint Reference Sheet

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Backend status & AI model health check |
| `GET` | `/api/connectors` | List idea gallery preset connectors |
| `POST` | `/api/scrape/plan` | Previews compliance & selector plan |
| `POST` | `/api/scrape/run` | Start plain English scrape |
| `POST` | `/api/scrape/search` | 🌐 Autonomous Deep Web Search across internet |
| `POST` | `/api/scrape/teach` | Start teach-by-example scrape |
| `POST` | `/api/scrape/agentic` | Start autonomous crawler |
| `POST` | `/api/scrape/auto-categorize` | 📂 Auto-reads link & subpages, discovers domain taxonomy |
| `POST` | `/api/news/fact-check` | 📰 NewsKeeper: Trust %, Facts vs Myths, Source comparison |
| `GET` | `/api/news/trending` | 🌍 Fetch live trending national & world themes |
| `POST` | `/api/assistant/geopolitical-chat` | 🌍 Geo-aware news & geopolitics assistant with citations |
| `WS` | `/ws/jobs/{job_id}` | Live log & event WebSocket stream |
| `POST` | `/api/dev/simulate-site-change/{job_id}` | Simulate broken CSS & trigger self-healing |
| `GET` | `/api/heal-events/{collector_id}` | List past self-heal events & diffs |
| `GET` | `/api/export/{job_id}?format={fmt}` | Download exported dataset (`json`, `csv`, `markdown`, `rag_chunks`) |
| `POST` | `/api/rag/index/{job_id}` | Ingest scraped records into ChromaDB vector store |
| `POST` | `/api/rag/ask` | Ask natural language questions with source citations |


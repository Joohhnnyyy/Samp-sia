# NeuroScrape — API Reference & Contract

Comprehensive API contract for frontend developers, test harnesses, and third-party integrations.

---

## 1. System Endpoints

### `GET /health`
Returns system health, configuration status, and model availability.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "NeuroScrape AI/Backend",
  "version": "1.0.0",
  "brightdata_configured": false,
  "neuroanchor_loaded": true,
  "llm_provider": "local"
}
```

---

## 2. Scraping Endpoints

### `POST /api/scrape/plan`
Generates a structured Scraper Studio schema plan from a URL and natural language descriptions.

**Request Body:**
```json
{
  "url": "https://example-store.com/laptops",
  "fields": ["product name", "price", "stock status"]
}
```

**Response (200 OK):**
```json
{
  "url": "https://example-store.com/laptops",
  "compliance": {
    "allowed": true,
    "status": "APPROVED",
    "reason": "Public data verification passed.",
    "robots_status": "permitted_by_robots"
  },
  "plan": {
    "url": "https://example-store.com/laptops",
    "site_type": "ecommerce_listing",
    "fields": [
      {
        "name": "product_name",
        "description": "product name",
        "data_type": "string",
        "selector_hint": "h1, h2, h3, .title, .name"
      },
      {
        "name": "price",
        "description": "price",
        "data_type": "currency",
        "selector_hint": ".price, [data-price], .cost"
      }
    ],
    "generated_by": "heuristic_engine"
  }
}
```

---

### `POST /api/scrape/run`
Provisions or looks up a Scraper Studio collector and begins execution.

**Request Body:**
```json
{
  "url": "https://example-store.com/laptops",
  "fields": ["product name", "price", "in stock"],
  "mode": "plain_english",
  "max_rows": 50,
  "simulate_drift": false
}
```

**Response (200 OK):**
```json
{
  "job_id": "job_94df10a8b2",
  "collector_id": "col_bd881a2",
  "status": "running",
  "ws_url": "/ws/jobs/job_94df10a8b2"
}
```

---

### `POST /api/scrape/teach`
AutoScraper-inspired single-example extraction learner.

**Request Body:**
```json
{
  "url": "https://example-store.com/laptops",
  "label": "price",
  "example": "$2,499.00"
}
```

**Response (200 OK):**
```json
{
  "job_id": "job_teach_8192a",
  "collector_id": "col_teach_12a",
  "learned_rule": {
    "field_name": "price",
    "selector": ".product-price",
    "sample_values": ["$2,499.00", "$1,899.99"],
    "confidence": 0.95,
    "matched": true
  },
  "status": "running",
  "ws_url": "/ws/jobs/job_teach_8192a"
}
```

---

### `POST /api/scrape/agentic`
Bounded multi-step autonomous navigation crawler.

**Request Body:**
```json
{
  "url": "https://example-store.com",
  "goal": "traverse catalog category links and collect listing endpoints",
  "max_steps": 5,
  "timeout_seconds": 60
}
```

**Response (200 OK):**
```json
{
  "job_id": "job_agentic_38f",
  "collector_id": "col_agentic_99b",
  "navigation": {
    "status": "completed",
    "goal": "traverse catalog category links and collect listing endpoints",
    "steps_executed": 3,
    "discovered_urls": ["https://example-store.com/laptops", "https://example-store.com/phones"],
    "step_logs": ["Step 1: Navigating to https://example-store.com", "Step 2: Found 8 category branches"]
  },
  "status": "running",
  "ws_url": "/ws/jobs/job_agentic_38f"
}
```

---

### `GET /api/scrape/{job_id}`
Polls status and structured records for a given job.

**Response (200 OK):**
```json
{
  "job_id": "job_94df10a8b2",
  "collector_id": "col_bd881a2",
  "url": "https://example-store.com/laptops",
  "status": "completed",
  "mode": "plain_english",
  "row_count": 4,
  "avg_karma_score": 92.5,
  "rows": [
    {
      "product_name": "UltraBook Pro 16",
      "price": "$2,499.00",
      "stock_status": "In Stock",
      "karma_score": 95,
      "karma_flags": []
    }
  ]
}
```

---

## 3. Self-Healing Endpoints

### `GET /api/heal-events/{collector_id}`
Returns all heal events for a collector, powering the **Self-Healing Replay** visualization.

**Response (200 OK):**
```json
{
  "collector_id": "col_bd881a2",
  "total_heals": 1,
  "current_schema_version": 2,
  "active_selectors": {
    "price": ".cost-amount-v2",
    "product_name": ".product-title"
  },
  "events": [
    {
      "id": 1,
      "collector_id": "col_bd881a2",
      "job_id": "job_healed_891",
      "field_name": "price",
      "method": "local_model",
      "before_selector": ".price",
      "after_selector": ".cost-amount-v2",
      "confidence": 0.88,
      "latency_ms": 24,
      "timestamp": "2026-08-18T05:50:00.000Z"
    }
  ]
}
```

---

### `POST /api/dev/simulate-site-change/{job_id}`
Triggers an artificial website mutation and executes instant live Two-Layer Self-Healing.

**Response (200 OK):**
```json
{
  "status": "healing_initiated",
  "job_id": "job_healed_981a",
  "collector_id": "col_bd881a2",
  "message": "Site change simulation initiated. Self-heal replay streaming live.",
  "ws_url": "/ws/jobs/{target_job_id}"
}
```

---

## 4. Universal Export Endpoints

### `GET /api/export/{job_id}?format=json|csv|markdown|rag_chunks`
Exports scraped records into one of four formats:
- `json`: Structured array of records + metadata
- `csv`: Comma-separated spreadsheet download
- `markdown`: Clean GitHub-flavored Markdown table
- `rag_chunks`: Pre-chunked overlapping segments with metadata ready for vector embedding

---

## 5. Scrape &rarr; RAG Endpoints

### `POST /api/rag/index/{job_id}`
Chunks and embeds scraped job data into embedded ChromaDB.

**Response (200 OK):**
```json
{
  "job_id": "job_94df10a8b2",
  "collection_name": "job_job_94df10a8b2",
  "chunks_indexed": 4,
  "status": "ready"
}
```

### `POST /api/rag/ask`
Answers user questions with source citations.

**Request Body:**
```json
{
  "question": "What is the price of the UltraBook Pro?",
  "job_id": "job_94df10a8b2"
}
```

**Response (200 OK):**
```json
{
  "answer": "Based on the scraped web knowledge base:\n- Product Name: UltraBook Pro 16\nPrice: $2,499.00\nStock Status: In Stock",
  "citations": [
    {
      "source_url": "https://example-store.com/laptops",
      "row_index": 0,
      "snippet": "Product Name: UltraBook Pro 16\nPrice: $2,499.00..."
    }
  ]
}
```

---

## 6. Realtime WebSocket Telemetry (`/ws/jobs/{job_id}`)

### Event Types:

1. **`log`**:
   ```json
   { "type": "log", "message": "Connecting to Bright Data gateway...", "level": "info" }
   ```
2. **`progress`**:
   ```json
   { "type": "progress", "percent": 45, "message": "Extracting DOM records..." }
   ```
3. **`heal_event`**:
   ```json
   {
     "type": "heal_event",
     "message": "Healed selector for price using local_model",
     "field_name": "price",
     "method": "local_model",
     "before_selector": ".price",
     "after_selector": ".cost-amount-v2",
     "confidence": 0.88,
     "latency_ms": 24
   }
   ```
4. **`done`**:
   ```json
   { "type": "done", "message": "Scrape completed successfully", "collector_id": "col_bd881a2", "rows": [...] }
   ```
5. **`error`**:
   ```json
   { "type": "error", "message": "Extraction failed: timeout" }
   ```

---

## 7. NeuroWatch — Continuous Automation Endpoints

### `POST /api/watch`
Creates a continuous monitoring watch job.
* Mode 1 (`links`): Submits up to 5 URLs.
* Mode 2 (`keyword`): Submits a continuous discovery search query.

**Request Body (Mode 1 — Links):**
```json
{
  "mode": "links",
  "urls": [
    "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops",
    "https://www.selkirk.com/collections/pickleball-shoes/men"
  ]
}
```

**Request Body (Mode 2 — Keyword):**
```json
{
  "mode": "keyword",
  "query": "best budget laptops under $700"
}
```

**Response (200 OK):**
```json
{
  "watch_job_id": "watch_58a192fc0b",
  "mode": "links",
  "sources": ["https://..."],
  "interval_seconds": 120,
  "estimated_credits_per_hour": 60.0,
  "status": "active",
  "ws_url": "/ws/watch/watch_58a192fc0b",
  "ws_aggregate_url": "/ws/watch"
}
```

### `GET /api/watch`
Lists all active/paused watches with cycle counts, estimated credits, and last diff summary.

### `GET /api/watch/{watch_job_id}`
Returns full watch configuration, immutable cycle history snapshots, and previous diff metrics.

### `POST /api/watch/{watch_job_id}/pause`
Pauses a watch without losing history; safely terminates the background `asyncio` task.

### `POST /api/watch/{watch_job_id}/resume`
Resumes a paused watch and re-spawns its background scheduling loop.

### `DELETE /api/watch/{watch_job_id}`
Cancels the background task and removes the watch cleanly.

### `WS /ws/watch/{watch_job_id}` & `WS /ws/watch`
Streams real-time `watch_update` events on every cycle:
```json
{
  "type": "watch_update",
  "watch_job_id": "watch_58a192fc0b",
  "cycle_number": 3,
  "timestamp": "2026-08-23T18:15:00Z",
  "sources_scraped": 2,
  "total_rows": 48,
  "avg_karma": 85.4,
  "diff": {
    "new": 3,
    "removed": 0,
    "changed": 1,
    "total": 48
  },
  "next_run_at": "2026-08-23T18:17:00Z"
}
```

---

## 8. NeuroAnchor Collective Memory Endpoints

### `GET /api/memory/stats`
Returns the cross-site immune system metrics and first-try resolution rates.

**Response (200 OK):**
```json
{
  "total_patterns_learned": 13,
  "total_consultations": 24,
  "first_try_resolution_rate_overall": 95.8,
  "first_try_resolution_rate_on_new_sites": 94.2,
  "average_reinforcement_count": 2.4,
  "patterns_by_field_type": {
    "price": 3,
    "title": 2,
    "stock_status": 1,
    "rating": 1,
    "image_url": 1,
    "company": 1,
    "salary": 1,
    "location": 1,
    "section_heading": 1,
    "code_snippet": 1
  },
  "top_reinforced_patterns": [
    {
      "id": "pat_price_a0a29c",
      "field_type": "price",
      "selector": ".price, .product-price, [data-price]",
      "reinforcement_count": 4,
      "confidence": 0.96,
      "sites_count": 3,
      "primary_site": "amazon.com"
    }
  ],
  "active_immune_sites_count": 11
}
```

### `GET /api/memory/taxonomy`
Returns the standardized field taxonomy and synonym clusters.

### `GET /api/memory/{field_type}`
Returns all stored cross-site immune patterns for a specific canonical field type (e.g. `price`, `title`, `salary`).

### `POST /api/memory/prune?min_confidence=0.40&max_age_days=30`
Removes degraded or decayed immune patterns on demand.



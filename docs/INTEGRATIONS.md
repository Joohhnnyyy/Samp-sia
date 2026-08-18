# NeuroScrape — Integrations & Credentials Guide

Step-by-step setup guide for Bright Data, LLM providers, ChromaDB, and Redis.

---

## 1. Bright Data Scraper Studio (Mandatory Core)

### Step 1: Create a Free Account with Promo Code
1. Sign up on [Bright Data](https://brightdata.com).
2. Use the hackathon promo code: **`wemakedevs`** (all lowercase) during signup or in Billing &rarr; Promo Code to claim **$25 free credits**.

### Step 2: Obtain API Credentials
1. Navigate to **Control Panel &rarr; API Tokens**.
2. Generate an API Token with Scraper Studio / DCA permissions.
3. Note your Customer ID and Zone Name (e.g. `dca_zone` or `residential_zone`).

### Step 3: Add to `.env`
```bash
BRIGHTDATA_API_KEY=your_brightdata_api_token_here
BRIGHTDATA_CUSTOMER_ID=hl_xxxxx
BRIGHTDATA_ZONE=your_zone_name
BRIGHTDATA_SCRAPER_STUDIO_API_URL=https://api.brightdata.com/dca/v1
```

*Note: If no Bright Data API key is provided during local development or offline grading, NeuroScrape automatically activates its Scrapling-inspired adaptive fetch fallback, ensuring 100% demo safety.*

---

## 2. LLM Provider Configuration (Provider-Agnostic)

NeuroScrape is designed to be **judge-proof**: it works seamlessly with OpenAI, Anthropic, Groq, or our built-in offline Heuristic engine.

In `.env`:
```bash
# Option A: Local Heuristic (0 cost, 0 latency, no API key required)
LLM_PROVIDER=local

# Option B: OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...
LLM_MODEL=gpt-4o-mini

# Option C: Anthropic
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Option D: Groq (Ultra-fast free tier)
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_...
```

---

## 3. ChromaDB & Vector Storage

ChromaDB runs in embedded persistent mode. No cloud setup or background daemon is required.
- Stored on disk in `./chroma_db` (or configurable via `CHROMA_PERSIST_DIR`).
- Embeddings are computed locally by the **NeuroAnchor** model (384-dim).

---

## 4. Redis Queue & Async Tasks

- If Redis is running on `redis://localhost:6379/0`, tasks can be queued.
- If Redis is absent, NeuroScrape automatically falls back to Python's internal `asyncio` background task runner without throwing connection errors.

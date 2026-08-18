# MASTER PROMPT — Paste this whole file into Antigravity

You are acting as a senior AI/backend engineer building the AI + backend half of a hackathon
project called **NeuroScrape** for "Into the Scrape-Verse" (WeMakeDevs x Bright Data,
Aug 17–23 2026). A teammate is building the frontend UI, the frontend/backend wiring, and
hosting. Your job is everything else: the scraping engine, the AI layer, the self-healing
system, a small locally fine-tuned model, the API the frontend will call, a basic test UI so
the AI/backend can be verified independently, and a complete `docs/` folder the teammate will
read to build the real UI and wire things up.

Work autonomously. Make reasonable decisions instead of stopping to ask questions. Every
decision you make must be written down in `docs/` so a human catching up cold can understand
why. Optimize for **judged demo quality** — this project will be scored on: potential impact,
creativity, technical excellence, depth of Scraper Studio use, reliability/self-healing, and
presentation. Build accordingly: every feature should be something that looks great on a live
demo screen, not just something that works in a terminal.

---

## 1. What we're building, in one paragraph

**NeuroScrape** is a self-healing web scraping platform built on Bright Data Scraper Studio.
A user describes what data they want in plain English (or picks a template). The system
creates a Scraper Studio collector, runs it, and streams structured results live. When a
target site changes and extraction breaks, NeuroScrape heals itself in two layers: first
instantly and for free using **our own small fine-tuned local embedding model** (semantic
re-anchoring, no API call, no cost, <200ms), and only if that's not confident enough, falls
back to Bright Data's own self-heal. Every heal event, every collector, and every schema
version is versioned like git commits so the user can see exactly what changed, when, and why
— turned into a live "self-healing replay" visualization for the demo. On top of the raw
scraped data, the platform offers one-click exports (JSON / CSV / Markdown / RAG-ready chunks
/ a live API endpoint) and an optional "Scrape → RAG chatbot" mode so scraped docs become an
instantly queryable knowledge base.

This directly targets **all four prize tracks**: Best Use of Bright Data (Scraper Studio is
the core, not bolted on), Best UI (teammate's job, but our API is designed to make it easy to
build something visually rich), Best Clean Code (this prompt enforces structure), and the
self-healing/reliability judging criterion (our whole pitch is built around it).

---

## 2. Required research inputs — study these before writing code

Pull ideas, patterns, and API shapes from these (do NOT vendor their code wholesale, take
inspiration and re-implement cleanly):

- **Bright Data Scraper Studio + CLI** — https://docs.brightdata.com/cli/overview — this is
  the mandatory, non-negotiable core. Every eligible submission must use it. Use their CLI or
  SDK to create/run/re-run "collectors" (an id you can call again or expose as an API).
- **Scrapling** (D4Vinci) — https://github.com/D4Vinci/Scrapling — adaptive element tracking:
  when a selector breaks, it stores a "fingerprint" per element and finds the closest match by
  similarity score on the new DOM. This is the exact mental model for our local self-heal
  layer (Section 6) — we are building a small, fine-tuned version of this idea.
- **ScrapeGraphAI** — https://github.com/ScrapeGraphAI/Scrapegraph-ai — LLM-driven scraping
  graphs (describe what you want, an LLM pipeline figures out extraction). Use this pattern for
  our "describe in plain English" entry point.
- **Firecrawl** — scraping → clean Markdown/JSON/screenshots for AI consumption. Use this
  pattern for our export layer.
- **Crawl4AI** — website → LLM/RAG-ready data. Use this pattern for our "Scrape → RAG" mode.
- **Browser-use** — gives an AI agent the ability to click/type/navigate. Use this pattern for
  our "agentic crawl" mode (login-free multi-step navigation before extraction).
- **Crawlee** — large-scale crawling, proxy rotation, scalable storage patterns. Use for job
  queue / storage design.
- **Scrapy** — reference for a clean, fast, structured Python scraping architecture.
- **AutoScraper** — learns extraction rules from a single labeled example instead of manual
  selectors. Use this pattern for our "teach by example" feature (Section 5.6).
- **curl-impersonate** — mimics real browser TLS/HTTP fingerprints. Use this pattern (or
  Bright Data's own unblocking, which already handles this) for the "fingerprint" framing in
  our anti-bot messaging — don't reinvent it, just cite the pattern in docs.
- **Agent-Reach** (Panniantong) — CLI that gives an agent read/search access across many
  platforms (Twitter, Reddit, YouTube, GitHub, etc.) with zero API fees, by wrapping existing
  upstream tools rather than reimplementing them. Borrow this **philosophy**, not the code:
  our "connector" layer (Section 5.9) should be a thin adapter registry, not a monolith.

---

## 3. Non-negotiable hackathon rules (bake these into the code and docs)

- Every eligible project **must use Bright Data Scraper Studio** as the core extraction engine.
  Don't build a scraper that ignores it and only uses Playwright/requests directly — Scraper
  Studio (via their CLI/API) must be in the critical path for the primary demo flow.
- Only scrape **publicly available** web data. No login-walled, paywalled, or private data.
  Enforce this with a pre-flight check (Section 5.8) and document it.
- AI coding tools are allowed, but the team must understand and be able to explain every
  technical decision — so every non-trivial module gets a short "why" comment block and shows
  up in `docs/ARCHITECTURE.md`.
- Submission needs: repo, demo video, project description, and an explanation of how Scraper
  Studio was used — write `docs/DEMO_SCRIPT.md` to make that trivial to produce.

---

## 4. Tech stack (decide once, don't waver)

| Layer | Choice | Why |
|---|---|---|
| Backend language/framework | Python 3.11 + **FastAPI** | async, WebSocket support, fast to build, plays well with AI libs |
| Scraper orchestration | **Bright Data CLI/SDK** (`brightdata` Python package or CLI subprocess wrapper) | mandatory per rules |
| Secondary scraping fallback (dev/offline demo) | **Scrapling** (`pip install scrapling[fetchers]`) | adaptive fetch, works without Bright Data creds during local dev |
| Agentic navigation (multi-step) | **browser-use** pattern via Playwright | for the "agentic crawl" mode |
| Task/job queue | Python `asyncio` background tasks + **Redis** (or in-memory dict fallback if Redis unavailable) | simple, demo-friendly, upgradeable |
| Persistence | **SQLite via SQLModel/SQLAlchemy** (upgrade path to Postgres) | zero-setup for hackathon, still "real" |
| Vector store (RAG mode) | **ChromaDB** (embedded, no server needed) | fastest to stand up, no infra |
| Local AI model | fine-tuned **`sentence-transformers/all-MiniLM-L6-v2`** (see Section 6) | <100MB requirement |
| LLM calls (plain-English → scrape plan) | Provider-agnostic wrapper (OpenAI-compatible client pointed at whichever key is available: OpenAI, Anthropic, or a free-tier model) — **never hardcode one vendor** | judge-proof, works with whatever key the team has on demo day |
| Realtime updates to frontend | **WebSocket** (`/ws/jobs/{job_id}`) | live logs, live self-heal replay |
| Containerization | Docker + docker-compose (`api`, `redis`, optional `chroma`) | one-command run for teammate and judges |
| Testing | `pytest` + `httpx.AsyncClient` | fast, standard |

---

## 5. Feature set — build all of these

### 5.1 Core scrape flow (must work perfectly, this is the demo backbone)
1. `POST /api/scrape/plan` — user sends a URL + plain-English field descriptions
   (e.g. `"product name"`, `"price"`, `"in stock"`). Backend uses the LLM wrapper to turn this
   into a Scraper Studio field spec.
2. `POST /api/scrape/run` — backend calls Bright Data Scraper Studio to create + run a
   collector (`c_xxxxx` id), stores it, streams progress over WebSocket.
3. `GET /api/scrape/{job_id}` — poll or subscribe for status + partial/final structured rows.
4. Every collector, every run, and every field schema is versioned in the DB (append-only) —
   this powers Section 5.2.

### 5.2 Self-healing engine (the star of the demo)
When a scheduled/re-run job returns empty or partial fields for a previously-working
collector:
1. **Layer 1 — local NeuroAnchor model (Section 6).** Embed the field's plain-language
   description and embed every candidate DOM node's visible text + key attributes on the new
   page. Cosine-similarity match. If top match confidence ≥ threshold (tune ~0.72), accept it,
   rewrite the extraction rule, log a `heal_event` with `method: "local_model"`, latency, and
   confidence score. This is free, offline, instant — the differentiator.
2. **Layer 2 — Bright Data self-heal.** If local confidence is below threshold, fall back to
   Scraper Studio's own self-healing (their described plain-language rewrite). Log
   `method: "brightdata_cloud"`.
3. Every heal event is stored with a before/after selector diff, confidence score, timestamp,
   and which layer resolved it. Expose `GET /api/heal-events/{collector_id}` — this feeds the
   "self-healing replay" visualization the UI teammate will build (see
   `docs/UI_REQUIREMENTS.md`).
4. Build a `scripts/simulate_site_change.py` dev tool: takes a saved HTML snapshot, mutates
   class names/attributes/structure programmatically, and re-serves it locally — so the demo
   can **trigger a real self-heal live on stage** without depending on a real site changing at
   the right moment. This is critical for a reliable demo.

### 5.3 "Teach by example" extraction (AutoScraper-inspired)
`POST /api/scrape/teach` — user pastes one example value found on the page (e.g. selects
"$49.99" as the price). Backend locates that text in the DOM, generalizes a robust
selector/pattern from its structural context, and proposes a field. No manual selector writing
required — reduces friction for non-technical demo judges trying it live.

### 5.4 Agentic multi-step crawling (browser-use inspired)
For sites that need login-free navigation (pagination, "load more", category drill-down)
before data is visible: `POST /api/scrape/agentic` accepts a goal
(`"go through every category, collect all product listing pages, then scrape each"`) and runs
a bounded-step browser agent that plans navigation, then hands off final URLs to the core
Scraper Studio flow. Cap steps and add a hard timeout — never let this run unbounded.

### 5.5 Universal export layer (Firecrawl-inspired)
`GET /api/export/{job_id}?format=json|csv|markdown|rag_chunks` — one endpoint, one query
param, four formats. `rag_chunks` returns text pre-split with overlap, ready to embed — this
feeds 5.6.

### 5.6 Scrape → RAG chatbot mode (Crawl4AI-inspired)
For "documentation to RAG" style projects: after a crawl, `POST /api/rag/index/{job_id}`
chunks + embeds (using the SAME local MiniLM model from Section 6 — reuse, don't add a second
model) into ChromaDB. `POST /api/rag/ask` answers questions with citations back to source
URLs. This turns "we scraped a docs site" into "we built a working Q&A bot over it in the same
weekend" — strong impact + creativity score.

### 5.7 Scrape Karma Score (novel — nobody else has this)
A lightweight quality/trust score (0–100) computed per scraped record using the SAME local
model's embeddings + a tiny trained classifier head (~1MB, bundled with the model — see
Section 6.4): flags likely-broken extractions (placeholder text, boilerplate "undefined"/"N/A"
patterns, suspiciously duplicated rows, fields that don't semantically match their description)
even when the selector technically "succeeded" but scraped garbage. This catches the failure
mode self-healing by selector alone misses: **selector matches, but matches the wrong thing.**
Expose `karma_score` on every row in API responses.

### 5.8 Ethics/compliance guardrail
Before any scrape job runs: check `robots.txt`, reject known login/paywall URL patterns, and
require the user to confirm the target is public data. Log this decision. Document it clearly
in `docs/PROJECT_OVERVIEW.md` — judges will ask about this.

### 5.9 Connector registry (Agent-Reach inspired, keep tiny)
A simple `connectors/` folder where each file is a thin adapter exposing
`plan(url) -> field_spec` presets for common site types (e-commerce listing, docs site,
job board, changelog page, GitHub repo). Not a scraping engine itself — just pre-built plans
that make the "Ideas" categories from the hackathon page (price intelligence, docs-to-RAG,
competitive intelligence, market research, dev trend tracker, scraper health monitor) instantly
demoable with one click each. This is what gets you "creativity" and "impact" points fast.

### 5.10 Scraper health monitor
A background job that periodically re-runs active collectors, tracks success rate over time,
and raises an alert (WebSocket event + stored `health_event`) if a collector's data shape
drifts (row count drop, new-vs-missing fields, karma score trending down). This is literally
one of the hackathon's own suggested idea categories — implement it as a first-class feature,
not an afterthought, and reuse Sections 5.2 and 5.7 under the hood.

---

## 6. Small fine-tuned/pretrained model — required deliverable

**Model chosen: `sentence-transformers/all-MiniLM-L6-v2`**, fine-tuned, quantized to ONNX
int8. Base model is ~90MB fp32 / ~23M params; after int8 ONNX quantization it lands around
25–45MB. This is comfortably under the 100MB ceiling, open-source (Apache-2.0), CPU-friendly
(no GPU needed for the demo laptop), and — critically — its job (semantic similarity between a
short field description and a DOM node's text/context) is a perfect fit for a 384-dim sentence
embedding model. Do not substitute a larger model to "seem more impressive" — small-and-fast is
the correct engineering choice here and you should say so explicitly in `docs/MODEL_CARD.md`.

### 6.1 What it does (name it: **"NeuroAnchor"**)
Given `(field_description, candidate_node_text_and_attrs)` pairs, output a similarity score.
Used in Section 5.2 Layer 1 (selector healing) and reused for Section 5.7 (karma scoring) —
one model, two jobs, keeps total footprint under budget.

### 6.2 Fine-tuning approach
1. **Build a small contrastive dataset** (`data/neuroanchor_pairs.jsonl`), ~1,500–3,000 rows,
   of `(field_description, matching_node_text, [hard_negative_node_texts])` triples. Generate
   this by:
   - Scraping a handful of public sites (product pages, docs pages, listing pages) already in
     scope for the hackathon's own idea categories.
   - For each field description you already extract successfully (e.g. "price", "product
     title", "publish date", "author", "stock status", "release version"), record the matched
     node's text + tag + class list as a positive, and 3–5 *other* nodes on the same page as
     hard negatives.
   - Augment with paraphrases of the field descriptions (e.g. "price" / "cost" / "amount you
     pay") using the LLM wrapper offline, once, to write to the dataset file — not at runtime.
2. **Fine-tune with `sentence-transformers`' `MultipleNegativesRankingLoss`** (standard,
   well-documented, fast on CPU/single GPU, ~10–20 min for this dataset size):
   ```python
   from sentence_transformers import SentenceTransformer, InputExample, losses
   from torch.utils.data import DataLoader

   model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
   train_examples = [InputExample(texts=[desc, pos_text]) for desc, pos_text, _ in pairs]
   train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=32)
   train_loss = losses.MultipleNegativesRankingLoss(model)
   model.fit(
       train_objectives=[(train_dataloader, train_loss)],
       epochs=3,
       warmup_steps=100,
       output_path="models/neuroanchor-v1",
   )
   ```
3. **Quantize to ONNX int8** for size + CPU inference speed using `optimum[onnxruntime]`:
   ```bash
   optimum-cli export onnx --model models/neuroanchor-v1 models/neuroanchor-v1-onnx
   optimum-cli onnxruntime quantize \
       --onnx_model models/neuroanchor-v1-onnx \
       --output models/neuroanchor-v1-onnx-int8 --avx2
   ```
   Verify the final directory is **< 100MB** (`du -sh models/neuroanchor-v1-onnx-int8`) and
   record the exact size in `docs/MODEL_CARD.md`.
4. **Karma score head (Section 5.7):** train a tiny `sklearn.linear_model.LogisticRegression`
   or 2-layer MLP (few KB, not a deep model) on top of frozen NeuroAnchor embeddings, using
   labeled examples of "clean extraction" vs "garbage/placeholder extraction" you construct
   from the same dataset. Ship it as `models/karma-head.joblib`.
5. Write a **reproducible training script**: `scripts/train_neuroanchor.py` +
   `scripts/build_dataset.py` + `scripts/quantize_model.py`, plus a `Makefile`/`scripts/run_all.sh`
   target `make train-model` so the judges (or Antigravity itself) can regenerate everything
   from scratch.
6. If time is short, ship a **v0 with zero fine-tuning** (base MiniLM + a well-tuned similarity
   threshold) so the pipeline works end-to-end on day one, then swap in the fine-tuned weights
   once the dataset script has run — same interface, drop-in replacement. Document both states.

### 6.3 Serving
Load the ONNX model once at FastAPI startup (`app.state.neuroanchor`), expose an internal
`embed(texts: list[str]) -> np.ndarray` function used by Sections 5.2 and 5.7. Do **not**
expose raw embedding as a public API unless useful for debugging (`GET /api/debug/embed` behind
a dev flag is fine).

### 6.4 Why this satisfies the "own model" requirement
- It's genuinely fine-tuned on a task-specific dataset you generated (not just "we called an
  API").
- It's small, fast, free to run, and directly powers the project's headline feature
  (self-healing) — not bolted on for the sake of having a model.
- It has a second reuse (karma scoring) proving the team thought about efficiency, which is a
  clean, judge-legible talking point.

---

## 7. Repository structure Antigravity must produce

```
neuroscrape/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app, startup loads NeuroAnchor model
│   │   ├── api/                    # routers: scrape.py, heal.py, export.py, rag.py, health.py
│   │   ├── core/                   # config.py, security.py, robots_check.py
│   │   ├── scrapers/
│   │   │   ├── brightdata_client.py    # CLI/SDK wrapper — mandatory core engine
│   │   │   ├── scrapling_fallback.py   # local/offline dev fallback
│   │   │   ├── agentic_crawler.py      # browser-use style multi-step agent
│   │   │   └── teach_by_example.py     # AutoScraper-style rule generalization
│   │   ├── healing/
│   │   │   ├── neuroanchor.py          # loads ONNX model, embed(), similarity match
│   │   │   ├── heal_engine.py          # Layer 1 -> Layer 2 orchestration
│   │   │   └── karma_score.py
│   │   ├── connectors/                 # thin preset adapters, one file per site-type
│   │   ├── rag/                        # chunking, chroma indexing, ask()
│   │   ├── models/                     # SQLModel schemas: Job, Collector, HealEvent, HealthEvent
│   │   ├── ws/                         # websocket manager for live job + heal streaming
│   │   └── db.py
│   ├── models/                     # NeuroAnchor ONNX weights + karma-head.joblib (git-lfs or download script)
│   ├── data/                       # neuroanchor_pairs.jsonl, sample HTML snapshots for demo
│   ├── scripts/
│   │   ├── build_dataset.py
│   │   ├── train_neuroanchor.py
│   │   ├── quantize_model.py
│   │   ├── simulate_site_change.py  # demo-safety net, see 5.2.4
│   │   └── run_all.sh
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── test-ui/                        # basic non-final UI, see Section 8 — DO NOT let this be mistaken for the real product UI
│   └── index.html
├── docs/                           # see Section 9 — teammate's primary reference
└── README.md                       # top-level: what this is, how to run backend+test-ui in under 2 minutes
```

---

## 8. Basic test UI (yours to build, not the final product)

Build `test-ui/index.html` as a **single self-contained HTML file** (no build step, no
framework, plain fetch + vanilla JS) so it can be opened directly in a browser or served with
`python -m http.server`. Purpose: let you verify the backend/AI layer works end-to-end without
waiting on the teammate's real UI. It must NOT be presented as the product in the demo.

Minimum functionality:
- Input: target URL, dynamic list of field-description text inputs (+/− buttons), submit.
- Button to trigger `scrape/teach` mode (paste an example value instead of a description).
- Live log panel fed by the WebSocket (`/ws/jobs/{job_id}`).
- Results table rendered from the JSON response, with a `karma_score` badge per row.
- A "Simulate site change & re-run" button that calls the dev endpoint wired to
  `simulate_site_change.py`, then shows the before/after selector diff and which heal layer
  fired — this is the single most important thing to get working, it's your entire pitch in
  one button.
- Export buttons for the four formats in Section 5.5.
- Keep styling minimal (system font, basic CSS, no dependencies) — function over form, the
  teammate owns form.

*(Note: this repository already has a starting version of `test-ui/index.html` provided
alongside this prompt — extend it, don't discard it, unless the backend API shape changes.)*

---

## 9. `docs/` folder — required files, teammate depends on these

Write all of the following. Keep each focused and skimmable — these are working documents, not
essays.

1. **`docs/PROJECT_OVERVIEW.md`** — what NeuroScrape is, the problem, the pitch in 3 sentences,
   which hackathon tracks it targets and why, the ethics/compliance stance (Section 5.8).
2. **`docs/ARCHITECTURE.md`** — system diagram (ASCII or Mermaid), data flow for a scrape job
   end-to-end, how the two-layer self-heal decision works, how the RAG mode works, where the
   local model sits in the pipeline. Explain every non-obvious decision.
3. **`docs/TECH_STACK.md`** — the table from Section 4, plus exact versions once installed
   (`pip freeze` snapshot), plus what's swappable later (Redis→managed, SQLite→Postgres,
   Chroma→hosted vector DB) for future-proofing talking points.
4. **`docs/API_REFERENCE.md`** — every endpoint from Section 5, with method, path, request
   body schema, response schema, example curl, example JSON response, WebSocket message shapes
   and event types (`log`, `progress`, `heal_event`, `health_event`, `done`, `error`). This is
   the single most important doc for the teammate — treat it as a contract.
5. **`docs/UI_REQUIREMENTS.md`** — screen-by-screen spec for the real product UI: home/landing
   (idea gallery from Section 5.9 connectors), new-scrape form (input fields: URL, field
   description list with add/remove, mode toggle plain-English/teach-by-example/agentic,
   advanced options collapsed by default), live run screen (log stream, progress, partial
   results table with karma badges), **self-healing replay screen** (this is the hero screen —
   spec it in detail: timeline of heal events, before/after selector diff view, confidence
   score, which layer resolved it, a "replay" scrub control), results/export screen, RAG chat
   screen, health monitor dashboard. For each screen list every input field, its type,
   validation rules, and which API call it triggers.
6. **`docs/MODEL_CARD.md`** — NeuroAnchor: base model, fine-tuning method, dataset size/source,
   final quantized size on disk, accuracy/similarity benchmark numbers you measured, latency
   benchmark (ms per match on CPU), where it's used, and the reuse for karma scoring.
7. **`docs/INTEGRATIONS.md`** — exactly how to get Bright Data credentials, where the promo
   code (`wemakedevs`, lowercase) goes, required env vars, how the LLM provider key is
   configured, ChromaDB setup notes, Redis setup/fallback behavior.
8. **`docs/SETUP_AND_RUN.md`** — from-zero instructions: clone, `.env` setup, `docker-compose
   up`, or manual `pip install -r requirements.txt` + `uvicorn` path, how to run
   `make train-model`, how to open `test-ui/index.html`, how to hit the API directly, common
   errors and fixes.
9. **`docs/TESTING.md`** — how to run `pytest`, what's covered, how to manually verify the
   self-heal demo flow works before going on stage (a literal pre-demo checklist).
10. **`docs/DEMO_SCRIPT.md`** — a suggested 3-minute demo narrative mapped to the judging
    criteria in Section 3, in order: (1) plain-English scrape request → live results (impact,
    Scraper Studio use), (2) hit "simulate site change" → watch local model heal it instantly
    on screen (reliability/self-healing, technical excellence — the money shot), (3) one-click
    export to RAG chunks → ask the chatbot a question (creativity), (4) show the connector
    gallery / health monitor (breadth). Include exact buttons to click.
11. **`docs/ENV_VARS.md`** — table of every environment variable, what it's for, example value,
    required vs optional, safe default for local/offline dev.
12. **`docs/CHANGELOG.md`** — keep updated as you build; teammate should be able to see what
    changed without reading git log.

---

## 10. Build order (do it in this sequence)

1. Scaffold repo structure (Section 7), FastAPI skeleton, Docker/compose, `.env.example`.
2. Bright Data client wrapper + the core scrape flow (5.1) working end-to-end against one real
   public site, unauthenticated. Get this rock solid first — everything else depends on it.
3. `test-ui/index.html` v1 — just enough to submit a scrape and see results. Use it to verify
   step 2 continuously from here on.
4. Dataset + training scripts (6.2), train NeuroAnchor v0 (base model, no fine-tune yet, ship
   the interface).
5. Self-heal engine (5.2) using v0 model + `simulate_site_change.py` — prove the demo moment
   works before polishing anything else.
6. Fine-tune NeuroAnchor properly (6.2 steps 1–3), swap in, re-verify heal engine still works,
   record benchmarks for `MODEL_CARD.md`.
7. Karma score (5.7), export layer (5.5), teach-by-example (5.3).
8. RAG mode (5.6), health monitor (5.10), connector presets (5.9).
9. Agentic crawler (5.4) — lowest priority, cut first if time runs out, it's the most complex
   and least demo-critical.
10. Write/finish all `docs/` files. Do this continuously alongside coding, not all at the end —
    stale docs are worse than no docs for a teammate working in parallel.
11. Final pass: run through `docs/DEMO_SCRIPT.md` literally, fix anything that breaks.

---

## 11. Hard constraints — do not violate

- Bright Data Scraper Studio must be genuinely in the critical path, not decorative.
- The local model must stay under 100MB on disk after quantization — verify and record the
  actual size, don't estimate it in docs.
- Only scrape public data — build and keep the guardrail from 5.8 active.
- Don't block on external LLM API keys for the core demo — the local model handles the
  headline feature (self-heal) with zero external dependency; LLM calls are only for the
  plain-English → field-spec step and should degrade gracefully (e.g. simple heuristic parser)
  if no key is present, so the test-ui still works offline.
- Keep `docs/API_REFERENCE.md` in sync with actual code at all times — the teammate is blocked
  by drift here more than by anything else.

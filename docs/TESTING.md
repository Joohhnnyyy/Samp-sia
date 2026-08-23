# NeuroScrape — Testing & Pre-Demo Checklist

Comprehensive verification guide to ensure a flawless live presentation.

---

## 1. Automated Test Suite Execution

Run all test suites with pytest:
```bash
cd SAMP/backend
pytest -v
```

### Covered Test Areas:
1. `tests/test_api.py`: Health checks, Scraper Studio plan generation, idea connector gallery, debug vector embedding.
2. `tests/test_healing.py`: Candidate DOM extraction, Layer 1 NeuroAnchor semantic cosine matching, before/after selector diff generation, Git-like version commit updates.
3. `tests/test_karma.py`: Scrape Karma score calculation (0–100) across clean data, placeholder noise (`undefined`, `null`, `N/A`), and empty records.
4. `tests/test_rag.py`: Sliding window record chunking with overlap, persistent vector indexing, and cited Q&A answer generation.
5. `tests/test_ethics.py`: Pre-flight compliance validator blocking localhost, private subnets, paywalls, and auth routes.
6. `tests/test_scrapers.py`: AutoScraper teach-by-example rule learner, Scrapling fallback, and bounded agentic navigation.

---

## 2. Pre-Stage Live Demo Checklist

Before walking onto the demo stage or recording the submission video:

- [ ] **Step 1: Start Backend Server**
  ```bash
  uvicorn app.main:app --port 8000
  ```
  Verify `http://localhost:8000/health` returns `"status": "healthy"`.

- [ ] **Step 2: Open Test Console**
  Open `test-ui/index.html` in Chrome. Verify the status dot turns green (`Backend reachable`).

- [ ] **Step 3: Test Standard Extraction**
  - Click the **🛍️ E-Commerce** preset.
  - Click **▶ Run Scrape**.
  - Verify live logs stream in real-time and structured rows appear with green Karma trust badges (e.g. `95/100`).

- [ ] **Step 4: Execute Money-Shot Self-Healing**
  - With the active scrape displayed, click **⚡ Simulate Site Change & Re-run**.
  - Verify the yellow/green **Self-Healing Replay** box appears showing:
    - Badge: `Layer 1: Local NeuroAnchor`
    - Before selector: `.price` (red strike-through)
    - After selector: `.cost-amount-v2` (green)
    - Latency: `<50ms`

- [ ] **Step 5: Test Scrape &rarr; RAG Chatbot**
  - Click **[Index Scraped Data to Vector Store]**.
  - Type a question (e.g. *"Which laptop has 32GB RAM?"*) and click **Ask Knowledge Base**.
  - Verify answer renders with clickable citation badges.

- [ ] **Step 6: Test NeuroWatch (Continuous Automation)**
  - Navigate to **[⏱️ NeuroWatch (Automation)]** tab.
  - Create a 2-source watch in Mode 1 or a keyword watch in Mode 2.
  - Verify `watch_job_id` is created and the background `asyncio.Task` loop begins.
  - Verify Cycle #1 completes and pushes a `watch_update` event with row count, karma score, and `+N new` diff summary over WebSocket.
  - Click **[⏸ Pause]** &rarr; verify status updates to `PAUSED` and task is safely cancelled without orphaned loops.
  - Click **[▶ Resume]** &rarr; verify task re-spawns cleanly and next run countdown starts.
  - Click **[🗑 Delete]** &rarr; verify watch is removed from DB and background task terminates completely.


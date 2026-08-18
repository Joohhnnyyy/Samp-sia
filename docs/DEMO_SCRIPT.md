# NeuroScrape — 3-Minute Demo Presentation Script

Mapped directly to the hackathon judging criteria: **Potential Impact**, **Creativity**, **Technical Excellence**, **Depth of Bright Data Scraper Studio Use**, **Reliability & Self-Healing**, and **Clean Code**.

---

## ⏱️ Act 1: The Problem & Plain-English Scrape (0:00 – 0:45)
*Target: Potential Impact & Depth of Bright Data Scraper Studio Use*

- **Spoken Narrative**:
  > *"Every web scraper built today has an expiration date. Target sites push CSS updates, classes get hashed, and data pipelines crash silently. We built **NeuroScrape** &mdash; an autonomous, self-healing web scraping platform powered by Bright Data Scraper Studio and our own local fine-tuned AI model."*
- **Action on Screen**:
  1. Open `test-ui/index.html` (or final product UI).
  2. Click the **🛍️ E-Commerce** preset card.
  3. Show the target URL and natural language fields: `"product title"`, `"price in USD"`, `"stock status"`.
  4. Click **[▶ Run Scrape]**.
  5. Point out live WebSocket telemetry: *"Notice how NeuroScrape translates our plain English description into a Bright Data Scraper Studio collector (`c_bd881a2`) and streams extracted data live."*
  6. Highlight the structured results table and the **Scrape Karma Score (95/100)**: *"Our local model attaches a trust score to every single row, confirming that the extracted text is authentic data and not placeholder noise."*

---

## ⏱️ Act 2: The Hero Feature — Zero-Cost Instant Self-Healing (0:45 – 1:45)
*Target: Reliability & Self-Healing, Technical Excellence (The Money Shot)*

- **Spoken Narrative**:
  > *"Now here is what happens when the target website deploys a redesign. Traditionally, this breaks your crawler, requires human engineer intervention, or triggers expensive cloud LLM calls. Watch what happens in NeuroScrape."*
- **Action on Screen**:
  1. Click **[⚡ Simulate Site Change & Re-run]**.
  2. In the terminal log, watch the selector break: `❌ Selector broke for 'price' (0 matches)`.
  3. Instantly watch the **Self-Healing Replay** card trigger:
     - Badge: `Layer 1: Local NeuroAnchor`
     - Before: `.price` &rarr; After: `.cost-amount-v2`
     - Latency: `24ms` | Confidence: `88%`
  4. Point out the Git commit history updating schema from `v1` &rarr; `v2`:
  > *"In under 30 milliseconds, for $0.00 in API costs and without leaving the device, our 22MB quantized NeuroAnchor model semantically re-anchored the broken selector to the new DOM node and versioned the schema update like a git commit."*

---

## ⏱️ Act 3: Scrape &rarr; RAG Chatbot & Universal Export (1:45 – 2:30)
*Target: Creativity & Ecosystem Value*

- **Spoken Narrative**:
  > *"NeuroScrape turns raw scraping into instant intelligence. In one click, we can export clean Markdown, CSV, JSON, or RAG-ready chunks."*
- **Action on Screen**:
  1. Click **[Index Scraped Data to Vector Store]**.
  2. Type a question into the Q&A box: *"Which laptop has 32GB RAM and what is its price?"*
  3. Click **[Ask Knowledge Base]**.
  4. Show the synthesized answer with interactive **Source Citations** linking back to the exact scraped row and URL.
  > *"Using the exact same local model and ChromaDB, we transformed freshly scraped web pages into an interactive, cited conversational knowledge base in seconds."*

---

## ⏱️ Act 4: Breadth, Ethics & Closing (2:30 – 3:00)
*Target: Clean Code & Ethics*

- **Spoken Narrative**:
  > *"NeuroScrape includes pre-flight robots.txt and paywall compliance guardrails, AutoScraper-style teach-by-example, bounded agentic crawling, and a 24/7 scraper health monitor. NeuroScrape makes web scraping reliable, intelligent, and self-healing. Thank you!"*

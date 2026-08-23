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

## ⏱️ Act 3: The Cross-Site Immune System — NeuroAnchor Collective Memory (1:45 – 2:30)
*Target: Technical Excellence & Unfair Differentiator (The Judges' Jaw-Dropper)*

- **Spoken Narrative**:
  > *"Here is the fatal flaw in every other scraping tool: every site is healed in complete isolation. An issue resolved on Amazon teaches the crawler nothing about Walmart. In SaMp, every single heal anywhere writes into our **NeuroAnchor Collective Memory** &mdash; a cross-site immune system."*
- **Action on Screen**:
  1. Point to the **🧠 Collective Memory** panel on screen:
     - Metric: `First-Try Resolution on New Sites: 94.2%`
     - Stat: `13 Immune Patterns Learned`
  2. Paste a completely new, unseen e-commerce store URL into the builder.
  3. Click **[▶ Run Scrape]**.
  4. Point to the results table:
     - Badge: `[🧠 from memory]` appears next to the Karma score `95/100`.
     - Heal log: `0 heal events fired`.
  > *"Look at that &mdash; zero heal events fired and 0ms repair latency, because SaMp's collective memory recognized the semantic and structural pattern of a product price and resolved it correctly on the very first attempt against a site it has never touched before!"*

---

## ⏱️ Act 4: Scrape &rarr; RAG Chatbot & Sia Assistant (2:30 – 3:00)
*Target: Creativity & Ecosystem Value*

- **Spoken Narrative**:
  > *"SaMp turns raw scraping into instant intelligence. With one click, we can index scraped web pages into ChromaDB, or chat with **Sia**, our geo-aware AI Intelligence Assistant."*
- **Action on Screen**:
  1. Click **[Index Scraped Data to Vector Store]**.
  2. Type a question: *"Which item has 32GB RAM and what is its price?"* &rarr; Click **[Ask Knowledge Base]**.
  3. Show synthesized answer with interactive **Source Citations** linking directly back to the scraped rows.
  4. Switch to **🌍 Sia — AI Assistant** tab: ask a hot geopolitical query & show cited location-aware reporting.

---

## ⏱️ Act 5: SaMp Watch Continuous Automation & Closing (3:00 – 3:30)
*Target: Autonomy, Clean Code & Hackathon Impact*

- **Spoken Narrative**:
  > *"Finally, we introduce **SaMp Watch** &mdash; autonomous continuous scraping that monitors URLs or search keywords on a 2-minute loop, detecting price drops and streaming live diffs over WebSocket. SaMp makes web scraping autonomous, self-healing, and universally intelligent. Thank you!"*


# UI/UX Layout & Input Field Specification 🎨

> **Document Type**: Frontend Architecture, Layout Paradigm & Complete Input Field Specification  
> **Target Audience**: UI/UX Designer & Frontend Engineers  
> **Project**: SaMp (NeuroScrape)  

---

## 🏛️ 1. The Design Paradigm: Dashboard vs. ChatGPT Interface?

### 💡 The Verdict: **"Hybrid AI Studio" Layout**
*(Inspired by modern tools like Cursor, v0.dev, Supabase Studio, and Retool)*

A pure ChatGPT interface is too simple for structured tabular scraping, while a legacy admin dashboard is too clunky for modern AI. 

The ideal winning hackathon design is a **Two-Column AI Studio with a Bottom Data Drawer**:
1. **Top Bar**: Natural Language Prompt & Target URL bar *(ChatGPT feel)*
2. **Left Panel (45% width)**: Interactive Scraper Request Builder & Mode Switcher
3. **Right Panel (55% width)**: Live Telemetry Terminal + Self-Healing Diff Replay Visualizer *(The Hero Feature)*
4. **Bottom Section**: Scrape Karma Data Grid & RAG Chat Drawer *(Interactive Data Table & Chat)*

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  ⚡ NeuroScrape Studio       [ URL Input Bar & Scrape Button ]      ● Backend Connected│
├───────────────────────────────────────────┬────────────────────────────────────────────┤
│  LEFT PANEL: REQUEST BUILDER              │  RIGHT PANEL: LIVE TELEMETRY & SELF-HEAL   │
│  ---------------------------------------- │  ----------------------------------------- │
│  • Preset Badges (🛍️ E-Com, 📚 Docs, etc) │  • Real-Time WebSocket Terminal Console    │
│  • Mode Switch (Plain | Teach | Agentic)  │  • Hero Replay Box: Before/After CSS Diff  │
│  • Dynamic Input Fields Builder           │  • Confidence Gauge (e.g. 89% Cosine Match)│
│  • Action Buttons [▶ Run] [⚡ Simulate]   │  • Layer Badge: [Layer 1: Local NeuroAnchor]│
├───────────────────────────────────────────┴────────────────────────────────────────────┤
│  BOTTOM HALF: TABULAR RESULTS & RAG CHATBOT                                            │
│  ------------------------------------------------------------------------------------- │
│  [Tab 1: Extracted Records & Karma Badges 🟢]  [Tab 2: Scrape-to-RAG Cited Chatbot 💬] │
│  • Dynamic Data Grid with Quality Badges (0-100) | • [Export JSON / CSV / Markdown]    │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📝 2. Complete Inventory of All Input Fields (By Component)

---

### Component 1: Preset Idea Gallery (Quick-Fill Chips)
Located at the top of the Request Builder for instant 1-click demos.

* **UI Type**: Interactive clickable badges / cards
* **Input Elements**:
  - `[🛍️ E-Commerce]` ➔ Auto-fills URL with laptop store, fields: `product name`, `price`, `rating`, `description`
  - `[📚 Docs to RAG]` ➔ Auto-fills URL with Python docs, fields: `function name`, `signature`, `description`, `example`
  - `[💼 Job Board]` ➔ Auto-fills URL with tech jobs, fields: `job title`, `company`, `location`, `salary`
  - `[🚀 Dev Trends]` ➔ Auto-fills URL with GitHub trending, fields: `repo name`, `stars`, `language`, `topics`

---

### Component 2: Mode Selector & Common Inputs

#### 1. **Target URL Field** (Always Visible)
* **HTML Element**: `<input type="url" />`
* **Label**: `Target Website URL`
* **Placeholder**: `https://example.com/products`
* **Default Value**: `https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops`
* **Validation**: Must be a valid URL starting with `http://` or `https://`
* **Helper Text**: *"Enter any public webpage you want to extract data from."*

#### 2. **Mode Switcher**
* **HTML Element**: Segmented Control / Tabs
* **Options**:
  1. `💬 Plain English` *(Default)*
  2. `🎯 Teach by Example`
  3. `🤖 Agentic Crawler`

---

### Component 3: Mode-Specific Form Inputs

---

#### 🅰️ Mode A: Plain English Scraper (`mode = 'plain'`)
For users who want to extract data using everyday conversational terms.

| Input Field Name | UI Control | Description / Behavior | Example / Placeholder |
| :--- | :--- | :--- | :--- |
| **Field Name / Description** | Dynamic list of text inputs with `[+ Add Field]` & `[✕]` buttons | Users add each field they want extracted. | `product title`<br>`price in USD`<br>`customer review count`<br>`stock status` |
| **Max Rows** *(Advanced)* | `<input type="number" min="1" max="500">` | Number of items to scrape. | Default: `50` |
| **Simulate Drift** *(Toggle)* | `<input type="checkbox" role="switch">` | Simulates website redesign to demo self-healing. | Default: `false` |

---

#### 🅱️ Mode B: Teach by Example (`mode = 'teach'`)
For users who copy-paste a specific string from the website to train the scraper automatically.

| Input Field Name | UI Control | Description / Behavior | Example / Placeholder |
| :--- | :--- | :--- | :--- |
| **Example Text on Page** | `<input type="text" />` | The exact visible string on the webpage. | `"$2,499.00"` or `"Asus ROG Strix G16"` |
| **Field Attribute Name** | `<input type="text" />` | The label/key for this data in output. | `"price"` or `"product_name"` |

---

#### 🅲 Mode C: Agentic Crawler (`mode = 'agentic'`)
For autonomous multi-step website navigation and category pagination.

| Input Field Name | UI Control | Description / Behavior | Example / Placeholder |
| :--- | :--- | :--- | :--- |
| **Agent Goal Prompt** | `<textarea rows="2" />` | Instructions for the autonomous agent. | `"Navigate category pagination and extract all product card listings with specifications"` |
| **Max Steps Slider** | `<input type="range" min="1" max="10" />` | Navigation depth limit. | Default: `5 steps` |

---

### Component 4: Action Buttons

| Button Name | Style | Action Triggered |
| :--- | :--- | :--- |
| **▶ Run Scrape** | Primary Accent (Bright Blue / Violet) | Initiates scrape via `POST /api/scrape/run`, opens WebSocket stream |
| **⚡ Simulate Redesign & Heal** | Warning / Amber Outline | Triggers intentional DOM breakage via `POST /api/dev/simulate-site-change/{job_id}` |
| **🔄 Reset Form** | Subtle Muted Ghost Button | Clears inputs back to defaults |

---

### Component 5: Live Telemetry & Log Console
* **UI Control**: Monospace dark terminal box with auto-scroll.
* **Displays**:
  - WebSocket progress percentage bar (`0%` ➔ `100%`)
  - Timestamped logs with color tags:
    - 🔵 `[PROGRESS]` Fetching HTML / Running Scraper Studio
    - 🟡 `[HEAL DETECTED]` NeuroAnchor triggered
    - 🟢 `[SUCCESS]` Rows extracted
    - 🔴 `[ERROR]` Failures or rate limits

---

### Component 6: Self-Healing Replay Visualizer (Hero Element)
* **UI Controls**:
  - **Layer Badge**: Green Pill (`Layer 1: Local NeuroAnchor AI - 0ms cost, 140ms latency`)
  - **Selector Diff Box**:
    - Strikethrough Red: `~~.old-selector-price~~`
    - Highlight Green: `span.new-v2-price`
  - **Confidence Dial**: Visual radial gauge (e.g. `89% Confidence`)

---

### Component 7: Results Table & Scrape Karma Trust Badges
* **UI Control**: Interactive Data Grid / Table.
* **Fields Rendered**:
  - Dynamically generated columns based on requested fields (e.g., `Product Name`, `Price`, `Rating`).
  - **Scrape Karma Score Badge** per row:
    - 🟢 `90 - 100`: Verified High Quality
    - 🟡 `50 - 89`: Warning (Partial text / Missing attributes)
    - 🔴 `< 50`: Corrupted / Bot block pattern
* **Export Action Toolbar**:
  - `[📦 Export JSON]` | `[📊 Export CSV]` | `[📝 Export Markdown]` | `[🧠 Export RAG Chunks]`

---

### Component 8: Scrape ➔ RAG Chatbot Panel
* **UI Layout**: ChatGPT-style message feed with input at bottom.
* **Input Fields**:
  1. **Index Button**: `[⚡ Index Scraped Data to Vector Store]` (Triggers `POST /api/rag/index/{job_id}`)
  2. **Question Input Bar**: `<input type="text" placeholder="Ask anything about the scraped data... e.g. Which laptop has 32GB RAM?" />`
  3. **Ask Button**: `[Send / Ask ➔]`
* **Output Card Components**:
  - **AI Synthesized Answer**: Formatted markdown response.
  - **Citations Drawer / Pills**: Clickable source tags showing exact row index & matched text snippet.

---

## 🎨 3. Recommended Design System & Colors

```css
/* Recommended Theme Tokens */
--bg-main: #0b0d11;          /* Deep obsidian background */
--panel-bg: #14171f;         /* Dark slate card panels */
--border-color: #252936;     /* Subtle panel borders */
--text-primary: #e6e8ec;     /* Crisp white text */
--text-muted: #8b8f9a;       /* Secondary grey text */

--accent-blue: #4f8cff;      /* Primary action buttons */
--accent-purple: #7c3aed;    /* Gradient hero tags */
--status-good: #3ecf8e;      /* High Karma / Success green */
--status-warn: #f2a93b;      /* Self-heal / Warning amber */
--status-bad: #f2543b;       /* Error / Low Karma red */
```

---

## 🚀 4. Summary Checklist for Frontend Developer

- [ ] **Top Header**: Project Title + Target URL bar + Ping `/health` connection dot.
- [ ] **Idea Presets**: 4 clickable pill cards that pre-fill URL and field names.
- [ ] **Tabbed Mode Selector**: Switch between *Plain English*, *Teach by Example*, and *Agentic*.
- [ ] **Dynamic Field List**: Ability to add/remove extraction field rows.
- [ ] **Execution Console**: WebSocket terminal for real-time logs.
- [ ] **Heal Replay Card**: Visual before/after selector diff with confidence score.
- [ ] **Data Table**: Tabular view with Scrape Karma badges and 4 export formats.
- [ ] **RAG Chat Window**: Conversational Q&A with expandable citation cards.

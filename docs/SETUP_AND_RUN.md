# NeuroScrape — Setup & Execution Guide

Complete guide to running NeuroScrape locally or via Docker in under 2 minutes.

---

## 1. Quickstart via Docker Compose (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/your-team/neuroscrape.git
cd neuroscrape/backend

# 2. Configure environment variables (optional for local/mock demo)
cp .env.example .env

# 3. Build & Run
docker-compose up --build
```
- API is live at `http://localhost:8000`
- Interactive OpenAPI Docs at `http://localhost:8000/docs`
- Open `test-ui/index.html` directly in your browser.

---

## 2. Local Python Setup (Without Docker)

### Prerequisites
- Python 3.11+ installed

```bash
# 1. Navigate to backend directory
cd SAMP/backend

# 2. Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate dataset & build NeuroAnchor model
python scripts/build_dataset.py
python scripts/quantize_model.py
python scripts/train_karma_head.py

# 5. Start FastAPI Backend Server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 3. Running the Test Console

1. In any modern browser, open `test-ui/index.html` (or `SAMP/index.html`).
2. Alternatively, serve via simple Python HTTP server:
   ```bash
   cd SAMP/test-ui
   python -m http.server 3000
   ```
3. Open `http://localhost:3000` to verify live telemetry, self-healing, and RAG Q&A.

---

## 4. Running the Automated Test Suite

```bash
cd SAMP/backend
pytest -v
```
All test suites in `tests/` will execute and validate API endpoints, Layer 1 NeuroAnchor healing, Scrape Karma evaluation, ethics compliance, and RAG retrieval.

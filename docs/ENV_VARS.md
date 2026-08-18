# NeuroScrape — Environment Variables Reference

Complete reference table for all configuration settings supported in `.env`.

---

| Variable Name | Description | Default Value | Required? | Safe Offline Dev Value |
|---|---|---|---|---|
| `ENVIRONMENT` | Runtime environment (`development`, `production`, `test`) | `development` | Optional | `development` |
| `LOG_LEVEL` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `INFO` | Optional | `INFO` |
| `HOST` | Server bind host address | `0.0.0.0` | Optional | `0.0.0.0` |
| `PORT` | Server bind port | `8000` | Optional | `8000` |
| `CORS_ORIGINS` | Allowed CORS origins for frontend client | `["*"]` | Optional | `["*"]` |
| `BRIGHTDATA_API_KEY` | Bright Data API token (Promo code: `wemakedevs`) | *None* | Required for live Scraper Studio runs | `""` (activates adaptive fallback) |
| `BRIGHTDATA_CUSTOMER_ID` | Bright Data Account / Customer ID | *None* | Optional | `""` |
| `BRIGHTDATA_ZONE` | Bright Data zone name for proxies | *None* | Optional | `""` |
| `BRIGHTDATA_SCRAPER_STUDIO_API_URL` | Bright Data Scraper Studio DCA API endpoint | `https://api.brightdata.com/dca/v1` | Optional | `https://api.brightdata.com/dca/v1` |
| `LLM_PROVIDER` | LLM planning engine (`openai`, `anthropic`, `groq`, `local`) | `local` | Optional | `local` (0 cost heuristic) |
| `OPENAI_API_KEY` | OpenAI API key for schema planning | *None* | Optional | `""` |
| `ANTHROPIC_API_KEY` | Anthropic API key | *None* | Optional | `""` |
| `GROQ_API_KEY` | Groq high-speed free tier API key | *None* | Optional | `""` |
| `LLM_MODEL` | Target LLM model name | `gpt-4o-mini` | Optional | `gpt-4o-mini` |
| `DATABASE_URL` | Database connection URL | `sqlite:///./neuroscrape.db` | Optional | `sqlite:///./neuroscrape.db` |
| `REDIS_URL` | Redis instance connection string | `redis://localhost:6379/0` | Optional | `redis://localhost:6379/0` |
| `CHROMA_PERSIST_DIR` | Embedded ChromaDB persistent storage path | `./chroma_db` | Optional | `./chroma_db` |
| `MODEL_PATH` | Quantized NeuroAnchor ONNX model directory | `./models/neuroanchor-v1-onnx` | Optional | `./models/neuroanchor-v1-onnx` |
| `KARMA_MODEL_PATH` | Scrape Karma classifier head path | `./models/karma-head.joblib` | Optional | `./models/karma-head.joblib` |
| `NEUROANCHOR_CONFIDENCE_THRESHOLD` | Cosine similarity threshold for Layer 1 heal acceptance | `0.72` | Optional | `0.72` |
| `ENFORCE_ROBOTS_TXT` | Flag to enforce pre-flight robots.txt rules | `true` | Optional | `true` |
| `BLOCK_PRIVATE_URLS` | Flag to block private/auth/localhost URLs | `true` | Optional | `true` |

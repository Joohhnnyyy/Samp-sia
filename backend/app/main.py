"""
NeuroScrape - FastAPI Backend Main Application
Into the Scrape-Verse (WeMakeDevs x Bright Data Hackathon)
Autonomous, Self-Healing Web Scraping Platform.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import settings
from .db import init_db
from .healing.neuroanchor import neuroanchor_engine
from .healing.karma_score import karma_engine
from .ws.manager import ws_manager

from .api.scrape import router as scrape_router
from .api.heal import router as heal_router
from .api.export import router as export_router
from .api.rag import router as rag_router
from .api.health import router as health_router
from .api.dev import router as dev_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("neuroscrape")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing NeuroScrape Database...")
    init_db()
    
    logger.info("Loading NeuroAnchor semantic embedding model & Karma classifier...")
    app.state.neuroanchor = neuroanchor_engine
    app.state.karma = karma_engine
    
    logger.info("NeuroScrape AI & Backend Engine started successfully.")
    yield
    # Shutdown
    logger.info("Shutting down NeuroScrape Engine.")


app = FastAPI(
    title="NeuroScrape API",
    description="Autonomous, Self-Healing Web Scraping Platform built on Bright Data Scraper Studio & Local NeuroAnchor AI.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for frontend teammate and test harness
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(scrape_router)
app.include_router(heal_router)
app.include_router(export_router)
app.include_router(rag_router)
app.include_router(health_router)
app.include_router(dev_router)


# ==========================================
# Core System Endpoints
# ==========================================

@app.get("/health", tags=["System"])
async def health_check():
    """System health check endpoint for frontend and monitoring probes."""
    return {
        "status": "healthy",
        "service": "NeuroScrape AI/Backend",
        "version": "1.0.0",
        "brightdata_configured": bool(settings.BRIGHTDATA_API_KEY),
        "neuroanchor_loaded": True,
        "llm_provider": settings.LLM_PROVIDER
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "name": "NeuroScrape API",
        "docs_url": "/docs",
        "health_check": "/health",
        "message": "Welcome to NeuroScrape — Autonomous Self-Healing Scraping Platform"
    }


# ==========================================
# Realtime WebSocket Stream
# ==========================================

@app.websocket("/ws/jobs/{job_id}")
async def websocket_job_endpoint(websocket: WebSocket, job_id: str):
    """
    Live streaming channel for job status, execution logs, self-heal replays, and results.
    """
    await ws_manager.connect(websocket, job_id)
    try:
        while True:
            # Keep-alive receive loop
            data = await websocket.receive_text()
            logger.debug(f"Received WS text on job {job_id}: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, job_id)
    except Exception as e:
        logger.warning(f"WebSocket error on job {job_id}: {e}")
        ws_manager.disconnect(websocket, job_id)

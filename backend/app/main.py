"""
NeuroScrape - FastAPI Backend Main Application
Into the Scrape-Verse (WeMakeDevs x Bright Data Hackathon)
Autonomous, Self-Healing Web Scraping Platform.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import Session

from .core.config import settings
from .db import init_db, get_session
from .healing.neuroanchor import neuroanchor_engine
from .healing.karma_score import karma_engine
from .ws.manager import ws_manager

from .api.scrape import router as scrape_router
from .api.heal import router as heal_router
from .api.export import router as export_router
from .api.rag import router as rag_router
from .api.health import router as health_router
from .api.dev import router as dev_router
from .api.news import router as news_router
from .api.watch import router as watch_router
from .api.memory import router as memory_router
from .services.watch_engine import watch_scheduler

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("neuroscrape")


from .api.health import health_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing NeuroScrape Database...")
    init_db()
    
    logger.info("Loading NeuroAnchor semantic embedding model & Karma classifier...")
    app.state.neuroanchor = neuroanchor_engine
    app.state.karma = karma_engine

    logger.info("Starting SaMp Watch scheduler...")
    await watch_scheduler.start()

    logger.info("Starting Scraper Health Monitor scheduler...")
    await health_scheduler.start(interval_seconds=300)
    
    logger.info("SaMp AI & Backend Engine started successfully.")
    yield
    # Shutdown
    logger.info("Stopping SaMp Watch scheduler...")
    await watch_scheduler.stop()
    logger.info("Stopping Scraper Health Monitor scheduler...")
    await health_scheduler.stop()
    logger.info("Shutting down SaMp Engine.")


app = FastAPI(
    title="SaMp API",
    description="SaMp — Autonomous, Self-Healing Web Scraping Platform built on Bright Data Scraper Studio & Local NeuroAnchor AI.",
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
app.include_router(news_router)
app.include_router(watch_router)
app.include_router(memory_router)


# ==========================================
# Core System Endpoints
# ==========================================

import os
from pathlib import Path
from fastapi.responses import FileResponse, JSONResponse

# UI Path resolution
SAMP_ROOT = Path(__file__).resolve().parent.parent.parent
TEST_UI_PATH = SAMP_ROOT / "test-ui" / "index.html"
ROOT_UI_PATH = SAMP_ROOT / "index.html"


@app.get("/health", tags=["System"])
async def health_check():
    """System health check endpoint for frontend and monitoring probes."""
    return {
        "status": "healthy",
        "service": "SaMp AI/Backend",
        "version": "1.0.0",
        "brightdata_configured": bool(settings.BRIGHTDATA_API_KEY),
        "neuroanchor_loaded": True,
        "llm_provider": settings.LLM_PROVIDER
    }


@app.get("/", tags=["System"])
async def root():
    """Serves the interactive SaMp Studio UI directly at http://localhost:8000"""
    if TEST_UI_PATH.exists():
        return FileResponse(str(TEST_UI_PATH))
    elif ROOT_UI_PATH.exists():
        return FileResponse(str(ROOT_UI_PATH))
    return {
        "name": "SaMp API",
        "docs_url": "/docs",
        "health_check": "/health",
        "message": "Welcome to SaMp — Autonomous Self-Healing Scraping Platform"
    }


@app.get("/ui", tags=["System"])
async def studio_ui():
    """Serves the interactive SaMp Studio UI at http://localhost:8000/ui"""
    if TEST_UI_PATH.exists():
        return FileResponse(str(TEST_UI_PATH))
    elif ROOT_UI_PATH.exists():
        return FileResponse(str(ROOT_UI_PATH))
    return JSONResponse(status_code=404, content={"error": "UI index.html not found"})


@app.get("/api/jobs/{job_id}", tags=["System"])
async def get_job_alias(job_id: str, db: Session = Depends(get_session)):
    """Job status polling alias with managed DB session lifecycle."""
    from .api.scrape import get_job
    return await get_job(job_id=job_id, db=db)


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
            data = await websocket.receive_text()
            logger.debug(f"Received WS text on job {job_id}: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, job_id)
    except Exception as e:
        logger.warning(f"WebSocket error on job {job_id}: {e}")
        ws_manager.disconnect(websocket, job_id)


@app.websocket("/ws/watch/{watch_job_id}")
async def websocket_watch_endpoint(websocket: WebSocket, watch_job_id: str):
    """Per-watch live streaming channel for NeuroWatch cycle updates."""
    await ws_manager.connect(websocket, f"watch_{watch_job_id}")
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Received WS text on watch {watch_job_id}: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, f"watch_{watch_job_id}")
    except Exception as e:
        logger.warning(f"WebSocket error on watch {watch_job_id}: {e}")
        ws_manager.disconnect(websocket, f"watch_{watch_job_id}")


@app.websocket("/ws/watch")
async def websocket_watch_aggregate(websocket: WebSocket):
    """Global aggregate feed for all NeuroWatch updates — the mission control dashboard."""
    await ws_manager.connect_global(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Received WS text on global watch feed: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect_global(websocket)
    except Exception as e:
        logger.warning(f"WebSocket error on global watch feed: {e}")
        ws_manager.disconnect_global(websocket)

"""
NeuroScrape - NewsKeeper, Auto-Categorization & Geopolitical Assistant API Router
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..scrapers.taxonomy_categorizer import taxonomy_categorizer
from ..services.news_keeper import news_keeper
from ..services.geopolitical_assistant import geopolitical_assistant

router = APIRouter(prefix="/api", tags=["NewsKeeper & Intelligence"])


# ==========================================
# Request Models
# ==========================================

class AutoCategorizeRequest(BaseModel):
    url: str
    max_subpages: int = Field(default=3, ge=1, le=8)


class FactCheckRequest(BaseModel):
    query_or_url: str
    user_region: str = Field(default="India")
    max_sources: int = Field(default=4, ge=2, le=8)


class GeopoliticalChatRequest(BaseModel):
    message: str
    user_location: str = Field(default="India")
    chat_history: Optional[List[Dict[str, str]]] = None


# ==========================================
# Endpoints
# ==========================================

@router.post("/scrape/auto-categorize")
async def auto_categorize_url(req: AutoCategorizeRequest):
    """
    Ingests a target URL, crawls its primary pages & subpages,
    and automatically organizes entities into AI-inferred hierarchical category cards.
    """
    if not req.url.startswith("http"):
        raise HTTPException(status_code=400, detail="Valid HTTP/HTTPS URL required.")
    
    result = await taxonomy_categorizer.extract_and_categorize(
        url=req.url,
        max_subpages=req.max_subpages
    )
    return result


@router.post("/news/fact-check")
async def fact_check_news(req: FactCheckRequest):
    """
    NewsKeeper Engine: Scrapes cross-web sources for any news headline, keyword, or link.
    Outputs: Trust %, Consensus Rating, Facts vs. Myths breakdown, and Source Comparison Matrix.
    """
    if not req.query_or_url.strip():
        raise HTTPException(status_code=400, detail="Search query or article URL is required.")

    result = await news_keeper.analyze_news_topic(
        query_or_url=req.query_or_url,
        user_region=req.user_region,
        max_sources=req.max_sources
    )
    return result


@router.get("/news/trending")
async def get_trending_news(location: str = Query(default="India", description="User country/region")):
    """
    Retrieves live trending national and world geopolitical themes for the specified geography.
    """
    topics = await geopolitical_assistant.get_trending_topics(user_location=location)
    return {
        "location": location,
        "topics_count": len(topics),
        "trending_topics": topics
    }


@router.post("/assistant/geopolitical-chat")
async def geopolitical_chat(req: GeopoliticalChatRequest):
    """
    Conversational Geopolitical & World News AI Assistant:
    Answers user queries grounded in real-time scraped web news with source citations.
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    result = await geopolitical_assistant.chat(
        message=req.message,
        user_location=req.user_location,
        chat_history=req.chat_history
    )
    return result

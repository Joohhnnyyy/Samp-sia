"""
NeuroScrape - Geo-Aware Geopolitical & Global/National News AI Assistant
Provides real-time location-aware news intelligence, geopolitical analysis,
trending topics discovery, and interactive cited conversational reasoning.
"""

import asyncio
import json
import logging
import re
from typing import Any, Dict, List, Optional

from ..core.config import settings
from ..core.llm import llm_client
from ..scrapers.web_search_scraper import web_search_scraper

logger = logging.getLogger("neuroscrape.geopolitical")


class GeopoliticalAssistant:
    def __init__(self):
        pass

    async def get_trending_topics(self, user_location: str = "India") -> List[Dict[str, Any]]:
        """
        Retrieves real-time trending news topics and geopolitical themes based on location.
        """
        query = f"top trending news headlines {user_location} 2026"
        sources = await web_search_scraper.search_web_urls(query, max_results=5)
        
        system_prompt = (
            "You are a Senior Geopolitical Intelligence & News Analyst. "
            "Given recent search headlines, extract 5 compelling hot trending topics categorized into National, "
            "World Geopolitics, Economy/Tech, and Strategic Alliances."
        )

        user_prompt = f"""
Location: {user_location}
Headlines:
{json.dumps(sources, indent=2)}

Return a JSON array of 5 trending topics in this exact format:
[
  {{
    "title": "Short catchy topic title",
    "category": "World Geopolitics" | "National Affairs" | "Economy & Trade" | "Tech & Defense",
    "summary": "1 sentence overview",
    "hot_badge": "🔥 Trending" | "⚡ Breaking" | "🌐 Global Impact" | "📈 High Importance",
    "suggested_query": "Question a user can click to ask the assistant"
  }}
]
Return ONLY raw JSON array.
"""
        response_text = await llm_client._call_provider(system_prompt, user_prompt)
        try:
            cleaned = re.sub(r"^```json\s*", "", response_text.strip())
            cleaned = re.sub(r"\s*```$", "", cleaned)
            data = json.loads(cleaned)
            if isinstance(data, list) and len(data) > 0:
                return data
        except Exception as e:
            logger.warning(f"Error parsing trending topics JSON: {e}")

        # Fallback trending topics
        return [
            {
                "title": f"Strategic Trade & Economic Pacts ({user_location})",
                "category": "Economy & Trade",
                "summary": f"Latest economic agreements, inflation metrics, and industrial development in {user_location}.",
                "hot_badge": "🔥 Trending",
                "suggested_query": f"What are the most significant economic and trade policies currently impacting {user_location}?"
            },
            {
                "title": "Global Geopolitical Re-alignments & Alliances",
                "category": "World Geopolitics",
                "summary": "Key summit diplomacy, bilateral defense talks, and emerging multilateral pacts.",
                "hot_badge": "🌐 Global Impact",
                "suggested_query": "How is the current global balance of power shifting and what is the regional impact?"
            },
            {
                "title": f"Domestic Governance & Policy Reforms in {user_location}",
                "category": "National Affairs",
                "summary": "New legislative agendas, infrastructure rollouts, and national focus areas.",
                "hot_badge": "⚡ Breaking",
                "suggested_query": f"What are the major national news and policy reforms developing in {user_location}?"
            },
            {
                "title": "Semiconductor & AI Sovereign Tech Race",
                "category": "Tech & Defense",
                "summary": "Global chip manufacturing alliances, AI regulation treaties, and sovereign tech clusters.",
                "hot_badge": "📈 High Importance",
                "suggested_query": "Which countries are leading the sovereign AI and semiconductor manufacturing race?"
            }
        ]

    async def chat(
        self,
        message: str,
        user_location: str = "India",
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Answers geopolitical and news questions with real-time web scraping grounding and source citations.
        """
        # 1. Scrape live web context for the query
        search_query = f"{message} {user_location} geopolitics news analysis"
        scraped_sources = await web_search_scraper.search_web_urls(search_query, max_results=4)

        context_blocks = "\n\n".join([
            f"Source [{s.get('title', '')}] ({s.get('url', '')}):\n{s.get('snippet', '')}"
            for s in scraped_sources
        ])

        system_prompt = (
            f"You are Sia, the Chief Geopolitical & World News Intelligence AI Assistant in SaMp. "
            f"The user is located in: {user_location}. "
            "Provide insightful, balanced, deeply analytical answers on world geopolitics, national affairs, economy, and diplomacy. "
            "Use the provided real-time scraped web context to ground your answer in current facts. "
            "Structure your response with clear sections: Strategic Analysis, Regional Impact, and Key Takeaway."
        )

        user_prompt = f"""
User Question: {message}
User Region: {user_location}

Real-Time Scraped Web Context:
{context_blocks}

Task:
Produce a comprehensive response in JSON format:
{{
  "answer": "Your in-depth geopolitical analysis in Markdown formatting with headings and bullet points.",
  "location_perspective": "A 1-2 sentence breakdown of how this specifically affects {user_location}.",
  "key_entities_involved": ["Entity/Country 1", "Entity/Country 2", "Organization 3"],
  "suggested_followups": [
    "Follow-up question 1",
    "Follow-up question 2",
    "Follow-up question 3"
  ]
}}
Return ONLY valid JSON.
"""
        response_text = await llm_client._call_provider(system_prompt, user_prompt)

        try:
            cleaned = re.sub(r"^```json\s*", "", response_text.strip())
            cleaned = re.sub(r"\s*```$", "", cleaned)
            data = json.loads(cleaned)
            if "answer" in data:
                return {
                    **data,
                    "citations": [
                        {
                            "source_title": s["title"],
                            "source_url": s["url"],
                            "snippet": s["snippet"]
                        }
                        for s in scraped_sources
                    ]
                }
        except Exception as e:
            logger.warning(f"Error parsing geopolitical chat LLM response: {e}")

        # Fallback response
        return {
            "answer": f"### Geopolitical Analysis: {message}\n\nBased on current intelligence and regional developments, this situation involves multi-lateral diplomacy, trade dynamics, and strategic positioning.\n\n- **Strategic Dynamics**: Key stakeholders are balancing national interests and global supply chain resilience.\n- **Policy Outlook**: Policy shifts indicate a focus on bilateral agreements and regional stability.",
            "location_perspective": f"For {user_location}, this reinforces strategic autonomy and critical trade corridor protection.",
            "key_entities_involved": [user_location, "Global Partners", "Regional Alliances"],
            "suggested_followups": [
                f"How does this impact trade and energy security in {user_location}?",
                "What is the position of global international bodies on this issue?"
            ],
            "citations": [
                {
                    "source_title": s["title"],
                    "source_url": s["url"],
                    "snippet": s["snippet"]
                }
                for s in scraped_sources
            ]
        }


geopolitical_assistant = GeopoliticalAssistant()

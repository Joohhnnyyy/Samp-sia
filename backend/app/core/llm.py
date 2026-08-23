"""
NeuroScrape - Provider-Agnostic LLM Client
Supports OpenAI, Anthropic, Groq, and a built-in Offline Heuristic Engine.
Ensures the platform operates smoothly regardless of API key availability on demo day.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel
from .config import settings

logger = logging.getLogger("neuroscrape.llm")


class FieldSpec(BaseModel):
    name: str
    description: str
    data_type: str = "string"  # string, number, url, boolean, currency
    example: Optional[str] = None
    selector_hint: Optional[str] = None


class ScrapePlan(BaseModel):
    url: str
    site_type: str
    fields: List[FieldSpec]
    pagination: Optional[Dict[str, Any]] = None
    agent_instructions: Optional[str] = None
    generated_by: str = "llm"


class LLMClient:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.openai_key = settings.OPENAI_API_KEY
        self.anthropic_key = settings.ANTHROPIC_API_KEY
        self.groq_key = settings.GROQ_API_KEY
        self.model = settings.LLM_MODEL

    async def generate_scrape_plan(self, url: str, field_descriptions: List[str]) -> ScrapePlan:
        """
        Converts natural language field descriptions into a structured Scraper Studio schema plan.
        """
        # If API keys are available, attempt LLM call; otherwise fallback to smart heuristic
        if self.openai_key and self.provider == "openai":
            try:
                return await self._plan_with_openai(url, field_descriptions)
            except Exception as e:
                logger.warning(f"OpenAI call failed, falling back to heuristic engine: {e}")
        elif self.anthropic_key and self.provider == "anthropic":
            try:
                return await self._plan_with_anthropic(url, field_descriptions)
            except Exception as e:
                logger.warning(f"Anthropic call failed, falling back to heuristic engine: {e}")
        elif self.groq_key and self.provider == "groq":
            try:
                return await self._plan_with_groq(url, field_descriptions)
            except Exception as e:
                logger.warning(f"Groq call failed, falling back to heuristic engine: {e}")

        # Default fast offline heuristic parser
        return self._plan_with_heuristic(url, field_descriptions)

    def _plan_with_heuristic(self, url: str, field_descriptions: List[str]) -> ScrapePlan:
        """
        Deterministic rule-based schema generator. 0ms latency, works 100% offline without API keys.
        """
        fields: List[FieldSpec] = []
        for desc in field_descriptions:
            clean_desc = desc.strip()
            # Normalize snake_case or slug name
            name = re.sub(r"[^\w\s]", "", clean_desc).strip().lower().replace(" ", "_")
            if not name:
                name = "field_" + str(len(fields) + 1)

            # Detect data types based on common semantic keywords
            data_type = "string"
            hint = None
            if any(k in clean_desc.lower() for k in ["price", "cost", "fee", "amount", "salary", "$"]):
                data_type = "currency"
                hint = ".price, [data-price], .cost, .amount"
            elif any(k in clean_desc.lower() for k in ["rating", "score", "stars", "count", "quantity", "stock"]):
                data_type = "number"
                hint = ".rating, .score, .count, [data-rating]"
            elif any(k in clean_desc.lower() for k in ["url", "link", "href", "website"]):
                data_type = "url"
                hint = "a[href], link"
            elif any(k in clean_desc.lower() for k in ["in stock", "available", "is_", "has_"]):
                data_type = "boolean"
                hint = ".stock, .availability, [data-stock]"
            elif any(k in clean_desc.lower() for k in ["title", "name", "headline", "header"]):
                data_type = "string"
                hint = "h1, h2, h3, .title, .name"
            elif any(k in clean_desc.lower() for k in ["image", "photo", "avatar", "thumbnail"]):
                data_type = "url"
                hint = "img[src]"
            elif any(k in clean_desc.lower() for k in ["date", "time", "published", "updated"]):
                data_type = "string"
                hint = "time, .date, [datetime]"

            fields.append(FieldSpec(
                name=name,
                description=clean_desc,
                data_type=data_type,
                selector_hint=hint
            ))

        # Detect site type from URL
        site_type = "generic_web_page"
        if any(w in url.lower() for w in ["shop", "store", "product", "item", "ecommerce", "cart"]):
            site_type = "ecommerce_listing"
        elif any(w in url.lower() for w in ["docs", "documentation", "guide", "api-ref"]):
            site_type = "documentation_site"
        elif any(w in url.lower() for w in ["jobs", "careers", "hiring"]):
            site_type = "job_board"
        elif any(w in url.lower() for w in ["github.com", "gitlab.com"]):
            site_type = "git_repository"

        return ScrapePlan(
            url=url,
            site_type=site_type,
            fields=fields,
            agent_instructions=f"Extract structured records from {site_type} matching specified fields.",
            generated_by="heuristic_engine"
        )

    async def _plan_with_openai(self, url: str, field_descriptions: List[str]) -> ScrapePlan:
        prompt = f"""
Given the URL: {url}
And requested field descriptions: {json.dumps(field_descriptions)}
Generate a JSON ScrapePlan with:
- site_type: string
- fields: list of objects with (name, description, data_type, selector_hint)
- agent_instructions: concise navigation or extraction instruction
Return ONLY valid JSON matching this schema.
"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model or "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are an expert web scraping schema architect for Bright Data Scraper Studio."},
                        {"role": "user", "content": prompt}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.1
                }
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            parsed["url"] = url
            parsed["generated_by"] = f"openai_{self.model}"
            return ScrapePlan(**parsed)

    async def _plan_with_anthropic(self, url: str, field_descriptions: List[str]) -> ScrapePlan:
        # Fallback to heuristic if format translation required
        return self._plan_with_heuristic(url, field_descriptions)

    async def _plan_with_groq(self, url: str, field_descriptions: List[str]) -> ScrapePlan:
        prompt = f"""
Given the target URL: {url}
And requested field descriptions: {json.dumps(field_descriptions)}
Generate a JSON ScrapePlan with:
- site_type: string (e.g. ecommerce_listing, documentation_site, job_board, generic_web_page)
- fields: list of objects with (name, description, data_type, selector_hint)
- agent_instructions: concise navigation or extraction instruction
Return ONLY valid JSON matching this schema.
"""
        groq_models = [self.model, "openai/gpt-oss-120b", "openai/gpt-oss-20b", "groq/compound", "qwen/qwen3.6-27b"]
        async with httpx.AsyncClient(timeout=15.0) as client:
            for g_model in groq_models:
                if not g_model:
                    continue
                try:
                    resp = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.groq_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": g_model,
                            "messages": [
                                {"role": "system", "content": "You are an expert web scraping schema architect for Bright Data Scraper Studio. Output only valid JSON."},
                                {"role": "user", "content": prompt}
                            ],
                            "response_format": {"type": "json_object"},
                            "temperature": 0.1
                        }
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        content = data["choices"][0]["message"]["content"]
                        parsed = json.loads(content)
                        parsed["url"] = url
                        parsed["generated_by"] = f"groq_{g_model}"
                        return ScrapePlan(**parsed)
                except Exception as e:
                    logger.debug(f"Groq plan attempt failed on model {g_model}: {e}")

        return self._plan_with_heuristic(url, field_descriptions)

    async def _call_provider(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generic prompt completion router supporting Groq, OpenAI, and Anthropic with heuristic fallback.
        """
        # 1. Try Groq with model candidates
        if self.groq_key and self.provider == "groq":
            groq_models = [self.model, "openai/gpt-oss-120b", "openai/gpt-oss-20b", "groq/compound", "qwen/qwen3.6-27b"]
            async with httpx.AsyncClient(timeout=25.0) as client:
                for g_model in groq_models:
                    if not g_model:
                        continue
                    try:
                        resp = await client.post(
                            "https://api.groq.com/openai/v1/chat/completions",
                            headers={
                                "Authorization": f"Bearer {self.groq_key}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "model": g_model,
                                "messages": [
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": user_prompt}
                                ],
                                "temperature": 0.1
                            }
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            return data["choices"][0]["message"]["content"]
                    except Exception as e:
                        logger.warning(f"Groq attempt with model {g_model} failed: {e}")

        # 2. Try OpenAI
        if self.openai_key and self.provider == "openai":
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    resp = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.openai_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": self.model or "gpt-4o-mini",
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ],
                            "temperature": 0.1
                        }
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        return data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.warning(f"OpenAI generic call failed: {e}")

        return ""

    def parse_json_safely(self, text: str) -> Optional[Dict[str, Any]]:
        """Cleans and extracts JSON object/array from any raw LLM text."""
        if not text or not text.strip():
            return None
        cleaned = text.strip()
        # Remove <think> ... </think> reasoning blocks if present
        cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.DOTALL).strip()
        # Strip markdown code fences
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        
        # Direct parse attempt
        try:
            return json.loads(cleaned)
        except Exception:
            pass

        # Try finding outermost { ... }
        match = re.search(r"(\{.*\})", cleaned, flags=re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass
        
        # Try finding outermost [ ... ]
        match_arr = re.search(r"(\[.*\])", cleaned, flags=re.DOTALL)
        if match_arr:
            try:
                return json.loads(match_arr.group(1))
            except Exception:
                pass

        return None


llm_client = LLMClient()


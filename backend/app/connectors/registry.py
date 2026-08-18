"""
NeuroScrape - Connector Registry (Section 5.9)
Inspired by Agent-Reach: Thin preset adapters that expose pre-built plans
for common site archetypes, enabling one-click instant demos for hackathon idea tracks.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class PresetConnector(BaseModel):
    id: str
    name: str
    category: str
    description: str
    example_url: str
    fields: List[str]
    suggested_selectors: Dict[str, str]


CONNECTORS: Dict[str, PresetConnector] = {
    "ecommerce": PresetConnector(
        id="ecommerce",
        name="E-Commerce Price Intelligence",
        category="Price Intelligence",
        description="Extracts product names, prices, stock availability, and ratings for competitive pricing intelligence.",
        example_url="https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops",
        fields=["product_name", "price", "stock_status", "rating", "description"],
        suggested_selectors={
            "product_name": ".title, h4 > a, .product-title",
            "price": ".price, .product-price, [data-price]",
            "stock_status": ".stock, .availability, [data-stock]",
            "rating": ".ratings, .rating, [data-rating]",
            "description": ".description, p.desc"
        }
    ),
    "docs_to_rag": PresetConnector(
        id="docs_to_rag",
        name="Documentation to RAG Knowledge Base",
        category="Docs-to-RAG",
        description="Extracts documentation titles, hierarchical sections, code snippets, and explanations ready for vector RAG.",
        example_url="https://docs.brightdata.com/cli/overview",
        fields=["page_title", "section_heading", "code_snippet", "body_text"],
        suggested_selectors={
            "page_title": "h1, .article-title, .doc-title",
            "section_heading": "h2, h3, .section-header",
            "code_snippet": "pre code, pre, .code-block",
            "body_text": "article p, .markdown-body p, main p"
        }
    ),
    "job_board": PresetConnector(
        id="job_board",
        name="Tech Job Market & Salary Tracker",
        category="Market Research",
        description="Extracts job titles, companies, locations, salary ranges, and required skills.",
        example_url="https://news.ycombinator.com/jobs",
        fields=["job_title", "company", "location", "salary_range", "tech_stack"],
        suggested_selectors={
            "job_title": ".title, .job-title, h2 a",
            "company": ".company, .employer, .company-name",
            "location": ".location, .remote-badge",
            "salary_range": ".salary, .compensation",
            "tech_stack": ".tags, .skills, .badges"
        }
    ),
    "dev_trend": PresetConnector(
        id="dev_trend",
        name="Developer Changelog & Release Monitor",
        category="Dev Trend Tracker",
        description="Tracks software release versions, release dates, new features, and breaking changes.",
        example_url="https://github.com/fastapi/fastapi/releases",
        fields=["release_version", "release_date", "release_title", "highlights"],
        suggested_selectors={
            "release_version": ".release-header, .tag, h1 a",
            "release_date": "relative-time, time, .date",
            "release_title": ".release-title, h2",
            "highlights": ".markdown-body ul, .release-desc"
        }
    ),
    "github_repo": PresetConnector(
        id="github_repo",
        name="GitHub Open Source Intelligence",
        category="Competitive Intelligence",
        description="Extracts repository stats, stars, forks, latest releases, and description.",
        example_url="https://github.com/trending",
        fields=["repo_name", "stars", "forks", "description", "language"],
        suggested_selectors={
            "repo_name": "h2.h3 a, .repo-name",
            "stars": "a[href$='/stargazers'], .stars-count",
            "forks": "a[href$='/forks'], .forks-count",
            "description": "p.col-9, .repo-desc",
            "language": "[itemprop='programmingLanguage'], .lang"
        }
    )
}


class ConnectorRegistry:
    @staticmethod
    def list_all() -> List[PresetConnector]:
        return list(CONNECTORS.values())

    @staticmethod
    def get(connector_id: str) -> Optional[PresetConnector]:
        return CONNECTORS.get(connector_id)


connector_registry = ConnectorRegistry()

"""
NeuroScrape - Data Models & Schemas
SQLModel / SQLAlchemy schemas representing Jobs, Collectors, HealEvents, HealthEvents,
Schema Versions, and Scraped Rows.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field as PyField
from sqlmodel import Field, SQLModel, Column, JSON


# ==========================================
# Database Tables
# ==========================================

class Collector(SQLModel, table=True):
    __tablename__ = "collectors"

    id: str = Field(primary_key=True, index=True)
    name: str
    target_url: str
    schema_version: int = Field(default=1)
    brightdata_collector_id: Optional[str] = None
    active_selector_map: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    field_specs: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    status: str = Field(default="active")  # active, degraded, broken, archived
    success_rate: float = Field(default=1.0)
    total_runs: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Job(SQLModel, table=True):
    __tablename__ = "jobs"

    id: str = Field(primary_key=True, index=True)
    collector_id: Optional[str] = Field(default=None, index=True)
    url: str
    mode: str = Field(default="plain_english")  # plain_english, teach_by_example, agentic
    status: str = Field(default="pending")  # pending, running, completed, healing, failed
    row_count: int = Field(default=0)
    avg_karma_score: Optional[float] = None
    plan: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class ScrapedRow(SQLModel, table=True):
    __tablename__ = "scraped_rows"

    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: str = Field(index=True)
    collector_id: Optional[str] = Field(default=None, index=True)
    row_index: int = Field(default=0)
    data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    karma_score: int = Field(default=100)
    karma_flags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class HealEvent(SQLModel, table=True):
    __tablename__ = "heal_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    collector_id: str = Field(index=True)
    job_id: str = Field(index=True)
    field_name: str
    method: str  # "local_model" or "brightdata_cloud"
    before_selector: str
    after_selector: str
    confidence: float
    latency_ms: int
    candidate_scores: Dict[str, float] = Field(default_factory=dict, sa_column=Column(JSON))
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthEvent(SQLModel, table=True):
    __tablename__ = "health_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    collector_id: str = Field(index=True)
    status: str  # "healthy", "warning", "broken"
    drift_detected: bool = False
    row_count: int = 0
    missing_fields: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    avg_karma: float = 100.0
    message: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SchemaVersion(SQLModel, table=True):
    __tablename__ = "schema_versions"

    id: Optional[int] = Field(default=None, primary_key=True)
    collector_id: str = Field(index=True)
    version_num: int
    field_specs: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    selector_map: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    commit_message: str = "Initial schema creation"
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ==========================================
# NeuroWatch — Continuous Automation Models
# ==========================================

class WatchJob(SQLModel, table=True):
    __tablename__ = "watch_jobs"

    id: str = Field(primary_key=True, index=True)
    mode: str  # "links" or "keyword"
    input_urls: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    keyword_query: Optional[str] = None
    interval_seconds: int = Field(default=120)
    status: str = Field(default="active")  # active, paused, error
    total_cycles: int = Field(default=0)
    estimated_credits_per_hour: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None


class WatchCycle(SQLModel, table=True):
    __tablename__ = "watch_cycles"

    id: Optional[int] = Field(default=None, primary_key=True)
    watch_job_id: str = Field(index=True)
    cycle_number: int = Field(default=1)
    run_at: datetime = Field(default_factory=datetime.utcnow)
    source_results: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    diff_summary: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    heal_events_fired: int = Field(default=0)
    health_events_fired: int = Field(default=0)
    avg_karma: float = Field(default=100.0)
    status: str = Field(default="completed")  # completed, failed


class MemoryUsageEvent(SQLModel, table=True):
    __tablename__ = "memory_usage_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    field_type: str = Field(index=True)
    matched_entry_id: Optional[str] = None
    match_confidence: float = 0.0
    accepted_as_first_guess: bool = False
    verified_correct: bool = False
    target_site: str = Field(index=True)
    is_new_site: bool = True  # Site never scraped before by this deployment
    latency_saved_ms: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ==========================================
# API Request / Response DTOs
# ==========================================

class ScrapePlanRequest(BaseModel):
    url: str
    fields: List[str] = PyField(default_factory=list)


class ScrapeRunRequest(BaseModel):
    url: str
    fields: Optional[List[str]] = None
    collector_id: Optional[str] = None
    mode: str = "plain_english"
    max_rows: int = 50
    simulate_drift: bool = False


class TeachScrapeRequest(BaseModel):
    url: str
    label: str
    example: str
    additional_fields: Optional[List[Dict[str, str]]] = None


class AgenticScrapeRequest(BaseModel):
    url: str
    goal: str
    max_steps: int = 5
    timeout_seconds: int = 60


class SearchScrapeRequest(BaseModel):
    query: str
    fields: Optional[List[str]] = None
    max_sources: int = 4


class RAGIndexRequest(BaseModel):
    job_id: str
    collection_name: Optional[str] = None


class RAGAskRequest(BaseModel):
    question: str
    collection_name: Optional[str] = None
    job_id: Optional[str] = None
    top_k: int = 4


class WatchCreateRequest(BaseModel):
    mode: str  # "links" or "keyword"
    urls: Optional[List[str]] = None  # max 5 for mode=links
    query: Optional[str] = None  # for mode=keyword

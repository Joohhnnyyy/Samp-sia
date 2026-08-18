"""
NeuroScrape - Database Session & Initialization
Zero-setup SQLite via SQLModel / SQLAlchemy with clean upgrade path to PostgreSQL.
"""

from typing import Generator
from sqlmodel import SQLModel, Session, create_engine
from .core.config import settings

# In SQLite, connect_args check_same_thread is needed for multi-threaded FastAPI handlers
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, echo=False, connect_args=connect_args)


def init_db() -> None:
    """Creates all database tables if they do not already exist."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency for obtaining a database session per request."""
    with Session(engine) as session:
        yield session

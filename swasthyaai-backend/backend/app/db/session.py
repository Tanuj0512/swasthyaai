"""
SQLAlchemy engine and session management.

Decision — sync engine, not async: the domain logic here (rule evaluation,
forecasting arithmetic) is CPU-bound, not I/O-bound, and FastAPI already runs
sync dependencies in a threadpool. An async engine (asyncpg) would add
complexity (async repositories, async context managers throughout every
layer) without a real throughput benefit at this scale. Sync SQLAlchemy 2.0
with `psycopg` (v3) is simpler to reason about, simpler to test, and just as
production-viable for a service handling PHC-scale traffic. Revisit only if
this evolves into a high-concurrency national platform.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: one session per request, always closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

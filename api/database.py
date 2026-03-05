"""SQLAlchemy database configuration."""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

_PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{_PROJECT_ROOT / 'raphael.db'}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

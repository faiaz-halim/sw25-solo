from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os

# Database URL - can be overridden by environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://swordworld:swordworld@localhost:5432/swordworld")

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.

    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    """
    from . import models  # Import models to ensure they are registered
    Base.metadata.create_all(bind=engine)


def get_db_session() -> Session:
    """
    Get a database session for direct use.

    Returns:
        Session: Database session
    """
    return SessionLocal()

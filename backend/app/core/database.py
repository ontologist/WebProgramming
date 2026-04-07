"""
Database engine setup. Uses PostgreSQL if available, falls back to SQLite.
"""
import logging
import os

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings

logger = logging.getLogger(__name__)

SQLITE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
SQLITE_PATH = os.path.join(SQLITE_DIR, "wp200.db")


def _try_postgres() -> bool:
    """Test if PostgreSQL is reachable."""
    if not settings.DATABASE_URL or "postgresql" not in settings.DATABASE_URL:
        return False
    try:
        eng = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        eng.dispose()
        return True
    except Exception as e:
        logger.warning(f"PostgreSQL not available ({e}), falling back to SQLite")
        return False


def _get_engine():
    if _try_postgres():
        logger.info(f"Using PostgreSQL: {settings.DATABASE_URL.split('@')[-1]}")
        return create_engine(
            settings.DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )
    else:
        os.makedirs(SQLITE_DIR, exist_ok=True)
        sqlite_url = f"sqlite:///{SQLITE_PATH}"
        logger.info(f"Using SQLite: {SQLITE_PATH}")
        eng = create_engine(sqlite_url, connect_args={"check_same_thread": False})

        # Enable WAL mode for SQLite
        @event.listens_for(eng, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        return eng


engine = _get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_engine_type() -> str:
    """Return 'postgresql' or 'sqlite'."""
    return "postgresql" if "postgresql" in str(engine.url) else "sqlite"

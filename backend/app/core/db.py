from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# ============================================================
# DATABASE ENGINE CONFIGURATION - HANDLES BOTH SQLITE & POSTGRES
# ============================================================

if "sqlite" in str(settings.DATABASE_URL).lower():
    # SQLite with connection pooling fix for concurrent requests
    logger.info("[DB] Configuring SQLite with WAL mode and connection pooling")
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={
            "check_same_thread": False,
            "timeout": 30,  # Wait 30 seconds for database lock
            "isolation_level": "DEFERRED"  # Use DEFERRED transactions
        },
        poolclass=StaticPool,  # Single connection, no pool overhead
        pool_pre_ping=True,  # Check connection health before use
        echo=False
    )
    
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        """Configure SQLite for production use"""
        cursor = dbapi_conn.cursor()
        try:
            cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging (prevents locks)
            cursor.execute("PRAGMA synchronous=NORMAL")  # Faster writes, still safe
            cursor.execute("PRAGMA foreign_keys=ON")  # Enable foreign key constraints
            cursor.execute("PRAGMA cache_size=10000")  # Larger cache
            cursor.close()
            logger.debug("[DB] SQLite pragmas configured")
        except Exception as e:
            logger.error(f"[DB] Error setting SQLite pragmas: {e}")
            raise
else:
    # PostgreSQL/MySQL (production databases)
    logger.info("[DB] Configuring PostgreSQL/MySQL connection pool")
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=20,  # Number of connections to maintain
        max_overflow=40,  # Additional connections when needed
        pool_pre_ping=True,  # Test connections before use
        pool_recycle=3600,  # Recycle connections every hour
        echo=False
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Prevent stale object errors
)
Base = declarative_base()

def get_db():
    """Dependency injection for database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"[DB] Session error: {str(e)}")
        db.rollback()  # Rollback on error
        raise
    finally:
        db.close()  # Always close connection

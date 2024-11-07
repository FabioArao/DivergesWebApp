from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
import logging
from typing import Generator
from app.config.settings import settings

logger = logging.getLogger(__name__)

def setup_database():
    try:
        # Configure engine with connection pooling
        engine = create_engine(
            settings.DATABASE_URL,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_pre_ping=True,  # Enable connection health checks
            pool_recycle=3600,   # Recycle connections after 1 hour
        )
        
        # Test the connection
        with engine.connect() as connection:
            connection.execute("SELECT 1")
            
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
            expire_on_commit=False
        )
        
        logger.info("Database connection established successfully")
        return engine, SessionLocal
        
    except SQLAlchemyError as e:
        logger.error(f"Database connection error: {str(e)}")
        raise

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    Ensures proper handling of sessions with automatic cleanup.
    """
    if not SessionLocal:
        raise RuntimeError("Database not initialized. Call setup_database() first.")
    
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database session error: {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in database session: {str(e)}")
        raise
    finally:
        session.close()

# Initialize database connection
engine = None
SessionLocal = None

def init_db():
    global engine, SessionLocal
    try:
        engine, SessionLocal = setup_database()
    except Exception as e:
        logger.critical(f"Failed to initialize database: {str(e)}")
        raise

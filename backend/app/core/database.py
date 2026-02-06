"""
Database configuration and session management.
Supports both SQLAlchemy (SQL) and Motor (MongoDB) connections.
"""

from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
import logging

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy Base
Base = declarative_base()

# Global database instances
_engine: Optional[AsyncEngine] = None
_async_session_maker: Optional[async_sessionmaker] = None
_mongo_client: Optional[AsyncIOMotorClient] = None


def get_database_url() -> Optional[str]:
    """
    Get the database URL from settings.

    Returns:
        Database URL or None if not configured
    """
    return settings.DATABASE_URL


def create_engine() -> AsyncEngine:
    """
    Create SQLAlchemy async engine.

    Returns:
        AsyncEngine instance
    """
    database_url = get_database_url()

    if not database_url:
        raise ValueError("DATABASE_URL not configured")

    # Choose appropriate pool based on environment
    if settings.is_production:
        poolclass = QueuePool
        pool_kwargs = {
            "pool_size": settings.DATABASE_POOL_SIZE,
            "max_overflow": settings.DATABASE_MAX_OVERFLOW,
            "pool_pre_ping": True,
            "pool_recycle": 3600,
        }
    else:
        poolclass = NullPool
        pool_kwargs = {}

    engine = create_async_engine(
        database_url,
        echo=settings.DATABASE_ECHO,
        poolclass=poolclass,
        **pool_kwargs,
    )

    logger.info(f"Database engine created for: {database_url.split('@')[-1]}")
    return engine


async def init_db() -> None:
    """
    Initialize database connection and create tables.
    Should be called on application startup.
    """
    global _engine, _async_session_maker

    if not settings.database_enabled:
        logger.warning("Database not configured, using in-memory storage")
        return

    try:
        _engine = create_engine()
        _async_session_maker = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

        # Create tables
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Database initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_db() -> None:
    """
    Close database connections.
    Should be called on application shutdown.
    """
    global _engine, _async_session_maker

    if _engine:
        await _engine.dispose()
        logger.info("Database connections closed")

    _engine = None
    _async_session_maker = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for dependency injection.

    Yields:
        AsyncSession instance

    Example:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    if not _async_session_maker:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    async with _async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session as context manager.

    Yields:
        AsyncSession instance

    Example:
        async with get_db_context() as db:
            result = await db.execute(select(Item))
            items = result.scalars().all()
    """
    if not _async_session_maker:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    async with _async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# MongoDB Support

def init_mongo() -> AsyncIOMotorClient:
    """
    Initialize MongoDB client.

    Returns:
        AsyncIOMotorClient instance
    """
    global _mongo_client

    if not settings.DATABASE_URL or "mongodb" not in settings.DATABASE_URL:
        logger.warning("MongoDB not configured")
        return None

    try:
        _mongo_client = AsyncIOMotorClient(
            settings.DATABASE_URL,
            maxPoolSize=settings.DATABASE_POOL_SIZE,
            minPoolSize=5,
            serverSelectionTimeoutMS=5000,
        )

        logger.info("MongoDB client initialized successfully")
        return _mongo_client

    except Exception as e:
        logger.error(f"Failed to initialize MongoDB: {e}")
        raise


async def close_mongo() -> None:
    """
    Close MongoDB connections.
    """
    global _mongo_client

    if _mongo_client:
        _mongo_client.close()
        logger.info("MongoDB connections closed")

    _mongo_client = None


def get_mongo_client() -> AsyncIOMotorClient:
    """
    Get MongoDB client instance.

    Returns:
        AsyncIOMotorClient instance

    Raises:
        RuntimeError: If MongoDB is not initialized
    """
    if not _mongo_client:
        raise RuntimeError("MongoDB not initialized. Call init_mongo() first.")

    return _mongo_client


def get_mongo_db(database_name: Optional[str] = None):
    """
    Get MongoDB database instance.

    Args:
        database_name: Name of the database (defaults to name from connection string)

    Returns:
        AsyncIOMotorDatabase instance
    """
    client = get_mongo_client()

    if database_name:
        return client[database_name]

    # Extract database name from connection string
    if settings.DATABASE_URL:
        # Format: mongodb://host:port/database or mongodb+srv://host/database
        parts = settings.DATABASE_URL.split("/")
        if len(parts) > 3:
            db_name = parts[-1].split("?")[0]  # Remove query params
            return client[db_name]

    # Default database name
    return client["chatbot_db"]


# Health check functions

async def check_db_health() -> dict:
    """
    Check database connection health.

    Returns:
        Dictionary with health status
    """
    if not settings.database_enabled:
        return {
            "status": "disabled",
            "message": "Database not configured",
        }

    try:
        if _engine:
            async with _engine.connect() as conn:
                await conn.execute("SELECT 1")

            return {
                "status": "healthy",
                "type": "sql",
                "message": "Database connection is healthy",
            }
        else:
            return {
                "status": "error",
                "message": "Database engine not initialized",
            }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": str(e),
        }


async def check_mongo_health() -> dict:
    """
    Check MongoDB connection health.

    Returns:
        Dictionary with health status
    """
    if not _mongo_client:
        return {
            "status": "disabled",
            "message": "MongoDB not configured",
        }

    try:
        # Ping the database
        await _mongo_client.admin.command("ping")

        return {
            "status": "healthy",
            "type": "mongodb",
            "message": "MongoDB connection is healthy",
        }
    except Exception as e:
        logger.error(f"MongoDB health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": str(e),
        }

#!/usr/bin/env python3
"""
Database Initialization Script

This script initializes the database by creating all tables defined in the models.
It can be run standalone or as part of the deployment process.

Usage:
    python scripts/init_db.py

    or

    python scripts/init_db.py --drop  # Drop existing tables first
"""

import asyncio
import sys
import argparse
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.database import init_db, close_db, Base, _engine
from app.core.config import settings
from app.core.logging_config import setup_logging, get_logger
from app.models.conversation import Conversation, Message, User

# Setup logging
setup_logging()
logger = get_logger(__name__)


async def drop_tables():
    """Drop all existing tables."""
    if not _engine:
        logger.error("Database engine not initialized")
        return False

    try:
        logger.warning("Dropping all tables...")
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("All tables dropped successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to drop tables: {e}")
        return False


async def create_tables():
    """Create all tables defined in models."""
    try:
        logger.info("Creating database tables...")
        await init_db()
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        return False


async def verify_tables():
    """Verify that tables were created."""
    if not _engine:
        logger.error("Database engine not initialized")
        return False

    try:
        async with _engine.connect() as conn:
            # Check if conversations table exists
            result = await conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'"
                if "sqlite" in settings.DATABASE_URL
                else "SELECT table_name FROM information_schema.tables WHERE table_name='conversations'"
            )
            tables = result.fetchall()

            if tables:
                logger.info("✓ Conversations table exists")
                return True
            else:
                logger.error("✗ Conversations table not found")
                return False
    except Exception as e:
        logger.error(f"Failed to verify tables: {e}")
        return False


async def main(drop_first: bool = False):
    """
    Main initialization function.

    Args:
        drop_first: If True, drop existing tables before creating new ones
    """
    logger.info("=" * 60)
    logger.info("Database Initialization Script")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database URL: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    logger.info("=" * 60)

    # Drop tables if requested
    if drop_first:
        confirm = input("\n⚠️  WARNING: This will delete all existing data. Continue? (yes/no): ")
        if confirm.lower() != "yes":
            logger.info("Operation cancelled")
            return

        if not await drop_tables():
            logger.error("Failed to drop tables")
            return

    # Create tables
    if not await create_tables():
        logger.error("Failed to create tables")
        return

    # Verify tables
    if await verify_tables():
        logger.info("\n" + "=" * 60)
        logger.info("✓ Database initialization completed successfully!")
        logger.info("=" * 60)
    else:
        logger.error("\n" + "=" * 60)
        logger.error("✗ Database initialization failed!")
        logger.error("=" * 60)

    # Cleanup
    await close_db()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize the database")
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop existing tables before creating new ones"
    )

    args = parser.parse_args()

    try:
        asyncio.run(main(drop_first=args.drop))
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

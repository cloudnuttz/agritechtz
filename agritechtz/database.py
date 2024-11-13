"""Database connectivity module"""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from agritechtz.models import Base
from agritechtz.settings import Settings


# Load environment variables from a .env file, if available
settings = Settings()


# Initialize the async engine
engine = create_async_engine(settings.database_url, echo=True)


# Async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
)


# Dependency to get an async database session
@asynccontextmanager
async def acquire_session() -> AsyncGenerator[AsyncSession, Any]:
    """Acquire database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


# Initialize database function (optional, can be used for setup/migration)
async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        # This will create tables according to all Base subclasses (if they do not already exist)
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

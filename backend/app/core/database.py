from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData
from app.core.config import settings
from sqlalchemy.pool import NullPool

# Create async engine with proper URL handling
database_url = settings.DATABASE_URL

# Convert to async URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
elif database_url.startswith("sqlite"):
    database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")

engine = create_async_engine(
    database_url,
    echo=False,
    future=True,
    pool_pre_ping=False,  # Disable pre-ping for pooler
    poolclass=NullPool,
    execution_options={
        "isolation_level": "AUTOCOMMIT"
    },
    connect_args={
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0,
        "server_settings": {
            "jit": "off",
            "application_name": "tutor_system"
        }
    }
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()

async def get_db() -> AsyncSession:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_tables():
    """Create all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
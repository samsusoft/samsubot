#   backend/apps/core/postgres.py
# PostgreSQL utilities for handling database connections and sessions   
"""PostgreSQL utilities for handling database connections and sessions"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from apps.core.settings import settings

class Base(DeclarativeBase):
    pass

# Database engine and session
engine = None
AsyncSessionLocal = None

def init_db():
    """Initialize database connection"""
    global engine, AsyncSessionLocal
    
    database_url = settings.DATABASE_URL or "postgresql+asyncpg://samsu:secret123@samsubot_postgres/samsubot"
    engine = create_async_engine(database_url, echo=True)
    AsyncSessionLocal = async_sessionmaker(
        engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )

async def get_db():
    """Dependency to get database session"""
    if not AsyncSessionLocal:
        init_db()
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
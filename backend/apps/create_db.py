from apps.models.pg_models import Base
from apps.core.postgres import engine
import asyncio

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(create_db())
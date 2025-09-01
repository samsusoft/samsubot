# backend/apps/core/redis_client.py
# Redis client for caching and session management   
"""Redis client for caching and session management"""
import redis.asyncio as redis
from apps.core.settings import settings
import json
from typing import Any, Optional

class RedisManager:
    def __init__(self):
        self.redis_client = None
    
    async def connect(self):
        """Initialize Redis connection"""
        if not self.redis_client:
            redis_url = settings.REDIS_URL or "redis://samsubot_redis:6379/0"
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
    
    async def set_cache(self, key: str, value: Any, expire: int = 3600):
        """Set cache value with expiration"""
        await self.connect()
        await self.redis_client.setex(key, expire, json.dumps(value))
    
    async def get_cache(self, key: str) -> Optional[Any]:
        """Get cache value"""
        await self.connect()
        value = await self.redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def delete_cache(self, key: str):
        """Delete cache key"""
        await self.connect()
        await self.redis_client.delete(key)

# Global instance
redis_manager = RedisManager()
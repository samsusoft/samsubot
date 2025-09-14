# apps/rag/cache.py
# Simple in-memory cache for RAG responses
# Caching utilities

import time
response_cache = {}
CACHE_MAX_SIZE = 100

def get_cache_key(question: str) -> str:
    return question.lower().strip()

def cache_response(question: str, response: dict):
    global response_cache
    if len(response_cache) >= CACHE_MAX_SIZE:
        response_cache.pop(next(iter(response_cache)))
    response_cache[get_cache_key(question)] = {**response, 'cached_at': time.time()}

def get_cached_response(question: str) -> dict | None:
    cached = response_cache.get(get_cache_key(question))
    if cached and time.time() - cached['cached_at'] < 300:
        return {k: v for k, v in cached.items() if k != 'cached_at'}
    return None

def clear_cache():
    response_cache.clear()

def get_cache_stats():
    return {"cache_size": len(response_cache), "max_size": CACHE_MAX_SIZE}

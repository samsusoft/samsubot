import redis

redis_client = redis.Redis(host="samsubot_redis", port=6379, decode_responses=True)
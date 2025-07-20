import time
from apps.core.redis_client import redis_client
from apps.core.mongo import chat_log_collection
from apps.models.pg_models import ChatMetric
from apps.core.postgres import AsyncSessionLocal

async def process_message(session_id: str, message: str):
    start = time.time()
    intent = "general_query"
    bot_response = f"Echo: {message}"

    redis_client.set(session_id, message)
    chat_log_collection.insert_one({
        "session_id": session_id,
        "user_message": message,
        "bot_response": bot_response
    })

    response_time = time.time() - start
    async with AsyncSessionLocal() as session:
        metric = ChatMetric(session_id=session_id, intent=intent, response_time=response_time)
        session.add(metric)
        await session.commit()

    return {
        "session_id": session_id,
        "bot_response": bot_response,
        "intent": intent,
        "response_time": round(response_time, 2)
    }
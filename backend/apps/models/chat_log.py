from datetime import datetime
from pymongo import MongoClient
import os

mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise ValueError("MONGO_URI is not set in environment variables")

client = MongoClient(mongo_uri)
db = client["samsubot"]
chat_collection = db["chat_logs"]

def save_chat(session_id: str, user_message: str, bot_response: str):
    chat_collection.insert_one({
        "session_id": session_id,
        "user_message": user_message,
        "bot_response": bot_response,
        "timestamp": datetime.utcnow()
    })

def get_chat_history(session_id: str):
    return list(chat_collection.find({"session_id": session_id}).sort("timestamp", 1))
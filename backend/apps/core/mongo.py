# backend/apps/core/mongo.py
# MongoDB utilities for handling chat logs and other data storage   
"""MongoDB utilities for handling chat logs and other data storage"""
from pymongo import MongoClient
from datetime import datetime
from typing import List, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

from apps.core.settings import settings

class MongoManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.chat_log_collection = None
        self._executor = ThreadPoolExecutor(max_workers=4)
    
    def connect(self):
        """Initialize MongoDB connection"""
        if not self.client:
            print("Connecting to MongoDB...")
            print(f"Using MONGO_URI: {settings.MONGO_URI}")
            mongo_uri = settings.MONGO_URI or "mongodb://samsu:secret123@samsubot_mongodb:27017/samsubot?authSource=samsubot"
            self.client = MongoClient(mongo_uri)
            self.db = self.client["samsubot"]
            self.chat_log_collection = self.db["chat_logs"]
    
    async def save_chat_log(
        self, 
        username: str, 
        user_message: str, 
        bot_response: str
    ) -> None:
        """Save chat log asynchronously"""
        self.connect()
        
        def _save():
            self.chat_log_collection.insert_one({
                "username": username,
                "user_message": user_message,
                "bot_response": bot_response,
                "timestamp": datetime.utcnow()
            })
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self._executor, _save)
    
    async def get_chat_history(
        self, 
        username: str, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get chat history for user"""
        self.connect()
        
        def _get_history():
            return list(
                self.chat_log_collection
                .find({"username": username})
                .sort("timestamp", -1)
                .limit(limit)
            )
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, _get_history)

# Global instance
mongo_manager = MongoManager()

# Convenience functions
async def save_chat_log(username: str, user_message: str, bot_response: str):
    await mongo_manager.save_chat_log(username, user_message, bot_response)

async def get_chat_history(username: str, limit: int = 50):
    return await mongo_manager.get_chat_history(username, limit)
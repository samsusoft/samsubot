from pymongo import MongoClient
import os

# Read from env or fallback to the default
MONGO_URI = os.getenv("MONGO_URI", "mongodb://samsu:secret123@samsubot_mongodb:27017/samsubot")

client = MongoClient(MONGO_URI)
mongo_db = client["samsubot"]
chat_log_collection = mongo_db["chat_logs"]
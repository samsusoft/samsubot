from pymongo import MongoClient

client = MongoClient("mongodb://samsubot_mongodb:27017")
mongo_db = client["samsubot"]
chat_log_collection = mongo_db["chat_logs"]
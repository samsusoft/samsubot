# /apps/apps/api/models.py
"""Pydantic models for API requests and responses"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)

class ChatResponse(BaseModel):
    message: str
    sources: List[str] = [] 

class QueryRequest(BaseModel):
    q: str = Field(..., min_length=1, max_length=1000)

class QueryResponse(BaseModel):
    answer: str

class ChatHistoryItem(BaseModel):
    user_message: str
    bot_response: str
    timestamp: datetime

class ChatHistoryResponse(BaseModel):
    history: list[ChatHistoryItem]
# backend/apps/core/llm.py
# LLM utilities for handling queries with Retrieval-Augmented Generation    
from backend.Unwanted.rag_chain import run_query

async def get_llm_response(query: str) -> str:
    return await run_query(query)

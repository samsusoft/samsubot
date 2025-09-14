# apps/rag/query.py

import time
import asyncio
import functools
from concurrent.futures import ThreadPoolExecutor
from typing import List
from langchain.schema import Document
from qdrant_client import QdrantClient

from apps.rag.cache import cache_response, get_cached_response, clear_cache, get_cache_stats
from apps.rag.llm import llm
from apps.rag.prompt import rag_prompt
from apps.rag.retriever import retriever
from apps.rag.config import VECTOR_DB_URL, QDRANT_COLLECTION

# ---------------------------
# Performance optimizations
# ---------------------------
executor = ThreadPoolExecutor(max_workers=4)

# ---------------------------
# Document processing
# ---------------------------
def process_documents_sync(docs: List[Document], question: str) -> str:
    """Synchronously process documents with LLM."""
    if not docs:
        return "I don't have relevant information to answer this question."
    
    # Truncate context if too long
    context_parts = []
    total_length = 0
    max_context = 1500
    
    for doc in docs:
        content = doc.page_content
        if total_length + len(content) <= max_context:
            context_parts.append(content)
            total_length += len(content)
        else:
            # Add partial content if space allows
            remaining = max_context - total_length
            if remaining > 100:
                context_parts.append(content[:remaining] + "...")
            break
    
    context = "\n\n".join(context_parts)
    
    # Generate response using the imported prompt template
    prompt = rag_prompt.format(context=context, question=question)
    return llm.invoke(prompt)

# ---------------------------
# Main query function
# ---------------------------
async def run_rag_query(question: str) -> dict:
    """Execute RAG query with performance optimizations."""
    start_time = time.time()
    
    try:
        # Handle greetings immediately
        greetings = {"hello", "hi", "hey", "good morning", "good afternoon", "good evening"}
        if question.lower().strip() in greetings:
            return {
                "message": "Hello! I'm SamsuBot, your assistant.",
                "sources": [],
                "response_time": round(time.time() - start_time, 3),
                "cached": False
            }
        
        # Check cache first
        cached_response = get_cached_response(question)
        if cached_response:
            cached_response['response_time'] = round(time.time() - start_time, 3)
            cached_response['cached'] = True
            return cached_response
        
        # Parallel execution
        loop = asyncio.get_running_loop()
        
        # 1. Document retrieval
        retrieval_start = time.time()
        docs = await loop.run_in_executor(
            executor, 
            functools.partial(retriever.get_relevant_documents, question)
        )
        retrieval_time = time.time() - retrieval_start
        
        # 2. LLM processing
        llm_start = time.time()
        answer = await loop.run_in_executor(
            executor,
            process_documents_sync,
            docs,
            question
        )
        llm_time = time.time() - llm_start
        
        # Process response
        clean_answer = " ".join(answer.split()).strip()
        if not clean_answer:
            clean_answer = "I don't have relevant information to answer this question."
        
        # Extract sources efficiently
        sources = list({
            doc.metadata.get("source", "Unknown") 
            for doc in docs[:3]
        })
        
        response_time = round(time.time() - start_time, 3)
        
        response = {
            "message": clean_answer,
            "sources": sorted(sources),
            "response_time": response_time,
            "cached": False,
            "metrics": {
                "retrieval_time": round(retrieval_time, 3),
                "llm_time": round(llm_time, 3),
                "docs_retrieved": len(docs)
            }
        }
        
        # Cache successful responses
        cache_response(question, response)
        
        return response
        
    except Exception as e:
        error_time = round(time.time() - start_time, 3)
        print(f"❌ RAG query error: {e}")
        return {
            "message": "I'm sorry, I encountered an error processing your query.",
            "sources": [],
            "response_time": error_time,
            "cached": False,
            "error": str(e)
        }

# ---------------------------
# Batch processing for multiple queries
# ---------------------------
async def run_batch_queries(questions: List[str]) -> List[dict]:
    """Process multiple queries efficiently."""
    tasks = [run_rag_query(q) for q in questions]
    return await asyncio.gather(*tasks, return_exceptions=True)

# ---------------------------
# Synchronous wrapper //this can be moved to rag_service.py in the future
# ---------------------------
def ask_question(query: str) -> dict:
    """Synchronous wrapper with performance monitoring."""
    try:
        return asyncio.run(run_rag_query(query))
    except Exception as e:
        return {
            "message": "System error occurred.",
            "sources": [],
            "response_time": 0.0,
            "cached": False,
            "error": str(e)
        }

# ---------------------------
# Performance utilities
# ---------------------------
def optimize_collection():
    """Optimize the Qdrant collection for better performance."""
    try:
        client = QdrantClient(url=VECTOR_DB_URL)
        client.optimize_vectors(collection_name=QDRANT_COLLECTION)
        print("✅ Collection optimized")
    except Exception as e:
        print(f"⚠️ Collection optimization failed: {e}")

# ---------------------------
# Health check
# ---------------------------
async def health_check() -> dict:
    """Check system health and performance."""
    start_time = time.time()
    
    try:
        # Test query
        test_result = await run_rag_query("hello")
        
        return {
            "status": "healthy",
            "response_time": round(time.time() - start_time, 3),
            "cache_stats": get_cache_stats(),
            "test_query_time": test_result.get("response_time", 0)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "response_time": round(time.time() - start_time, 3)
        }
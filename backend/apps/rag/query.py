# apps/rag/query.py

import os
import time
import asyncio
import functools
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.schema import Document
from apps.rag.config import VECTOR_DB_URL, EMBEDDING_MODEL, OLLAMA_BASE_URL, QDRANT_COLLECTION

# ---------------------------
# Performance optimizations
# ---------------------------
# Thread pool for CPU-bound operations
executor = ThreadPoolExecutor(max_workers=4)

# Cache for frequently asked questions
response_cache = {}
CACHE_MAX_SIZE = 100

# ---------------------------
# Global Embedding (load once)
# ---------------------------
embedding = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={'device': 'cpu'},  # Explicit device setting
    encode_kwargs={'normalize_embeddings': True}  # Normalize for better similarity
)
print(f"⚡ Using local HuggingFace embeddings: {EMBEDDING_MODEL}")

# ---------------------------
# Optimized Vectorstore
# ---------------------------
def get_vectorstore():
    client = QdrantClient(
        url=VECTOR_DB_URL,
        timeout=10,  # Reduced timeout
        prefer_grpc=True  # Use gRPC for better performance
    )
    
    if not client.collection_exists(QDRANT_COLLECTION):
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=rest.VectorParams(
                size=384, 
                distance=rest.Distance.COSINE,
                hnsw_config=rest.HnswConfigDiff(
                    m=16,  # Reduced connections for faster search
                    ef_construct=100,  # Balanced build/search performance
                )
            ),
            optimizers_config=rest.OptimizersConfigDiff(
                default_segment_number=2,  # Optimize for small collections
                memmap_threshold=1000,
                indexing_threshold=1000,
            )
        )
        print(f"✅ Created optimized collection: {QDRANT_COLLECTION}")
    else:
        print(f"ℹ️ Using existing collection: {QDRANT_COLLECTION}")
    
    return QdrantVectorStore(
        client=client, 
        collection_name=QDRANT_COLLECTION, 
        embedding=embedding
    )

vectorstore = get_vectorstore()

# ---------------------------
# High-performance Retriever
# ---------------------------
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 3,  # Retrieve fewer documents for speed
        "search_params": {
            "hnsw_ef": 16,  # Much lower ef for faster search
            "exact": False  # Use approximate search
        }
    }
)

# ---------------------------
# Optimized LLM (Non-streaming for speed)
# ---------------------------
llm = OllamaLLM(
    model="mistral",
    base_url=OLLAMA_BASE_URL,
    streaming=False,  # Disable streaming for faster response
    num_ctx=2048,     # Reduced context window
    num_predict=150,  # Limit response length
    temperature=0.1,  # Lower temperature for faster, more focused responses
    top_p=0.9,
    repeat_penalty=1.1
)

# Warm up LLM with connection pooling
try:
    print("🟡 Warming up LLM...")
    start = time.time()
    _ = llm.invoke("Hi")
    warmup_time = time.time() - start
    print(f"✅ LLM warmup complete ({warmup_time:.2f}s)")
except Exception as e:
    print(f"⚠️ LLM warmup failed: {e}")

# ---------------------------
# Optimized Prompt (shorter for speed)
# ---------------------------
prompt_template = PromptTemplate.from_template(
    "You are SamsuBot. Answer concisely using only the context below.\n\n"
    "Context: {context}\n\n"
    "Question: {question}\n\n"
    "Answer (1-2 sentences max):"
)

# ---------------------------
# Caching utilities
# ---------------------------
def get_cache_key(question: str) -> str:
    """Generate a cache key for the question."""
    return question.lower().strip()

def cache_response(question: str, response: dict):
    """Cache response with size limit."""
    global response_cache
    if len(response_cache) >= CACHE_MAX_SIZE:
        # Remove oldest entry
        oldest_key = next(iter(response_cache))
        del response_cache[oldest_key]
    
    cache_key = get_cache_key(question)
    response_cache[cache_key] = {
        **response,
        'cached_at': time.time()
    }

def get_cached_response(question: str) -> Optional[dict]:
    """Get cached response if available and fresh."""
    cache_key = get_cache_key(question)
    if cache_key in response_cache:
        cached = response_cache[cache_key]
        # Cache valid for 5 minutes
        if time.time() - cached['cached_at'] < 300:
            return {k: v for k, v in cached.items() if k != 'cached_at'}
    return None

# ---------------------------
# Optimized document processing
# ---------------------------
def process_documents_sync(docs: List[Document], question: str) -> str:
    """Synchronously process documents with LLM."""
    if not docs:
        return "I don't have relevant information to answer this question."
    
    # Truncate context if too long
    context_parts = []
    total_length = 0
    max_context = 1500  # Reduced context length
    
    for doc in docs:
        content = doc.page_content
        if total_length + len(content) <= max_context:
            context_parts.append(content)
            total_length += len(content)
        else:
            # Add partial content if space allows
            remaining = max_context - total_length
            if remaining > 100:  # Only if significant space left
                context_parts.append(content[:remaining] + "...")
            break
    
    context = "\n\n".join(context_parts)
    
    # Generate response
    prompt = prompt_template.format(context=context, question=question)
    return llm.invoke(prompt)

# ---------------------------
# High-speed async query
# ---------------------------
async def run_rag_query(question: str) -> dict:
    """Execute RAG query with maximum performance optimizations."""
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
        
        # Parallel execution of retrieval and embedding if needed
        loop = asyncio.get_running_loop()
        
        # 1. Fast retrieval
        retrieval_start = time.time()
        docs = await loop.run_in_executor(
            executor, 
            functools.partial(retriever.get_relevant_documents, question)
        )
        retrieval_time = time.time() - retrieval_start
        
        # 2. Fast LLM processing
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
            for doc in docs[:3]  # Limit sources for speed
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
# Synchronous wrapper (optimized)
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
def clear_cache():
    """Clear the response cache."""
    global response_cache
    response_cache.clear()
    print("Cache cleared.")

def get_cache_stats():
    """Get cache statistics."""
    return {
        "cache_size": len(response_cache),
        "max_size": CACHE_MAX_SIZE,
        "hit_ratio": "N/A"  # Could be implemented with counters
    }

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
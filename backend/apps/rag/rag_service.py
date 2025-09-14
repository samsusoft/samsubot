# apps/rag/rag_service.py
# High-level RAG service interface
from apps.rag.query import run_rag_query

# thin wrapper (if you want sync call)
def ask_question(query: str):
    """Wrapper around async RAG query"""
    import asyncio
    return asyncio.run(run_rag_query(query))

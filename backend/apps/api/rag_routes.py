# apps/api/rag_routes.py
# RAG routes for handling queries with Retrieval-Augmented Generation   
from fastapi import APIRouter, HTTPException, status
from apps.api.models import QueryRequest, QueryResponse
from apps.rag.query import run_rag_query  # renamed for clarity
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/rag-query", response_model=QueryResponse)
async def rag_query(request: QueryRequest):
    """Process RAG query and return answer"""
    print("Chat routes loaded successfully-rag_routes - rag_query()"),
    try:
        answer = await run_rag_query(request.query)
        return QueryResponse(answer=answer)
    except Exception as e:
        logger.error(f"Error in RAG query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process query"
        )

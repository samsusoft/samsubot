# apps/api/chat_routes.py
# Chat routes for handling user queries with RAG (Retrieval-Augmented Generation)
"""Chat routes for handling user queries with RAG"""
from fastapi import APIRouter, Depends, HTTPException, status
from apps.api.models import ChatRequest, ChatResponse
from apps.core.auth import get_current_user
from apps.rag.query import run_rag_query
from apps.core.mongo import save_chat_log
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/rag", response_model=ChatResponse)
#print("Chat routes loaded successfully-chat.py")
async def chat(request: ChatRequest,current_user: dict = Depends(get_current_user)):
    """Process chat message with RAG and return response"""
    print("Chat routes loaded successfully-chat.py - chat()"),
    try:
        response = await run_rag_query(request.message)
        message = response["message"]
        sources = response["sources"]
        print("Chat routes loaded successfully-chat_routes.py - rag_qry()"),
        # Save to chat history
        await save_chat_log(
            username=current_user["username"],
            user_message=request.message,
            bot_response=response
        )
        return {
            "message": message,
            "sources": sources
        }
        #return ChatResponse(message=response)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
from fastapi import APIRouter, Depends, Request
from apps.core.auth import get_current_user
from apps.models.chat_log import save_chat, get_chat_history

router = APIRouter()

@router.post("/")
async def chat(request: Request, user=Depends(get_current_user)):
    data = await request.json()  # ✅ must await this
    session_id = data.get("session_id")
    user_message = data.get("message")
    
    # Fake bot response
    bot_response = f"Echo: {user_message}"
    
    # Save to DB
    save_chat(session_id, user_message, bot_response)

    return {"message": bot_response}

@router.get("/history")
def history(session_id: str, user=Depends(get_current_user)):
    records = get_chat_history(session_id)
    return [
        {
            "user_message": r["user_message"],
            "bot_response": r["bot_response"],
            "timestamp": r["timestamp"]
        } for r in records
    ]
# apps/api/chat.py

from fastapi import APIRouter, Depends
from apps.core.auth import get_current_user

router = APIRouter()

@router.post("")
def chat(user=Depends(get_current_user)):
    return {"message": f"Hello, {user['username']}! You are authorized."}
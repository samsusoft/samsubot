# apps/api/protected.py
# Protected routes that require authentication
"""Protected routes that require authentication"""
from fastapi import APIRouter, Depends
from apps.core.auth import get_current_user

router = APIRouter()

@router.get("/")
async def protected_route(current_user: dict = Depends(get_current_user)):
    """Protected endpoint that requires authentication"""
    return {"message": f"Hello, {current_user['username']}. This is a protected route!"}

@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile information"""
    return {
        "username": current_user["username"],
        "message": "Profile information retrieved successfully"
    }
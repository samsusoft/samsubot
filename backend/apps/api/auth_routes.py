#\apps\api\auth_routes.py
# Auth routes for user login and token generation
"""Auth routes for user login and token generation"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from apps.core.auth import verify_password, create_access_token
from apps.core.userstore import get_user_by_username
from apps.core.settings import settings

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Authenticate user and return access token"""
    user = get_user_by_username(request.username)
    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": request.username},
        expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return TokenResponse(access_token=access_token, token_type="bearer")
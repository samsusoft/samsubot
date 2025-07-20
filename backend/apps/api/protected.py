from fastapi import APIRouter, Depends
from apps.core.deps import get_current_user

router = APIRouter()

@router.get("/protected")
def protected_route(user: str = Depends(get_current_user)):
    return {"message": f"Hello, {user}. This is a protected route!"}
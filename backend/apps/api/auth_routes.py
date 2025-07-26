from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from apps.core.auth import verify_password, create_access_token
from apps.core.userstore import fake_user

router = APIRouter()
print("Auth routes initialized")

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(request: LoginRequest):
    print("Login request received")
    if not request.username or not request.password:
        if request.username != fake_user["username"]:
            print("Invalid username or password")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

    if not verify_password(request.password, fake_user["hashed_password"]):
        print("NP: Invalid username or password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = create_access_token(data={"sub": request.username})
    return {
        "access_token": token,
        "token_type": "bearer"
    }

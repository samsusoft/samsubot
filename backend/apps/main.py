from fastapi import FastAPI
from apps.api import chat  # make sure this matches the import path
from apps.api import auth_routes, protected   # new import for auth

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to SamsuBot Backend API!"}

# include your chat router here
app.include_router(chat.router, prefix="/chat", tags=["chat"]) # include the chat router
app.include_router(auth_routes.router, prefix="/auth", tags=["auth"]) # include the auth router
app.include_router(protected.router)  # register protected routes
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # 👈 NEW import

from apps.api import chat  # your chat routes
from apps.api import auth_routes, protected  # your auth and protected routes

app = FastAPI()

# ✅ Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # ⚠️ Allow all in dev. Use specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Health check route
@app.get("/")
async def root():
    return {"message": "Welcome to SamsuBot Backend API!"}

# ✅ Include your routers
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(protected.router, prefix="/protected", tags=["protected"]) # Protected routes

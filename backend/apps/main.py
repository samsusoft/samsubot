"""Main FastAPI application"""
from apps.api import chat_routes
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import your route modules
try:
    from apps.api import auth_routes, protected, rag_routes, chat_routes
    routes_imported = True
except ImportError as e:
    print(f"Route import error: {e}")
    routes_imported = False

app = FastAPI(title="SamsuBot API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint (always available)
@app.get("/")
async def root():
    return {"message": "SamsuBot API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include routers only if they imported successfully
try:
    from apps.api import auth_routes
    app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
    print("Auth routes loaded successfully")
except ImportError as e:
    print(f"Auth route import error: {e}")

try:
    from apps.api import chat_routes
    app.include_router(chat_routes.router, prefix="/chat", tags=["chat"])
    print("Chat routes loaded successfully")
except ImportError as e:
    print(f"Chat route import error: {e}")

try:
    from apps.api import protected
    app.include_router(protected.router, prefix="/protected", tags=["protected"])
    print("Protected routes loaded successfully")
except ImportError as e:
    print(f"Protected route import error: {e}")

try:
    from apps.api import rag_routes
    app.include_router(rag_routes.router, prefix="/rag", tags=["rag"])
    print("RAG routes loaded successfully")
except ImportError as e:
    print(f"RAG route import error: {e}")

#if routes_imported:
#    app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
#    app.include_router(chat.router, prefix="/chat", tags=["chat"])
#    app.include_router(protected.router, prefix="/protected", tags=["protected"])
#    app.include_router(rag_routes.router, prefix="/rag", tags=["rag"])
#    print("All routes loaded successfully")
#else:
#    print("Running in minimal mode - only health endpoints available")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
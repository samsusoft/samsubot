from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create the FastAPI app
app = FastAPI()

# ✅ Add CORS middleware just after app creation
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development. Use specific origin in prod.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your route definitions below
@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}

# Other routes like /auth/login or /chat can go here
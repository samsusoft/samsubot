from fastapi import APIRouter
from pydantic import BaseModel
from apps.rag.rag_chain import run_query

router = APIRouter()

class QueryRequest(BaseModel):
    q: str

@router.post("/rag-query")
async def rag_query(request: QueryRequest):
    answer = run_query(request.q)
    return {"answer": answer}

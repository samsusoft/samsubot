# rag/chain.py

import httpx
from apps.rag.retriever import retrieve_context

OLLAMA_URL = "http://samsubot_llm:11434"

async def run_query(query: str) -> str:
    context = retrieve_context(query)
    full_prompt = f"""You are a helpful assistant.
Use the following context to answer the question.
If the context is not relevant, just say 'I don't know'.

Context:
{context}

Question:
{query}
"""

    payload = {
        "model": "mistral",
        "prompt": full_prompt,
        "stream": False
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
        response.raise_for_status()
        result = response.json()
        return result["response"].strip()

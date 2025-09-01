import requests
import json

# --- Test LLM via Ollama ---
print("🔍 Testing LLM (Ollama Mistral)...")
llm_resp = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "mistral",
        "prompt": "What is SamsuBot?",
    }
)
print("LLM Response:", llm_resp.text, "\n")


# --- Test RAG endpoint ---
print("🔍 Testing RAG API...")
rag_resp = requests.post(
    "http://localhost:8000/rag-query",
    headers={"Content-Type": "application/json"},
    data=json.dumps({"query": "What is SamsuBot?"})
)
print("RAG Response:", rag_resp.text)

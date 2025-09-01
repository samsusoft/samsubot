# apps/rag/llm.py

import requests

def call_llm(prompt: str) -> str:
    response = requests.post("http://samsubot_llm:11434/api/generate", json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    })
    return response.json()["response"]
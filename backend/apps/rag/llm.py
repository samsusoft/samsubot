# apps/rag/llm.py
# LLM configuration + warmup

import time
from langchain_ollama import OllamaLLM
from apps.rag.config import OLLAMA_BASE_URL

llm = OllamaLLM(
    model="mistral",
    base_url=OLLAMA_BASE_URL,
    streaming=False,
    num_ctx=2048,
    num_predict=150,
    temperature=0.1,
    top_p=0.9,
    repeat_penalty=1.1
)

def warmup_llm():
    try:
        print("🟡 Warming up LLM...")
        start = time.time()
        _ = llm.invoke("Hi")
        print(f"✅ LLM warmup complete ({time.time() - start:.2f}s)")
    except Exception as e:
        print(f"⚠️ LLM warmup failed: {e}")

warmup_llm()

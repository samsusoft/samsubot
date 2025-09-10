# apps/rag/query.py

import os
import time
import asyncio
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from apps.rag.config import VECTOR_DB_URL, EMBEDDING_MODEL, OLLAMA_BASE_URL, QDRANT_COLLECTION

# ---------------------------
# Global Embedding (load once)
# ---------------------------
embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
print(f"⚡ Using local HuggingFace embeddings: {EMBEDDING_MODEL}")

# ---------------------------
# Vectorstore
# ---------------------------
def get_vectorstore():
    client = QdrantClient(url=VECTOR_DB_URL)
    if not client.collection_exists(QDRANT_COLLECTION):
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=rest.VectorParams(size=384, distance=rest.Distance.COSINE),
        )
        print(f"✅ Created collection: {QDRANT_COLLECTION} (384d)")
    else:
        print(f"ℹ️ Using existing collection: {QDRANT_COLLECTION}")

    return QdrantVectorStore(client=client, collection_name=QDRANT_COLLECTION, embedding=embedding)

vectorstore = get_vectorstore()

# ---------------------------
# Retriever (optimized)
# ---------------------------
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 3,
        "search_params": {"hnsw_ef": 32}  # Lower ef for faster search
    }
)

# ---------------------------
# LLM (Streaming + Optional Warmup)
# ---------------------------
llm = OllamaLLM(
    model="mistral",
    base_url=OLLAMA_BASE_URL,
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)

# Optional warmup (send a short dummy request at startup)
try:
    print("🟡 Warming up LLM…")
    _ = llm.invoke("Hello")
    print("✅ LLM warmup complete")
except Exception as e:
    print(f"⚠️ LLM warmup skipped: {e}")

# ---------------------------
# Prompt
# ---------------------------
prompt_template = PromptTemplate.from_template(
    "You are SamsuBot, a helpful assistant.\n\n"
    "Use ONLY the context provided below to answer the question.\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}\n\n"
    "Guidelines:\n"
    "- Answer concisely.\n"
    "- Cite sources in square brackets using the file name.\n"
    "- If context does not contain the answer, reply:\n"
    "  'I don't know based on the provided documents.'\n\n"
    "Answer:"
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt_template}
)

# ---------------------------
# Async query with timing
# ---------------------------
async def run_rag_query(question: str) -> dict:
    loop = asyncio.get_running_loop()
    try:
        greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
        if question.lower().strip() in greetings:
            return {"message": "Hello! I'm SamsuBot, your assistant.", "sources": []}

        t0 = time.time()

        # 1️⃣ Retrieval
        retrieval_start = time.time()
        docs = retriever.get_relevant_documents(question)
        retrieval_time = time.time() - retrieval_start
        print(f"⏱ Retrieval time: {retrieval_time:.2f}s")

        # 2️⃣ LLM Generation
        llm_start = time.time()
        result = await loop.run_in_executor(None, lambda: qa_chain.combine_documents_chain.run(
            {"input_documents": docs, "question": question}
        ))
        llm_time = time.time() - llm_start
        print(f"⏱ LLM generation time: {llm_time:.2f}s")

        total_time = time.time() - t0
        print(f"⚡ Total query time: {total_time:.2f}s")

        answer = " ".join(result.split())
        sources = sorted({doc.metadata.get("source", "Unknown") for doc in docs})

        return {"message": answer, "sources": sources}

    except Exception as e:
        print(f"❌ Error running RAG query: {e}")
        return {"message": "❌ Error processing your query", "sources": []}

def ask_question(query: str):
    return asyncio.run(run_rag_query(query))

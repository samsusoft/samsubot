# apps/rag/query.py

import os
import asyncio
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
#from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from apps.rag.config import VECTOR_DB_URL, EMBEDDING_MODEL, OLLAMA_BASE_URL, QDRANT_COLLECTION


# ---------------------------
# Select Embedding Model
# ---------------------------
def get_embedding_model():
    provider = os.getenv("EMBEDDING_PROVIDER", "local").lower()
    print(f"⚡ Embedding provider: {provider}") 

    if provider == "openai":
        print("🔗 Using OpenAI embeddings (1536d)")
        #return OpenAIEmbeddings(model="text-embedding-3-small")
    else:
        print(f"⚡ Using local HuggingFace embeddings: {EMBEDDING_MODEL}")
        return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


# ---------------------------
# Helper: Initialize Qdrant collection safely
# ---------------------------
def get_vectorstore():
    client = QdrantClient(url=VECTOR_DB_URL)

    # Choose vector dimension based on embedding provider
    if os.getenv("EMBEDDING_PROVIDER", "local").lower() == "openai":
        vector_size = 1536
    else:
        # BGE large embeddings are 1024d
        vector_size = 384

    # Ensure collection exists
    if not client.collection_exists(QDRANT_COLLECTION):
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=rest.VectorParams(size=vector_size, distance=rest.Distance.COSINE),
        )
        print(f"✅ Created collection: {QDRANT_COLLECTION} ({vector_size}d)")
    else:
        print(f"ℹ️ Using existing collection: {QDRANT_COLLECTION}")

    embedding = get_embedding_model()

    return QdrantVectorStore(
        client=client,
        collection_name=QDRANT_COLLECTION,
        embedding=embedding
    )


# ---------------------------
# Vectorstore + Retriever
# ---------------------------
vectorstore = get_vectorstore()

retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 3, "fetch_k": 6}
)


# ---------------------------
# LLM
# ---------------------------
llm = OllamaLLM(model="mistral", base_url=OLLAMA_BASE_URL)


# ---------------------------
# Prompt Template
# ---------------------------
prompt_template = PromptTemplate.from_template(
    "You are SamsuBot, a helpful assistant.\n\n"
    "Use ONLY the context provided below to answer the question.\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}\n\n"
    "Guidelines:\n"
    "- Answer concisely and in a human-friendly manner.\n"
    "- Cite sources in square brackets using the file name.\n"
    "- Do NOT include information beyond the context.\n"
    "- If multiple sources support the same fact, list them together.\n"
    "- If the context does not contain the answer, reply exactly:\n"
    "  'I don't know based on the provided documents.'\n\n"
    "Answer:"
)


# ---------------------------
# QA Chain
# ---------------------------
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt_template}
)


# ---------------------------
# Async query function
# ---------------------------
async def run_rag_query(question: str) -> dict:
    """
    Run RAG pipeline and return human-friendly answer with clean citations.
    Automatically detects greetings and responds without pulling docs.
    """
    loop = asyncio.get_running_loop()
    try:
        # Handle greetings
        greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
        if question.lower().strip() in greetings:
            return {
                "message": "Hello! I'm SamsuBot, your assistant for customer support and knowledge-base queries. How can I help you today?",
                "sources": []
            }

        # Run query
        result = await loop.run_in_executor(
            None, lambda: qa_chain.invoke({"query": question})
        )

        answer = result.get("result", "No answer returned").strip()

        # Replace context markers with filenames
        for doc in result.get("source_documents", []):
            src = doc.metadata.get("source", "Unknown")
            answer = answer.replace("[Context]", f"[{src}]")

        # Deduplicate sources
        sources = sorted(set(
            doc.metadata.get("source", "Unknown")
            for doc in result.get("source_documents", [])
        ))

        # Clean answer
        answer = " ".join(answer.split())

        return {"message": answer, "sources": sources}

    except Exception as e:
        print(f"❌ Error running RAG query: {e}")
        return {"message": "❌ Error processing your query", "sources": []}


# ---------------------------
# Sync wrapper
# ---------------------------
def ask_question(query: str):
    return asyncio.run(run_rag_query(query))

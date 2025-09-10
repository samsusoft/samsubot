# apps/rag/debug.py

import os
import sys
import time
import asyncio
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from apps.rag.config import VECTOR_DB_URL, EMBEDDING_MODEL, OLLAMA_BASE_URL, QDRANT_COLLECTION

# ---------------------------
# Embeddings
# ---------------------------
embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
print(f"⚡ Using embeddings: {EMBEDDING_MODEL}")

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

retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3, "search_params": {"hnsw_ef": 32}}
)

llm = OllamaLLM(
    model="mistral",
    base_url=OLLAMA_BASE_URL,
    streaming=False  # disable streaming for easier timing logs
)

prompt_template = PromptTemplate.from_template(
    "You are SamsuBot, a helpful assistant.\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}\n\n"
    "Answer concisely and cite sources."
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt_template}
)

# ---------------------------
# Debug Query Function
# ---------------------------
async def debug_query(question: str):
    print(f"⚡ Debug Query: {question}")
    try:
        t0 = time.time()

        # Retrieval
        t_retrieval_start = time.time()
        docs = retriever.get_relevant_documents(question)
        retrieval_time = time.time() - t_retrieval_start
        print(f"⏱ Retrieval time: {retrieval_time:.2f}s")

        print("\n🔎 Retrieved Chunks:")
        for i, d in enumerate(docs, 1):
            source = d.metadata.get("source", "Unknown")
            preview = d.page_content[:150].replace("\n", " ")
            print(f"{i}. [{source}] {preview}...")

        # LLM Generation
        t_llm_start = time.time()
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: qa_chain.combine_documents_chain.run(
                {"input_documents": docs, "question": question}
            )
        )
        llm_time = time.time() - t_llm_start
        print(f"⏱ LLM generation time: {llm_time:.2f}s")

        total_time = time.time() - t0
        print(f"⚡ Total query time: {total_time:.2f}s")

        print("\n✅ Final Answer:\n ", result.strip())

    except Exception as e:
        print(f"❌ Debug query failed: {e}")

def ask_question(question: str):
    asyncio.run(debug_query(question))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Please provide a question.")
        sys.exit(1)
    ask_question(sys.argv[1])

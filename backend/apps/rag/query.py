# apps/rag/query.py

import asyncio
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from apps.rag.config import VECTOR_DB_PATH

# Constants
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
PERSIST_DIR = VECTOR_DB_PATH
OLLAMA_BASE_URL = "http://samsubot_llm:11434"  # Docker container name of Ollama

# 1. Embeddings
embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

# 2. Vectorstore
vectorstore = Chroma(
    persist_directory=PERSIST_DIR,
    embedding_function=embedding
)

# 3. Ollama LLM
llm = OllamaLLM(model="mistral", base_url=OLLAMA_BASE_URL)

# 4. Prompt Template (strict instruction to avoid hallucination)
prompt_template = PromptTemplate.from_template(
    "You are a helpful assistant.\n\n"
    "Use ONLY the following context to answer the question.\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}\n\n"
    "Rules:\n"
    "- Answer ONLY based on the provided context.\n"
    "- Do NOT use any external knowledge or make assumptions.\n"
    "- After each statement or fact, cite its source using the file name in square brackets.\n"
    "- If the answer cannot be found in the context, say exactly: 'I don't know based on the provided documents.'\n\n"
    "Answer:"
)

# 5. Retriever with MMR for diverse sources
retriever = vectorstore.as_retriever(
    search_type="mmr",               # ensures variety
    search_kwargs={"k": 4, "fetch_k": 10}
)

# 6. Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt_template}
)

# 7. Query function
async def run_rag_query(question: str) -> dict:
    print(f"⚡ Running RAG query: {question}")

    loop = asyncio.get_running_loop()

    try:
        result = await loop.run_in_executor(
            None, lambda: qa_chain.invoke({"query": question})
        )

        print(f"✅ RAG query result: {result}")

        # Extract clean answer
        answer = result.get("result", "No answer returned")

        # Extract sources (dedup + sorted)
        sources = sorted(set(
            doc.metadata.get("source", "Unknown")
            for doc in result.get("source_documents", [])
        ))

        return {
            "message": answer,
            "sources": sources
        }

    except Exception as e:
        print(f"❌ Error running RAG query: {e}")
        return {
            "message": "❌ Error processing your query",
            "sources": []
        }

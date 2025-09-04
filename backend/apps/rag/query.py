# apps/rag/query.py

import asyncio
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from apps.rag.config import VECTOR_DB_PATH, EMBEDDING_MODEL, OLLAMA_BASE_URL

# Constants
EMBEDDING_MODEL = EMBEDDING_MODEL
PERSIST_DIR = VECTOR_DB_PATH
OLLAMA_BASE_URL = OLLAMA_BASE_URL

# 1. Embeddings
embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

# 2. Vectorstore
vectorstore = Chroma(
    persist_directory=PERSIST_DIR,
    embedding_function=embedding
)

# 3. Ollama LLM
llm = OllamaLLM(model="mistral", base_url=OLLAMA_BASE_URL)

# 4. Prompt Template (strict instructions for accurate, friendly answers)
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

# 5. Retriever with MMR for diverse sources
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 3, "fetch_k": 6}
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
    """
    Run RAG pipeline and return human-friendly answer with clean citations.
    Automatically detects greetings and responds without pulling docs.
    """
    loop = asyncio.get_running_loop()
    try:
        # Handle common greetings separately
        greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
        if question.lower().strip() in greetings:
            return {
                "message": "Hello! I'm SamsuBot, your assistant for customer support and knowledge-base queries. How can I help you today?",
                "sources": []
            }

        # Run RAG query
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

        # Optional: clean extra whitespace
        answer = " ".join(answer.split())

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

# 8. Thin wrapper for synchronous calls
def ask_question(query: str):
    import asyncio
    return asyncio.run(run_rag_query(query))

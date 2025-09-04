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

# 4. Prompt Template (strict instruction to avoid hallucination)
prompt_template = PromptTemplate.from_template(
    "You are SamsuBot, a helpful assistant.\n\n"
    "Use ONLY the context provided below to answer the question.\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}\n\n"
    "Guidelines:\n"
    "- Provide a clear, concise, and friendly answer.\n"
    "- After each important fact, cite the source(s) in square brackets using the file name.\n"
    "- If multiple sources support the same fact, list them all together inside the brackets.\n"
    "- Do NOT add extra details beyond the context.\n"
    "- If the context does not contain the answer, reply exactly:\n"
    "  'I don't know based on the provided documents.'\n\n"
    "Answer in a natural, human-friendly way:"
)

# 5. Retriever with MMR for diverse sources
retriever = vectorstore.as_retriever(
    search_type="mmr",               # ensures variety
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
    print(f"⚡ Running RAG query: {question}")

    loop = asyncio.get_running_loop()

    try:
        result = await loop.run_in_executor(
            None, lambda: qa_chain.invoke({"query": question})
        )

        print(f"✅ RAG query result: {result}")

        # Extract clean answer
        answer = result.get("result", "No answer returned").strip()

        # Make citations cleaner (replace numbered refs with filenames)
        for doc in result.get("source_documents", []):
            src = doc.metadata.get("source", "Unknown")
            answer = answer.replace("[Context]", f"[{src}]")

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

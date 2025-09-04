# apps/rag/debug_vectordb.py
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from apps.rag.config import VECTOR_DB_PATH, EMBEDDING_MODEL

def debug_vectordb():
    print(f"🔍 Inspecting Chroma DB at: {VECTOR_DB_PATH}")

    # Reload embeddings and vector DB
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectordb = Chroma(
        persist_directory=VECTOR_DB_PATH,
        embedding_function=embeddings
    )

    # Get all documents
    results = vectordb.get()
    print(f"✅ Found {len(results['ids'])} entries in DB")

    for i, (doc_id, metadata, doc) in enumerate(
        zip(results["ids"], results["metadatas"], results["documents"])
    ):
        print(f"\n--- Doc #{i+1} ---")
        print(f"ID: {doc_id}")
        print(f"Source: {metadata.get('source', 'Unknown')}")
        print(f"Preview: {doc[:200]}...")  # first 200 chars

if __name__ == "__main__":
    debug_vectordb()

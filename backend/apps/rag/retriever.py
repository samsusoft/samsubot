# rag/retriever.py

from apps.rag.vector_store import load_vector_store

def retrieve_context(query: str, k=3):
    db = load_vector_store()
    results = db.similarity_search(query, k=k)
    context = "\n\n".join([doc.page_content for doc in results])
    return context

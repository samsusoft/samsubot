# apps/rag/vector_store.py

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient
from apps.rag.config import *

def load_vector_store():
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    client = QdrantClient(url=VECTOR_DB_URL)
    db = Qdrant(
        client=client,
        collection_name=QDRANT_COLLECTION,
        embeddings=embeddings
    )
    return db
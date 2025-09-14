# apps/rag/retriever.py
 # Vector store + retriever setup

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from apps.rag.config import VECTOR_DB_URL, EMBEDDING_MODEL, QDRANT_COLLECTION

embedding = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

def get_vectorstore():
    client = QdrantClient(url=VECTOR_DB_URL, timeout=10, prefer_grpc=True)

    if not client.collection_exists(QDRANT_COLLECTION):
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=rest.VectorParams(size=384, distance=rest.Distance.COSINE)
        )

    return QdrantVectorStore(
        client=client,
        collection_name=QDRANT_COLLECTION,
        embedding=embedding
    )

vectorstore = get_vectorstore()

retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 3, "search_params": {"hnsw_ef": 16, "exact": True}}
)

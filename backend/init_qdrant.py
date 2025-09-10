from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

client = QdrantClient(host="qdrant", port=6333)

client.recreate_collection(
    collection_name="samsubot_docs",
    vectors_config=rest.VectorParams(size=1536, distance=rest.Distance.COSINE),
)

print("✅ Qdrant collection 'samsubot_docs' created successfully")

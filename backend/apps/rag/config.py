# apps/rag/config.py

from pathlib import Path

# Where your raw documents live (mounted into the backend container)
DOCS_DIR = "apps/docs"

# Keep this model IDENTICAL in ingest.py and your query code.
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Qdrant configuration
VECTOR_DB_URL = "http://samsubot_qdrant:6333"
QDRANT_COLLECTION = "vectorstore"

# Docker container name of Ollama
OLLAMA_BASE_URL = "http://samsubot_llm:11434"

# Document chunking parameters
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

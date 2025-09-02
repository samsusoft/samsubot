# apps/rag/config.py

from pathlib import Path

# Where your raw documents live (mounted into the backend container)
DOCS_DIR = "apps/docs"

# Keep this model IDENTICAL in ingest.py and your query code.
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Where Chroma should persist the vector DB (mounted host directory)
VECTOR_DB_PATH = "apps/rag/chroma_db"

# Document chunking parameters
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

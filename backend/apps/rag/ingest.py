# apps/rag/ingest.py
"""Ingest documents into Chroma vector database"""

"""Ingest documents into Qdrant vector database"""

import argparse
import hashlib
import logging
import uuid
from pathlib import Path
from typing import List

from langchain_community.document_loaders import TextLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from apps.rag.config import DOCS_DIR, VECTOR_DB_URL, EMBEDDING_MODEL, QDRANT_COLLECTION

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("ingest")

# Initialize embeddings globally
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def load_all_docs(docs_dir: Path) -> List:
    """Load .txt and .md files from DOCS_DIR, normalize 'source' metadata."""
    docs = []
    for path in docs_dir.rglob("*"):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()

        try:
            if suffix == ".txt":
                loader = TextLoader(str(path), encoding="utf-8")
            elif suffix == ".md":
                loader = UnstructuredMarkdownLoader(str(path))
            else:
                continue  # skip unsupported files

            loaded = loader.load()

            rel = path.relative_to(docs_dir).as_posix()
            for d in loaded:
                d.metadata.clear()
                d.metadata["source"] = rel

            log.info(f"📄 Loaded file: {rel} → {len(loaded)} docs")
            docs.extend(loaded)

        except Exception as e:
            log.error(f"❌ Failed to load {path.name}: {e}")

    return docs


def split_docs(docs: List) -> List:
    """Chunk documents for better retrieval."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    per_file = {}
    for c in chunks:
        src = c.metadata.get("source", "unknown")
        per_file[src] = per_file.get(src, 0) + 1

    for src, count in per_file.items():
        log.info(f"✂️  {src} → {count} chunks")

    return chunks


def make_ids(chunks: List) -> List[str]:
    """Generate stable UUIDs from chunk content."""
    ids = []
    for d in chunks:
        raw = (d.page_content + "|" + d.metadata.get("source", "")).encode("utf-8")
        sha1 = hashlib.sha1(raw).hexdigest()
        ids.append(str(uuid.UUID(sha1[:32])))  # Convert to UUID format
    return ids


def main(rebuild: bool = False):
    Path(DOCS_DIR).mkdir(parents=True, exist_ok=True)

    # 1️⃣ Load and split documents
    log.info(f"📚 Loading documents from: {DOCS_DIR}")
    raw_docs = load_all_docs(Path(DOCS_DIR))
    if not raw_docs:
        log.warning("⚠️ No documents found. Add files to apps/docs and re-run.")
        return

    chunks = split_docs(raw_docs)
    ids = make_ids(chunks)

    # 2️⃣ Setup Qdrant client
    log.info(f"🧠 Connecting to Qdrant at: {VECTOR_DB_URL}")
    client = QdrantClient(url=VECTOR_DB_URL)

    if rebuild:
        if client.collection_exists(QDRANT_COLLECTION):
            client.delete_collection(QDRANT_COLLECTION)
            log.info(f"🗑️ Deleted existing collection: {QDRANT_COLLECTION}")

        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=rest.VectorParams(size=384, distance=rest.Distance.COSINE),
        )
        log.info(f"✅ Created new collection: {QDRANT_COLLECTION}")

    # 3️⃣ Upsert into Qdrant
    vectordb = QdrantVectorStore(
        client=client,
        collection_name=QDRANT_COLLECTION,
        embedding=embeddings,
    )

    vectordb.add_documents(chunks, ids=ids)
    log.info(f"🎉 Ingested {len(chunks)} chunks into Qdrant!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rebuild", action="store_true", help="Delete and rebuild the vector DB"
    )
    args = parser.parse_args()
    main(rebuild=args.rebuild)

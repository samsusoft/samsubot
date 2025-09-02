# apps/rag/ingest.py
"""Ingest documents into Chroma vector database"""

import argparse
import hashlib
import logging
from pathlib import Path
from typing import List
import shutil

from langchain_community.document_loaders import (
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from apps.rag.config import DOCS_DIR, VECTOR_DB_PATH, EMBEDDING_MODEL

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("ingest")


def load_all_docs(docs_dir: Path) -> List:
    """Load .txt and .md from DOCS_DIR, normalize 'source' metadata."""
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
                continue  # skip everything else

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
        chunk_size=800,
        chunk_overlap=120,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    # Count chunks per source
    per_file = {}
    for c in chunks:
        src = c.metadata.get("source", "unknown")
        per_file[src] = per_file.get(src, 0) + 1

    for src, count in per_file.items():
        log.info(f"✂️  {src} → {count} chunks")

    return chunks


def make_ids(chunks: List) -> List[str]:
    """Stable IDs so re-running only upserts changed content."""
    ids = []
    for d in chunks:
        raw = (d.page_content + "|" + d.metadata.get("source", "")).encode("utf-8")
        ids.append(hashlib.sha1(raw).hexdigest())
    return ids


def reset_vectorstore(path: str):
    """Delete the vector DB directory."""
    shutil.rmtree(path, ignore_errors=True)


def main(rebuild: bool = False):
    Path(DOCS_DIR).mkdir(parents=True, exist_ok=True)
    Path(VECTOR_DB_PATH).mkdir(parents=True, exist_ok=True)

    if rebuild:
        log.info(f"🧹 Rebuilding vector DB at {VECTOR_DB_PATH} …")
        reset_vectorstore(VECTOR_DB_PATH)

    log.info(f"📚 Loading documents from: {DOCS_DIR}")
    raw_docs = load_all_docs(Path(DOCS_DIR))
    if not raw_docs:
        log.warning("⚠️ No documents found. Add files to apps/docs and re-run.")
        return

    log.info(f"✂️ Splitting into chunks …")
    chunks = split_docs(raw_docs)
    ids = make_ids(chunks)
    log.info(f"✅ {len(raw_docs)} docs → {len(chunks)} chunks in total")

    log.info("🔢 Building embeddings …")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    log.info(f"🧠 Upserting into Chroma at: {VECTOR_DB_PATH}")
    vectordb = Chroma(
        persist_directory=VECTOR_DB_PATH,
        embedding_function=embeddings,
    )

    vectordb.add_documents(chunks, ids=ids)

    log.info("🎉 Ingestion complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rebuild", action="store_true", help="Delete and rebuild the vector DB"
    )
    args = parser.parse_args()
    main(rebuild=args.rebuild)

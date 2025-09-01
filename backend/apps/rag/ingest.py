# ingest.py

from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma  # Or use langchain_chroma if installed
from langchain_community.embeddings import HuggingFaceEmbeddings  # Or use langchain_huggingface

from apps.rag.config import *

def ingest(file_path: str):
    loader = TextLoader(file_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DB_PATH
    )
    db.persist()
    print(f"[✅] Ingested {len(chunks)} chunks from {file_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        ingest(sys.argv[1])
    else:
        print("Usage: python ingest.py <path_to_file>")

# rag/vector_store.py

#from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
#from langchain.vectorstores import Chroma
from langchain_community.vectorstores import Chroma
from apps.rag.config import *

def load_vector_store():
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    db = Chroma(
        persist_directory=VECTOR_DB_PATH,
        embedding_function=embeddings
    )
    return db

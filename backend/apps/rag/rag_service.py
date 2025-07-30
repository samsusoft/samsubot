# rag_service.py
from langchain_community.llms import Ollama  # or better: from langchain_ollama import OllamaLLM
from langchain_community.vectorstores import Chroma  # or better: from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceEmbeddings  # or better: from langchain_huggingface import HuggingFaceEmbeddings

# 1. Connect to Ollama Mistral
llm = Ollama(
    model="mistral",
    base_url="http://samsubot_llm:11434"  # Use container name or service name
)

# 2. Define embedding model (change if you need multilingual)
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 3. Load existing Chroma vector store
vectordb = Chroma(persist_directory="./chroma_db", embedding_function=embedding)

# 4. Build the QA chain (retriever + LLM)
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectordb.as_retriever())

def ask_question(query: str) -> str:
    """Runs RAG pipeline and returns the LLM response."""
    return qa_chain.run(query)
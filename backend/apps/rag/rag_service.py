# apps/rag/rag_service.py
#from langchain_community.llms import Ollama  # or better: from langchain_ollama import OllamaLLM
from langchain_ollama import OllamaLLM
from langchain_community.vectorstores import Chroma  # or better: from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceEmbeddings  # or better: from langchain_huggingface import HuggingFaceEmbeddings
from apps.rag.config import VECTOR_DB_PATH

# 1. Connect to Ollama Mistral
llm = OllamaLLM(
    model="mistral",
    base_url="http://samsubot_llm:11434"  # Use container name or service name
)

# 2. Define embedding model (change if you need multilingual)
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 3. Load existing Chroma vector store
vectordb = Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embedding)

# 4. Build the QA chain (retriever + LLM)
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectordb.as_retriever())

def ask_question(query: str) -> str:
    """Runs RAG pipeline and returns the LLM response."""
    print(f"Running RAG query: {query}")  # Debugging line temporary
    return qa_chain.invoke({"query": query})["result"]
    #return qa_chain.invoke({"query": query})
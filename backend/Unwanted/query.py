# query.py

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM  # ✅ New import
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.schema import HumanMessage
import asyncio
# Constants
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
PERSIST_DIR = "apps/rag/chroma_db"

# 1. Embeddings
embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

# 2. Vectorstore
vectorstore = Chroma(
    persist_directory=PERSIST_DIR,
    embedding_function=embedding
)

# 3. Ollama LLM
llm = OllamaLLM(model="mistral")  # ✅ Modernized usage

# 4. Prompt Template (optional but recommended for formatting)
prompt_template = PromptTemplate.from_template(
    "Use the following context to answer the question:\n\n{context}\n\nQuestion: {question}"
)

# 5. Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(),
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt_template}
)

# 6. Query function
async def run_rag_query(question: str) -> str:
    print(f"Running RAG query: {question}")

    loop = asyncio.get_running_loop()

    # Run the synchronous invoke in a thread pool
    result = await loop.run_in_executor(None,lambda: qa_chain.invoke({"query": question}))

    print(f"RAG query result: {result}")  # Debug print

    return result["result"]
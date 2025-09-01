from ingest import load_vector_store

def test_vector_store():
    db = load_vector_store()
    
    try:
        print("✅ Vector store loaded successfully.")
        print("📦 Number of vectors stored:", db._collection.count())
    except Exception as e:
        print("❌ Error while accessing vector store:", e)

if __name__ == "__main__":
    test_vector_store()
import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Load environment variables
load_dotenv(dotenv_path="e:/Antigravity Project/vibe_cording/.env")

DB_DIR = "e:/Antigravity Project/vibe_cording/data/chroma_db"

# Initialize singletons to avoid reloading the DB repeatedly
_embeddings = None
_db = None

def get_db():
    """Lazy loads the Chroma DB."""
    global _embeddings, _db
    if _db is None:
        # Initialize the HuggingFace Multilingual Embedding Model (100% Free, Local)
        _embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
        if os.path.exists(DB_DIR):
            _db = Chroma(persist_directory=DB_DIR, embedding_function=_embeddings)
        else:
            raise FileNotFoundError("Chroma DB not found. Please run rag_ingest.py first.")
    return _db

def query_knowledge_base(query: str, k: int = 3) -> str:
    """
    Searches the RAG database for the given query and returns the top k relevant text chunks.
    """
    try:
        db = get_db()
        results = db.similarity_search(query, k=k)
        
        if not results:
            return "No relevant knowledge found in the database."
            
        context_chunks = []
        for i, doc in enumerate(results):
            source = doc.metadata.get("source", "Unknown Source")
            page = doc.metadata.get("page", "Unknown Page")
            snippet = f"[Source: {os.path.basename(source)}, Page: {page}]\n{doc.page_content}"
            context_chunks.append(snippet)
            
        # Join the chunks into a single context string to inject into LLM prompts
        return "\n\n---\n\n".join(context_chunks)
        
    except Exception as e:
        return f"Error retrieving from knowledge base: {e}"

if __name__ == "__main__":
    # Test query when run directly
    test_query = "ComfyUI 인페인트 방법"
    print(f"Testing Query: '{test_query}'\n")
    print(query_knowledge_base(test_query))

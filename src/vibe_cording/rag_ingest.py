import os
import glob
import time
from dotenv import load_dotenv
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Load environment variables
load_dotenv(dotenv_path="e:/Antigravity Project/vibe_cording/.env")

# Ensure API keys exist
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

# Directories
KNOWLEDGE_DIR = "e:/Antigravity Project/vibe_cording/knowledge"
DB_DIR = "e:/Antigravity Project/vibe_cording/data/chroma_db"

def ingest_pdf(file_path, db):
    """Parses a PDF, chunks the text, and stores it in the Chroma DB."""
    print(f"[{time.strftime('%X')}] Processing: {os.path.basename(file_path)}")
    try:
        loader = PDFPlumberLoader(file_path)
        documents = loader.load()
        
        # We split the massive PDFs into manageable chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_documents(documents)
        print(f"  -> Extracted {len(chunks)} chunks.")
        
        if not chunks:
            print("  -> No text found (could be an image-only PDF).")
            return

        # Add chunks to DB in batches to prevent API rate limiting
        batch_size = 50
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            db.add_documents(batch)
            print(f"  -> Embedded and stored chunks {i} to {i+len(batch)}...")
            time.sleep(2)  # Respect Gemini Free API rate limits
            
        print(f"[{time.strftime('%X')}] Successfully ingested: {os.path.basename(file_path)}")
        
    except Exception as e:
        print(f"  -> Error processing {file_path}: {e}")

def main():
    print("Initializing RAG Ingestion Pipeline...")
    
    # Initialize the HuggingFace Multilingual Embedding Model (100% Free, Local)
    embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
    
    # Initialize or load Chroma DB
    db = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    
    # Find all PDFs in the knowledge directory
    pdf_files = glob.glob(os.path.join(KNOWLEDGE_DIR, "**", "*.pdf"), recursive=True)
    
    if not pdf_files:
        print("No PDF files found in the knowledge directory.")
        return
        
    print(f"Found {len(pdf_files)} PDF files to process.")
    
    # For full processing, process all PDF files
    # pdf_files = [f for f in pdf_files if "HOWTO_TEMPLATE" in f]
    
    for pdf in pdf_files:
        ingest_pdf(pdf, db)
        
    print("RAG Ingestion Complete. Data is safely stored in Chroma DB.")

if __name__ == "__main__":
    main()

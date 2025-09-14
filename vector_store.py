import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from config import EMBEDDING_MODEL_NAME, EMBEDDING_DEVICE, FAISS_INDEX_PATH
import data_loader

def get_embedding_model():
    """Initializes and returns the sentence transformer embedding model."""
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={'device': EMBEDDING_DEVICE}
    )

def create_and_save_vector_store():
    """
    The main ingestion pipeline.
    1. Loads documents from the knowledge base.
    2. Splits them into chunks.
    3. Generates embeddings for each chunk.
    4. Creates a FAISS vector store.
    5. Saves the vector store locally.
    """
    print("--- Starting Ingestion Process ---")
    
    documents = data_loader.load_documents()
    if not documents:
        print("No documents found. Aborting ingestion.")
        return
        
    texts = data_loader.split_documents(documents)
    
    print(f"Initializing embedding model: {EMBEDDING_MODEL_NAME}")
    embeddings = get_embedding_model()
    
    print("Creating FAISS vector store... (This may take a while for large document sets)")
    try:
        vector_store = FAISS.from_documents(texts, embeddings)
        
        print(f"Saving FAISS index to: {FAISS_INDEX_PATH}")
        # Ensure the directory exists before saving
        if not os.path.exists(FAISS_INDEX_PATH):
            os.makedirs(FAISS_INDEX_PATH)
        vector_store.save_local(FAISS_INDEX_PATH)
        
        print("--- Ingestion Complete ---")
    except Exception as e:
        print(f"An error occurred during vector store creation: {e}")

def load_vector_store():
    """
    Loads an existing FAISS vector store from the local file system.

    Returns:
        FAISS: The loaded vector store object, or None if it fails.
    """
    if not os.path.exists(FAISS_INDEX_PATH):
        print(f"Error: FAISS index not found at '{FAISS_INDEX_PATH}'.")
        print("Please run the ingestion process first with `python main.py ingest`")
        return None

    print("Loading the vector store...")
    try:
        embeddings = get_embedding_model()
        # The `allow_dangerous_deserialization` is required for loading FAISS indexes
        # created with different environments. It's safe in this context.
        vector_store = FAISS.load_local(
            FAISS_INDEX_PATH, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        print("Vector store loaded successfully.")
        return vector_store
    except Exception as e:
        print(f"Failed to load vector store: {e}")
        return None

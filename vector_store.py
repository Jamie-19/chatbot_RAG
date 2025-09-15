import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from config.settings import get_settings
import data_loader

def get_embedding_model():
    """Initializes and returns the sentence transformer embedding model."""
    settings = get_settings()
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model_name,
        model_kwargs={'device': settings.embedding_device}
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
    
    settings = get_settings()
    print(f"Initializing embedding model: {settings.embedding_model_name}")
    embeddings = get_embedding_model()
    
    print("Creating FAISS vector store... (This may take a while for large document sets)")
    try:
        vector_store = FAISS.from_documents(texts, embeddings)
        
        settings = get_settings()
        print(f"Saving FAISS index to: {settings.faiss_index_path}")
        os.makedirs(settings.faiss_index_path, exist_ok=True)
        vector_store.save_local(settings.faiss_index_path)
        
        print("--- Ingestion Complete ---")
    except Exception as e:
        print(f"An error occurred during vector store creation: {e}")

def load_vector_store():
    """
    Loads an existing FAISS vector store from the local file system.

    Returns:
        FAISS: The loaded vector store object, or None if it fails.
    """
    settings = get_settings()
    if not os.path.exists(settings.faiss_index_path):
        print(f"Error: FAISS index not found at '{settings.faiss_index_path}'.")
        print("Please run the ingestion process first with `python main.py ingest`")
        return None

    print("Loading the vector store...")
    try:
        embeddings = get_embedding_model()
        vector_store = FAISS.load_local(
            settings.faiss_index_path, 
            embeddings,
            allow_dangerous_deserialization=True
        )
        print("Vector store loaded successfully.")
        return vector_store
    except Exception as e:
        print(f"Failed to load vector store: {e}")
        return None
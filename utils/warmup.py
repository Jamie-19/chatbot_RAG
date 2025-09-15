"""
Warmup utilities for faster startup.
"""
import asyncio
import logging
from typing import Optional, Tuple
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from utils.logging_config import get_logger

logger = get_logger(__name__)

def warmup_ollama_connection() -> Optional[Ollama]:
    """Warm up Ollama connection and return the LLM instance."""
    try:
        from rag_pipeline import get_ollama_llm
        llm = get_ollama_llm()
        if llm:
            llm.invoke("test")
            logger.info("Ollama connection warmed up successfully")
            return llm
    except Exception as e:
        logger.warning(f"Failed to warm up Ollama connection: {e}")
    return None

def warmup_vector_store() -> Optional[FAISS]:
    """Warm up vector store and return the instance."""
    try:
        from vector_store import load_vector_store
        vector_store = load_vector_store()
        if vector_store:
            vector_store.similarity_search("test", k=1)
            logger.info("Vector store warmed up successfully")
            return vector_store
    except Exception as e:
        logger.warning(f"Failed to warm up vector store: {e}")
    return None

def warmup_system() -> Tuple[Optional[FAISS], Optional[Ollama]]:
    """Warm up the entire system and return the instances."""
    logger.info("Starting system warmup...")
    
    vector_store = warmup_vector_store()
    llm = warmup_ollama_connection()
    
    if vector_store and llm:
        logger.info("System warmup completed successfully")
    else:
        logger.warning("System warmup completed with some failures")
    
    return vector_store, llm

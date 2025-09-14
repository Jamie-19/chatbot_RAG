# --- Path Configurations ---
KNOWLEDGE_BASE_DIR = "knowledge_base"
FAISS_INDEX_PATH = "faiss_index"

# --- Embedding Model Configurations ---
# Using a CPU-friendly model from SentenceTransformers
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DEVICE = "cpu"  # Explicitly set to CPU

# --- Text Splitting Configurations ---
# Defines how documents are chunked
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# --- Retriever Configurations ---
# Number of relevant document chunks to retrieve for context
SEARCH_K = 3

# --- Ollama LLM Configurations ---
# The name of the model to use from Ollama
# Ensure you have pulled this model with `ollama pull <model_name>`
OLLAMA_MODEL_NAME = "mistral"

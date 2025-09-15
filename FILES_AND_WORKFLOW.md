# Chatbot RAG – Files, Connections, and Workflow

This document explains what every key file does, how modules depend on one another, and how the system boots up in both CLI and Web modes.

## 1) Entry Points and Top-Level Flow

- `main.py`
  - CLI entry with actions: `ingest`, `chat`, `health`, `web`.
  - Dispatches to:
    - `handle_ingest()` → builds FAISS index
    - `handle_chat()` → interactive terminal chat (RAG)
    - `handle_health()` → print health/metrics summary
    - `handle_web()` → starts FastAPI + WebSocket server (serves React app)

- `web/backend/main.py`
  - FastAPI application with a WebSocket endpoint `/chat`.
  - On startup: loads vector store, creates a single RAG chain instance, stores it in `app.state`.
  - WebSocket handler streams the RAG response back to the browser.

- `web/frontend/`
  - React single page app that connects to WebSocket `/chat`, sends user queries, renders streamed responses.

## 2) Core RAG Modules

- `data_loader.py`
  - `load_documents(directory)`: loads `.pdf`/`.txt` from the knowledge base.
  - `split_documents(documents)`: splits into overlapping chunks using `RecursiveCharacterTextSplitter`.
  - Depends on `config.settings.get_settings()` for `knowledge_base_dir`, `chunk_size`, `chunk_overlap`.

- `vector_store.py`
  - `get_embedding_model()`: creates SentenceTransformers embeddings (CPU-friendly).
  - `create_and_save_vector_store()`: pipelines load → split → embed → FAISS build → save.
  - `load_vector_store()`: loads FAISS index from disk with the same embeddings.
  - Depends on `data_loader.py` and `config.settings.get_settings()` (for paths and model/device).

- `rag_pipeline.py`
  - `get_ollama_llm()`: returns the Ollama LLM client using configured model name and service URL.
  - `create_rag_chain(vector_store)`: constructs a LangChain graph:
    - `vector_store.as_retriever(k=settings.search_k)`
    - Prompt template combining `Context` and `Question`
    - LLM call
    - Output parsed to string
  - Depends on `config.settings.get_settings()` and `langchain_community.llms.Ollama`.

## 3) Utilities and Support

- `config/settings.py`
  - Centralized configuration with Pydantic Settings (environment-driven).
  - Typical fields: paths (`knowledge_base_dir`, `faiss_index_path`), splitting (`chunk_size`, `chunk_overlap`), retrieval (`search_k`), LLM (`ollama_model_name`, `ollama_base_url`, `ollama_timeout`).
  - Use: `from config.settings import get_settings` → `settings = get_settings()`

- `utils/logging_config.py`
  - `setup_logging(log_level, log_file)`: structured console/file logging with rotation.
  - `get_logger(__name__)`: module logger factory.

- `utils/monitoring.py`
  - In-memory metrics (totals, success rate, average response time, CPU/memory usage, error counts).
  - `get_health_status()` summarizes system health for `main.py health`.

- `utils/cache.py` (optional use)
  - Lightweight in-memory cache helpers for responses or function results.

- `utils/performance.py` and `utils/warmup.py` (optional)
  - Helpers for performance monitoring and pre-warming.

## 4) Web Layer (Backend + Frontend)

### Backend – `web/backend/main.py`
- Startup sequence:
  1. `load_vector_store()`
  2. `create_rag_chain(vector_store)`
  3. Save the chain into `app.state.rag_chain`
- WebSocket `/chat` flow:
  1. Accept connection and send a small greeting message
  2. Wait for text queries from the client
  3. For each query, iterate `rag_chain.astream(query)` and send chunks back immediately
  4. Handle disconnects and errors gracefully
- Serves static React `build/` at `/` using `StaticFiles`.

### Frontend – `web/frontend/`
- `src/App.js`:
  - Opens a WebSocket to `ws://<host>/chat`.
  - On submit: send user message, render bot stream (accumulate chunks).
  - Minimal UI with basic CSS in `src/App.css`.
- Build output resides in `web/frontend/build/` (ignored by Git).

## 5) How the Workflows Start

### A) Ingestion (CLI)
1. `python main.py ingest`
2. `main.py` → `handle_ingest()`
3. `vector_store.create_and_save_vector_store()`
   - `data_loader.load_documents()`
   - `data_loader.split_documents()`
   - `get_embedding_model()`
   - `FAISS.from_documents(...)` → save to `faiss_index/`

### B) CLI Chat
1. `python main.py chat`
2. `main.py` → `handle_chat()`
3. `vector_store.load_vector_store()`
4. `rag_pipeline.create_rag_chain(...)`
5. Read user input → `rag_chain.invoke(question)` → print answer

### C) Web Chat
1. `python main.py web`
2. `main.py` → `handle_web()` → start Uvicorn/ASGI server
3. `web/backend/main.py` startup loads vector store and creates `rag_chain`
4. Browser loads React app → opens WebSocket `/chat`
5. Browser sends user messages → backend streams responses via `rag_chain.astream()`

## 6) File-by-File Responsibility Map

- `main.py` – CLI dispatcher; orchestrates ingestion, chat loop, health, and web server start.
- `data_loader.py` – IO + deterministic splitting; no model/LLM knowledge here.
- `vector_store.py` – Embedding model management + FAISS persistence and loading.
- `rag_pipeline.py` – LLM client creation + RAG chain definition (retriever + prompt + LLM).
- `config/settings.py` – Single source of truth for configuration; encourages environment-based config.
- `utils/logging_config.py` – Standardized logs for consistent troubleshooting.
- `utils/monitoring.py` – Centralized metrics/health view used by CLI `health`.
- `web/backend/main.py` – ASGI app; initializes chain once, exposes streaming chat.
- `web/frontend/src/App.js` – Simple WebSocket client for chat, appends streamed chunks.

## 7) Data Flow (End-to-End)

1. Documents → `data_loader` → chunked texts
2. Chunked texts + embeddings → `FAISS` index → saved to `faiss_index/`
3. Query → retriever → top-K chunks → prompt → LLM (Ollama) → final string
4. CLI: prints answer; Web: streams to client over WebSocket

## 8) Error Handling and Diagnostics
- Logging
  - Each major step logs INFO/ERROR and warnings.
- Health Check
  - `python main.py health` prints status, uptime, averages, CPU/memory.
- Common Issues
  - Vector index missing → run ingest.
  - Ollama not running → start the service and confirm model is pulled.
  - WebSocket problems → ensure `uvicorn[standard]` (or `websockets`) installed.

## 9) Extensibility Pointers
- Swap embeddings: modify `get_embedding_model()` in `vector_store.py`.
- Change prompt/behavior: update `create_rag_chain()` in `rag_pipeline.py`.
- Adjust retrieval: tune `search_k` in settings.
- Add middlewares/caching: utilize `utils/cache.py` or LangChain retriever/LLM wrappers.

---
This documentation complements `ARCHITECTURE.md`. Start here to understand file responsibilities and cross-module wiring; consult the architecture doc for deeper context, performance tips, and troubleshooting.

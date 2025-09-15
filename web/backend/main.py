
import asyncio
import logging
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
import sys

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from rag_pipeline import create_rag_chain
from vector_store import load_vector_store
from utils.logging_config import setup_logging, get_logger
from langchain.schema.runnable import Runnable

# Setup logging
setup_logging()
logger = get_logger(__name__)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Load the RAG pipeline on startup."""
    logger.info("Loading vector store and RAG chain...")
    try:
        vector_store = load_vector_store()
        if vector_store:
            app.state.rag_chain = create_rag_chain(vector_store)
            logger.info("RAG chain loaded successfully.")
        else:
            logger.error("Failed to load vector store. The chatbot will not be available.")
    except Exception as e:
        logger.exception(f"Error during startup: {e}")
        logger.error("Chatbot initialization failed due to an unexpected error.")

async def get_rag_chain() -> Runnable:
    """Dependency that provides the RAG chain."""
    if not hasattr(app.state, "rag_chain") or app.state.rag_chain is None:
        raise HTTPException(status_code=503, detail="Chatbot is not initialized.")
    return app.state.rag_chain


@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections for the chat, maintaining conversation history."""
    await websocket.accept()
    logger.info("WebSocket connection accepted.")
    
    rag_chain = getattr(app.state, "rag_chain", None)
    if not rag_chain:
        error_msg = "Error: Chatbot not initialized. Please check server logs."
        await websocket.send_text(error_msg)
        await websocket.close()
        logger.error("Closing WebSocket due to uninitialized RAG chain.")
        return

    # In-memory chat history for the duration of the connection
    chat_history = []

    await websocket.send_text("Ready to answer your questions!")
        
    try:
        while True:
            try:
                data = await websocket.receive_text()
                logger.info(f"Received query: {data}")

                # Format chat history into a string
                formatted_history = "\n".join([f"{speaker}: {message}" for speaker, message in chat_history])

                # Stream the response
                response_buffer = ""
                logger.info("Starting RAG chain astream with history...")
                async for chunk in rag_chain.astream({
                    "question": data,
                    "chat_history": formatted_history
                }):
                    response_buffer += chunk
                    await websocket.send_text(chunk)
                
                logger.info(f"Finished RAG chain astream. Full response: {response_buffer}")

                # Update chat history
                chat_history.append(("User", data))
                chat_history.append(("BOT", response_buffer))
                
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected gracefully.")
                break
            except Exception as e:
                logger.error(f"Error during chat loop: {e}", exc_info=True)
                await websocket.send_text("An error occurred while processing your message. Please try again.")
                continue

    except Exception as e:
        logger.error(f"An unexpected error occurred in the WebSocket endpoint: {e}", exc_info=True)
    finally:
        logger.info("Closing WebSocket connection.")



# Mount the React app
app.mount("/", StaticFiles(directory=Path(__file__).parent.parent / "frontend" / "build", html=True), name="static")

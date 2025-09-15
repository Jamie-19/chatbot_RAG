import argparse
import sys
import time
from typing import Optional

import vector_store as vs
import rag_pipeline as rag
from config.settings import get_settings
from utils.logging_config import setup_logging, get_logger
from utils.validation import validate_query, ValidationError
from utils.monitoring import get_metrics_collector
from utils.cache import cache_query_response, get_cached_response
from utils.warmup import warmup_system
from utils.performance import performance_monitor

def handle_ingest():
    """Handles the document ingestion process."""
    logger = get_logger(__name__)
    logger.info("Starting document ingestion process")
    
    try:
        vs.create_and_save_vector_store()
        logger.info("Document ingestion completed successfully")
    except Exception as e:
        logger.error(f"Document ingestion failed: {e}")
        raise

def handle_chat():
    """Handles the interactive chat session."""
    logger = get_logger(__name__)
    settings = get_settings()
    metrics = get_metrics_collector()
    
    logger.info("Starting chat session")
    
    # Warm up the system for optimal performance
    vector_store_instance, llm = warmup_system()
    
    if not vector_store_instance:
        logger.error("Failed to load vector store")
        return

    rag_chain = rag.create_rag_chain(vector_store_instance, llm=llm)
    if not rag_chain:
        logger.error("Failed to create RAG chain")
        return

    print("\n---")
    print("Chatbot is ready! Type 'exit' or 'quit' to end the session.")
    print("---")
    
    chat_history = []

    while True:
        try:
            query = input("> ")
            if query.lower() in ["exit", "quit"]:
                print("Exiting chatbot. Goodbye!")
                logger.info("Chat session ended by user")
                break

            if not query.strip():
                continue

            # Validate input
            try:
                validated_query = validate_query(query)
            except ValidationError as e:
                print(f"\nError: {e}")
                logger.warning(f"Invalid query rejected: {query[:50]}...")
                continue

            print("\nThinking...")
            start_time = time.time()
            
            try:
                # Check cache first
                # Note: Caching with history requires a more complex key.
                # For now, we bypass cache if history is present.
                history_key = "\n".join([f"{turn['role']}: {turn['content']}" for turn in chat_history])
                cached_response = get_cached_response(f"{history_key}\nUser: {validated_query}")

                if cached_response:
                    response_time = time.time() - start_time
                    print("\nBot:", cached_response)
                    print("-" * 50)
                    print("(Response from cache)")
                    
                    metrics.record_request(success=True, response_time=response_time)
                    logger.info(f"Query processed from cache in {response_time:.2f}s")
                    
                    # Update history from cached response
                    chat_history.append({"role": "user", "content": validated_query})
                    chat_history.append({"role": "assistant", "content": cached_response})
                else:
                    # Prepare history for the chain
                    history_str = "\n".join([f"{turn['role']}: {turn['content']}" for turn in chat_history])

                    # Get and print the response from the chain
                    @performance_monitor
                    def invoke_chain(inputs):
                        return rag_chain.invoke(inputs)
                    
                    response = invoke_chain({
                        "question": validated_query,
                        "chat_history": history_str
                    })
                    response_time = time.time() - start_time
                    
                    print("\nBot:", response)
                    print("-" * 50)
                    
                    # Update history
                    chat_history.append({"role": "user", "content": validated_query})
                    chat_history.append({"role": "assistant", "content": response})
                    
                    # Cache the new response
                    cache_key = f"{history_key}\nUser: {validated_query}"
                    cache_query_response(cache_key, response)
                    
                    # Record successful request
                    metrics.record_request(success=True, response_time=response_time)
                    logger.info(f"Query processed successfully in {response_time:.2f}s")
                    
                    # Performance feedback
                    if response_time > 10:
                        logger.warning(f"Slow response detected: {response_time:.2f}s")
                    elif response_time < 2:
                        logger.info(f"Fast response: {response_time:.2f}s")
                
            except Exception as e:
                response_time = time.time() - start_time
                metrics.record_request(success=False, response_time=response_time, error_type=type(e).__name__)
                logger.error(f"Error processing query: {e}")
                print(f"\nAn error occurred while processing your query: {e}")

        except KeyboardInterrupt:
            print("\nExiting chatbot. Goodbye!")
            logger.info("Chat session ended by keyboard interrupt")
            break
        except Exception as e:
            logger.error(f"Unexpected error in chat loop: {e}")
            print(f"\nAn unexpected error occurred: {e}")
            break

def handle_web():
    """Handles the web server."""
    import uvicorn
    uvicorn.run("web.backend.main:app", host="0.0.0.0", port=8000, reload=False, ws="websockets")

def main():
    """
    Main function to parse command-line arguments and run the application.
    """
    # Parse arguments first to get debug mode
    parser = argparse.ArgumentParser(
        description="A Production-Ready RAG Chatbot.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "action", 
        choices=["ingest", "chat", "health", "web"],
        help="""Action to perform:
'ingest' - Process documents in the knowledge base and create a vector store.
'chat'   - Start an interactive chat session with the RAG chatbot.
'health' - Check system health and metrics.
'web'    - Start the web interface."""
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        help="Specify log file path"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    settings = get_settings()
    log_level = "DEBUG" if args.debug else "INFO"
    log_file = args.log_file or settings.log_file
    
    setup_logging(log_level=log_level, log_file=log_file)
    logger = get_logger(__name__)
    
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {args.debug}")
    
    try:
        if args.action == 'ingest':
            handle_ingest()
        elif args.action == 'chat':
            handle_chat()
        elif args.action == 'health':
            handle_health()
        elif args.action == 'web':
            handle_web()
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

def handle_health():
    """Handle health check command."""
    logger = get_logger(__name__)
    metrics = get_metrics_collector()
    
    try:
        health_status = metrics.get_health_status()
        print(f"Health Status: {health_status['status']}")
        print(f"Uptime: {health_status['uptime_seconds']:.2f} seconds")
        print(f"Total Requests: {health_status['total_requests']}")
        print(f"Success Rate: {health_status['success_rate']:.2f}%")
        print(f"Average Response Time: {health_status['average_response_time']:.2f}s")
        print(f"Memory Usage: {health_status['memory_usage_mb']:.2f} MB")
        print(f"CPU Usage: {health_status['cpu_usage_percent']:.2f}%")
        
        if health_status['error_counts']:
            print("Recent Errors:")
            for error_type, count in health_status['error_counts'].items():
                print(f"  {error_type}: {count}")
        
        logger.info("Health check completed")
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        print(f"Health check failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

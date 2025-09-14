import argparse
import vector_store as vs
import rag_pipeline as rag

def handle_ingest():
    """Handles the document ingestion process."""
    vs.create_and_save_vector_store()

def handle_chat():
    """Handles the interactive chat session."""
    vector_store_instance = vs.load_vector_store()
    if not vector_store_instance:
        # Error message is printed in the load_vector_store function
        return

    rag_chain = rag.create_rag_chain(vector_store_instance)
    if not rag_chain:
        # Error message is printed in the create_rag_chain function
        return

    print("\n---")
    print("Chatbot is ready! Type 'exit' or 'quit' to end the session.")
    print("---")
    
    while True:
        try:
            query = input("> ")
            if query.lower() in ["exit", "quit"]:
                print("Exiting chatbot. Goodbye!")
                break

            if not query.strip():
                continue

            print("\nThinking...")
            
            # Get and print the response from the chain
            response = rag_chain.invoke(query)
            print("\nBot:", response)
            print("-" * 50)

        except KeyboardInterrupt:
            print("\nExiting chatbot. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            break

def main():
    """
    Main function to parse command-line arguments and run the application.
    """
    parser = argparse.ArgumentParser(
        description="A CPU-Only RAG Chatbot.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "action", 
        choices=["ingest", "chat"],
        help="""Action to perform:
'ingest' - Process documents in the knowledge base and create a vector store.
'chat'   - Start an interactive chat session with the RAG chatbot."""
    )
    
    args = parser.parse_args()

    if args.action == 'ingest':
        handle_ingest()
    elif args.action == 'chat':
        handle_chat()

if __name__ == "__main__":
    main()

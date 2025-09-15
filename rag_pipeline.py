from typing import Optional
from operator import itemgetter
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import Runnable, RunnablePassthrough, RunnableLambda
from langchain.schema.output_parser import StrOutputParser
from langchain_community.vectorstores import FAISS
import re

from config.settings import get_settings
from utils.performance import performance_monitor
from utils.logging_config import get_logger

logger = get_logger(__name__)

def get_ollama_llm():
    """
    Initializes and returns the Ollama LLM instance.
    Tests the connection to ensure the Ollama service is running.
    """
    settings = get_settings()
    try:
        llm = Ollama(
            model=settings.ollama_model_name,
            temperature=0.4,  # Optimal for TinyDolphin
            num_predict=200,  # Limit response length
            top_p=0.9,
            repeat_penalty=1.1
        )
        # Simple test to check if the LLM is responsive
        test_response = llm.invoke("Hi")
        logger.info(f"Successfully connected to Ollama with model: {settings.ollama_model_name}")
        logger.info(f"Test response: {test_response[:50]}...")
        return llm
    except Exception as e:
        logger.error(f"Error connecting to Ollama: {e}")
        print(f"\nError connecting to Ollama: {e}")
        print("Please make sure the Ollama application is running and you have pulled the model.")
        print(f"You can pull the model with: `ollama pull {settings.ollama_model_name}`")
        return None

def classify_query_type(question: str) -> dict:
    """Classify the type of user input for better response handling"""
    question_lower = question.lower().strip()
    
    greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'how are you']
    thanks = ['thank', 'thanks', 'appreciate', 'grateful']
    
    is_greeting = any(greet in question_lower for greet in greetings)
    is_thanks = any(thank in question_lower for thank in thanks)
    has_question = '?' in question or any(word in question_lower for word in ['what', 'how', 'why', 'when', 'where', 'who', 'can you', 'could you', 'tell me', 'explain'])
    
    return {
        'is_greeting': is_greeting,
        'is_thanks': is_thanks,
        'has_question': has_question,
        'is_social': is_greeting or is_thanks
    }

def optimize_context_for_tinydolphin(docs, max_chars=1000) -> str:
    """
    Optimize context length and quality for TinyDolphin model
    
    Args:
        docs: Retrieved documents
        max_chars: Maximum character limit for context
    """
    if not docs:
        return "No relevant information available."
    
    # Combine and prioritize most relevant content
    combined_content = ""
    char_count = 0
    
    for doc in docs:
        content = doc.page_content.strip()
        # Clean up content - remove excessive whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r'\s+', ' ', content)
        
        # Add content if it fits within limit
        if char_count + len(content) <= max_chars:
            combined_content += content + "\n\n"
            char_count += len(content)
        else:
            # Add partial content if possible
            remaining_chars = max_chars - char_count
            if remaining_chars > 150:  # Only add if meaningful amount
                # Try to cut at sentence boundary
                partial = content[:remaining_chars]
                last_period = partial.rfind('.')
                if last_period > remaining_chars * 0.7:  # If we can cut at a reasonable sentence
                    partial = partial[:last_period + 1]
                else:
                    partial = partial + "..."
                combined_content += partial
            break
    
    return combined_content.strip()

@performance_monitor
def create_rag_chain(vector_store: FAISS, llm: Optional[Ollama] = None) -> Optional[Runnable]:
    """
    Creates an enhanced RAG pipeline optimized for TinyDolphin with improved prompting and context handling.
    This version incorporates chat history for conversational context.
    """
    if not llm:
        llm = get_ollama_llm()
        if not llm:
            return None
        
    settings = get_settings()
    retriever = vector_store.as_retriever(search_kwargs={'k': settings.search_k})

    # Template with chat history support
    enhanced_template = """You are a friendly AI assistant named Dolphin.

Current conversation:
{chat_history}

Context for the user's question:
{context}

Rules:
• Use the 'Current conversation' to understand the flow of the dialogue.
• Use the 'Context' to answer the user's specific question.
• If the user ask for short explanation explain in 2 to 3 sentences.
• For greetings like "hi", "hello": respond warmly without using context.
• If no relevant information in context: say "I don't have information about that topic."
• Be natural and conversational.
• Keep responses clear and focused.

User: {question}
Dolphin:"""

    def log_retrieved_docs(docs):
        """Enhanced logging with relevance info"""
        logger.info(f"Retrieved {len(docs)} documents for processing")
        for i, doc in enumerate(docs):
            content_preview = doc.page_content[:100].replace('\n', ' ')
            source = getattr(doc, 'metadata', {}).get('source', 'Unknown')
            logger.debug(f"Doc {i+1} [{source}]: {content_preview}...")
        return docs

    def smart_context_processing(docs):
        """Intelligent context processing based on query type and TinyDolphin optimization"""
        # Log retrieved documents
        docs = log_retrieved_docs(docs)
        
        # Optimize context for TinyDolphin
        optimized_context = optimize_context_for_tinydolphin(docs)
        
        return optimized_context

    def enhanced_question_processing(question: str) -> str:
        """Process the question and add metadata for better responses"""
        query_info = classify_query_type(question)
        
        # Log query classification
        logger.debug(f"Query classification: {query_info}")
        
        return question

    prompt = PromptTemplate(
        template=enhanced_template,
        input_variables=["chat_history", "context", "question"]
    )

    # RAG chain with chat history
    rag_chain = (
        {
            "context": itemgetter("question") | retriever | smart_context_processing,
            "question": itemgetter("question"),
            "chat_history": itemgetter("chat_history")
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def create_streamlined_rag_chain(vector_store: FAISS, llm: Optional[Ollama] = None) -> Optional[Runnable]:
    """
    Creates a more streamlined RAG chain for maximum efficiency with TinyDolphin.
    Use this version if the enhanced version is too complex.
    """
    if not llm:
        llm = get_ollama_llm()
        if not llm:
            return None
        
    settings = get_settings()
    retriever = vector_store.as_retriever(search_kwargs={'k': min(settings.search_k, 3)})  # Limit to 3 docs max

    # Ultra-streamlined template
    streamlined_template = """You are Dolphin. Be friendly and helpful.

Context:
{context}

Guidelines:
- Warm greetings for social interaction
- Answer using context only
- No context = "I don't have that information"
- Conversational tone, direct responses

Q: {question}
A:"""

    def minimal_context_processing(docs):
        """Minimal context processing for maximum efficiency"""
        if not docs:
            return "No information available."
        
        # Simple concatenation with basic optimization
        context_parts = []
        total_chars = 0
        
        for doc in docs:
            content = doc.page_content.strip()[:400]  # Limit each doc to 400 chars
            if total_chars + len(content) < 800:  # Total limit 800 chars
                context_parts.append(content)
                total_chars += len(content)
            else:
                break
        
        return "\n\n".join(context_parts)

    prompt = PromptTemplate(
        template=streamlined_template,
        input_variables=["context", "question"]
    )

    # Streamlined RAG chain
    rag_chain = (
        {
            "context": itemgetter("question") | retriever | minimal_context_processing,
            "question": itemgetter("question")
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain

def test_rag_chain(rag_chain: Runnable):
    """Test the RAG chain with various query types"""
    test_queries = [
        "Hello! How are you today?",
        "What is the main policy?",
        "Can you explain the process?",
        "Thank you for your help!",
        "I don't understand this concept"
    ]
    
    logger.info("Testing RAG chain with sample queries...")
    for query in test_queries:
        try:
            response = rag_chain.invoke({"question": query})
            logger.info(f"Q: {query}")
            logger.info(f"A: {response[:100]}...")
            print(f"\nUser: {query}")
            print(f"Dolphin: {response}")
        except Exception as e:
            logger.error(f"Error with query '{query}': {e}")

# Usage example and recommendations
"""
Usage Examples:

# For most use cases (recommended):
rag_chain = create_rag_chain(vector_store, llm)

# For maximum efficiency with limited resources:
streamlined_chain = create_streamlined_rag_chain(vector_store, llm)

# Test the chain:
test_rag_chain(rag_chain)

# In your main application:
response = rag_chain.invoke({"question": "Your question here"})
"""
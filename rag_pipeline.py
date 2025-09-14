from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain_community.vectorstores import FAISS

from config import OLLAMA_MODEL_NAME, SEARCH_K

def get_ollama_llm():
    """
    Initializes and returns the Ollama LLM instance.
    Tests the connection to ensure the Ollama service is running.
    """
    try:
        llm = Ollama(model=OLLAMA_MODEL_NAME)
        # Simple test to check if the LLM is responsive
        llm.invoke("Hi")
        print(f"Successfully connected to Ollama with model: {OLLAMA_MODEL_NAME}")
        return llm
    except Exception as e:
        print(f"\nError connecting to Ollama: {e}")
        print("Please make sure the Ollama application is running and you have pulled the model.")
        print(f"You can pull the model with: `ollama pull {OLLAMA_MODEL_NAME}`")
        return None

def create_rag_chain(vector_store: FAISS):
    """
    Creates and returns a RAG (Retrieval-Augmented Generation) chain.

    Args:
        vector_store (FAISS): The vector store to be used for document retrieval.

    Returns:
        A LangChain runnable object representing the RAG chain, or None on failure.
    """
    llm = get_ollama_llm()
    if not llm:
        return None
        
    retriever = vector_store.as_retriever(search_kwargs={'k': SEARCH_K})

    # This template structures the input to the LLM, providing the retrieved
    # context along with the user's question.
    template = """
Answer the question based only on the following context.
If you don't know the answer, just say that you don't know.

Context:
{context}

Question:
{question}
"""
    prompt = PromptTemplate(template=template, input_variables=["context", "question"])

    # This chain defines the RAG workflow:
    # 1. The user's question is passed to the retriever.
    # 2. The retriever finds relevant documents and passes them as 'context'.
    # 3. The 'context' and 'question' are formatted by the prompt.
    # 4. The formatted prompt is sent to the LLM for a response.
    # 5. The output is parsed into a string.
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

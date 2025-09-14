import os
import glob
from tqdm import tqdm
from typing import List

from langchain.docstore.document import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from config import CHUNK_SIZE, CHUNK_OVERLAP, KNOWLEDGE_BASE_DIR

def load_documents(directory: str = KNOWLEDGE_BASE_DIR) -> List[Document]:
    """
    Loads all supported documents (.pdf, .txt) from the specified directory.
    
    Args:
        directory (str): The path to the directory containing documents.

    Returns:
        List[Document]: A list of loaded document objects.
    """
    documents = []
    file_paths = glob.glob(os.path.join(directory, "*.pdf")) + glob.glob(os.path.join(directory, "*.txt"))
    
    if not file_paths:
        print(f"No .pdf or .txt files found in '{directory}'. Please add your knowledge base files.")
        return []

    print(f"Found {len(file_paths)} documents to ingest.")

    for file_path in tqdm(file_paths, desc="Loading Documents"):
        try:
            if file_path.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            elif file_path.endswith(".txt"):
                loader = TextLoader(file_path)
            else:
                continue # Skip unsupported file types
            documents.extend(loader.load())
        except Exception as e:
            print(f"Error loading document {file_path}: {e}")
            
    return documents

def split_documents(documents: List[Document]) -> List[Document]:
    """
    Splits the loaded documents into smaller chunks.

    Args:
        documents (List[Document]): A list of documents to be split.

    Returns:
        List[Document]: A list of smaller document chunks.
    """
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    texts = text_splitter.split_documents(documents)
    print(f"Created {len(texts)} text chunks.")
    return texts

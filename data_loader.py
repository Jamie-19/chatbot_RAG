import glob
from pathlib import Path
from tqdm import tqdm
from typing import List
from config.settings import get_settings

from langchain.docstore.document import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


def load_documents() -> List[Document]:
    """
    Loads all supported documents (.pdf, .txt) from the knowledge base directory.

    Returns:
        List[Document]: A list of loaded document objects.
    """
    settings = get_settings()
    knowledge_base_path = Path(settings.knowledge_base_dir)
    file_paths = glob.glob(str(knowledge_base_path / "*.pdf")) + glob.glob(str(knowledge_base_path / "*.txt"))
    
    if not file_paths:
        print(f"No .pdf or .txt files found in '{settings.knowledge_base_dir}'. Please add your knowledge base files.")
        return []

    print(f"Found {len(file_paths)} documents to ingest.")

    documents = []
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
    settings = get_settings()
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)
    texts = text_splitter.split_documents(documents)
    print(f"Created {len(texts)} text chunks.")
    return texts
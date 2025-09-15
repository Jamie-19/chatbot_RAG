"""
Pytest configuration and fixtures.
"""
import pytest
import tempfile
import os
from pathlib import Path

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture
def sample_documents(temp_dir):
    """Create sample documents for testing."""
    # Create knowledge base directory
    kb_dir = temp_dir / "knowledge_base"
    kb_dir.mkdir()
    
    # Create sample text file
    sample_file = kb_dir / "sample.txt"
    sample_file.write_text("""
    Company Policy Document
    
    This is a sample company policy document for testing purposes.
    It contains information about vacation policies, work from home guidelines,
    and other important company information.
    
    Vacation Policy:
    - 20 paid vacation days per year
    - Accrued monthly
    - Can roll over up to 5 days
    
    Work From Home:
    - Hybrid model
    - Office days: Tuesday and Thursday
    - Remote days: Monday, Wednesday, Friday
    """)
    
    return kb_dir

@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    return {
        "chunk_size": 100,
        "chunk_overlap": 20,
        "search_k": 2,
        "embedding_model_name": "all-MiniLM-L6-v2",
        "embedding_device": "cpu",
        "ollama_model_name": "mistral",
        "ollama_base_url": "http://localhost:11434",
        "ollama_timeout": 30,
        "max_retries": 3,
        "max_query_length": 1000,
        "min_query_length": 2
    }

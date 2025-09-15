"""
Production-ready configuration management for the RAG chatbot.
"""
import os
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from pathlib import Path

# Define the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    """Application settings with validation."""
    
    # Application
    app_name: str
    app_version: str
    debug: bool
    
    # Paths
    knowledge_base_dir: str
    faiss_index_path: str
    log_file: Optional[str]
    
    # Embedding Model
    embedding_model_name: str
    embedding_device: str
    
    # Text Processing
    chunk_size: int = Field(ge=100, le=2000)
    chunk_overlap: int = Field(ge=0, le=200)
    
    # Retrieval
    search_k: int = Field(ge=1, le=10)
    
    # LLM Configuration
    ollama_model_name: str
    ollama_base_url: str
    ollama_timeout: int = Field(ge=5, le=300)
    max_retries: int = Field(ge=1, le=10)
    
    # Security
    max_query_length: int = Field(ge=10, le=5000)
    min_query_length: int = Field(ge=1, le=10)
    
    # Performance
    enable_caching: bool
    cache_ttl: int = Field(ge=60, le=86400)
    max_concurrent_requests: int = Field(ge=1, le=50)
    
    # Monitoring
    enable_metrics: bool
    metrics_port: int = Field(ge=1000, le=65535)
    health_check_interval: int = Field(ge=5, le=300)
    
    @field_validator('knowledge_base_dir', 'faiss_index_path', 'log_file')
    @classmethod
    def make_paths_absolute(cls, v: str) -> str:
        """Constructs absolute paths from the project root."""
        if v and not Path(v).is_absolute():
            # PROJECT_ROOT is defined at the module level
            absolute_path = PROJECT_ROOT / v
            # For log file, ensure parent directory exists
            if 'log' in v:
                absolute_path.parent.mkdir(parents=True, exist_ok=True)
            return str(absolute_path)
        return v

    @field_validator('chunk_overlap')
    @classmethod
    def validate_chunk_overlap(cls, v, info):
        """Ensure chunk overlap is less than chunk size."""
        if 'chunk_size' in info.data and v >= info.data['chunk_size']:
            raise ValueError("chunk_overlap must be less than chunk_size")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings."""
    return settings

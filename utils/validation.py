"""
Input validation utilities for the RAG chatbot.
"""
import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

def validate_query(query: str) -> str:
    """
    Validates and sanitizes user input query.
    
    Args:
        query (str): Raw user input
        
    Returns:
        str: Sanitized query
        
    Raises:
        ValidationError: If query is invalid
    """
    if not query:
        raise ValidationError("Query cannot be empty")
    
    # Remove leading/trailing whitespace
    query = query.strip()
    
    if not query:
        raise ValidationError("Query cannot be empty or only whitespace")
    
    # Check length limits
    if len(query) > 2000:
        raise ValidationError("Query too long. Maximum 2000 characters allowed.")
    
    if len(query) < 2:
        raise ValidationError("Query too short. Minimum 2 characters required.")
    
    # Check for potentially malicious patterns
    dangerous_patterns = [
        r'<script.*?>.*?</script>',  # Script tags
        r'javascript:',              # JavaScript URLs
        r'data:text/html',           # Data URLs
        r'vbscript:',                # VBScript
        r'on\w+\s*=',                # Event handlers
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            logger.warning(f"Potentially malicious input detected: {query[:50]}...")
            raise ValidationError("Query contains potentially unsafe content")
    
    # Remove excessive whitespace
    query = re.sub(r'\s+', ' ', query)
    
    return query

def validate_file_path(file_path: str) -> str:
    """
    Validates file path for security.
    
    Args:
        file_path (str): File path to validate
        
    Returns:
        str: Validated file path
        
    Raises:
        ValidationError: If path is invalid
    """
    if not file_path:
        raise ValidationError("File path cannot be empty")
    
    # Check for path traversal attempts
    if '..' in file_path or file_path.startswith('/'):
        raise ValidationError("Invalid file path")
    
    # Check for allowed extensions
    allowed_extensions = ['.txt', '.pdf']
    if not any(file_path.lower().endswith(ext) for ext in allowed_extensions):
        raise ValidationError("Only .txt and .pdf files are allowed")
    
    return file_path
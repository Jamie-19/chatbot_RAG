"""
Retry utilities with exponential backoff for production reliability.
"""
import time
import random
from typing import Callable, Any, Optional, Type, Tuple
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class RetryError(Exception):
    """Exception raised when all retry attempts are exhausted."""
    pass

def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter to prevent thundering herd
        exceptions: Tuple of exceptions to catch and retry on
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
                        raise RetryError(f"Function {func.__name__} failed after {max_attempts} attempts") from e
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    
                    # Add jitter to prevent thundering herd
                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            raise RetryError(f"Function {func.__name__} failed after {max_attempts} attempts") from last_exception
        
        return wrapper
    return decorator

def retry_ollama_connection(func: Callable) -> Callable:
    """
    Specialized retry decorator for Ollama connections.
    """
    return retry_with_backoff(
        max_attempts=5,
        base_delay=2.0,
        max_delay=30.0,
        exponential_base=2.0,
        jitter=True,
        exceptions=(ConnectionError, TimeoutError, Exception)
    )(func)

def retry_vector_store_operation(func: Callable) -> Callable:
    """
    Specialized retry decorator for vector store operations.
    """
    return retry_with_backoff(
        max_attempts=3,
        base_delay=1.0,
        max_delay=10.0,
        exponential_base=1.5,
        jitter=True,
        exceptions=(OSError, IOError, Exception)
    )(func)

"""
Performance optimization utilities.
"""
import asyncio
import time
from typing import Any, Callable, Optional
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def performance_monitor(func: Callable) -> Callable:
    """Decorator to monitor function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if execution_time > 5:
                logger.warning(f"Slow function {func.__name__}: {execution_time:.2f}s")
            elif execution_time < 1:
                logger.debug(f"Fast function {func.__name__}: {execution_time:.2f}s")
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Function {func.__name__} failed after {execution_time:.2f}s: {e}")
            raise
    
    return wrapper

class PerformanceOptimizer:
    """Performance optimization utilities."""
    
    @staticmethod
    def optimize_chunk_size(doc_count: int) -> int:
        """Optimize chunk size based on document count."""
        if doc_count < 10:
            return 200
        elif doc_count < 50:
            return 300
        else:
            return 400
    
    @staticmethod
    def optimize_search_k(doc_count: int) -> int:
        """Optimize search_k based on document count."""
        if doc_count < 10:
            return 2
        elif doc_count < 50:
            return 3
        else:
            return 4
    
    @staticmethod
    def should_use_cache(query: str) -> bool:
        """Determine if query should use cache."""
        # Cache short, common queries
        return len(query) < 50 and any(word in query.lower() for word in 
            ['what', 'how', 'when', 'where', 'who', 'company', 'policy', 'vacation', 'work'])

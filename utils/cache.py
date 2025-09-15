"""
Caching utilities for improved performance.
"""
import time
import hashlib
import json
from typing import Any, Optional, Dict
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class SimpleCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, default_ttl: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        if time.time() > entry['expires_at']:
            del self.cache[key]
            return None
        
        logger.debug(f"Cache hit for key: {key[:20]}...")
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        ttl = ttl or self.default_ttl
        self.cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl
        }
        logger.debug(f"Cache set for key: {key[:20]}...")
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def size(self) -> int:
        """Get number of cache entries."""
        return len(self.cache)

# Global cache instance
cache = SimpleCache()

def cached(ttl: int = 3600, key_func: Optional[callable] = None):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time to live in seconds
        key_func: Custom key generation function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_data = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator

def cache_query_response(query: str, response: str, ttl: int = 1800) -> None:
    """Cache a query response."""
    cache_key = f"query:{hashlib.md5(query.encode()).hexdigest()}"
    cache.set(cache_key, response, ttl)

def get_cached_response(query: str) -> Optional[str]:
    """Get cached response for a query."""
    cache_key = f"query:{hashlib.md5(query.encode()).hexdigest()}"
    return cache.get(cache_key)

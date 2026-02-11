"""Centralized error handling and logging"""
import logging
from functools import wraps
from typing import Any, Callable

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RetrievalError(Exception):
    """Raised when document retrieval fails"""
    pass

class EmbeddingError(Exception):
    """Raised when embedding generation fails"""
    pass

class LLMError(Exception):
    """Raised when LLM call fails"""
    pass

def safe_execute(func: Callable, fallback: Any = None) -> Callable:
    """Decorator for safe function execution with fallback"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"{func.__name__} failed: {str(e)}")
            return fallback if fallback is not None else {}
    return wrapper

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Retry decorator with exponential backoff"""
    import time
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"{func.__name__} failed after {max_retries} attempts: {e}")
                        raise
                    logger.warning(f"{func.__name__} attempt {attempt+1} failed: {e}. Retrying...")
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
            return None
        return wrapper
    return decorator
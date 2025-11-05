"""
Caching System
==============

Result caching for improved performance.
"""

import hashlib
import json
import pickle
from pathlib import Path
from typing import Any, Optional, Callable
import functools
import time
import logging

logger = logging.getLogger(__name__)


class Cache:
    """File-based cache for analysis results."""

    def __init__(self, cache_dir: str = "./.cache", max_age_hours: int = 24):
        """
        Initialize cache.

        Args:
            cache_dir: Directory for cache files
            max_age_hours: Maximum age for cached items
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_age_hours = max_age_hours
        self.enabled = True

        logger.info(f"Initialized cache at {cache_dir}")

    def _get_cache_key(self, *args, **kwargs) -> str:
        """
        Generate cache key from arguments.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Cache key (hex string)
        """
        # Create deterministic string from args
        key_data = {
            'args': str(args),
            'kwargs': sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True)

        # Hash to create key
        key_hash = hashlib.sha256(key_str.encode()).hexdigest()
        return key_hash

    def _get_cache_path(self, key: str) -> Path:
        """Get path to cache file."""
        return self.cache_dir / f"{key}.pkl"

    def get(self, key: str) -> Optional[Any]:
        """
        Get cached value.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if not self.enabled:
            return None

        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        try:
            # Check age
            age_hours = (time.time() - cache_path.stat().st_mtime) / 3600
            if age_hours > self.max_age_hours:
                logger.debug(f"Cache expired for key {key}")
                cache_path.unlink()
                return None

            # Load cached value
            with open(cache_path, 'rb') as f:
                value = pickle.load(f)

            logger.debug(f"Cache hit for key {key}")
            return value

        except Exception as e:
            logger.error(f"Error reading cache for key {key}: {str(e)}")
            return None

    def set(self, key: str, value: Any):
        """
        Set cached value.

        Args:
            key: Cache key
            value: Value to cache
        """
        if not self.enabled:
            return

        cache_path = self._get_cache_path(key)

        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)

            logger.debug(f"Cached value for key {key}")

        except Exception as e:
            logger.error(f"Error writing cache for key {key}: {str(e)}")

    def clear(self):
        """Clear all cached values."""
        try:
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()

            logger.info("Cleared cache")

        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")

    def cleanup_old(self):
        """Remove expired cache entries."""
        try:
            removed = 0
            current_time = time.time()

            for cache_file in self.cache_dir.glob("*.pkl"):
                age_hours = (current_time - cache_file.stat().st_mtime) / 3600
                if age_hours > self.max_age_hours:
                    cache_file.unlink()
                    removed += 1

            if removed > 0:
                logger.info(f"Removed {removed} expired cache entries")

        except Exception as e:
            logger.error(f"Error cleaning up cache: {str(e)}")

    def enable(self):
        """Enable caching."""
        self.enabled = True
        logger.info("Enabled caching")

    def disable(self):
        """Disable caching."""
        self.enabled = False
        logger.info("Disabled caching")


def cached(cache_instance: Cache, key_func: Optional[Callable] = None):
    """
    Decorator to cache function results.

    Args:
        cache_instance: Cache instance to use
        key_func: Optional function to generate cache key from args

    Example:
        @cached(my_cache)
        def expensive_function(x, y):
            return x + y
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = cache_instance._get_cache_key(func.__name__, *args, **kwargs)

            # Try to get from cache
            cached_value = cache_instance.get(key)
            if cached_value is not None:
                return cached_value

            # Compute value
            result = func(*args, **kwargs)

            # Store in cache
            cache_instance.set(key, result)

            return result

        return wrapper
    return decorator


# Global cache instance
_global_cache: Optional[Cache] = None


def get_cache() -> Cache:
    """Get global cache instance."""
    global _global_cache

    if _global_cache is None:
        _global_cache = Cache()

    return _global_cache

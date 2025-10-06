"""Helper utilities for caching, rate limiting, and retry logic."""

import time
import logging
from typing import Any, Callable, Dict, Optional, TypeVar
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CacheManager:
    """Simple in-memory cache with TTL support."""

    def __init__(self) -> None:
        """Initialize the cache manager."""
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if expired/not found
        """
        if key in self._cache:
            entry = self._cache[key]
            if datetime.now() < entry["expires"]:
                logger.debug(f"Cache hit for key: {key}")
                return entry["value"]
            else:
                logger.debug(f"Cache expired for key: {key}")
                del self._cache[key]

        logger.debug(f"Cache miss for key: {key}")
        return None

    def set(self, key: str, value: Any, ttl: int = 60) -> None:
        """
        Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        self._cache[key] = {
            "value": value,
            "expires": datetime.now() + timedelta(seconds=ttl)
        }
        logger.debug(f"Cached key: {key} (TTL: {ttl}s)")

    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()
        logger.debug("Cache cleared")

    def cleanup(self) -> None:
        """Remove expired entries from cache."""
        now = datetime.now()
        expired_keys = [k for k, v in self._cache.items() if now >= v["expires"]]
        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")


class RateLimiter:
    """Rate limiter for API calls with configurable limits."""

    def __init__(self, calls_per_second: float) -> None:
        """
        Initialize rate limiter.

        Args:
            calls_per_second: Maximum number of calls per second
        """
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second if calls_per_second > 0 else 0
        self.last_call = 0.0

    def wait(self) -> None:
        """Wait if necessary to respect rate limit."""
        if self.min_interval > 0:
            elapsed = time.time() - self.last_call
            if elapsed < self.min_interval:
                sleep_time = self.min_interval - elapsed
                logger.debug(f"Rate limiting: sleeping {sleep_time:.3f}s")
                time.sleep(sleep_time)

        self.last_call = time.time()


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    exponential: bool = True
) -> Callable:
    """
    Decorator for retrying function calls with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential: Use exponential backoff if True, constant delay if False

    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        if exponential:
                            delay = min(base_delay * (2 ** attempt), max_delay)
                        else:
                            delay = base_delay

                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_attempts}): {str(e)}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {str(e)}"
                        )

            # If we get here, all attempts failed
            raise last_exception  # type: ignore

        return wrapper
    return decorator


def format_usd(value: float) -> str:
    """
    Format value as USD string.

    Args:
        value: Numeric value

    Returns:
        Formatted USD string
    """
    return f"${value:,.2f}"


def format_percentage(value: float) -> str:
    """
    Format value as percentage string.

    Args:
        value: Numeric value (0.15 = 15%)

    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.2f}%"


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculate percentage change between two values.

    Args:
        old_value: Original value
        new_value: New value

    Returns:
        Percentage change (0.15 = 15% increase)
    """
    if old_value == 0:
        return 0.0
    return (new_value - old_value) / old_value


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.

    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero

    Returns:
        Result of division or default
    """
    return numerator / denominator if denominator != 0 else default

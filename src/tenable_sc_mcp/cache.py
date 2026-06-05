"""Caching layer for Tenable.sc MCP Server.

Provides multi-tier caching with in-memory and Redis backends to reduce
token usage and improve performance.
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Optional


@dataclass
class CacheMetrics:
    """Cache performance metrics."""

    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    invalidations: int = 0
    start_time: float = field(default_factory=time.time)

    @property
    def total_requests(self) -> int:
        """Total cache requests (hits + misses)."""
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        """Cache hit rate as percentage."""
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests

    @property
    def miss_rate(self) -> float:
        """Cache miss rate as percentage."""
        return 1.0 - self.hit_rate

    @property
    def uptime_seconds(self) -> float:
        """Cache uptime in seconds."""
        return time.time() - self.start_time

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "sets": self.sets,
            "deletes": self.deletes,
            "invalidations": self.invalidations,
            "total_requests": self.total_requests,
            "hit_rate": f"{self.hit_rate:.1%}",
            "miss_rate": f"{self.miss_rate:.1%}",
            "uptime_hours": f"{self.uptime_seconds / 3600:.2f}",
        }


@dataclass
class CacheEntry:
    """Cache entry with data and expiration."""

    data: Any
    expires_at: float

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return time.time() > self.expires_at


class CacheBackend(ABC):
    """Abstract base class for cache backends."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Set value in cache with TTL."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        pass

    @abstractmethod
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries."""
        pass

    @abstractmethod
    def key_count(self) -> int:
        """Get total number of keys."""
        pass


class InMemoryCache(CacheBackend):
    """Thread-safe in-memory cache with TTL support.

    Uses Python dict with threading.RLock for thread safety.
    Suitable for single-instance deployments or development.
    """

    def __init__(self) -> None:
        """Initialize in-memory cache."""
        self._cache: dict[str, CacheEntry] = {}
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None

            if entry.is_expired():
                del self._cache[key]
                return None

            return entry.data

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time-to-live in seconds
        """
        with self._lock:
            expires_at = time.time() + ttl_seconds
            self._cache[key] = CacheEntry(data=value, expires_at=expires_at)

    def delete(self, key: str) -> bool:
        """Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if key was deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern.

        Args:
            pattern: Pattern to match (simple substring match)

        Returns:
            Number of keys deleted
        """
        with self._lock:
            keys_to_delete = [k for k in self._cache if pattern in k]
            for key in keys_to_delete:
                del self._cache[key]
            return len(keys_to_delete)

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()

    def key_count(self) -> int:
        """Get total number of keys."""
        with self._lock:
            return len(self._cache)

    def cleanup_expired(self) -> int:
        """Remove expired entries.

        Returns:
            Number of entries removed
        """
        with self._lock:
            keys_to_delete = [k for k, v in self._cache.items() if v.is_expired()]
            for key in keys_to_delete:
                del self._cache[key]
            return len(keys_to_delete)


class RedisCache(CacheBackend):
    """Redis-backed cache with persistence and distributed support.

    Suitable for production deployments and multi-instance setups.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        key_prefix: str = "tsc:",
    ) -> None:
        """Initialize Redis cache.

        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password (optional)
            key_prefix: Prefix for all keys (default: "tsc:")
        """
        try:
            import redis
        except ImportError as e:
            raise ImportError("redis package required for RedisCache. Install with: pip install redis") from e

        self.key_prefix = key_prefix
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=False,  # We handle JSON serialization
            socket_connect_timeout=5,
            socket_timeout=5,
        )

        # Test connection
        try:
            self.client.ping()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Redis at {host}:{port}: {e}") from e

    def _make_key(self, key: str) -> str:
        """Add prefix to key."""
        return f"{self.key_prefix}{key}"

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        try:
            value = self.client.get(self._make_key(key))
            if value is None:
                return None
            return json.loads(value.decode("utf-8"))
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache (must be JSON-serializable)
            ttl_seconds: Time-to-live in seconds
        """
        try:
            serialized = json.dumps(value).encode("utf-8")
            self.client.setex(self._make_key(key), ttl_seconds, serialized)
        except Exception:
            pass  # Fail silently on cache set errors

    def delete(self, key: str) -> bool:
        """Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if key was deleted, False if not found
        """
        try:
            return bool(self.client.delete(self._make_key(key)))
        except Exception:
            return False

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern.

        Args:
            pattern: Pattern to match (Redis pattern syntax)

        Returns:
            Number of keys deleted
        """
        try:
            pattern_with_prefix = f"{self.key_prefix}*{pattern}*"
            keys = list(self.client.scan_iter(match=pattern_with_prefix, count=100))
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception:
            return 0

    def clear(self) -> None:
        """Clear all cache entries with our prefix."""
        try:
            keys = list(self.client.scan_iter(match=f"{self.key_prefix}*", count=100))
            if keys:
                self.client.delete(*keys)
        except Exception:
            pass

    def key_count(self) -> int:
        """Get total number of keys with our prefix."""
        try:
            return len(list(self.client.scan_iter(match=f"{self.key_prefix}*", count=100)))
        except Exception:
            return 0


class Cache:
    """Main cache interface with metrics tracking.

    Wraps a cache backend and tracks metrics for monitoring.
    """

    def __init__(self, backend: CacheBackend) -> None:
        """Initialize cache with backend.

        Args:
            backend: Cache backend (InMemoryCache or RedisCache)
        """
        self.backend = backend
        self.metrics = CacheMetrics()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        value = self.backend.get(key)
        if value is not None:
            self.metrics.hits += 1
        else:
            self.metrics.misses += 1
        return value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time-to-live in seconds
        """
        self.backend.set(key, value, ttl_seconds)
        self.metrics.sets += 1

    def delete(self, key: str) -> bool:
        """Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted
        """
        deleted = self.backend.delete(key)
        if deleted:
            self.metrics.deletes += 1
        return deleted

    def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern.

        Args:
            pattern: Pattern to match

        Returns:
            Number of keys deleted
        """
        count = self.backend.delete_pattern(pattern)
        self.metrics.deletes += count
        self.metrics.invalidations += 1
        return count

    def clear(self) -> None:
        """Clear all cache entries."""
        self.backend.clear()
        self.metrics.invalidations += 1

    def key_count(self) -> int:
        """Get total number of keys."""
        return self.backend.key_count()


# TTL configuration for different resource types
DEFAULT_TTL_SECONDS = {
    # Static data (24 hours)
    "catalog": 86400,
    "plugin": 86400,
    "pluginFamily": 86400,
    # Semi-static data (30 minutes)
    "repository": 1800,
    "scanPolicy": 1800,
    "credential": 1800,
    "alert": 1800,
    "user": 1800,
    "group": 1800,
    # Dynamic data (5 minutes)
    "asset": 300,
    "assetTemplate": 300,
    "query": 300,
    # Real-time data (1 minute)
    "scan": 60,
    "scanResult": 60,
    "analysis": 60,
}


def generate_cache_key(
    resource: str,
    object_id: Optional[str] = None,
    params: Optional[dict[str, Any]] = None,
    fields: Optional[list[str]] = None,
) -> str:
    """Generate deterministic cache key.

    Args:
        resource: Resource name (e.g., "repository", "scan")
        object_id: Object ID (optional)
        params: Query parameters (optional)
        fields: Field selection (optional)

    Returns:
        Cache key string

    Examples:
        >>> generate_cache_key("repository")
        'repository'
        >>> generate_cache_key("repository", object_id="5")
        'repository:5'
        >>> generate_cache_key("scan", object_id="10", fields=["id", "name"])
        'scan:10:fields=id,name'
    """
    parts = [resource]

    if object_id:
        parts.append(str(object_id))

    if fields:
        parts.append(f"fields={','.join(sorted(fields))}")

    if params:
        # Hash params for deterministic key
        param_str = json.dumps(params, sort_keys=True)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
        parts.append(f"params={param_hash}")

    return ":".join(parts)


def get_ttl_for_resource(resource: str, default: int = 300) -> int:
    """Get TTL for resource type.

    Args:
        resource: Resource name
        default: Default TTL if not configured (5 minutes)

    Returns:
        TTL in seconds
    """
    return DEFAULT_TTL_SECONDS.get(resource, default)


# Global cache instance (initialized by server)
_cache: Optional[Cache] = None


def get_cache() -> Cache:
    """Get global cache instance.

    Returns:
        Global cache instance

    Raises:
        RuntimeError: If cache not initialized
    """
    if _cache is None:
        raise RuntimeError("Cache not initialized. Call initialize_cache() first.")
    return _cache


def initialize_cache(backend: CacheBackend) -> Cache:
    """Initialize global cache instance.

    Args:
        backend: Cache backend to use

    Returns:
        Initialized cache instance
    """
    global _cache
    _cache = Cache(backend)
    return _cache

"""Tests for cache module."""

import time
from tenable_sc_mcp.cache import (
    InMemoryCache,
    Cache,
    CacheMetrics,
    generate_cache_key,
    get_ttl_for_resource,
    get_ttl_for_analysis,
    _normalize_query_for_cache,
    DEFAULT_TTL_SECONDS,
)


def test_cache_metrics_initialization():
    """Test that cache metrics initialize correctly."""
    metrics = CacheMetrics()
    assert metrics.hits == 0
    assert metrics.misses == 0
    assert metrics.total_requests == 0
    assert metrics.hit_rate == 0.0


def test_cache_metrics_hit_rate():
    """Test cache hit rate calculation."""
    metrics = CacheMetrics()
    metrics.hits = 7
    metrics.misses = 3
    assert metrics.total_requests == 10
    assert metrics.hit_rate == 0.7
    assert abs(metrics.miss_rate - 0.3) < 0.0001  # Handle floating point precision


def test_inmemory_cache_set_and_get():
    """Test setting and getting values from in-memory cache."""
    cache = InMemoryCache()
    cache.set("key1", {"data": "value1"}, ttl_seconds=60)
    
    value = cache.get("key1")
    assert value == {"data": "value1"}


def test_inmemory_cache_expiry():
    """Test that cache entries expire after TTL."""
    cache = InMemoryCache()
    cache.set("key1", "value1", ttl_seconds=1)
    
    # Should exist immediately
    assert cache.get("key1") == "value1"
    
    # Wait for expiry
    time.sleep(1.1)
    
    # Should be expired
    assert cache.get("key1") is None


def test_inmemory_cache_delete():
    """Test deleting keys from cache."""
    cache = InMemoryCache()
    cache.set("key1", "value1", ttl_seconds=60)
    
    assert cache.get("key1") == "value1"
    
    deleted = cache.delete("key1")
    assert deleted is True
    assert cache.get("key1") is None
    
    # Delete non-existent key
    deleted = cache.delete("key2")
    assert deleted is False


def test_inmemory_cache_delete_pattern():
    """Test deleting keys by pattern."""
    cache = InMemoryCache()
    cache.set("scan:1", "data1", ttl_seconds=60)
    cache.set("scan:2", "data2", ttl_seconds=60)
    cache.set("asset:1", "data3", ttl_seconds=60)
    
    # Delete all scan keys
    deleted = cache.delete_pattern("scan")
    assert deleted == 2
    
    # Scan keys should be gone
    assert cache.get("scan:1") is None
    assert cache.get("scan:2") is None
    
    # Asset key should still exist
    assert cache.get("asset:1") == "data3"


def test_inmemory_cache_clear():
    """Test clearing all cache entries."""
    cache = InMemoryCache()
    cache.set("key1", "value1", ttl_seconds=60)
    cache.set("key2", "value2", ttl_seconds=60)
    
    cache.clear()
    
    assert cache.get("key1") is None
    assert cache.get("key2") is None
    assert cache.key_count() == 0


def test_inmemory_cache_key_count():
    """Test getting key count."""
    cache = InMemoryCache()
    assert cache.key_count() == 0
    
    cache.set("key1", "value1", ttl_seconds=60)
    cache.set("key2", "value2", ttl_seconds=60)
    assert cache.key_count() == 2


def test_inmemory_cache_cleanup_expired():
    """Test cleanup of expired entries."""
    cache = InMemoryCache()
    cache.set("key1", "value1", ttl_seconds=1)
    cache.set("key2", "value2", ttl_seconds=60)
    
    time.sleep(1.1)
    
    deleted = cache.cleanup_expired()
    assert deleted == 1
    assert cache.get("key1") is None
    assert cache.get("key2") == "value2"


def test_cache_wrapper_tracks_metrics():
    """Test that Cache wrapper tracks hits and misses."""
    backend = InMemoryCache()
    cache = Cache(backend)
    
    cache.set("key1", "value1", ttl_seconds=60)
    
    # Miss (first get before set was tested above)
    assert cache.metrics.misses == 0
    
    # Hit
    value = cache.get("key1")
    assert value == "value1"
    assert cache.metrics.hits == 1
    
    # Miss
    value = cache.get("key2")
    assert value is None
    assert cache.metrics.misses == 1
    
    assert cache.metrics.total_requests == 2
    assert cache.metrics.hit_rate == 0.5


def test_generate_cache_key_simple():
    """Test generating simple cache keys."""
    key = generate_cache_key("repository")
    assert key == "repository"


def test_generate_cache_key_with_object_id():
    """Test generating cache keys with object ID."""
    key = generate_cache_key("repository", object_id="5")
    assert key == "repository:5"


def test_generate_cache_key_with_fields():
    """Test generating cache keys with field selection."""
    key = generate_cache_key("scan", object_id="10", fields=["id", "name"])
    assert key == "scan:10:fields=id,name"


def test_generate_cache_key_with_params():
    """Test generating cache keys with parameters (hashed)."""
    key1 = generate_cache_key("analysis", params={"type": "vuln", "filters": []})
    key2 = generate_cache_key("analysis", params={"type": "vuln", "filters": []})
    key3 = generate_cache_key("analysis", params={"type": "asset", "filters": []})
    
    # Same params should generate same key
    assert key1 == key2
    
    # Different params should generate different key
    assert key1 != key3
    
    # Key should contain params hash
    assert "params=" in key1


def test_get_ttl_for_resource():
    """Test getting TTL for different resource types."""
    # Static resources (24 hours)
    assert get_ttl_for_resource("catalog") == 86400
    assert get_ttl_for_resource("plugin") == 86400
    
    # Semi-static resources (30 minutes)
    assert get_ttl_for_resource("repository") == 1800
    assert get_ttl_for_resource("scanPolicy") == 1800
    
    # Dynamic resources (10 minutes) - updated for better cache hit rate
    assert get_ttl_for_resource("asset") == 600
    
    # Real-time resources (1-5 minutes)
    assert get_ttl_for_resource("scan") == 60
    assert get_ttl_for_resource("scanResult") == 300  # Historical results - 5 minutes
    
    # Unknown resource uses default
    assert get_ttl_for_resource("unknown") == 300
    assert get_ttl_for_resource("unknown", default=120) == 120


def test_get_ttl_for_analysis():
    """Test smart TTL for analysis queries based on query type."""
    # IP/asset inventory queries - 5 minutes
    assert get_ttl_for_analysis({"tool": "sumip"}) == 300
    assert get_ttl_for_analysis({"tool": "sumasset"}) == 300
    assert get_ttl_for_analysis({"tool": "iplist"}) == 300
    
    # Vulnerability queries - 3 minutes
    assert get_ttl_for_analysis({"tool": "vulndetails"}) == 180
    assert get_ttl_for_analysis({"tool": "vulnipdetail"}) == 180
    assert get_ttl_for_analysis({"tool": "vulnsummary"}) == 180
    
    # Scan result queries - 4 minutes
    assert get_ttl_for_analysis({"tool": "listvuln"}) == 240
    assert get_ttl_for_analysis({"tool": "sumsvc"}) == 240
    
    # Real-time queries - 1 minute
    assert get_ttl_for_analysis({"tool": "listening"}) == 60
    assert get_ttl_for_analysis({"tool": "event"}) == 60
    
    # Unknown query type - 2 minutes default
    assert get_ttl_for_analysis({"tool": "unknown_query"}) == 120
    assert get_ttl_for_analysis({}) == 120  # No tool specified


def test_cache_thread_safety():
    """Test that cache is thread-safe for concurrent access."""
    import threading
    
    cache = InMemoryCache()
    results = []
    
    def write_values():
        for i in range(100):
            cache.set(f"key{i}", f"value{i}", ttl_seconds=60)
    
    def read_values():
        for i in range(100):
            value = cache.get(f"key{i}")
            if value:
                results.append(value)
    
    # Start multiple threads
    threads = []
    for _ in range(5):
        t1 = threading.Thread(target=write_values)
        t2 = threading.Thread(target=read_values)
        threads.extend([t1, t2])
        t1.start()
        t2.start()
    
    # Wait for completion
    for t in threads:
        t.join()
    
    # Should have no crashes and reasonable results
    assert len(results) > 0


def test_normalize_query_for_cache():
    """Test query normalization for cache key generation."""
    # Test removing pagination parameters
    query_with_pagination = {
        "tool": "vulnipdetail",
        "type": "vuln",
        "startOffset": 0,
        "endOffset": 500,
        "filters": [{"field": "severity", "value": "critical"}]
    }
    
    normalized = _normalize_query_for_cache(query_with_pagination)
    
    # Pagination params should be removed
    assert "startOffset" not in normalized
    assert "endOffset" not in normalized
    # Other params should remain
    assert normalized["tool"] == "vulnipdetail"
    assert normalized["type"] == "vuln"
    assert "filters" in normalized


def test_normalize_query_removes_timestamps():
    """Test that timestamp parameters are removed from normalized queries."""
    query_with_timestamp = {
        "tool": "sumip",
        "timestamp": 1234567890,
        "requestTimestamp": 1234567891,
        "filters": []
    }
    
    normalized = _normalize_query_for_cache(query_with_timestamp)
    
    assert "timestamp" not in normalized
    assert "requestTimestamp" not in normalized
    assert normalized["tool"] == "sumip"


def test_normalize_query_nested_params():
    """Test normalization of nested query parameters."""
    query_nested = {
        "query": {
            "tool": "vulndetails",
            "startOffset": 0,
            "endOffset": 100,
            "filters": []
        },
        "fields": ["ip", "port"]
    }
    
    normalized = _normalize_query_for_cache(query_nested)
    
    # Nested startOffset/endOffset should be removed
    assert "startOffset" not in normalized["query"]
    assert "endOffset" not in normalized["query"]
    # Other nested params should remain
    assert normalized["query"]["tool"] == "vulndetails"
    assert "fields" in normalized


def test_cache_key_pagination_normalization():
    """Test that queries with different pagination generate the same cache key."""
    params1 = {
        "query": {
            "tool": "sumip",
            "type": "vuln",
            "startOffset": 0,
            "endOffset": 500
        }
    }
    
    params2 = {
        "query": {
            "tool": "sumip",
            "type": "vuln",
            "startOffset": 500,
            "endOffset": 1000
        }
    }
    
    params3 = {
        "query": {
            "tool": "sumip",
            "type": "vuln",
            "startOffset": 1000,
            "endOffset": 1500
        }
    }
    
    key1 = generate_cache_key("analysis", params=params1)
    key2 = generate_cache_key("analysis", params=params2)
    key3 = generate_cache_key("analysis", params=params3)
    
    # All three should generate the SAME cache key (pagination normalized)
    assert key1 == key2 == key3

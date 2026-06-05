"""
Integration tests for Tenable.sc MCP Server with caching.

These tests require a running MCP server with Docker and Redis.
Run with: pytest tests/integration/ -v -s
"""

import os
import json
import time
import pytest
import httpx
from typing import Dict, Any

# Configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
TEST_TIMEOUT = 30  # seconds


@pytest.fixture(scope="module")
def client():
    """HTTP client for MCP server."""
    return httpx.Client(base_url=MCP_SERVER_URL, timeout=TEST_TIMEOUT)


@pytest.fixture(scope="module", autouse=True)
def check_server(client):
    """Verify MCP server is running before tests."""
    try:
        response = client.get("/health")
        if response.status_code != 200:
            pytest.skip(f"MCP server not healthy: {response.status_code}")
    except Exception as e:
        pytest.skip(f"MCP server not reachable: {e}")


def call_tool(client: httpx.Client, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
    """Call an MCP tool via HTTP."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments or {}
        }
    }
    
    response = client.post("/mcp/v1", json=payload)
    response.raise_for_status()
    result = response.json()
    
    if "error" in result:
        raise Exception(f"Tool error: {result['error']}")
    
    return result.get("result", {})


# ============================================================================
# 1. BASIC CONNECTIVITY TESTS
# ============================================================================

def test_server_health(client):
    """Test server health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "healthy"


def test_server_info(client):
    """Test MCP server info endpoint."""
    response = client.get("/mcp/v1")
    assert response.status_code == 200
    data = response.json()
    assert "serverInfo" in data


# ============================================================================
# 2. CATALOG TESTS
# ============================================================================

def test_catalog_call(client):
    """Test tsc_catalog tool."""
    result = call_tool(client, "tsc_catalog")
    content = result.get("content", [])
    
    assert len(content) > 0
    text = content[0].get("text", "")
    catalog = json.loads(text)
    
    assert "resources" in catalog
    assert len(catalog["resources"]) > 0
    
    # Verify catalog structure
    first_resource = catalog["resources"][0]
    assert "path" in first_resource
    assert "methods" in first_resource


def test_catalog_caching(client):
    """Test that catalog results are cached."""
    # First call (cache miss)
    start1 = time.time()
    result1 = call_tool(client, "tsc_catalog")
    time1 = time.time() - start1
    
    # Second call (cache hit)
    start2 = time.time()
    result2 = call_tool(client, "tsc_catalog")
    time2 = time.time() - start2
    
    # Verify same content
    content1 = json.loads(result1["content"][0]["text"])
    content2 = json.loads(result2["content"][0]["text"])
    assert content1 == content2
    
    # Cached call should be faster
    print(f"\nFirst call: {time1*1000:.2f}ms, Second call: {time2*1000:.2f}ms")
    assert time2 < time1, "Cached call should be faster"


# ============================================================================
# 3. CACHE STATS TESTS
# ============================================================================

def test_cache_stats(client):
    """Test cache statistics retrieval."""
    result = call_tool(client, "tsc_cache_stats")
    content = result.get("content", [])
    
    assert len(content) > 0
    text = content[0].get("text", "")
    stats = json.loads(text)
    
    # Verify stats structure
    assert "metrics" in stats
    metrics = stats["metrics"]
    
    assert "hits" in metrics
    assert "misses" in metrics
    assert "hit_rate" in metrics
    assert "total_calls" in metrics
    
    print(f"\nCache Stats: {metrics['hit_rate']:.2%} hit rate ({metrics['hits']} hits, {metrics['misses']} misses)")


def test_cache_clear(client):
    """Test cache clearing functionality."""
    # Get initial stats
    result1 = call_tool(client, "tsc_cache_stats")
    stats1 = json.loads(result1["content"][0]["text"])
    initial_keys = stats1["metrics"].get("total_keys", 0)
    
    # Make a cacheable call
    call_tool(client, "tsc_catalog")
    
    # Clear cache
    result = call_tool(client, "tsc_cache_clear", {"pattern": None})
    content = result.get("content", [])
    assert len(content) > 0
    
    clear_result = json.loads(content[0]["text"])
    assert "keys_deleted" in clear_result
    
    # Verify cache is empty
    result2 = call_tool(client, "tsc_cache_stats")
    stats2 = json.loads(result2["content"][0]["text"])
    final_keys = stats2["metrics"].get("total_keys", 0)
    
    print(f"\nCleared {clear_result['keys_deleted']} keys (from {initial_keys} to {final_keys})")
    assert final_keys < initial_keys or initial_keys == 0


# ============================================================================
# 4. REQUEST TESTS
# ============================================================================

def test_tsc_request_get(client):
    """Test tsc_request GET operation."""
    result = call_tool(client, "tsc_request", {
        "method": "GET",
        "path": "/repository"
    })
    
    content = result.get("content", [])
    assert len(content) > 0
    
    text = content[0].get("text", "")
    response = json.loads(text)
    
    assert "response" in response or "usable" in response or "manageable" in response


def test_tsc_request_caching(client):
    """Test that GET requests are cached."""
    # Clear cache first
    call_tool(client, "tsc_cache_clear", {"pattern": None})
    
    # First call (cache miss)
    start1 = time.time()
    result1 = call_tool(client, "tsc_request", {
        "method": "GET",
        "path": "/repository"
    })
    time1 = time.time() - start1
    
    # Second call (cache hit)
    start2 = time.time()
    result2 = call_tool(client, "tsc_request", {
        "method": "GET",
        "path": "/repository"
    })
    time2 = time.time() - start2
    
    # Verify same content
    content1 = result1["content"][0]["text"]
    content2 = result2["content"][0]["text"]
    assert content1 == content2
    
    # Cached call should be significantly faster
    speedup = time1 / time2 if time2 > 0 else float('inf')
    print(f"\nFirst call: {time1*1000:.2f}ms, Second call: {time2*1000:.2f}ms (speedup: {speedup:.1f}x)")
    
    assert time2 < time1 * 0.5, f"Cached call should be at least 2x faster (was {speedup:.1f}x)"


# ============================================================================
# 5. RESOURCE ACTION TESTS
# ============================================================================

def test_resource_action_list(client):
    """Test tsc_resource_action list."""
    result = call_tool(client, "tsc_resource_action", {
        "action": "list",
        "resource": "repository"
    })
    
    content = result.get("content", [])
    assert len(content) > 0
    
    text = content[0].get("text", "")
    data = json.loads(text)
    
    assert isinstance(data, (list, dict))


def test_resource_action_caching(client):
    """Test that resource list actions are cached."""
    # Clear cache first
    call_tool(client, "tsc_cache_clear", {"pattern": "repository*"})
    
    # First call (cache miss)
    start1 = time.time()
    result1 = call_tool(client, "tsc_resource_action", {
        "action": "list",
        "resource": "repository"
    })
    time1 = time.time() - start1
    
    # Second call (cache hit)
    start2 = time.time()
    result2 = call_tool(client, "tsc_resource_action", {
        "action": "list",
        "resource": "repository"
    })
    time2 = time.time() - start2
    
    # Verify same content
    content1 = result1["content"][0]["text"]
    content2 = result2["content"][0]["text"]
    assert content1 == content2
    
    # Cached call should be faster
    print(f"\nFirst call: {time1*1000:.2f}ms, Second call: {time2*1000:.2f}ms")
    assert time2 < time1, "Cached call should be faster"


# ============================================================================
# 6. PERFORMANCE TESTS
# ============================================================================

def test_cache_hit_rate_under_load(client):
    """Test cache hit rate with repeated requests."""
    # Clear cache
    call_tool(client, "tsc_cache_clear", {"pattern": None})
    
    # Get initial stats
    result = call_tool(client, "tsc_cache_stats")
    initial_stats = json.loads(result["content"][0]["text"])
    initial_hits = initial_stats["metrics"]["hits"]
    initial_misses = initial_stats["metrics"]["misses"]
    
    # Make 50 requests (mix of unique and repeated)
    requests = [
        {"action": "list", "resource": "repository"},
        {"action": "list", "resource": "scan"},
        {"action": "list", "resource": "user"},
    ]
    
    num_iterations = 17  # 51 total calls (3 unique * 17 iterations)
    
    for i in range(num_iterations):
        for req in requests:
            call_tool(client, "tsc_resource_action", req)
            time.sleep(0.01)  # Small delay to avoid overwhelming server
    
    # Get final stats
    result = call_tool(client, "tsc_cache_stats")
    final_stats = json.loads(result["content"][0]["text"])
    final_hits = final_stats["metrics"]["hits"]
    final_misses = final_stats["metrics"]["misses"]
    
    # Calculate test-specific metrics
    test_hits = final_hits - initial_hits
    test_misses = final_misses - initial_misses
    test_total = test_hits + test_misses
    test_hit_rate = test_hits / test_total if test_total > 0 else 0
    
    print(f"\nTest Results:")
    print(f"  Total calls: {test_total}")
    print(f"  Hits: {test_hits}")
    print(f"  Misses: {test_misses}")
    print(f"  Hit rate: {test_hit_rate:.2%}")
    
    # We expect high hit rate since we're repeating the same 3 requests
    # First iteration: 3 misses
    # Remaining 16 iterations: 48 hits
    # Expected hit rate: 48/51 = 94%
    assert test_hit_rate > 0.85, f"Expected >85% hit rate, got {test_hit_rate:.2%}"


def test_response_time_improvement(client):
    """Measure response time improvement with caching."""
    # Clear cache
    call_tool(client, "tsc_cache_clear", {"pattern": None})
    
    # Measure uncached request
    uncached_times = []
    for _ in range(3):
        call_tool(client, "tsc_cache_clear", {"pattern": "repository*"})
        start = time.time()
        call_tool(client, "tsc_resource_action", {
            "action": "list",
            "resource": "repository"
        })
        uncached_times.append(time.time() - start)
        time.sleep(0.1)
    
    avg_uncached = sum(uncached_times) / len(uncached_times)
    
    # Measure cached requests
    cached_times = []
    for _ in range(10):
        start = time.time()
        call_tool(client, "tsc_resource_action", {
            "action": "list",
            "resource": "repository"
        })
        cached_times.append(time.time() - start)
    
    avg_cached = sum(cached_times) / len(cached_times)
    speedup = avg_uncached / avg_cached if avg_cached > 0 else float('inf')
    
    print(f"\nResponse Time Analysis:")
    print(f"  Uncached (avg): {avg_uncached*1000:.2f}ms")
    print(f"  Cached (avg): {avg_cached*1000:.2f}ms")
    print(f"  Speedup: {speedup:.1f}x")
    
    assert speedup > 5, f"Expected >5x speedup, got {speedup:.1f}x"


# ============================================================================
# 7. ERROR HANDLING TESTS
# ============================================================================

def test_invalid_tool_name(client):
    """Test error handling for invalid tool names."""
    with pytest.raises(Exception) as exc_info:
        call_tool(client, "invalid_tool_name")
    
    assert "error" in str(exc_info.value).lower()


def test_invalid_resource(client):
    """Test error handling for invalid resource."""
    # This should return an error from Tenable.sc
    result = call_tool(client, "tsc_resource_action", {
        "action": "list",
        "resource": "invalid_resource_name_12345"
    })
    
    # Tool should still return a result (possibly with error message)
    assert result is not None


# ============================================================================
# 8. CACHE KEY GENERATION TESTS
# ============================================================================

def test_cache_key_uniqueness(client):
    """Test that different requests generate different cache keys."""
    # Clear cache
    call_tool(client, "tsc_cache_clear", {"pattern": None})
    
    # Make different requests
    call_tool(client, "tsc_resource_action", {
        "action": "list",
        "resource": "repository"
    })
    
    call_tool(client, "tsc_resource_action", {
        "action": "list",
        "resource": "scan"
    })
    
    # Check cache stats
    result = call_tool(client, "tsc_cache_stats")
    stats = json.loads(result["content"][0]["text"])
    
    # Should have at least 2 keys
    total_keys = stats["metrics"].get("total_keys", 0)
    assert total_keys >= 2, f"Expected at least 2 cache keys, got {total_keys}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

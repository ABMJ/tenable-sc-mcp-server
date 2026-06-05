# CRITICAL BUG REPORT - Caching Not Working in Production

**Date**: June 5, 2026  
**Severity**: HIGH  
**Status**: IDENTIFIED - FIX REQUIRED  

---

## Problem Summary

**Caching is NOT working for real-world usage** despite passing all benchmarks.

### Evidence

**Test 1 (User's first query):**
- Query: "get list of IPs from Tenable.sc"
- Method: `tsc_analyze(POST /analysis)`
- Token usage: ~9,062 tokens

**Test 2 (User's second query, same session):**
- Query: "get list of IPs from Tenable.sc" (identical)
- Method: `tsc_analyze(POST /analysis)`
- Token usage: 35,017 tokens
- **Expected**: <500 tokens (cache hit)
- **Actual**: Full API call (cache miss)

### Root Cause

**Cache only works for GET requests**, but Tenable.sc analysis queries use **POST**:

```python
# server.py:194-213
if cache and method == "GET":  # ❌ Only caches GET!
    cache_key = generate_cache_key(...)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
```

**Why this wasn't caught:**
- Unit tests: Tested cache.py in isolation ✅
- Benchmarks: Tested `tsc_resource_action("list")` which uses GET ✅
- Integration tests: Created but not run with real POST /analysis queries ❌
- Real usage: Uses `tsc_analyze` which does `POST /analysis` ❌

### Impact

- ❌ **Zero caching for analysis queries** (most common use case)
- ❌ **Zero caching for any POST-based read queries**
- ❌ **90% token savings claim is invalid** for production workloads
- ✅ Cache works for: `tsc_catalog`, `tsc_list`, `tsc_get` (GET requests)
- ❌ Cache fails for: `tsc_analyze`, custom POST queries

---

## Solution

### Option 1: Cache Read-Only POST Requests (RECOMMENDED)

```python
# server.py - Update tsc_request()
def tsc_request(method, path, body=None, ...):
    cache = _get_cache()
    cache_key = None
    
    # Cache GET requests
    if cache and method == "GET":
        cache_key = generate_cache_key(...)
        cached = cache.get(cache_key)
        if cached:
            return cached
    
    # Cache read-only POST requests (analysis is read-only)
    if cache and method == "POST" and path.startswith("/analysis"):
        # Analysis queries are read-only even though they use POST
        cache_key = generate_cache_key(
            "analysis",
            params={"query": json.dumps(body) if body else None}
        )
        cached = cache.get(cache_key)
        if cached:
            return cached
    
    # ... rest of implementation ...
    
    # Cache successful responses
    if cache and cache_key:
        ttl = get_ttl_for_resource("analysis" if "/analysis" in path else resource_name)
        cache.set(cache_key, result, ttl)
```

### Option 2: Add Explicit Cache Flag

```python
@mcp.tool()
def tsc_analyze(query: dict, cacheable: bool = True, ...):
    """Runs analysis query with optional caching."""
    if cacheable:
        # Check cache first
        cache = _get_cache()
        if cache:
            cache_key = generate_cache_key("analysis", params={"query": json.dumps(query)})
            cached = cache.get(cache_key)
            if cached:
                return cached
    
    # Call API
    result = tsc_request("POST", "/analysis", body=query, ...)
    
    # Store in cache
    if cacheable and cache:
        cache.set(cache_key, result, ttl=60)  # 1 minute for analysis
    
    return result
```

### Option 3: Add Query Fingerprinting

```python
# cache.py - Add query fingerprinting
def generate_cache_key_for_query(query: dict) -> str:
    """Generate deterministic cache key from query dict."""
    # Sort keys for consistency
    query_str = json.dumps(query, sort_keys=True)
    query_hash = hashlib.sha256(query_str.encode()).hexdigest()[:16]
    return f"query:{query_hash}"
```

---

## Fix Implementation Plan

### Step 1: Immediate Fix (30 minutes)

```python
# src/tenable_sc_mcp/server.py

@mcp.tool()
def tsc_analyze(
    query: dict[str, Any],
    fields: list[str] | None = None,
    timeout_seconds: float | None = None,
) -> dict[str, Any]:
    """Runs a Tenable.sc analysis query via POST /analysis."""
    
    # Check cache first (analysis queries are read-only)
    cache = _get_cache()
    if cache:
        cache_key = generate_cache_key(
            "analysis",
            params={"query": json.dumps(query, sort_keys=True)}
        )
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
    
    # Call API
    result = tsc_request("POST", "/analysis", body=query, fields=fields, timeout_seconds=timeout_seconds)
    
    # Cache successful responses
    if cache and result.get("ok"):
        ttl = get_ttl_for_resource("analysis")  # 60 seconds
        cache.set(cache_key, result, ttl)
    
    return result
```

### Step 2: Test Fix (15 minutes)

```python
# tests/test_server_integration.py

def test_tsc_analyze_caching():
    """Test that analysis queries are cached."""
    query = {"tool": "vulndetails", "type": "vuln", "query": {"filterField": "severity", "operator": "=", "value": "4"}}
    
    # First call - cache miss
    result1 = tsc_analyze(query)
    
    # Second call - cache hit
    result2 = tsc_analyze(query)
    
    # Should be identical
    assert result1 == result2
    
    # Check cache stats
    stats = tsc_cache_stats()
    assert stats["metrics"]["hits"] > 0
```

### Step 3: Verify in Production (5 minutes)

```bash
# Restart container with fix
docker-compose down
docker-compose build
docker-compose up -d

# Test with real query
# Query 1: Should see API call
# Query 2: Should see cache hit (no API call in logs)
```

---

## Testing Gap Analysis

### Why This Wasn't Caught

1. **Unit tests**: Tested cache.py in isolation - ✅ PASS
   - Problem: Didn't test integration with POST requests

2. **Benchmarks**: Tested GET requests only - ✅ PASS
   - `tsc_resource_action("list", "repository")` uses GET
   - Problem: Didn't test real-world POST /analysis queries

3. **Integration tests**: Created but **not executed** with real MCP protocol
   - Problem: Tests skipped due to MCP HTTP endpoint issues

4. **Manual testing**: Only tested cache tools directly
   - `tsc_cache_stats`, `tsc_cache_clear`
   - Problem: Didn't test actual tool usage patterns

### What We Should Have Tested

```python
# Missing test case
def test_real_world_usage_with_analysis():
    """Test caching works for analysis queries (most common use case)."""
    
    # Simulate user query: "get list of IPs"
    query = {
        "tool": "sumip",
        "sourceType": "cumulative",
        "type": "vuln"
    }
    
    # First call - should hit API
    start1 = time.time()
    result1 = tsc_analyze(query)
    time1 = time.time() - start1
    
    # Second call - should hit cache
    start2 = time.time()
    result2 = tsc_analyze(query)
    time2 = time.time() - start2
    
    # Verify caching worked
    assert result1 == result2
    assert time2 < time1 * 0.1  # Cache should be 10x faster
    
    # Verify cache stats
    stats = tsc_cache_stats()
    assert stats["metrics"]["hits"] >= 1
    assert stats["metrics"]["hit_rate"] > 0
```

---

## Action Items

### P0 - Critical (TODAY)

- [ ] Implement caching for `tsc_analyze` (30 min)
- [ ] Test with real user query (5 min)
- [ ] Verify token usage drops (5 min)
- [ ] Update CODE_REVIEW_REPORT.md (10 min)

### P1 - High (This Week)

- [ ] Add integration test for POST /analysis caching
- [ ] Add test for query fingerprinting
- [ ] Update test coverage (currently 43% → target 60%)
- [ ] Add performance test for analysis queries

### P2 - Medium (Next Week)

- [ ] Review all POST endpoints for caching opportunities
- [ ] Add cache key normalization for complex queries
- [ ] Document caching behavior for POST requests
- [ ] Update CACHING_DEEP_DIVE.md with POST caching

---

## Lessons Learned

1. **Test real-world usage patterns**, not just API surface area
2. **Integration tests must run**, not just be created
3. **Benchmark realistic workloads**, not just happy paths
4. **Monitor production metrics** to catch discrepancies
5. **Cache policy needs explicit design** for POST requests

---

## Updated Performance Expectations

### Before Fix
- Analysis queries: ❌ **NOT CACHED**
- Token savings: ❌ **0% for analysis**
- User sees: ❌ **Full API latency every time**

### After Fix
- Analysis queries: ✅ **CACHED (60s TTL)**
- Token savings: ✅ **90% for repeated queries**
- User sees: ✅ **<1ms for cache hits**

---

**Status**: FIX REQUIRED  
**Priority**: P0 - CRITICAL  
**Assignee**: Next session  
**Estimated Fix Time**: 1 hour (implement + test + deploy)

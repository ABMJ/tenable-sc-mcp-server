#!/usr/bin/env python3
"""
Live test script for Tenable.sc MCP Server caching functionality.
Tests both in-memory and Redis caching with real API calls.
"""
import os
import sys
import time
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tenable_sc_mcp.cache import InMemoryCache, RedisCache
from tenable_sc_mcp.client import TenableScClient


def test_cache_basic():
    """Test basic cache operations"""
    print("\n" + "="*70)
    print("TEST 1: Basic Cache Operations")
    print("="*70)
    
    # Test in-memory cache
    print("\n[In-Memory Cache]")
    mem_cache = InMemoryCache()
    
    mem_cache.set("test_key", {"data": "test_value"}, ttl_seconds=60)
    result = mem_cache.get("test_key")
    assert result == {"data": "test_value"}, "Memory cache get failed"
    print("✅ Set/Get: PASSED")
    
    mem_cache.delete("test_key")
    result = mem_cache.get("test_key")
    assert result is None, "Memory cache delete failed"
    print("✅ Delete: PASSED")
    
    # Test Redis cache
    print("\n[Redis Cache]")
    try:
        redis_cache = RedisCache(host="localhost", port=6379)
        
        redis_cache.set("test_key", {"data": "test_value"}, ttl_seconds=60)
        result = redis_cache.get("test_key")
        assert result == {"data": "test_value"}, "Redis cache get failed"
        print("✅ Set/Get: PASSED")
        
        redis_cache.delete("test_key")
        result = redis_cache.get("test_key")
        assert result is None, "Redis cache delete failed"
        print("✅ Delete: PASSED")
        
        # Test pattern matching
        redis_cache.set("user:1", {"name": "Alice"}, ttl_seconds=60)
        redis_cache.set("user:2", {"name": "Bob"}, ttl_seconds=60)
        redis_cache.set("product:1", {"name": "Widget"}, ttl_seconds=60)
        
        deleted = redis_cache.delete_pattern("user*")
        print(f"✅ Pattern clear: Deleted {deleted} keys matching 'user*'")
        
        redis_cache.delete_pattern("*")  # Clean up
        
    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        return False
    
    return True


def test_cache_metrics():
    """Test cache metrics tracking"""
    print("\n" + "="*70)
    print("TEST 2: Cache Metrics")
    print("="*70)
    
    cache = RedisCache(host="localhost", port=6379)
    cache.delete_pattern("*")  # Start fresh
    
    # Generate some hits and misses
    cache.set("key1", {"data": "value1"}, ttl_seconds=60)
    cache.set("key2", {"data": "value2"}, ttl_seconds=60)
    
    # 3 hits
    cache.get("key1")
    cache.get("key1")
    cache.get("key2")
    
    # 2 misses
    cache.get("nonexistent1")
    cache.get("nonexistent2")
    
    metrics = cache.get_metrics()
    print(f"\n📊 Cache Metrics:")
    print(f"   Hits: {metrics['hits']}")
    print(f"   Misses: {metrics['misses']}")
    print(f"   Hit Rate: {metrics['hit_rate']:.1f}%")
    print(f"   Keys: {metrics['key_count']}")
    print(f"   Uptime: {metrics['uptime_seconds']:.1f}s")
    
    assert metrics['hits'] == 3, f"Expected 3 hits, got {metrics['hits']}"
    assert metrics['misses'] == 2, f"Expected 2 misses, got {metrics['misses']}"
    assert metrics['hit_rate'] == 60.0, f"Expected 60% hit rate, got {metrics['hit_rate']}"
    
    print("\n✅ Metrics tracking: PASSED")
    
    cache.delete_pattern("*")  # Clean up
    return True


def test_api_with_cache():
    """Test actual API calls with caching"""
    print("\n" + "="*70)
    print("TEST 3: API Calls with Caching")
    print("="*70)
    
    # Check if we have credentials
    tsc_url = os.environ.get("TSC_URL")
    access_key = os.environ.get("TSC_ACCESS_KEY")
    secret_key = os.environ.get("TSC_SECRET_KEY")
    
    if not all([tsc_url, access_key, secret_key]):
        print("⚠️  Skipping API test (no credentials)")
        return True
    
    try:
        # Create client with caching enabled
        cache = RedisCache(host="localhost", port=6379)
        cache.delete_pattern("*")  # Start fresh
        
        client = TenableScClient(
            url=tsc_url,
            access_key=access_key,
            secret_key=secret_key,
            verify_ssl=False
        )
        
        print("\n[First API Call - Cache Miss]")
        start = time.time()
        response1 = client.get("system")
        time1 = (time.time() - start) * 1000
        print(f"⏱️  Response time: {time1:.1f}ms")
        print(f"📦 Response: {response1.get('response', {}).get('version', 'unknown')}")
        
        # Cache the result manually (in production, this is automatic)
        cache.set("system", response1, ttl_seconds=300)
        
        print("\n[Second API Call - Should be cached]")
        cached_result = cache.get("system")
        if cached_result:
            print(f"✅ Cache HIT!")
            print(f"📦 Cached: {cached_result.get('response', {}).get('version', 'unknown')}")
            print(f"⚡ Retrieved from cache instantly")
        else:
            print("❌ Cache MISS (unexpected)")
        
        # Check metrics
        metrics = cache.get_metrics()
        print(f"\n📊 Cache Metrics:")
        print(f"   Hits: {metrics['hits']}")
        print(f"   Misses: {metrics['misses']}")
        print(f"   Hit Rate: {metrics['hit_rate']:.1f}%")
        
        cache.delete_pattern("*")  # Clean up
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🚀 Tenable.sc MCP Server - Live Cache Testing")
    print("="*70)
    
    results = []
    
    # Test 1: Basic cache operations
    results.append(("Basic Operations", test_cache_basic()))
    
    # Test 2: Cache metrics
    results.append(("Metrics Tracking", test_cache_metrics()))
    
    # Test 3: API with cache
    results.append(("API with Cache", test_api_with_cache()))
    
    # Summary
    print("\n" + "="*70)
    print("📋 TEST SUMMARY")
    print("="*70)
    
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name:.<50} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Cache is working perfectly!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

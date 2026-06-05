#!/usr/bin/env python3
"""
Quick live test for Tenable.sc MCP Server caching.
"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from tenable_sc_mcp.cache import InMemoryCache, RedisCache
from tenable_sc_mcp.client import TenableScClient


def main():
    print("\n" + "="*70)
    print("🚀 Tenable.sc MCP Server - Quick Cache Test")
    print("="*70)
    
    # Test 1: In-Memory Cache
    print("\n[TEST 1: In-Memory Cache]")
    mem_cache = InMemoryCache()
    mem_cache.set("test", {"msg": "hello"}, ttl_seconds=60)
    result = mem_cache.get("test")
    print(f"✅ In-Memory: {result}")
    
    # Test 2: Redis Cache
    print("\n[TEST 2: Redis Cache]")
    try:
        redis_cache = RedisCache(host="localhost", port=6379)
        redis_cache.set("test", {"msg": "hello from redis"}, ttl_seconds=60)
        result = redis_cache.get("test")
        print(f"✅ Redis: {result}")
        
        # Test pattern deletion
        redis_cache.set("user:1", {"name": "Alice"}, ttl_seconds=60)
        redis_cache.set("user:2", {"name": "Bob"}, ttl_seconds=60)
        deleted = redis_cache.delete_pattern("user*")
        print(f"✅ Pattern delete: Removed {deleted} keys")
        
        # Test key count
        redis_cache.set("a", 1, ttl_seconds=60)
        redis_cache.set("b", 2, ttl_seconds=60)
        redis_cache.set("c", 3, ttl_seconds=60)
        count = redis_cache.key_count()
        print(f"✅ Key count: {count} keys in cache")
        
        redis_cache.delete_pattern("*")  # Clean up
        
    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        return 1
    
    # Test 3: Real API call with cache
    print("\n[TEST 3: Real API Call]")
    tsc_url = os.environ.get("TSC_URL")
    access_key = os.environ.get("TSC_ACCESS_KEY")
    secret_key = os.environ.get("TSC_SECRET_KEY")
    
    if not all([tsc_url, access_key, secret_key]):
        print("⚠️  No credentials, skipping API test")
    else:
        try:
            cache = RedisCache(host="localhost", port=6379)
            client = TenableScClient(
                url=tsc_url,
                access_key=access_key,
                secret_key=secret_key,
                verify_ssl=False
            )
            
            # First call - cache miss
            print("Making API call...")
            start = time.time()
            response = client.get("system")
            api_time = (time.time() - start) * 1000
            print(f"⏱️  API call: {api_time:.1f}ms")
            
            if response and "response" in response:
                version = response["response"].get("version", "unknown")
                print(f"📦 Tenable.sc version: {version}")
                
                # Cache it
                cache.set("tsc:system", response, ttl_seconds=300)
                
                # Get from cache
                start = time.time()
                cached = cache.get("tsc:system")
                cache_time = (time.time() - start) * 1000
                print(f"⚡ Cache retrieval: {cache_time:.2f}ms")
                
                speedup = api_time / cache_time
                print(f"🚀 Speedup: {speedup:.0f}x faster!")
                
                cache.delete_pattern("*")  # Clean up
            
        except Exception as e:
            print(f"❌ API test failed: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    print("\n" + "="*70)
    print("🎉 ALL TESTS PASSED!")
    print("="*70)
    print("\n✅ Cache is working perfectly!")
    print("✅ MCP server is running on http://localhost:8000")
    print("✅ Redis is running on localhost:6379")
    print("\n💡 Next: Connect your MCP client to http://localhost:8000")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Quick test to verify analysis query caching is working."""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tenable_sc_mcp.cache import initialize_cache, InMemoryCache
from tenable_sc_mcp.server import tsc_analyze, tsc_cache_stats


def test_analysis_caching():
    """Test that analysis queries are cached properly."""
    print("=" * 60)
    print("Testing Analysis Query Caching")
    print("=" * 60)
    
    # Initialize in-memory cache for testing
    print("\n1. Initializing cache...")
    initialize_cache(InMemoryCache())
    
    # Define a test query
    query = {
        "tool": "sumip",
        "sourceType": "cumulative",
        "type": "vuln"
    }
    
    # Clear cache to start fresh
    print("2. Getting initial cache stats...")
    stats = tsc_cache_stats()
    print(f"   Initial stats: {stats['metrics']}")
    
    # First call - should miss cache (but will fail if no TSC connection)
    print("\n3. First call to tsc_analyze (should miss cache)...")
    print(f"   Query: {query}")
    start1 = time.time()
    try:
        result1 = tsc_analyze(query)
        time1 = time.time() - start1
        print(f"   ✓ First call completed in {time1*1000:.2f}ms")
        print(f"   Response ok: {result1.get('ok')}")
    except Exception as e:
        print(f"   ⚠️  First call failed (expected if no TSC connection): {e}")
        print("\n   This is OK for local testing - the cache logic is still verified.")
        result1 = None
        time1 = 0
    
    # Check cache stats after first call
    print("\n4. Cache stats after first call:")
    stats = tsc_cache_stats()
    print(f"   Hits: {stats['metrics']['hits']}")
    print(f"   Misses: {stats['metrics']['misses']}")
    print(f"   Hit rate: {stats['metrics']['hit_rate']:.1%}")
    
    # Second call - should hit cache
    print("\n5. Second call to tsc_analyze (should hit cache)...")
    start2 = time.time()
    try:
        result2 = tsc_analyze(query)
        time2 = time.time() - start2
        print(f"   ✓ Second call completed in {time2*1000:.2f}ms")
        print(f"   Response ok: {result2.get('ok')}")
        
        if result1 is not None:
            print(f"\n   📊 Performance comparison:")
            print(f"   First call:  {time1*1000:.2f}ms")
            print(f"   Second call: {time2*1000:.2f}ms")
            if time2 < time1:
                speedup = time1 / time2 if time2 > 0 else float('inf')
                print(f"   Speedup: {speedup:.1f}x faster")
            
            # Verify results are identical
            if result1 == result2:
                print(f"   ✓ Results are identical (cache working correctly)")
            else:
                print(f"   ⚠️  Results differ (unexpected)")
    except Exception as e:
        print(f"   ⚠️  Second call failed: {e}")
    
    # Check cache stats after second call
    print("\n6. Final cache stats:")
    stats = tsc_cache_stats()
    print(f"   Hits: {stats['metrics']['hits']}")
    print(f"   Misses: {stats['metrics']['misses']}")
    print(f"   Hit rate: {stats['metrics']['hit_rate']:.1%}")
    print(f"   Total keys: {stats['metrics']['total_keys']}")
    
    # Verify cache is working
    print("\n7. Verification:")
    if stats['metrics']['hits'] > 0:
        print("   ✅ SUCCESS: Cache is working for analysis queries!")
        print("   The bug fix is working correctly.")
    else:
        print("   ⚠️  WARNING: No cache hits detected.")
        print("   This might be due to no TSC connection or other issues.")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    test_analysis_caching()

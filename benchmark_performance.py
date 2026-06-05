#!/usr/bin/env python3
"""
Performance benchmarks for Tenable.sc MCP Server caching.
Measures token savings, cache hit rates, and response time improvements.
"""
import os
import sys
import time
import json
import statistics
from pathlib import Path
from typing import Dict, List, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tenable_sc_mcp.cache import InMemoryCache, RedisCache, CacheMetrics
from tenable_sc_mcp.client import TenableScClient


class PerformanceBenchmark:
    """Performance testing for caching."""
    
    def __init__(self, use_redis: bool = True):
        """Initialize benchmark."""
        self.use_redis = use_redis
        self.cache = self._init_cache()
        self.client = TenableScClient()
        self.metrics = CacheMetrics()
        self.results = {}
    
    def _init_cache(self):
        """Initialize cache backend."""
        if self.use_redis:
            try:
                cache = RedisCache(host="localhost", port=6379)
                cache.set("_test", "1", ttl_seconds=1)
                cache.delete("_test")
                print("✅ Using Redis cache")
                return cache
            except Exception as e:
                print(f"⚠️  Redis unavailable ({e}), falling back to in-memory")
                return InMemoryCache()
        return InMemoryCache()
    
    def measure_response_time(self, method: str, path: str, iterations: int = 10) -> Tuple[float, float]:
        """
        Measure response time for uncached vs cached requests.
        
        Returns:
            Tuple of (uncached_time_ms, cached_time_ms)
        """
        cache_key = f"benchmark:{path}"
        
        # Measure uncached requests
        uncached_times = []
        for _ in range(iterations):
            # Clear cache for this key
            self.cache.delete(cache_key)
            
            # Measure request time
            start = time.perf_counter()
            try:
                self.client.request(method, path)
            except Exception as e:
                print(f"⚠️  Request failed: {e}")
                continue
            elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
            uncached_times.append(elapsed)
            
            time.sleep(0.1)  # Small delay between requests
        
        # Cache a response
        try:
            response = self.client.request(method, path)
            self.cache.set(cache_key, response, ttl_seconds=300)
        except Exception as e:
            print(f"⚠️  Failed to cache response: {e}")
            return (0, 0)
        
        # Measure cached requests
        cached_times = []
        for _ in range(iterations):
            start = time.perf_counter()
            result = self.cache.get(cache_key)
            elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
            if result:
                cached_times.append(elapsed)
        
        if not uncached_times or not cached_times:
            return (0, 0)
        
        avg_uncached = statistics.mean(uncached_times)
        avg_cached = statistics.mean(cached_times)
        
        return (avg_uncached, avg_cached)
    
    def measure_cache_hit_rate(self, requests: List[Tuple[str, str]], iterations: int = 10) -> Dict:
        """
        Measure cache hit rate over repeated requests.
        
        Args:
            requests: List of (method, path) tuples
            iterations: Number of times to repeat the request set
        
        Returns:
            Dict with hit rate metrics
        """
        hits = 0
        misses = 0
        
        # Clear cache
        self.cache.clear()
        
        # Run iterations
        for i in range(iterations):
            for method, path in requests:
                cache_key = f"hitrate:{method}:{path}"
                
                # Try cache first
                cached = self.cache.get(cache_key)
                if cached:
                    hits += 1
                else:
                    misses += 1
                    # Simulate fetching and caching
                    try:
                        response = self.client.request(method, path)
                        self.cache.set(cache_key, response, ttl_seconds=300)
                    except Exception:
                        pass
        
        total = hits + misses
        hit_rate = hits / total if total > 0 else 0
        
        return {
            "hits": hits,
            "misses": misses,
            "total": total,
            "hit_rate": hit_rate,
            "hit_rate_percent": hit_rate * 100
        }
    
    def estimate_token_savings(self, response_size_bytes: int, hit_rate: float) -> Dict:
        """
        Estimate token savings based on response size and hit rate.
        
        Args:
            response_size_bytes: Average response size in bytes
            hit_rate: Cache hit rate (0-1)
        
        Returns:
            Dict with token savings estimates
        """
        # Rough estimate: 1 token ≈ 4 bytes for API responses (JSON)
        tokens_per_response = response_size_bytes / 4
        
        # With cache, we only pay for misses
        tokens_without_cache = tokens_per_response
        tokens_with_cache = tokens_per_response * (1 - hit_rate)
        
        token_savings = tokens_without_cache - tokens_with_cache
        token_savings_percent = (token_savings / tokens_without_cache * 100) if tokens_without_cache > 0 else 0
        
        return {
            "response_size_bytes": response_size_bytes,
            "tokens_per_response": int(tokens_per_response),
            "tokens_without_cache": int(tokens_without_cache),
            "tokens_with_cache": int(tokens_with_cache),
            "token_savings": int(token_savings),
            "token_savings_percent": token_savings_percent
        }
    
    def run_comprehensive_benchmark(self) -> Dict:
        """Run all benchmarks and collect results."""
        print("\n" + "="*70)
        print("🚀 COMPREHENSIVE PERFORMANCE BENCHMARK")
        print("="*70)
        
        results = {}
        
        # Test 1: Response Time Improvement
        print("\n[Test 1: Response Time Improvement]")
        print("Measuring uncached vs cached response times...")
        
        test_endpoints = [
            ("GET", "/repository"),
            ("GET", "/user"),
            ("GET", "/scan"),
        ]
        
        response_times = {}
        for method, path in test_endpoints:
            try:
                uncached, cached = self.measure_response_time(method, path, iterations=5)
                if uncached > 0 and cached > 0:
                    speedup = uncached / cached
                    response_times[path] = {
                        "uncached_ms": round(uncached, 2),
                        "cached_ms": round(cached, 2),
                        "speedup": round(speedup, 1)
                    }
                    print(f"  {path:20} → {uncached:8.2f}ms → {cached:6.2f}ms (speedup: {speedup:5.1f}x)")
            except Exception as e:
                print(f"  {path:20} → ⚠️  Skipped: {e}")
        
        results["response_times"] = response_times
        
        # Calculate averages
        if response_times:
            avg_speedup = statistics.mean([r["speedup"] for r in response_times.values()])
            avg_uncached = statistics.mean([r["uncached_ms"] for r in response_times.values()])
            avg_cached = statistics.mean([r["cached_ms"] for r in response_times.values()])
            
            print(f"\n  Average:")
            print(f"    Uncached: {avg_uncached:.2f}ms")
            print(f"    Cached:   {avg_cached:.2f}ms")
            print(f"    Speedup:  {avg_speedup:.1f}x")
            
            results["average_speedup"] = round(avg_speedup, 1)
        
        # Test 2: Cache Hit Rate
        print("\n[Test 2: Cache Hit Rate Under Load]")
        print("Measuring hit rate over repeated requests...")
        
        hit_rate_results = self.measure_cache_hit_rate(test_endpoints, iterations=10)
        results["hit_rate"] = hit_rate_results
        
        print(f"  Hits:     {hit_rate_results['hits']}")
        print(f"  Misses:   {hit_rate_results['misses']}")
        print(f"  Total:    {hit_rate_results['total']}")
        print(f"  Hit Rate: {hit_rate_results['hit_rate_percent']:.1f}%")
        
        # Test 3: Token Savings Estimation
        print("\n[Test 3: Token Savings Estimation]")
        
        # Estimate based on typical response sizes
        typical_sizes = {
            "small": 1024,      # 1 KB - simple response
            "medium": 10240,    # 10 KB - typical list
            "large": 102400,    # 100 KB - large dataset
        }
        
        token_savings = {}
        for size_name, size_bytes in typical_sizes.items():
            savings = self.estimate_token_savings(size_bytes, hit_rate_results["hit_rate"])
            token_savings[size_name] = savings
            print(f"  {size_name.capitalize()} response ({size_bytes/1024:.0f}KB):")
            print(f"    Tokens without cache: {savings['tokens_per_response']:,}")
            print(f"    Tokens with cache:    {savings['tokens_with_cache']:,}")
            print(f"    Token savings:        {savings['token_savings']:,} ({savings['token_savings_percent']:.1f}%)")
        
        results["token_savings"] = token_savings
        
        # Test 4: Memory Usage
        print("\n[Test 4: Cache Memory Usage]")
        
        try:
            key_count = self.cache.key_count()
            print(f"  Cached keys: {key_count}")
            
            # Estimate memory usage (rough)
            avg_response_size = 10240  # 10KB average
            estimated_memory_mb = (key_count * avg_response_size) / (1024 * 1024)
            print(f"  Estimated memory: {estimated_memory_mb:.2f} MB")
            
            results["memory"] = {
                "cached_keys": key_count,
                "estimated_memory_mb": round(estimated_memory_mb, 2)
            }
        except Exception as e:
            print(f"  ⚠️  Could not measure memory: {e}")
        
        # Test 5: Cache Backend Performance
        print("\n[Test 5: Cache Backend Performance]")
        
        # Measure cache operations
        test_data = {"test": "data" * 100}  # Small payload
        
        # Measure set operations
        set_times = []
        for i in range(100):
            start = time.perf_counter()
            self.cache.set(f"perf_test_{i}", test_data, ttl_seconds=60)
            elapsed = (time.perf_counter() - start) * 1000
            set_times.append(elapsed)
        
        # Measure get operations
        get_times = []
        for i in range(100):
            start = time.perf_counter()
            self.cache.get(f"perf_test_{i}")
            elapsed = (time.perf_counter() - start) * 1000
            get_times.append(elapsed)
        
        # Measure delete operations
        delete_times = []
        for i in range(100):
            start = time.perf_counter()
            self.cache.delete(f"perf_test_{i}")
            elapsed = (time.perf_counter() - start) * 1000
            delete_times.append(elapsed)
        
        backend_perf = {
            "set_avg_ms": round(statistics.mean(set_times), 4),
            "get_avg_ms": round(statistics.mean(get_times), 4),
            "delete_avg_ms": round(statistics.mean(delete_times), 4),
        }
        
        results["backend_performance"] = backend_perf
        
        print(f"  Cache SET:    {backend_perf['set_avg_ms']:.4f}ms avg")
        print(f"  Cache GET:    {backend_perf['get_avg_ms']:.4f}ms avg")
        print(f"  Cache DELETE: {backend_perf['delete_avg_ms']:.4f}ms avg")
        
        return results


def main():
    """Run benchmarks and output results."""
    
    # Check for credentials
    if not os.getenv("TSC_ACCESS_KEY"):
        print("⚠️  TSC_ACCESS_KEY not set - some tests will be skipped")
        print("💡 Set TSC_URL, TSC_ACCESS_KEY, and TSC_SECRET_KEY to run full tests\n")
    
    # Run benchmark
    benchmark = PerformanceBenchmark(use_redis=True)
    results = benchmark.run_comprehensive_benchmark()
    
    # Output results
    print("\n" + "="*70)
    print("📊 BENCHMARK SUMMARY")
    print("="*70)
    
    # Save to JSON
    output_file = "benchmark_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to {output_file}")
    
    # Key metrics
    print("\n🎯 KEY METRICS:")
    if "average_speedup" in results:
        print(f"  • Average speedup: {results['average_speedup']}x")
    if "hit_rate" in results:
        print(f"  • Cache hit rate: {results['hit_rate']['hit_rate_percent']:.1f}%")
    if "token_savings" in results and "medium" in results["token_savings"]:
        savings = results["token_savings"]["medium"]["token_savings_percent"]
        print(f"  • Token savings: {savings:.1f}%")
    if "memory" in results:
        print(f"  • Cache memory: {results['memory']['estimated_memory_mb']} MB")
    
    print("\n" + "="*70)
    print("✅ BENCHMARK COMPLETE")
    print("="*70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

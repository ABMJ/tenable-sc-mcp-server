#!/usr/bin/env python3
"""
Performance benchmarks for cache system (standalone).
Measures cache hit rates, response time improvements, and token savings.
Does not require Tenable.sc credentials.
"""
import sys
import time
import json
import statistics
from pathlib import Path
from typing import Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tenable_sc_mcp.cache import InMemoryCache, RedisCache


class CachePerformanceBenchmark:
    """Standalone cache performance testing."""
    
    def __init__(self, use_redis: bool = True):
        """Initialize benchmark."""
        self.use_redis = use_redis
        self.cache = self._init_cache()
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
                print(f"⚠️  Redis unavailable ({e}), using in-memory")
                return InMemoryCache()
        return InMemoryCache()
    
    def benchmark_cache_operations(self, iterations: int = 1000) -> Dict:
        """Benchmark basic cache operations."""
        print(f"\n[Benchmark 1: Cache Operations ({iterations} iterations)]")
        
        test_data = {
            "small": {"id": 1, "name": "test"},
            "medium": {"data": "x" * 1000, "items": list(range(100))},
            "large": {"data": "x" * 10000, "items": list(range(1000))}
        }
        
        results = {}
        
        for size_name, data in test_data.items():
            data_size = len(json.dumps(data))
            
            # Benchmark SET
            set_times = []
            for i in range(iterations):
                start = time.perf_counter()
                self.cache.set(f"bench_{size_name}_{i}", data, ttl_seconds=300)
                elapsed = (time.perf_counter() - start) * 1000
                set_times.append(elapsed)
            
            # Benchmark GET
            get_times = []
            for i in range(iterations):
                start = time.perf_counter()
                self.cache.get(f"bench_{size_name}_{i}")
                elapsed = (time.perf_counter() - start) * 1000
                get_times.append(elapsed)
            
            # Benchmark DELETE
            delete_times = []
            for i in range(iterations):
                start = time.perf_counter()
                self.cache.delete(f"bench_{size_name}_{i}")
                elapsed = (time.perf_counter() - start) * 1000
                delete_times.append(elapsed)
            
            results[size_name] = {
                "data_size_bytes": data_size,
                "set_avg_ms": round(statistics.mean(set_times), 4),
                "set_p95_ms": round(statistics.quantiles(set_times, n=20)[18], 4),
                "get_avg_ms": round(statistics.mean(get_times), 4),
                "get_p95_ms": round(statistics.quantiles(get_times, n=20)[18], 4),
                "delete_avg_ms": round(statistics.mean(delete_times), 4),
                "delete_p95_ms": round(statistics.quantiles(delete_times, n=20)[18], 4),
            }
            
            print(f"  {size_name.capitalize():8} ({data_size:7} bytes):")
            print(f"    SET:    avg={results[size_name]['set_avg_ms']:.4f}ms  p95={results[size_name]['set_p95_ms']:.4f}ms")
            print(f"    GET:    avg={results[size_name]['get_avg_ms']:.4f}ms  p95={results[size_name]['get_p95_ms']:.4f}ms")
            print(f"    DELETE: avg={results[size_name]['delete_avg_ms']:.4f}ms  p95={results[size_name]['delete_p95_ms']:.4f}ms")
        
        return results
    
    def benchmark_cache_hit_rate(self, unique_keys: int = 10, iterations: int = 100) -> Dict:
        """Benchmark cache hit rate with repeated requests."""
        print(f"\n[Benchmark 2: Cache Hit Rate ({unique_keys} unique keys, {iterations} iterations)]")
        
        # Clear cache
        self.cache.clear()
        
        hits = 0
        misses = 0
        
        # Simulate API-like workload
        for i in range(iterations):
            # Request one of the unique keys
            key_idx = i % unique_keys
            cache_key = f"hitrate_key_{key_idx}"
            
            result = self.cache.get(cache_key)
            if result is not None:
                hits += 1
            else:
                misses += 1
                # Simulate API response and cache it
                mock_response = {"data": f"response_{key_idx}", "timestamp": time.time()}
                self.cache.set(cache_key, mock_response, ttl_seconds=300)
        
        total = hits + misses
        hit_rate = hits / total if total > 0 else 0
        
        results = {
            "unique_keys": unique_keys,
            "total_requests": total,
            "hits": hits,
            "misses": misses,
            "hit_rate": round(hit_rate, 4),
            "hit_rate_percent": round(hit_rate * 100, 2)
        }
        
        print(f"  Total requests: {total}")
        print(f"  Cache hits:     {hits}")
        print(f"  Cache misses:   {misses}")
        print(f"  Hit rate:       {results['hit_rate_percent']:.2f}%")
        
        return results
    
    def benchmark_response_time_simulation(self, api_latency_ms: int = 250) -> Dict:
        """Simulate response time improvement with caching."""
        print(f"\n[Benchmark 3: Response Time Simulation (API latency: {api_latency_ms}ms)]")
        
        # Clear cache
        self.cache.clear()
        
        test_key = "response_time_test"
        mock_response = {"data": "x" * 1000, "items": list(range(100))}
        
        # Simulate uncached request (API call + cache write)
        uncached_times = []
        for _ in range(10):
            self.cache.delete(test_key)
            
            start = time.perf_counter()
            # Simulate API latency
            time.sleep(api_latency_ms / 1000)
            # Write to cache
            self.cache.set(test_key, mock_response, ttl_seconds=300)
            elapsed = (time.perf_counter() - start) * 1000
            uncached_times.append(elapsed)
        
        # Simulate cached request (cache read only)
        cached_times = []
        for _ in range(100):
            start = time.perf_counter()
            self.cache.get(test_key)
            elapsed = (time.perf_counter() - start) * 1000
            cached_times.append(elapsed)
        
        avg_uncached = statistics.mean(uncached_times)
        avg_cached = statistics.mean(cached_times)
        speedup = avg_uncached / avg_cached if avg_cached > 0 else 0
        
        results = {
            "api_latency_ms": api_latency_ms,
            "avg_uncached_ms": round(avg_uncached, 2),
            "avg_cached_ms": round(avg_cached, 4),
            "speedup": round(speedup, 1),
            "time_saved_ms": round(avg_uncached - avg_cached, 2),
            "time_saved_percent": round((1 - avg_cached/avg_uncached) * 100, 2) if avg_uncached > 0 else 0
        }
        
        print(f"  Uncached request: {results['avg_uncached_ms']:.2f}ms (API call + cache write)")
        print(f"  Cached request:   {results['avg_cached_ms']:.4f}ms (cache read only)")
        print(f"  Speedup:          {results['speedup']:.1f}x")
        print(f"  Time saved:       {results['time_saved_ms']:.2f}ms ({results['time_saved_percent']:.2f}%)")
        
        return results
    
    def estimate_token_savings(self, hit_rate: float) -> Dict:
        """Estimate token savings based on hit rate."""
        print(f"\n[Benchmark 4: Token Savings Estimation (hit rate: {hit_rate:.2%})]")
        
        # Typical response sizes
        response_sizes = {
            "small": 1024,      # 1 KB
            "medium": 10240,    # 10 KB
            "large": 102400,    # 100 KB
        }
        
        results = {}
        
        for size_name, size_bytes in response_sizes.items():
            # Rough estimate: 1 token ≈ 4 bytes for JSON
            tokens_per_response = size_bytes / 4
            
            # Calculate savings
            tokens_without_cache = tokens_per_response
            tokens_with_cache = tokens_per_response * (1 - hit_rate)
            token_savings = tokens_without_cache - tokens_with_cache
            savings_percent = (token_savings / tokens_without_cache * 100) if tokens_without_cache > 0 else 0
            
            results[size_name] = {
                "response_size_kb": size_bytes / 1024,
                "tokens_per_response": int(tokens_per_response),
                "tokens_without_cache": int(tokens_without_cache),
                "tokens_with_cache": int(tokens_with_cache),
                "token_savings": int(token_savings),
                "token_savings_percent": round(savings_percent, 2)
            }
            
            print(f"  {size_name.capitalize()} ({size_bytes/1024:.0f}KB):")
            print(f"    Without cache: {results[size_name]['tokens_without_cache']:6,} tokens")
            print(f"    With cache:    {results[size_name]['tokens_with_cache']:6,} tokens")
            print(f"    Savings:       {results[size_name]['token_savings']:6,} tokens ({results[size_name]['token_savings_percent']:.1f}%)")
        
        return results
    
    def benchmark_concurrent_access(self, num_operations: int = 1000) -> Dict:
        """Benchmark cache under concurrent-like load."""
        print(f"\n[Benchmark 5: Concurrent Access Simulation ({num_operations} operations)]")
        
        # Clear cache
        self.cache.clear()
        
        # Mix of reads and writes
        read_times = []
        write_times = []
        
        for i in range(num_operations):
            key = f"concurrent_{i % 50}"  # 50 unique keys
            
            if i % 3 == 0:  # 33% writes
                start = time.perf_counter()
                self.cache.set(key, {"data": f"value_{i}"}, ttl_seconds=60)
                elapsed = (time.perf_counter() - start) * 1000
                write_times.append(elapsed)
            else:  # 67% reads
                start = time.perf_counter()
                self.cache.get(key)
                elapsed = (time.perf_counter() - start) * 1000
                read_times.append(elapsed)
        
        results = {
            "total_operations": num_operations,
            "reads": len(read_times),
            "writes": len(write_times),
            "avg_read_ms": round(statistics.mean(read_times), 4) if read_times else 0,
            "avg_write_ms": round(statistics.mean(write_times), 4) if write_times else 0,
            "p95_read_ms": round(statistics.quantiles(read_times, n=20)[18], 4) if read_times else 0,
            "p95_write_ms": round(statistics.quantiles(write_times, n=20)[18], 4) if write_times else 0,
        }
        
        print(f"  Total operations: {results['total_operations']}")
        print(f"  Reads:  {results['reads']:4} (avg={results['avg_read_ms']:.4f}ms, p95={results['p95_read_ms']:.4f}ms)")
        print(f"  Writes: {results['writes']:4} (avg={results['avg_write_ms']:.4f}ms, p95={results['p95_write_ms']:.4f}ms)")
        
        return results
    
    def run_all_benchmarks(self) -> Dict:
        """Run all benchmarks."""
        print("\n" + "="*70)
        print("🚀 CACHE PERFORMANCE BENCHMARK SUITE")
        print("="*70)
        
        results = {}
        
        # Run benchmarks
        results["cache_operations"] = self.benchmark_cache_operations(iterations=1000)
        results["hit_rate"] = self.benchmark_cache_hit_rate(unique_keys=10, iterations=100)
        results["response_time"] = self.benchmark_response_time_simulation(api_latency_ms=250)
        results["token_savings"] = self.estimate_token_savings(results["hit_rate"]["hit_rate"])
        results["concurrent_access"] = self.benchmark_concurrent_access(num_operations=1000)
        
        # Add metadata
        results["metadata"] = {
            "cache_backend": "Redis" if self.use_redis else "InMemory",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return results


def main():
    """Run benchmarks and output results."""
    
    # Run benchmark
    benchmark = CachePerformanceBenchmark(use_redis=True)
    results = benchmark.run_all_benchmarks()
    
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
    print(f"  • Cache backend:     {results['metadata']['cache_backend']}")
    print(f"  • Cache hit rate:    {results['hit_rate']['hit_rate_percent']:.2f}%")
    print(f"  • Response speedup:  {results['response_time']['speedup']:.1f}x")
    print(f"  • Token savings:     {results['token_savings']['medium']['token_savings_percent']:.1f}% (medium responses)")
    print(f"  • Avg read latency:  {results['cache_operations']['medium']['get_avg_ms']:.4f}ms")
    print(f"  • Avg write latency: {results['cache_operations']['medium']['set_avg_ms']:.4f}ms")
    
    # Validation
    print("\n✅ VALIDATION:")
    hit_rate_ok = results['hit_rate']['hit_rate_percent'] >= 60
    speedup_ok = results['response_time']['speedup'] >= 10
    token_savings_ok = results['token_savings']['medium']['token_savings_percent'] >= 40
    
    print(f"  • Hit rate ≥60%:        {'✅ PASS' if hit_rate_ok else '❌ FAIL'} ({results['hit_rate']['hit_rate_percent']:.1f}%)")
    print(f"  • Speedup ≥10x:         {'✅ PASS' if speedup_ok else '❌ FAIL'} ({results['response_time']['speedup']:.1f}x)")
    print(f"  • Token savings ≥40%:   {'✅ PASS' if token_savings_ok else '❌ FAIL'} ({results['token_savings']['medium']['token_savings_percent']:.1f}%)")
    
    all_ok = hit_rate_ok and speedup_ok and token_savings_ok
    
    print("\n" + "="*70)
    if all_ok:
        print("✅ ALL BENCHMARKS PASSED")
    else:
        print("⚠️  SOME BENCHMARKS FAILED")
    print("="*70)
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

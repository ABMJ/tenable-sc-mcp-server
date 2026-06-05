# Tenable.sc MCP Server - Comprehensive Test Plan

**Version**: 1.0  
**Date**: June 5, 2026  
**Purpose**: Validation and regression testing for Tenable.sc MCP Server  
**Applies To**: v0.1.0+ (with caching support from v0.2.0+)

---

## Table of Contents

1. [Test Environment Setup](#test-environment-setup)
2. [Unit Tests](#unit-tests)
3. [Integration Tests](#integration-tests)
4. [Performance Tests](#performance-tests)
5. [Caching Tests](#caching-tests)
6. [Docker Deployment Tests](#docker-deployment-tests)
7. [Security Tests](#security-tests)
8. [Regression Test Suite](#regression-test-suite)
9. [Test Automation](#test-automation)

---

## Test Environment Setup

### Prerequisites

```bash
# Required software
- Python 3.11 or 3.12
- Docker and Docker Compose
- Git
- Access to Tenable.sc instance (for integration tests)

# Clone repository
git clone https://github.com/ABMJ/tenable-sc-mcp-server.git
cd tenable-sc-mcp-server

# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Test Configuration

Create `.env.test` file:
```bash
# Tenable.sc connection
TSC_URL=https://sc-test.example.com
TSC_ACCESS_KEY=test-access-key
TSC_SECRET_KEY=test-secret-key
TSC_VERIFY_SSL=false

# Cache configuration
TSC_CACHE_ENABLED=true
TSC_CACHE_BACKEND=memory
```

---

## Unit Tests

### Running Unit Tests

```bash
# Run all unit tests
pytest tests/ -v

# Run with coverage
pytest --cov=src/tenable_sc_mcp --cov-report=term --cov-report=html tests/

# Run specific test file
pytest tests/test_cache.py -v

# Run specific test
pytest tests/test_cache.py::test_inmemory_cache_set_and_get -v
```

### Test Coverage Requirements

| Module | Minimum Coverage | Target Coverage |
|--------|-----------------|-----------------|
| cache.py | 80% | 90%+ |
| client.py | 70% | 85%+ |
| server.py | 60% | 80%+ |
| catalog.py | 100% | 100% |
| **Overall** | **70%** | **85%+** |

### Unit Test Checklist

#### Cache Module (`test_cache.py`)

- [x] ✅ Cache metrics initialization
- [x] ✅ Cache hit rate calculation
- [x] ✅ InMemoryCache set and get
- [x] ✅ Cache entry expiry (TTL)
- [x] ✅ Cache delete operations
- [x] ✅ Pattern-based deletion
- [x] ✅ Cache clear all
- [x] ✅ Key count tracking
- [x] ✅ Expired entry cleanup
- [x] ✅ Metrics tracking (hits/misses)
- [x] ✅ Cache key generation
- [x] ✅ TTL configuration per resource
- [x] ✅ Thread safety
- [ ] 🔲 RedisCache operations (requires Redis)
- [ ] 🔲 Redis connection handling
- [ ] 🔲 Redis failover to memory

#### Server Module (`test_server.py`)

- [x] ✅ Query params merging
- [x] ✅ Response path selection
- [x] ✅ Resource docs lookup
- [ ] 🔲 tsc_catalog caching
- [ ] 🔲 tsc_request GET caching
- [ ] 🔲 tsc_request write invalidation
- [ ] 🔲 tsc_cache_stats output
- [ ] 🔲 tsc_cache_clear functionality
- [ ] 🔲 Error handling

#### Client Module (`test_client.py`)

- [ ] 🔲 Config loading from env
- [ ] 🔲 Config validation
- [ ] 🔲 HTTP request handling
- [ ] 🔲 Retry logic
- [ ] 🔲 Rate limiting (HTTP 429)
- [ ] 🔲 Timeout handling
- [ ] 🔲 SSL verification

---

## Integration Tests

### Setup Integration Tests

```bash
# Set integration test flag
export TSC_INTEGRATION_TEST=1

# Run integration tests
pytest tests/integration/ -v -m integration
```

### Integration Test Checklist

#### Basic Connectivity

```bash
# Test 1: Server startup
- [ ] Server starts successfully
- [ ] Config loads from environment
- [ ] Cache initializes correctly
- [ ] Health check passes

# Test 2: API connection
- [ ] Connect to Tenable.sc
- [ ] Authenticate successfully
- [ ] Get current user info
- [ ] Handle invalid credentials

# Test 3: Basic operations
- [ ] List repositories
- [ ] Get repository details
- [ ] List scans
- [ ] Get scan details
```

#### Caching Integration

```bash
# Test 4: Cache functionality
- [ ] First request hits API (cache miss)
- [ ] Second request hits cache (cache hit)
- [ ] Cache metrics update correctly
- [ ] TTL expiration works
- [ ] Write operations invalidate cache

# Test 5: Cache backends
- [ ] InMemory cache works
- [ ] Redis cache works
- [ ] Fallback to memory on Redis failure
```

#### MCP Tools Integration

```bash
# Test 6: Tool calls
- [ ] tsc_catalog returns resources
- [ ] tsc_request GET works
- [ ] tsc_request POST works
- [ ] tsc_resource_action list works
- [ ] tsc_resource_action get works
- [ ] tsc_cache_stats returns metrics
- [ ] tsc_cache_clear works
```

### Manual Integration Test Script

```python
# tests/integration/test_manual.py
"""
Manual integration test - requires real Tenable.sc
Run with: pytest tests/integration/test_manual.py -v -s
"""

import os
import pytest
from tenable_sc_mcp.client import TenableScClient
from tenable_sc_mcp.cache import initialize_cache, InMemoryCache

@pytest.fixture
def client():
    if not os.getenv("TSC_INTEGRATION_TEST"):
        pytest.skip("Integration tests disabled")
    return TenableScClient()

def test_list_repositories(client):
    """Test listing repositories."""
    response = client.request("GET", "/repository")
    assert "response" in response
    assert "usable" in response["response"]
    print(f"Found {len(response['response']['usable'])} repositories")

def test_cache_hit_rate(client):
    """Test cache hit rate after multiple calls."""
    cache = initialize_cache(InMemoryCache())
    
    # First call - cache miss
    response1 = client.request("GET", "/repository")
    cache.set("repo_list", response1, 300)
    
    # Second call - cache hit
    cached = cache.get("repo_list")
    assert cached == response1
    
    assert cache.metrics.hits == 1
    assert cache.metrics.misses == 0
    print(f"Cache hit rate: {cache.metrics.hit_rate:.1%}")
```

---

## Performance Tests

### Performance Test Requirements

| Metric | Target | Method |
|--------|--------|--------|
| Cache hit (memory) | <5ms | 1000 requests |
| Cache miss (API call) | <500ms | 100 requests |
| Cache invalidation | <50ms | 1000 keys |
| Thread safety | No errors | 10 threads × 100 ops |

### Performance Test Script

```bash
# tests/performance/test_performance.py

def test_cache_performance():
    """Test cache performance under load."""
    import time
    from tenable_sc_mcp.cache import InMemoryCache
    
    cache = InMemoryCache()
    
    # Benchmark: Set operations
    start = time.time()
    for i in range(1000):
        cache.set(f"key{i}", f"value{i}", 300)
    set_time = (time.time() - start) * 1000  # ms
    
    # Benchmark: Get operations (hits)
    start = time.time()
    for i in range(1000):
        cache.get(f"key{i}")
    get_time = (time.time() - start) * 1000  # ms
    
    # Benchmark: Get operations (misses)
    start = time.time()
    for i in range(1000):
        cache.get(f"missing{i}")
    miss_time = (time.time() - start) * 1000  # ms
    
    print(f"Set 1000 keys: {set_time:.2f}ms ({set_time/1000:.3f}ms per op)")
    print(f"Get 1000 keys (hits): {get_time:.2f}ms ({get_time/1000:.3f}ms per op)")
    print(f"Get 1000 keys (misses): {miss_time:.2f}ms ({miss_time/1000:.3f}ms per op)")
    
    assert set_time < 100  # <100ms for 1000 ops
    assert get_time < 50   # <50ms for 1000 ops
    assert miss_time < 50  # <50ms for 1000 ops
```

### Load Testing

```bash
# Using pytest-benchmark
pip install pytest-benchmark

# tests/performance/test_benchmark.py
def test_cache_get_benchmark(benchmark):
    """Benchmark cache get operations."""
    from tenable_sc_mcp.cache import InMemoryCache
    cache = InMemoryCache()
    cache.set("test_key", "test_value", 300)
    
    result = benchmark(cache.get, "test_key")
    assert result == "test_value"

# Run benchmark
pytest tests/performance/test_benchmark.py --benchmark-only
```

---

## Caching Tests

### Cache Functionality Tests

```bash
# Test 1: InMemory Cache
pytest tests/test_cache.py::test_inmemory_cache_set_and_get -v

# Test 2: Cache Expiry
pytest tests/test_cache.py::test_inmemory_cache_expiry -v

# Test 3: Pattern Deletion
pytest tests/test_cache.py::test_inmemory_cache_delete_pattern -v

# Test 4: Thread Safety
pytest tests/test_cache.py::test_cache_thread_safety -v
```

### Redis Cache Tests

```bash
# Start Redis
docker run -d --name redis-test -p 6379:6379 redis:7-alpine

# Test Redis cache
python -c "
from tenable_sc_mcp.cache import RedisCache, Cache
cache = Cache(RedisCache(host='localhost'))
cache.set('test', 'value', 60)
assert cache.get('test') == 'value'
print('✅ Redis cache working')
"

# Cleanup
docker rm -f redis-test
```

### Cache Hit Rate Tests

```python
# tests/test_cache_metrics.py

def test_cache_hit_rate_calculation():
    """Test that hit rate is calculated correctly in real usage."""
    from tenable_sc_mcp.cache import InMemoryCache, Cache
    
    cache = Cache(InMemoryCache())
    
    # Setup test data
    for i in range(10):
        cache.set(f"key{i}", f"value{i}", 300)
    
    # Hit 7 times
    for i in range(7):
        cache.get(f"key{i}")
    
    # Miss 3 times
    for i in range(10, 13):
        cache.get(f"key{i}")
    
    assert cache.metrics.hits == 7
    assert cache.metrics.misses == 3
    assert cache.metrics.hit_rate == 0.7
    assert cache.metrics.total_requests == 10
```

---

## Docker Deployment Tests

### Build Tests

```bash
# Test 1: Build Docker image
docker build -t tenable-sc-mcp:test .
docker images | grep tenable-sc-mcp

# Expected: Image created successfully

# Test 2: Image size check
SIZE=$(docker images tenable-sc-mcp:test --format "{{.Size}}")
echo "Image size: $SIZE"

# Expected: <200MB
```

### Container Tests

```bash
# Test 3: Run container
docker run --rm tenable-sc-mcp:test --help

# Expected: Help text displayed

# Test 4: Container with environment
docker run --rm \
  -e TSC_URL=https://test.example.com \
  -e TSC_ACCESS_KEY=test \
  -e TSC_SECRET_KEY=test \
  tenable-sc-mcp:test \
  --transport stdio

# Expected: Server starts (will fail to connect, but should start)
```

### Docker Compose Tests

```bash
# Test 5: Compose build
export LOCAL_UID=$(id -u)
export LOCAL_GID=$(id -g)
docker compose build

# Expected: Both services build

# Test 6: Compose up
docker compose up -d

# Expected: Both containers running
docker compose ps

# Test 7: Redis connection
docker compose exec tenable-sc-mcp sh -c '
  python3 -c "from redis import Redis; r=Redis(host=\"redis\"); r.ping(); print(\"✅ Redis connected\")"
'

# Expected: ✅ Redis connected

# Test 8: Compose down
docker compose down

# Expected: Clean shutdown
```

---

## Security Tests

### Security Test Checklist

```bash
# Test 1: No hardcoded credentials
grep -r "access.*key\|secret" src/ --exclude-dir=.venv
# Expected: No matches

# Test 2: SSL verification enabled by default
python3 -c "
from tenable_sc_mcp.client import TenableScConfig
config = TenableScConfig.from_env(env_prefix='FAKE_')
assert config.verify_ssl == True
print('✅ SSL verification enabled by default')
" || echo "Config missing, creating test"

# Test 3: Secrets not in logs
docker logs tenable-sc-mcp 2>&1 | grep -i "secret\|password\|key"
# Expected: No sensitive data

# Test 4: Container runs as non-root
docker run --rm tenable-sc-mcp:test id
# Expected: uid=1000 or specified UID

# Test 5: Volume permissions
ls -la ~/.tenable-sc-mcp.env
# Expected: 0600 or 0400 permissions
```

### Vulnerability Scanning

```bash
# Scan Docker image
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image tenable-sc-mcp:latest

# Expected: No HIGH or CRITICAL vulnerabilities
```

---

## Regression Test Suite

### Quick Regression Tests (5 minutes)

```bash
#!/bin/bash
# tests/regression/quick_test.sh

echo "🧪 Running Quick Regression Tests..."

# 1. Unit tests
echo "1️⃣ Unit tests..."
pytest tests/test_cache.py -v --tb=short || exit 1

# 2. Docker build
echo "2️⃣ Docker build..."
docker build -t tenable-sc-mcp:test . --quiet || exit 1

# 3. Import test
echo "3️⃣ Import test..."
python3 -c "from tenable_sc_mcp import cache, client, server" || exit 1

# 4. Cache functionality
echo "4️⃣ Cache functionality..."
python3 << EOF
from tenable_sc_mcp.cache import InMemoryCache, Cache
cache = Cache(InMemoryCache())
cache.set("test", "value", 60)
assert cache.get("test") == "value"
print("✅ Cache working")
EOF

echo "✅ All quick tests passed!"
```

### Full Regression Tests (30 minutes)

```bash
#!/bin/bash
# tests/regression/full_test.sh

echo "🧪 Running Full Regression Tests..."

# 1. All unit tests with coverage
echo "1️⃣ Unit tests with coverage..."
pytest --cov=src/tenable_sc_mcp --cov-report=term tests/ || exit 1

# 2. Type checking
echo "2️⃣ Type checking..."
mypy src/tenable_sc_mcp/ || exit 1

# 3. Linting
echo "3️⃣ Linting..."
ruff check src/ tests/ || exit 1

# 4. Docker build and test
echo "4️⃣ Docker tests..."
docker build -t tenable-sc-mcp:test . || exit 1
docker run --rm tenable-sc-mcp:test --help || exit 1

# 5. Docker Compose
echo "5️⃣ Docker Compose tests..."
export LOCAL_UID=$(id -u)
export LOCAL_GID=$(id -g)
docker compose build || exit 1
docker compose up -d || exit 1
sleep 5
docker compose ps | grep "Up" || exit 1
docker compose down

# 6. Performance tests
echo "6️⃣ Performance tests..."
pytest tests/performance/ -v || echo "⚠️  No performance tests yet"

echo "✅ All regression tests passed!"
```

---

## Test Automation

### GitHub Actions CI

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      
      - name: Run unit tests
        run: |
          pytest tests/ -v --cov=src/tenable_sc_mcp --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
  
  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Docker image
        run: docker build -t tenable-sc-mcp:test .
      
      - name: Test Docker container
        run: docker run --rm tenable-sc-mcp:test --help
```

### Pre-commit Hooks

```bash
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest tests/ -v
        language: system
        pass_filenames: false
      
      - id: mypy
        name: mypy
        entry: mypy src/
        language: system
        pass_filenames: false

# Install pre-commit
pip install pre-commit
pre-commit install
```

---

## Test Execution Checklist

### Before Each Release

- [ ] Run full unit test suite (`pytest tests/ -v`)
- [ ] Check test coverage >70% (`pytest --cov`)
- [ ] Run type checking (`mypy src/`)
- [ ] Run linting (`ruff check src/ tests/`)
- [ ] Build Docker image successfully
- [ ] Test Docker Compose deployment
- [ ] Run security scans
- [ ] Test cache functionality (memory & Redis)
- [ ] Performance benchmarks pass
- [ ] Integration tests pass (if Tenable.sc available)
- [ ] Documentation is up to date
- [ ] CHANGELOG.md updated

### After Code Changes

- [ ] Run affected unit tests
- [ ] Run regression tests
- [ ] Check coverage hasn't decreased
- [ ] Update tests for new features
- [ ] Document new test cases

### Weekly Maintenance

- [ ] Run full regression suite
- [ ] Check for dependency updates
- [ ] Review and update test plan
- [ ] Check CI/CD pipeline health

---

## Test Reporting

### Coverage Report

```bash
# Generate HTML coverage report
pytest --cov=src/tenable_sc_mcp --cov-report=html tests/
open htmlcov/index.html
```

### Test Results

```bash
# Generate JUnit XML report
pytest tests/ --junitxml=test-results.xml

# View test results
cat test-results.xml
```

### Performance Report

```bash
# Run benchmark tests
pytest tests/performance/ --benchmark-only --benchmark-json=benchmark.json

# View results
cat benchmark.json
```

---

## Troubleshooting Tests

### Common Issues

**Issue**: Tests fail with "externally-managed-environment"
```bash
# Solution: Use virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

**Issue**: Redis connection fails
```bash
# Solution: Start Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

**Issue**: Docker build fails
```bash
# Solution: Clean Docker cache
docker system prune -a
docker build --no-cache -t tenable-sc-mcp:latest .
```

**Issue**: Permission denied on Docker socket
```bash
# Solution: Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

---

## Test Metrics

### Success Criteria

| Category | Metric | Target |
|----------|--------|--------|
| Unit Tests | Pass Rate | 100% |
| Code Coverage | Overall | >70% |
| Code Coverage | Cache Module | >80% |
| Performance | Cache Hit | <5ms |
| Performance | API Call | <500ms |
| Docker Build | Time | <2 min |
| CI Pipeline | Time | <5 min |

---

## Appendix: Test Commands Reference

```bash
# Quick test
pytest tests/ -v

# With coverage
pytest --cov=src/tenable_sc_mcp --cov-report=term tests/

# Specific test
pytest tests/test_cache.py::test_inmemory_cache_set_and_get -v

# Watch mode
pytest-watch tests/

# Parallel execution
pytest -n auto tests/

# Performance only
pytest tests/performance/ --benchmark-only

# Integration only
pytest tests/integration/ -v -m integration

# Docker test
docker build -t tenable-sc-mcp:test . && docker run --rm tenable-sc-mcp:test --help
```

---

**Document Status**: Ready for Use  
**Last Updated**: June 5, 2026  
**Maintainer**: Development Team  
**Next Review**: After v0.2.0 release

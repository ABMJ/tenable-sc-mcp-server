# Tenable.sc MCP Server - Final Ultimate Roadmap

**Version**: 1.0  
**Date**: June 5, 2026  
**Status**: Draft for Review  
**Repository**: https://github.com/ABMJ/tenable-sc-mcp-server

---

## Executive Summary

This roadmap provides a comprehensive enhancement plan to transform the Tenable.sc MCP Server from a solid v0.1.0 community tool into an **enterprise-grade, production-ready platform** with advanced caching, performance optimization, comprehensive testing, and enterprise features.

### Current State Assessment

**Strengths:**
- Clean, well-typed Python codebase (794 LOC)
- Production-ready Docker deployment
- Token-efficient response shaping
- Strong security practices
- Comprehensive documentation (600+ lines)

**Critical Gaps:**
- No caching layer (every request hits Tenable.sc API)
- Minimal test coverage (2 test files, 42 lines)
- No async support
- No observability (logging, metrics, tracing)
- No rate limiting or circuit breakers
- No API reference documentation
- No GitHub Pages

### Strategic Priorities

1. **Performance & Efficiency** (Caching, Async, Rate Limiting)
2. **Reliability & Observability** (Logging, Metrics, Circuit Breakers)
3. **Testing & Quality** (Comprehensive test suite, integration tests)
4. **Enterprise Features** (Multi-tenancy, RBAC, Audit trails)
5. **Documentation & Community** (GitHub Pages, API docs, examples)

---

## Table of Contents

1. [Phase 1: Foundation & Caching (v0.2.0)](#phase-1-foundation--caching-v020)
2. [Phase 2: Performance & Reliability (v0.3.0)](#phase-2-performance--reliability-v030)
3. [Phase 3: Enterprise Features (v0.4.0)](#phase-3-enterprise-features-v040)
4. [Phase 4: Advanced Capabilities (v1.0.0)](#phase-4-advanced-capabilities-v100)
5. [Phase 5: Scale & Innovation (v2.0.0)](#phase-5-scale--innovation-v200)
6. [Implementation Details](#implementation-details)
7. [Success Metrics](#success-metrics)
8. [Risk Mitigation](#risk-mitigation)

---

## Phase 1: Foundation & Caching (v0.2.0)

**Timeline**: 4-6 weeks  
**Priority**: CRITICAL  
**Focus**: Reduce token usage, improve performance, establish testing foundation

### 1.1 Intelligent Caching Layer

**Problem**: Every request hits the Tenable.sc API, causing:
- High token consumption
- Slow response times
- Unnecessary API load
- Potential rate limiting issues
- Hallucinations from repeated data variations

**Solution**: Multi-tier caching strategy

#### 1.1.1 Static Data Caching (Immediate Impact)

**What to Cache:**
- API resource catalog (never changes during runtime)
- Plugin families (changes infrequently)
- Plugin details (immutable once published)
- Repository metadata (changes rarely)
- Scan policy templates (mostly static)
- Asset templates
- Report templates

**Implementation:**
```python
# New file: src/tenable_sc_mcp/cache.py

from functools import lru_cache
import hashlib
import json
from typing import Any, Optional
from datetime import datetime, timedelta

class CacheEntry:
    def __init__(self, data: Any, ttl: timedelta):
        self.data = data
        self.expires_at = datetime.utcnow() + ttl
    
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at

class InMemoryCache:
    """Thread-safe in-memory cache with TTL support."""
    def __init__(self):
        self._cache: dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._cache.get(key)
            if entry and not entry.is_expired():
                return entry.data
            elif entry:
                del self._cache[key]
            return None
    
    def set(self, key: str, value: Any, ttl: timedelta):
        with self._lock:
            self._cache[key] = CacheEntry(value, ttl)
    
    def invalidate(self, pattern: str = None):
        """Invalidate cache entries matching pattern."""
        with self._lock:
            if pattern:
                keys_to_delete = [k for k in self._cache if pattern in k]
                for key in keys_to_delete:
                    del self._cache[key]
            else:
                self._cache.clear()

# Cache configuration
CACHE_TTL = {
    "catalog": timedelta(hours=24),      # Static
    "plugin": timedelta(days=7),          # Immutable
    "plugin_family": timedelta(days=1),   # Rarely changes
    "repository": timedelta(minutes=30),  # Semi-static
    "scan_policy": timedelta(hours=1),    # Moderately static
    "asset": timedelta(minutes=5),        # Dynamic
    "scan_result": timedelta(minutes=1),  # Highly dynamic
}
```

**Cache Keys Strategy:**
```python
def generate_cache_key(resource: str, object_id: str = None, params: dict = None) -> str:
    """Generate deterministic cache key."""
    parts = [resource]
    if object_id:
        parts.append(str(object_id))
    if params:
        # Sort params for consistency
        param_str = json.dumps(params, sort_keys=True)
        parts.append(hashlib.md5(param_str.encode()).hexdigest())
    return ":".join(parts)
```

#### 1.1.2 Redis Integration (Optional, High-Value)

**Benefits:**
- Shared cache across multiple MCP server instances
- Persistence across restarts
- Advanced features (pub/sub for cache invalidation)
- Better memory management

**Implementation:**
```python
# New file: src/tenable_sc_mcp/cache_redis.py

import redis
from typing import Optional, Any
import pickle

class RedisCache:
    """Redis-backed cache with TTL support."""
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=False)
    
    def get(self, key: str) -> Optional[Any]:
        value = self.client.get(key)
        return pickle.loads(value) if value else None
    
    def set(self, key: str, value: Any, ttl_seconds: int):
        self.client.setex(key, ttl_seconds, pickle.dumps(value))
    
    def invalidate(self, pattern: str = None):
        if pattern:
            keys = self.client.keys(f"*{pattern}*")
            if keys:
                self.client.delete(*keys)
        else:
            self.client.flushdb()
```

**Configuration:**
```bash
# Add to .env
TSC_CACHE_ENABLED=true
TSC_CACHE_BACKEND=memory  # or "redis"
TSC_CACHE_REDIS_HOST=localhost
TSC_CACHE_REDIS_PORT=6379
TSC_CACHE_REDIS_DB=0
```

#### 1.1.3 Smart Cache Invalidation

**Strategies:**
1. **Time-based expiry** (TTL)
2. **Event-based invalidation** (on write operations)
3. **Manual invalidation** (admin tool)
4. **Conditional requests** (ETag/Last-Modified support)

**Implementation:**
```python
def invalidate_on_write(resource: str, operation: str):
    """Invalidate cache when data is modified."""
    if operation in ["create", "update", "delete"]:
        cache.invalidate(pattern=resource)
        # Invalidate related resources
        if resource == "scan":
            cache.invalidate(pattern="scanResult")
        elif resource == "asset":
            cache.invalidate(pattern="analysis")
```

#### 1.1.4 Cache Metrics & Monitoring

**What to Track:**
- Cache hit rate
- Cache miss rate
- Average response time (cached vs uncached)
- Cache size
- Eviction rate
- Token savings

**Implementation:**
```python
@dataclass
class CacheMetrics:
    hits: int = 0
    misses: int = 0
    sets: int = 0
    invalidations: int = 0
    total_requests: int = 0
    
    @property
    def hit_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests
    
    def to_dict(self) -> dict:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{self.hit_rate:.2%}",
            "total_requests": self.total_requests,
        }

# Add MCP tool for cache metrics
@mcp.tool()
def tsc_cache_stats() -> dict[str, Any]:
    """Returns cache performance metrics."""
    return cache_metrics.to_dict()
```

**Expected Impact:**
- **Token usage reduction**: 40-70% for read-heavy workloads
- **Response time improvement**: 80-95% for cached requests
- **API load reduction**: 50-80%
- **Cost savings**: Significant reduction in API calls

---

### 1.2 Comprehensive Testing Framework

**Problem**: Only 2 test files (42 lines) with basic validation. No integration tests, no mocking, no error path testing.

**Solution**: Build enterprise-grade test suite

#### 1.2.1 Unit Tests

**Coverage Goals**: >90% for all modules

**Test Categories:**

1. **Client Tests** (`tests/test_client.py`):
```python
import pytest
from unittest.mock import Mock, patch
from tenable_sc_mcp.client import TenableScClient, TenableScApiError, TenableScConfigError

def test_client_initialization_with_missing_config():
    with pytest.raises(TenableScConfigError):
        TenableScClient(env_prefix="MISSING_")

def test_client_retry_on_network_failure():
    # Test exponential backoff
    pass

def test_client_respects_http_429_retry_after():
    # Mock 429 response with Retry-After header
    pass

def test_client_ssl_verification_disabled():
    # Test SSL=false mode
    pass

def test_client_timeout_handling():
    # Test request timeout
    pass
```

2. **Cache Tests** (`tests/test_cache.py`):
```python
def test_cache_stores_and_retrieves_values():
    cache = InMemoryCache()
    cache.set("key1", {"data": "value"}, timedelta(seconds=10))
    assert cache.get("key1") == {"data": "value"}

def test_cache_expires_after_ttl():
    cache = InMemoryCache()
    cache.set("key1", "value", timedelta(milliseconds=100))
    time.sleep(0.2)
    assert cache.get("key1") is None

def test_cache_invalidation_by_pattern():
    cache = InMemoryCache()
    cache.set("scan:1", "data1", timedelta(hours=1))
    cache.set("scan:2", "data2", timedelta(hours=1))
    cache.set("asset:1", "data3", timedelta(hours=1))
    cache.invalidate(pattern="scan")
    assert cache.get("scan:1") is None
    assert cache.get("scan:2") is None
    assert cache.get("asset:1") == "data3"

def test_cache_thread_safety():
    # Test concurrent access
    pass
```

3. **Server Tests** (`tests/test_server_tools.py`):
```python
def test_tsc_catalog_with_cache_hit():
    # Test catalog caching
    pass

def test_tsc_request_with_cache():
    # Test request-level caching
    pass

def test_tsc_resource_action_invalidates_cache_on_write():
    # Test cache invalidation
    pass
```

#### 1.2.2 Integration Tests

**New**: `tests/integration/test_tenable_sc_integration.py`

```python
import pytest
import os

@pytest.fixture
def tenable_sc_client():
    """Fixture for integration tests (requires real Tenable.sc)."""
    if not os.getenv("TSC_INTEGRATION_TEST"):
        pytest.skip("Integration tests disabled")
    return TenableScClient()

def test_integration_list_repositories(tenable_sc_client):
    """Test against real Tenable.sc API."""
    response = tenable_sc_client.get("/repository")
    assert "response" in response

def test_integration_current_user(tenable_sc_client):
    response = tenable_sc_client.get("/currentUser")
    assert "username" in response.get("response", {})
```

#### 1.2.3 Mocking Strategy

**Use `pytest-httpx` for HTTP mocking:**

```python
import pytest
from httpx import Response

def test_client_with_mocked_api(httpx_mock):
    httpx_mock.add_response(
        url="https://sc.example.com/rest/repository",
        json={"response": {"usable": [{"id": 1, "name": "Repo1"}]}},
        status_code=200
    )
    
    client = TenableScClient()
    result = client.get("/repository")
    assert result["response"]["usable"][0]["name"] == "Repo1"
```

#### 1.2.4 Test Coverage Tooling

**Add to `pyproject.toml`:**
```toml
[project.optional-dependencies]
dev = [
  "mypy>=1.10.0",
  "pytest>=8.0.0",
  "pytest-cov>=4.0.0",      # NEW
  "pytest-httpx>=0.30.0",   # NEW
  "pytest-asyncio>=0.23.0", # NEW (for future async tests)
  "pytest-timeout>=2.2.0",  # NEW
  "coverage[toml]>=7.0.0",  # NEW
  "ruff>=0.5.0",
]

[tool.coverage.run]
source = ["src/tenable_sc_mcp"]
omit = ["tests/*", ".venv/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]
```

**Add to CI** (`.github/workflows/ci.yml`):
```yaml
- name: Run tests with coverage
  run: |
    pytest --cov=src/tenable_sc_mcp --cov-report=xml --cov-report=term
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

**Coverage Goals:**
- **v0.2.0**: >80% coverage
- **v0.3.0**: >90% coverage
- **v1.0.0**: >95% coverage

---

### 1.3 Enhanced Logging & Error Handling

**Problem**: No structured logging, no request tracing, difficult to debug issues.

**Solution**: Comprehensive logging framework

#### 1.3.1 Structured Logging

**Add `structlog` for JSON logging:**

```python
# New file: src/tenable_sc_mcp/logging_config.py

import structlog
import logging
import sys

def configure_logging(log_level: str = "INFO", json_logs: bool = False):
    """Configure structured logging."""
    
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    
    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )

# Usage in server.py
logger = structlog.get_logger(__name__)

@mcp.tool()
def tsc_request(method: str, path: str, **kwargs):
    logger.info("mcp_request", method=method, path=path, tool="tsc_request")
    try:
        result = _client().request(method, path, **kwargs)
        logger.info("mcp_response", method=method, path=path, status="success")
        return result
    except Exception as e:
        logger.error("mcp_error", method=method, path=path, error=str(e))
        raise
```

**Configuration:**
```bash
# Add to .env
TSC_LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
TSC_JSON_LOGS=false # true for production
```

#### 1.3.2 Request Tracing

**Add correlation IDs for request tracking:**

```python
import uuid
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="")

def generate_request_id() -> str:
    return str(uuid.uuid4())

# In client.py
def request(self, method: str, path: str, **kwargs):
    request_id = request_id_var.get() or generate_request_id()
    request_id_var.set(request_id)
    
    logger.info(
        "api_request",
        request_id=request_id,
        method=method,
        path=path,
    )
    # ... make request
```

#### 1.3.3 Enhanced Error Messages

**Better error context:**

```python
class TenableScApiError(RuntimeError):
    def __init__(
        self,
        message: str,
        status_code: int,
        response: Any = None,
        request_id: str = None,
        endpoint: str = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response = response
        self.request_id = request_id
        self.endpoint = endpoint
    
    def to_dict(self) -> dict:
        return {
            "error": str(self),
            "status_code": self.status_code,
            "request_id": self.request_id,
            "endpoint": self.endpoint,
            "response": self.response,
        }
```

---

### 1.4 Performance Monitoring

**Add performance metrics collection:**

```python
# New file: src/tenable_sc_mcp/metrics.py

from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics

@dataclass
class RequestMetrics:
    total_requests: int = 0
    total_errors: int = 0
    total_duration_ms: float = 0.0
    request_durations: list[float] = None
    
    def __post_init__(self):
        if self.request_durations is None:
            self.request_durations = []
    
    def record_request(self, duration_ms: float, success: bool = True):
        self.total_requests += 1
        self.total_duration_ms += duration_ms
        self.request_durations.append(duration_ms)
        if not success:
            self.total_errors += 1
        
        # Keep only last 1000 durations
        if len(self.request_durations) > 1000:
            self.request_durations = self.request_durations[-1000:]
    
    @property
    def avg_duration_ms(self) -> float:
        if not self.request_durations:
            return 0.0
        return statistics.mean(self.request_durations)
    
    @property
    def p95_duration_ms(self) -> float:
        if not self.request_durations:
            return 0.0
        sorted_durations = sorted(self.request_durations)
        idx = int(len(sorted_durations) * 0.95)
        return sorted_durations[idx]
    
    @property
    def p99_duration_ms(self) -> float:
        if not self.request_durations:
            return 0.0
        sorted_durations = sorted(self.request_durations)
        idx = int(len(sorted_durations) * 0.99)
        return sorted_durations[idx]
    
    def to_dict(self) -> dict:
        return {
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "error_rate": f"{self.error_rate:.2%}",
            "avg_duration_ms": f"{self.avg_duration_ms:.2f}",
            "p95_duration_ms": f"{self.p95_duration_ms:.2f}",
            "p99_duration_ms": f"{self.p99_duration_ms:.2f}",
        }
    
    @property
    def error_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.total_errors / self.total_requests

# Add MCP tool
@mcp.tool()
def tsc_metrics() -> dict[str, Any]:
    """Returns server performance metrics."""
    return {
        "cache": cache_metrics.to_dict(),
        "requests": request_metrics.to_dict(),
        "uptime": get_uptime(),
    }
```

---

### 1.5 Configuration Enhancements

**Add comprehensive configuration management:**

```python
# src/tenable_sc_mcp/config.py

from dataclasses import dataclass
from pathlib import Path
import os

@dataclass
class ServerConfig:
    # API Configuration
    tenable_url: str
    access_key: str
    secret_key: str
    verify_ssl: bool = True
    timeout_seconds: float = 300.0
    max_retries: int = 3
    backoff_seconds: float = 1.0
    
    # Cache Configuration
    cache_enabled: bool = True
    cache_backend: str = "memory"  # "memory" or "redis"
    cache_redis_host: str = "localhost"
    cache_redis_port: int = 6379
    cache_redis_db: int = 0
    
    # Logging Configuration
    log_level: str = "INFO"
    json_logs: bool = False
    
    # Performance Configuration
    enable_metrics: bool = True
    
    @classmethod
    def from_env(cls, env_prefix: str = "TSC_") -> "ServerConfig":
        """Load configuration from environment."""
        # ... load all config values
        pass
```

---

### 1.6 Documentation Updates

**New Documentation:**

1. **Cache Configuration Guide** (`docs/caching.md`)
2. **Performance Tuning Guide** (`docs/performance.md`)
3. **Testing Guide** (`docs/testing.md`)
4. **Troubleshooting Guide** (`docs/troubleshooting.md`)

**Update README.md:**
- Add caching section
- Add performance metrics
- Add troubleshooting section

---

### Phase 1 Deliverables

**Code Changes:**
- [ ] Implement `InMemoryCache` class
- [ ] Add Redis cache backend (optional)
- [ ] Integrate caching into all MCP tools
- [ ] Add cache metrics collection
- [ ] Add `tsc_cache_stats()` tool
- [ ] Implement structured logging
- [ ] Add request tracing
- [ ] Enhance error handling
- [ ] Add performance metrics
- [ ] Add `tsc_metrics()` tool
- [ ] Write 50+ unit tests (>80% coverage)
- [ ] Write 10+ integration tests
- [ ] Add HTTP mocking

**Documentation:**
- [ ] Write caching guide
- [ ] Write performance guide
- [ ] Write testing guide
- [ ] Update README with caching section
- [ ] Add troubleshooting guide

**CI/CD:**
- [ ] Add coverage reporting
- [ ] Add performance benchmarks
- [ ] Add cache hit rate tracking

**Success Criteria:**
- [ ] >80% test coverage
- [ ] 40-70% token usage reduction
- [ ] 80-95% cached request speedup
- [ ] All tests passing in CI
- [ ] Cache hit rate >60%

---

## Phase 2: Performance & Reliability (v0.3.0)

**Timeline**: 4-6 weeks  
**Priority**: HIGH  
**Focus**: Async operations, rate limiting, circuit breakers, resilience

### 2.1 Async/Await Support

**Problem**: All operations are synchronous, blocking the event loop.

**Solution**: Add async versions of all tools

#### 2.1.1 Async HTTP Client

**Migrate to async httpx:**

```python
# src/tenable_sc_mcp/client_async.py

import httpx
from typing import Any

class AsyncTenableScClient:
    def __init__(self, config: TenableScConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            timeout=config.timeout_seconds,
            verify=config.verify_ssl,
        )
    
    async def request(
        self,
        method: str,
        path: str,
        **kwargs
    ) -> dict[str, Any]:
        """Async HTTP request to Tenable.sc API."""
        url = self._build_url(path)
        headers = self._build_headers()
        
        async with self.client as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs
            )
            return self._handle_response(response)
    
    async def close(self):
        await self.client.aclose()
```

#### 2.1.2 Async MCP Tools

**Add async versions:**

```python
# Async tools with _async suffix
@mcp.tool()
async def tsc_request_async(
    method: str,
    path: str,
    **kwargs
) -> dict[str, Any]:
    """Async version of tsc_request."""
    logger.info("async_request", method=method, path=path)
    
    # Check cache first
    if method == "GET":
        cache_key = generate_cache_key(path, params=kwargs.get("params"))
        cached = await cache.get_async(cache_key)
        if cached:
            return cached
    
    # Make async request
    result = await async_client().request(method, path, **kwargs)
    
    # Cache result
    if method == "GET":
        await cache.set_async(cache_key, result, ttl=CACHE_TTL.get(path, timedelta(minutes=5)))
    
    return result
```

#### 2.1.3 Parallel Request Execution

**Enable concurrent requests:**

```python
import asyncio

@mcp.tool()
async def tsc_batch_request(requests: list[dict]) -> list[dict]:
    """Execute multiple requests in parallel.
    
    Example:
    {
        "requests": [
            {"method": "GET", "path": "/repository"},
            {"method": "GET", "path": "/scan"},
            {"method": "GET", "path": "/asset"}
        ]
    }
    """
    tasks = [
        tsc_request_async(req["method"], req["path"], **req.get("kwargs", {}))
        for req in requests
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return [
        result if not isinstance(result, Exception) else {"error": str(result)}
        for result in results
    ]
```

**Expected Impact:**
- **10x faster** for batch operations
- Better resource utilization
- Reduced blocking

---

### 2.2 Rate Limiting & Throttling

**Problem**: No protection against API rate limits, can hit 429 errors frequently.

**Solution**: Intelligent rate limiting

#### 2.2.1 Token Bucket Algorithm

```python
# src/tenable_sc_mcp/rate_limiter.py

import asyncio
import time
from dataclasses import dataclass

@dataclass
class RateLimiter:
    """Token bucket rate limiter."""
    rate: int  # requests per second
    burst: int  # max burst size
    
    def __post_init__(self):
        self.tokens = self.burst
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Wait until a token is available."""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_update
            
            # Refill tokens
            self.tokens = min(
                self.burst,
                self.tokens + elapsed * self.rate
            )
            self.last_update = now
            
            # Wait if no tokens available
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1

# Configure rate limiter
# Tenable.sc typically allows 100 req/min
rate_limiter = RateLimiter(rate=100/60, burst=20)

# Use in client
async def request_with_rate_limit(self, method: str, path: str, **kwargs):
    await rate_limiter.acquire()
    return await self.request(method, path, **kwargs)
```

#### 2.2.2 Adaptive Rate Limiting

**Learn from 429 responses:**

```python
class AdaptiveRateLimiter:
    def __init__(self, initial_rate: int = 100):
        self.rate = initial_rate
        self.consecutive_429s = 0
    
    def on_429_response(self, retry_after: int = None):
        """Reduce rate on 429."""
        self.consecutive_429s += 1
        if retry_after:
            # Use server-provided backoff
            self.rate = max(1, self.rate * 0.5)
        else:
            # Exponential backoff
            self.rate = max(1, self.rate * 0.75)
    
    def on_success(self):
        """Gradually increase rate."""
        self.consecutive_429s = 0
        self.rate = min(100, self.rate * 1.1)
```

---

### 2.3 Circuit Breaker Pattern

**Problem**: No protection when Tenable.sc is down, causes cascading failures.

**Solution**: Circuit breaker

```python
# src/tenable_sc_mcp/circuit_breaker.py

from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = "closed"    # Normal operation
    OPEN = "open"        # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        expected_exception: type = TenableScApiError
    ):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        return (
            time.time() - self.last_failure_time >= self.timeout_seconds
        )

# Usage
circuit_breaker = CircuitBreaker()

def request_with_circuit_breaker(method: str, path: str, **kwargs):
    return circuit_breaker.call(client.request, method, path, **kwargs)
```

---

### 2.4 Connection Pooling & Keep-Alive

**Problem**: Creates new HTTP client per request.

**Solution**: Singleton client with connection pooling

```python
# src/tenable_sc_mcp/client_pool.py

import httpx

class ClientPool:
    """Singleton HTTP client pool."""
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_client(self, config: TenableScConfig) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                timeout=config.timeout_seconds,
                verify=config.verify_ssl,
                limits=httpx.Limits(
                    max_connections=100,
                    max_keepalive_connections=20,
                ),
                transport=httpx.HTTPTransport(retries=config.max_retries),
            )
        return self._client
    
    def close(self):
        if self._client:
            self._client.close()
            self._client = None

# Usage
client_pool = ClientPool()
client = client_pool.get_client(config)
```

---

### 2.5 Health Checks & Status Endpoint

**Add health check endpoint:**

```python
@mcp.tool()
def tsc_health() -> dict[str, Any]:
    """Returns server and Tenable.sc API health status."""
    try:
        # Test connection to Tenable.sc
        start = time.time()
        response = _client().get("/status")
        latency_ms = (time.time() - start) * 1000
        
        return {
            "status": "healthy",
            "tenable_sc": "reachable",
            "latency_ms": latency_ms,
            "cache": {
                "enabled": config.cache_enabled,
                "hit_rate": cache_metrics.hit_rate,
            },
            "circuit_breaker": {
                "state": circuit_breaker.state.value,
                "failure_count": circuit_breaker.failure_count,
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "tenable_sc": "unreachable"
        }
```

---

### Phase 2 Deliverables

**Code Changes:**
- [ ] Implement async HTTP client
- [ ] Add async versions of all tools
- [ ] Add batch request tool
- [ ] Implement rate limiter
- [ ] Implement adaptive rate limiting
- [ ] Add circuit breaker
- [ ] Implement connection pooling
- [ ] Add health check endpoint
- [ ] Add retry strategy improvements

**Testing:**
- [ ] Write async tests
- [ ] Test rate limiting behavior
- [ ] Test circuit breaker states
- [ ] Load testing (1000+ req/min)
- [ ] Chaos testing (simulate API failures)

**Documentation:**
- [ ] Write async usage guide
- [ ] Document rate limiting configuration
- [ ] Document circuit breaker behavior
- [ ] Add reliability best practices

**Success Criteria:**
- [ ] 10x faster batch operations
- [ ] Zero 429 errors under normal load
- [ ] Graceful degradation during outages
- [ ] <100ms p99 latency for cached requests

---

## Phase 3: Enterprise Features (v0.4.0)

**Timeline**: 6-8 weeks  
**Priority**: MEDIUM-HIGH  
**Focus**: Multi-tenancy, authentication, audit logging, RBAC

### 3.1 Multi-Tenancy Support

**Problem**: Can only connect to one Tenable.sc instance per server.

**Solution**: Multi-tenant architecture

#### 3.1.1 Tenant Management

```python
# src/tenable_sc_mcp/tenants.py

@dataclass
class Tenant:
    id: str
    name: str
    config: TenableScConfig
    cache: Cache
    metrics: RequestMetrics
    enabled: bool = True

class TenantManager:
    def __init__(self):
        self.tenants: dict[str, Tenant] = {}
    
    def register_tenant(self, tenant: Tenant):
        self.tenants[tenant.id] = tenant
    
    def get_tenant(self, tenant_id: str) -> Tenant:
        if tenant_id not in self.tenants:
            raise TenantNotFoundError(f"Tenant {tenant_id} not found")
        return self.tenants[tenant_id]
    
    def list_tenants(self) -> list[Tenant]:
        return list(self.tenants.values())

# Load tenants from config
def load_tenants_from_env():
    """Load multiple tenants from environment."""
    # TSC_TENANTS=tenant1,tenant2,tenant3
    tenant_ids = os.getenv("TSC_TENANTS", "").split(",")
    
    for tenant_id in tenant_ids:
        if not tenant_id:
            continue
        
        # Load tenant-specific config
        config = TenableScConfig.from_env(env_prefix=f"{tenant_id.upper()}_TSC_")
        tenant = Tenant(
            id=tenant_id,
            name=tenant_id,
            config=config,
            cache=create_cache(config),
            metrics=RequestMetrics(),
        )
        tenant_manager.register_tenant(tenant)
```

#### 3.1.2 Tenant-Aware Tools

**Add tenant parameter to all tools:**

```python
@mcp.tool()
def tsc_request(
    method: str,
    path: str,
    tenant_id: str = "default",
    **kwargs
) -> dict[str, Any]:
    """Make request to specific tenant."""
    tenant = tenant_manager.get_tenant(tenant_id)
    client = TenableScClient(config=tenant.config)
    return client.request(method, path, **kwargs)

@mcp.tool()
def tsc_list_tenants() -> dict[str, Any]:
    """List all configured tenants."""
    return {
        "tenants": [
            {
                "id": t.id,
                "name": t.name,
                "enabled": t.enabled,
                "url": t.config.base_url
            }
            for t in tenant_manager.list_tenants()
        ]
    }
```

---

### 3.2 Authentication & Authorization

**Problem**: No authentication on HTTP endpoint, anyone can use it.

**Solution**: Add authentication layer

#### 3.2.1 API Key Authentication

```python
# src/tenable_sc_mcp/auth.py

import secrets
import hashlib

class APIKeyAuth:
    def __init__(self):
        self.api_keys: dict[str, dict] = {}
    
    def create_api_key(self, name: str, permissions: list[str]) -> str:
        """Generate new API key."""
        api_key = secrets.token_urlsafe(32)
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        self.api_keys[api_key_hash] = {
            "name": name,
            "permissions": permissions,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        return api_key
    
    def verify_api_key(self, api_key: str) -> bool:
        """Verify API key."""
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return api_key_hash in self.api_keys
    
    def get_permissions(self, api_key: str) -> list[str]:
        """Get permissions for API key."""
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return self.api_keys.get(api_key_hash, {}).get("permissions", [])

# Middleware for FastMCP
def auth_middleware(request):
    api_key = request.headers.get("X-API-Key")
    if not api_key or not auth.verify_api_key(api_key):
        raise AuthenticationError("Invalid API key")
```

#### 3.2.2 OAuth 2.0 Support

**For enterprise SSO integration:**

```python
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()
oauth.register(
    name="azure",
    client_id=os.getenv("OAUTH_CLIENT_ID"),
    client_secret=os.getenv("OAUTH_CLIENT_SECRET"),
    server_metadata_url=os.getenv("OAUTH_METADATA_URL"),
)

@app.route("/oauth/login")
async def oauth_login(request):
    redirect_uri = request.url_for("oauth_callback")
    return await oauth.azure.authorize_redirect(request, redirect_uri)

@app.route("/oauth/callback")
async def oauth_callback(request):
    token = await oauth.azure.authorize_access_token(request)
    user = await oauth.azure.parse_id_token(request, token)
    # Create session
    return {"user": user}
```

---

### 3.3 Audit Logging

**Problem**: No audit trail of operations.

**Solution**: Comprehensive audit logging

```python
# src/tenable_sc_mcp/audit.py

@dataclass
class AuditLog:
    timestamp: datetime
    user: str
    tenant_id: str
    tool: str
    method: str
    path: str
    params: dict
    response_status: int
    duration_ms: float
    ip_address: str
    request_id: str

class AuditLogger:
    def __init__(self, backend: str = "file"):
        self.backend = backend
        self.log_file = Path("audit.log")
    
    def log(self, entry: AuditLog):
        """Log audit entry."""
        if self.backend == "file":
            self._log_to_file(entry)
        elif self.backend == "database":
            self._log_to_db(entry)
        elif self.backend == "syslog":
            self._log_to_syslog(entry)
    
    def _log_to_file(self, entry: AuditLog):
        with open(self.log_file, "a") as f:
            f.write(json.dumps(asdict(entry)) + "\n")
    
    def search(
        self,
        user: str = None,
        tenant_id: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
    ) -> list[AuditLog]:
        """Search audit logs."""
        # Implementation depends on backend
        pass

@mcp.tool()
def tsc_audit_logs(
    user: str = None,
    tenant_id: str = None,
    limit: int = 100
) -> dict[str, Any]:
    """Query audit logs."""
    logs = audit_logger.search(user=user, tenant_id=tenant_id)
    return {
        "logs": [asdict(log) for log in logs[:limit]]
    }
```

---

### 3.4 Role-Based Access Control (RBAC)

**Add granular permissions:**

```python
# src/tenable_sc_mcp/rbac.py

class Permission(Enum):
    READ_SCANS = "read:scans"
    WRITE_SCANS = "write:scans"
    DELETE_SCANS = "delete:scans"
    READ_ASSETS = "read:assets"
    WRITE_ASSETS = "write:assets"
    READ_POLICIES = "read:policies"
    WRITE_POLICIES = "write:policies"
    ADMIN = "admin"

class Role:
    def __init__(self, name: str, permissions: list[Permission]):
        self.name = name
        self.permissions = permissions
    
    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions or Permission.ADMIN in self.permissions

# Predefined roles
ROLES = {
    "admin": Role("admin", [Permission.ADMIN]),
    "analyst": Role("analyst", [Permission.READ_SCANS, Permission.READ_ASSETS]),
    "operator": Role("operator", [Permission.READ_SCANS, Permission.WRITE_SCANS]),
}

def require_permission(permission: Permission):
    """Decorator for permission checking."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user.role.has_permission(permission):
                raise PermissionDeniedError(f"Missing permission: {permission.value}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@mcp.tool()
@require_permission(Permission.DELETE_SCANS)
def tsc_delete_scan(scan_id: str, tenant_id: str = "default"):
    """Delete scan (requires delete:scans permission)."""
    # ...
```

---

### 3.5 Data Retention & Compliance

**Add configurable data retention:**

```python
# src/tenable_sc_mcp/retention.py

class DataRetentionPolicy:
    def __init__(self):
        self.cache_retention_days = 30
        self.audit_log_retention_days = 365
        self.metrics_retention_days = 90
    
    async def cleanup_expired_data(self):
        """Remove data older than retention period."""
        cutoff_cache = datetime.utcnow() - timedelta(days=self.cache_retention_days)
        cutoff_audit = datetime.utcnow() - timedelta(days=self.audit_log_retention_days)
        cutoff_metrics = datetime.utcnow() - timedelta(days=self.metrics_retention_days)
        
        # Cleanup cache
        await cache.cleanup_before(cutoff_cache)
        
        # Cleanup audit logs
        await audit_logger.cleanup_before(cutoff_audit)
        
        # Cleanup metrics
        await metrics_store.cleanup_before(cutoff_metrics)

# Run cleanup daily
async def schedule_cleanup():
    while True:
        await asyncio.sleep(86400)  # 24 hours
        await retention_policy.cleanup_expired_data()
```

---

### 3.6 Configuration Management UI

**Add web UI for configuration:**

```python
# src/tenable_sc_mcp/admin_ui.py

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

async def admin_dashboard(request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "tenants": tenant_manager.list_tenants(),
        "metrics": metrics.to_dict(),
        "cache_stats": cache_metrics.to_dict(),
    })

async def admin_tenants(request):
    return templates.TemplateResponse("tenants.html", {
        "request": request,
        "tenants": tenant_manager.list_tenants(),
    })

admin_app = Starlette(routes=[
    Route("/admin", admin_dashboard),
    Route("/admin/tenants", admin_tenants),
])
```

---

### Phase 3 Deliverables

**Code Changes:**
- [ ] Multi-tenant architecture
- [ ] API key authentication
- [ ] OAuth 2.0 integration
- [ ] Audit logging
- [ ] RBAC system
- [ ] Data retention policies
- [ ] Admin UI (basic)

**Testing:**
- [ ] Multi-tenant isolation tests
- [ ] Authentication tests
- [ ] Authorization tests
- [ ] Audit log tests

**Documentation:**
- [ ] Multi-tenancy setup guide
- [ ] Authentication configuration guide
- [ ] RBAC guide
- [ ] Compliance documentation

**Success Criteria:**
- [ ] Support 10+ tenants simultaneously
- [ ] 100% audit coverage for write operations
- [ ] Zero permission leaks between tenants
- [ ] OAuth integration working

---

## Phase 4: Advanced Capabilities (v1.0.0)

**Timeline**: 8-10 weeks  
**Priority**: MEDIUM  
**Focus**: Advanced features, integrations, automation

### 4.1 GraphQL API

**Add GraphQL endpoint for flexible queries:**

```python
# src/tenable_sc_mcp/graphql_schema.py

import strawberry
from typing import List, Optional

@strawberry.type
class Repository:
    id: int
    name: str
    description: Optional[str]

@strawberry.type
class Scan:
    id: int
    name: str
    status: str
    repository: Optional[Repository]

@strawberry.type
class Query:
    @strawberry.field
    async def repositories(self, tenant_id: str = "default") -> List[Repository]:
        # Fetch from Tenable.sc
        pass
    
    @strawberry.field
    async def scan(self, id: int, tenant_id: str = "default") -> Optional[Scan]:
        # Fetch scan details
        pass

schema = strawberry.Schema(query=Query)

# Add to FastMCP
from strawberry.fastapi import GraphQLRouter
graphql_app = GraphQLRouter(schema)
```

---

### 4.2 Webhook Support

**Add webhooks for event notifications:**

```python
# src/tenable_sc_mcp/webhooks.py

@dataclass
class Webhook:
    id: str
    url: str
    events: list[str]
    secret: str
    enabled: bool = True

class WebhookManager:
    def __init__(self):
        self.webhooks: dict[str, Webhook] = {}
    
    async def trigger(self, event: str, payload: dict):
        """Trigger webhooks for event."""
        for webhook in self.webhooks.values():
            if event in webhook.events and webhook.enabled:
                await self._send_webhook(webhook, event, payload)
    
    async def _send_webhook(self, webhook: Webhook, event: str, payload: dict):
        """Send webhook HTTP request."""
        signature = self._generate_signature(webhook.secret, payload)
        
        async with httpx.AsyncClient() as client:
            await client.post(
                webhook.url,
                json={
                    "event": event,
                    "payload": payload,
                    "timestamp": datetime.utcnow().isoformat(),
                },
                headers={"X-Webhook-Signature": signature},
                timeout=5.0,
            )

# Events
WEBHOOK_EVENTS = [
    "scan.completed",
    "scan.failed",
    "vulnerability.discovered",
    "cache.invalidated",
]

@mcp.tool()
def tsc_create_webhook(
    url: str,
    events: list[str],
    tenant_id: str = "default"
) -> dict[str, Any]:
    """Register webhook for events."""
    webhook = Webhook(
        id=str(uuid.uuid4()),
        url=url,
        events=events,
        secret=secrets.token_urlsafe(32),
    )
    webhook_manager.register(webhook)
    return {"webhook_id": webhook.id, "secret": webhook.secret}
```

---

### 4.3 Scheduled Jobs & Automation

**Add cron-like scheduling:**

```python
# src/tenable_sc_mcp/scheduler.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

class JobScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
    
    def schedule_job(
        self,
        job_id: str,
        cron: str,
        tool: str,
        params: dict,
        tenant_id: str = "default"
    ):
        """Schedule recurring job."""
        self.scheduler.add_job(
            func=self._execute_job,
            trigger=CronTrigger.from_crontab(cron),
            id=job_id,
            args=[tool, params, tenant_id],
        )
    
    async def _execute_job(self, tool: str, params: dict, tenant_id: str):
        """Execute scheduled job."""
        logger.info("executing_scheduled_job", job_id=job_id, tool=tool)
        # Execute MCP tool
        result = await execute_tool(tool, params, tenant_id)
        # Trigger webhooks
        await webhook_manager.trigger("job.completed", {
            "job_id": job_id,
            "result": result
        })

@mcp.tool()
def tsc_schedule_job(
    job_id: str,
    cron: str,
    tool: str,
    params: dict,
    tenant_id: str = "default"
) -> dict[str, Any]:
    """Schedule recurring job.
    
    Example:
    {
        "job_id": "daily_scan_report",
        "cron": "0 9 * * *",  # 9 AM daily
        "tool": "tsc_analyze",
        "params": {"query": {...}}
    }
    """
    scheduler.schedule_job(job_id, cron, tool, params, tenant_id)
    return {"status": "scheduled", "job_id": job_id}
```

---

### 4.4 Integration with SIEM/SOAR

**Add connectors for popular platforms:**

```python
# src/tenable_sc_mcp/integrations/splunk.py

class SplunkIntegration:
    def __init__(self, host: str, token: str):
        self.host = host
        self.token = token
        self.client = httpx.AsyncClient()
    
    async def send_event(self, event: dict):
        """Send event to Splunk HEC."""
        await self.client.post(
            f"{self.host}/services/collector/event",
            headers={
                "Authorization": f"Splunk {self.token}",
                "Content-Type": "application/json",
            },
            json={"event": event},
        )

# src/tenable_sc_mcp/integrations/palo_alto_xsoar.py

class XSOARIntegration:
    def __init__(self, host: str, api_key: str):
        self.host = host
        self.api_key = api_key
    
    async def create_incident(self, incident: dict):
        """Create incident in XSOAR."""
        await self.client.post(
            f"{self.host}/incident",
            headers={"Authorization": self.api_key},
            json=incident,
        )

@mcp.tool()
def tsc_export_to_siem(
    platform: str,  # "splunk", "xsoar", "sentinel"
    query: dict,
    tenant_id: str = "default"
) -> dict[str, Any]:
    """Export vulnerability data to SIEM."""
    # Run analysis query
    results = tsc_analyze(query, tenant_id)
    
    # Send to SIEM
    if platform == "splunk":
        await splunk.send_event(results)
    elif platform == "xsoar":
        await xsoar.create_incident(results)
    
    return {"status": "exported", "count": len(results)}
```

---

### 4.5 Advanced Analytics & Reporting

**Add built-in analytics:**

```python
# src/tenable_sc_mcp/analytics.py

@mcp.tool()
def tsc_vulnerability_trends(
    days: int = 30,
    tenant_id: str = "default"
) -> dict[str, Any]:
    """Analyze vulnerability trends over time."""
    # Fetch historical data
    data = fetch_vulnerability_data(days, tenant_id)
    
    return {
        "trend": "increasing" or "decreasing" or "stable",
        "change_percent": 15.2,
        "critical_count": 45,
        "high_count": 120,
        "chart_data": [...],
    }

@mcp.tool()
def tsc_risk_score(tenant_id: str = "default") -> dict[str, Any]:
    """Calculate overall risk score."""
    # Aggregate vulnerability data
    vulns = fetch_all_vulnerabilities(tenant_id)
    
    # Calculate risk score (0-100)
    risk_score = calculate_risk_score(vulns)
    
    return {
        "risk_score": risk_score,
        "grade": "A" to "F",
        "top_risks": [...],
        "recommendations": [...],
    }

@mcp.tool()
def tsc_compliance_report(
    framework: str,  # "PCI-DSS", "HIPAA", "NIST"
    tenant_id: str = "default"
) -> dict[str, Any]:
    """Generate compliance report."""
    # Map vulnerabilities to compliance controls
    controls = map_to_compliance_framework(framework, tenant_id)
    
    return {
        "framework": framework,
        "compliance_score": 87.5,
        "passed_controls": 35,
        "failed_controls": 5,
        "details": [...],
    }
```

---

### 4.6 Machine Learning Integration

**Add ML-powered features:**

```python
# src/tenable_sc_mcp/ml.py

class VulnerabilityPrioritizer:
    """ML model for vulnerability prioritization."""
    
    def __init__(self):
        self.model = self._load_model()
    
    def predict_priority(self, vulnerability: dict) -> float:
        """Predict priority score (0-1) for vulnerability."""
        features = self._extract_features(vulnerability)
        return self.model.predict([features])[0]
    
    def _extract_features(self, vuln: dict) -> list:
        return [
            vuln.get("cvss_score", 0),
            vuln.get("exploitability", 0),
            vuln.get("age_days", 0),
            vuln.get("asset_criticality", 0),
            # ... more features
        ]

@mcp.tool()
def tsc_prioritize_vulnerabilities(
    limit: int = 100,
    tenant_id: str = "default"
) -> dict[str, Any]:
    """Get ML-prioritized vulnerabilities."""
    vulns = fetch_vulnerabilities(tenant_id)
    
    # Add ML priority scores
    for vuln in vulns:
        vuln["ml_priority"] = prioritizer.predict_priority(vuln)
    
    # Sort by priority
    vulns.sort(key=lambda v: v["ml_priority"], reverse=True)
    
    return {"vulnerabilities": vulns[:limit]}
```

---

### 4.7 Export Formats & Integrations

**Support multiple export formats:**

```python
@mcp.tool()
def tsc_export_report(
    query: dict,
    format: str,  # "pdf", "csv", "json", "xlsx", "html"
    tenant_id: str = "default"
) -> dict[str, Any]:
    """Export report in various formats."""
    data = tsc_analyze(query, tenant_id)
    
    if format == "pdf":
        pdf_bytes = generate_pdf_report(data)
        return {"file": base64.b64encode(pdf_bytes).decode()}
    elif format == "csv":
        csv_content = generate_csv(data)
        return {"content": csv_content}
    elif format == "xlsx":
        xlsx_bytes = generate_excel(data)
        return {"file": base64.b64encode(xlsx_bytes).decode()}
    elif format == "html":
        html_content = generate_html_report(data)
        return {"content": html_content}
    else:
        return {"data": data}
```

---

### Phase 4 Deliverables

**Code Changes:**
- [ ] GraphQL API
- [ ] Webhook system
- [ ] Job scheduler
- [ ] SIEM integrations (Splunk, XSOAR, Sentinel)
- [ ] Advanced analytics tools
- [ ] ML prioritization
- [ ] Export formats (PDF, CSV, XLSX)

**Testing:**
- [ ] GraphQL query tests
- [ ] Webhook delivery tests
- [ ] Scheduler tests
- [ ] Integration tests
- [ ] ML model accuracy tests

**Documentation:**
- [ ] GraphQL schema documentation
- [ ] Webhook integration guide
- [ ] Scheduler documentation
- [ ] SIEM integration guides
- [ ] Analytics documentation

**Success Criteria:**
- [ ] GraphQL API functional
- [ ] 99%+ webhook delivery rate
- [ ] Scheduled jobs running reliably
- [ ] SIEM integrations working
- [ ] ML model >85% accuracy

---

## Phase 5: Scale & Innovation (v2.0.0)

**Timeline**: 10-12 weeks  
**Priority**: LOW-MEDIUM  
**Focus**: Scale, performance, next-gen features

### 5.1 Distributed Architecture

**Support horizontal scaling:**

```python
# src/tenable_sc_mcp/distributed.py

class DistributedCache:
    """Redis-backed distributed cache with pub/sub."""
    
    def __init__(self):
        self.redis = Redis()
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe("cache:invalidate")
    
    async def listen_for_invalidations(self):
        """Listen for cache invalidation messages."""
        async for message in self.pubsub.listen():
            if message["type"] == "message":
                key = message["data"]
                self.local_cache.invalidate(key)
    
    async def invalidate_distributed(self, key: str):
        """Invalidate cache across all instances."""
        await self.redis.publish("cache:invalidate", key)

# Load balancing
from fastapi import FastAPI
from starlette.middleware.load_balancing import LoadBalancingMiddleware

app.add_middleware(
    LoadBalancingMiddleware,
    backends=["instance1:8000", "instance2:8000", "instance3:8000"]
)
```

---

### 5.2 Kubernetes Deployment

**Add Kubernetes manifests:**

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tenable-sc-mcp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tenable-sc-mcp
  template:
    metadata:
      labels:
        app: tenable-sc-mcp
    spec:
      containers:
      - name: mcp-server
        image: tenable-sc-mcp:latest
        ports:
        - containerPort: 8000
        env:
        - name: TSC_URL
          valueFrom:
            secretKeyRef:
              name: tenable-sc-config
              key: url
        - name: TSC_ACCESS_KEY
          valueFrom:
            secretKeyRef:
              name: tenable-sc-config
              key: access-key
        - name: TSC_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: tenable-sc-config
              key: secret-key
        - name: TSC_CACHE_BACKEND
          value: "redis"
        - name: TSC_CACHE_REDIS_HOST
          value: "redis-service"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: tenable-sc-mcp
spec:
  selector:
    app: tenable-sc-mcp
  ports:
  - port: 8000
    targetPort: 8000
  type: LoadBalancer

---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
```

**Helm Chart:**

```yaml
# helm/values.yaml
replicaCount: 3

image:
  repository: tenable-sc-mcp
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: LoadBalancer
  port: 8000

resources:
  requests:
    memory: 256Mi
    cpu: 250m
  limits:
    memory: 512Mi
    cpu: 500m

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

redis:
  enabled: true
  master:
    persistence:
      enabled: true
      size: 8Gi
```

---

### 5.3 OpenTelemetry Integration

**Full observability:**

```python
# src/tenable_sc_mcp/observability.py

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# Setup tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
span_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317")
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(span_exporter)
)

# Setup metrics
metrics.set_meter_provider(MeterProvider())
meter = metrics.get_meter(__name__)
metric_exporter = OTLPMetricExporter(endpoint="http://otel-collector:4317")

# Define metrics
request_counter = meter.create_counter(
    "mcp.requests.total",
    description="Total MCP requests"
)
request_duration = meter.create_histogram(
    "mcp.request.duration",
    description="MCP request duration in ms"
)

# Instrument requests
@tracer.start_as_current_span("mcp_request")
async def instrumented_request(method: str, path: str, **kwargs):
    span = trace.get_current_span()
    span.set_attribute("http.method", method)
    span.set_attribute("http.url", path)
    
    start = time.time()
    try:
        result = await client.request(method, path, **kwargs)
        span.set_attribute("http.status_code", 200)
        request_counter.add(1, {"status": "success"})
        return result
    except Exception as e:
        span.set_attribute("http.status_code", 500)
        span.record_exception(e)
        request_counter.add(1, {"status": "error"})
        raise
    finally:
        duration = (time.time() - start) * 1000
        request_duration.record(duration)
```

---

### 5.4 AI-Powered Query Assistant

**Natural language to Tenable.sc queries:**

```python
# src/tenable_sc_mcp/ai_assistant.py

from langchain import LLMChain, OpenAI
from langchain.prompts import PromptTemplate

class QueryAssistant:
    def __init__(self):
        self.llm = OpenAI(temperature=0)
        self.prompt = PromptTemplate(
            input_variables=["question"],
            template="""
            Convert this natural language question to a Tenable.sc analysis query:
            
            Question: {question}
            
            Return JSON query in this format:
            {{
                "type": "vuln",
                "sourceType": "cumulative",
                "query": {{
                    "tool": "vulndetails",
                    "filters": [...]
                }}
            }}
            """
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def natural_language_query(self, question: str) -> dict:
        """Convert natural language to query."""
        response = self.chain.run(question=question)
        return json.loads(response)

@mcp.tool()
def tsc_ask(
    question: str,
    tenant_id: str = "default"
) -> dict[str, Any]:
    """Ask a question in natural language.
    
    Examples:
    - "Show me all critical vulnerabilities from last week"
    - "What are the top 10 assets with the most high severity issues?"
    - "List all Windows servers with unpatched vulnerabilities"
    """
    # Convert to query
    query = assistant.natural_language_query(question)
    
    # Execute query
    results = tsc_analyze(query, tenant_id)
    
    return {
        "question": question,
        "generated_query": query,
        "results": results
    }
```

---

### 5.5 Real-Time Dashboard

**WebSocket-based live dashboard:**

```python
# src/tenable_sc_mcp/dashboard.py

from starlette.websockets import WebSocket, WebSocketDisconnect

class DashboardManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast update to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                await self.disconnect(connection)

@app.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    await dashboard_manager.connect(websocket)
    try:
        while True:
            # Send periodic updates
            await asyncio.sleep(5)
            data = {
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": metrics.to_dict(),
                "cache": cache_metrics.to_dict(),
                "active_scans": get_active_scans(),
            }
            await websocket.send_json(data)
    except WebSocketDisconnect:
        dashboard_manager.disconnect(websocket)
```

---

### Phase 5 Deliverables

**Code Changes:**
- [ ] Distributed cache
- [ ] Kubernetes manifests
- [ ] Helm chart
- [ ] OpenTelemetry integration
- [ ] AI query assistant
- [ ] Real-time dashboard

**Testing:**
- [ ] Load testing (10k+ req/min)
- [ ] Distributed system tests
- [ ] Chaos engineering tests
- [ ] Performance benchmarks

**Documentation:**
- [ ] Kubernetes deployment guide
- [ ] Scaling guide
- [ ] Observability guide
- [ ] AI assistant documentation

**Success Criteria:**
- [ ] Support 10k+ requests/min
- [ ] <50ms p99 latency
- [ ] 99.9% uptime
- [ ] Full distributed tracing
- [ ] AI assistant accuracy >90%

---

## Implementation Details

### Development Workflow

**Branch Strategy:**
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: Feature branches
- `hotfix/*`: Critical fixes

**Commit Convention:**
```
type(scope): description

Types: feat, fix, docs, test, refactor, perf, chore
Scope: cache, auth, tenant, metrics, etc.

Examples:
feat(cache): add Redis backend support
fix(client): handle connection timeout gracefully
docs(api): add caching configuration guide
test(cache): add cache expiry tests
```

**Pull Request Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Performance Impact
- [ ] Improves performance
- [ ] No performance impact
- [ ] May impact performance (explain)

## Documentation
- [ ] README updated
- [ ] API docs updated
- [ ] Migration guide added (if breaking)
```

---

### Code Quality Standards

**Coverage Requirements:**
- Phase 1: >80%
- Phase 2: >85%
- Phase 3+: >90%

**Linting:**
- Ruff for formatting
- mypy for type checking
- No warnings in CI

**Performance:**
- <100ms p95 for cached requests
- <500ms p95 for uncached requests
- <5s for analysis queries

---

### Testing Strategy

**Test Pyramid:**
```
    /\
   /  \   5% E2E Tests
  /____\
 /      \  20% Integration Tests
/________\
/          \  75% Unit Tests
/____________\
```

**Test Categories:**

1. **Unit Tests**: Fast, isolated, no I/O
2. **Integration Tests**: Test API integration
3. **E2E Tests**: Full workflow testing
4. **Performance Tests**: Load testing
5. **Security Tests**: Vulnerability scanning

**CI Pipeline:**
```yaml
stages:
  - lint
  - test
  - build
  - security-scan
  - deploy

lint:
  - ruff check
  - mypy

test:
  - pytest unit tests
  - pytest integration tests
  - coverage report

build:
  - docker build
  - push to registry

security-scan:
  - trivy scan
  - snyk scan

deploy:
  - deploy to staging
  - smoke tests
  - deploy to production
```

---

## Success Metrics

### Performance Metrics

| Metric | Current | v0.2.0 Target | v1.0.0 Target |
|--------|---------|---------------|---------------|
| Token usage (read workload) | 100% | 30-60% | 20-40% |
| Response time (cached) | N/A | <50ms p95 | <30ms p95 |
| Response time (uncached) | ~500ms | <500ms p95 | <300ms p95 |
| Cache hit rate | 0% | >60% | >80% |
| API calls | 100% | 20-50% | 10-30% |
| Max throughput | ~10 req/s | ~100 req/s | ~1000 req/s |

### Reliability Metrics

| Metric | Current | v0.3.0 Target | v1.0.0 Target |
|--------|---------|---------------|---------------|
| Uptime | N/A | 99% | 99.9% |
| MTTR | N/A | <1 hour | <15 min |
| Error rate | Unknown | <1% | <0.1% |
| Circuit breaker trips | N/A | <10/day | <5/day |

### Quality Metrics

| Metric | Current | v0.2.0 Target | v1.0.0 Target |
|--------|---------|---------------|---------------|
| Test coverage | ~10% | >80% | >95% |
| Documentation coverage | Good | Excellent | Comprehensive |
| Security vulnerabilities | 0 known | 0 high/critical | 0 any |
| Code duplication | Low | <5% | <3% |

---

## Risk Mitigation

### Technical Risks

**Risk 1: Cache invalidation complexity**
- **Impact**: High
- **Probability**: Medium
- **Mitigation**: 
  - Start with simple TTL-based caching
  - Add event-based invalidation incrementally
  - Extensive testing of edge cases
  - Manual invalidation as fallback

**Risk 2: Breaking changes**
- **Impact**: Medium
- **Probability**: Low
- **Mitigation**:
  - Semantic versioning
  - Deprecation warnings
  - Migration guides
  - Support for legacy tools

**Risk 3: Performance degradation**
- **Impact**: High
- **Probability**: Low
- **Mitigation**:
  - Performance benchmarks in CI
  - Load testing before release
  - Monitoring in production
  - Feature flags for new features

### Operational Risks

**Risk 1: Data consistency issues**
- **Impact**: High
- **Probability**: Medium
- **Mitigation**:
  - Strict cache TTLs
  - Invalidation on writes
  - Consistency checks
  - Manual cache clear tools

**Risk 2: Security vulnerabilities**
- **Impact**: Critical
- **Probability**: Low
- **Mitigation**:
  - Security scanning in CI
  - Dependency updates
  - Penetration testing
  - Bug bounty program

---

## GitHub Pages Setup

Create a comprehensive documentation site with:

1. **Landing Page**
   - Project overview
   - Key features
   - Quick start guide
   - Live demo (if available)

2. **Documentation**
   - Installation guide
   - Configuration reference
   - API reference
   - Best practices
   - Troubleshooting

3. **Guides**
   - Caching guide
   - Performance tuning
   - Multi-tenancy setup
   - SIEM integration
   - Enterprise deployment

4. **Release Notes**
   - Changelog
   - Migration guides
   - Breaking changes

5. **Community**
   - Contributing guide
   - Code of conduct
   - Support channels

**Setup Instructions:**

```bash
# Create gh-pages branch
git checkout --orphan gh-pages
git rm -rf .

# Create docs site structure
mkdir -p docs/{api,guides,releases}

# Add index.html (use MkDocs or Jekyll)
# Configure GitHub Pages in repo settings

# Build and deploy
mkdocs build
mkdocs gh-deploy
```

---

## Conclusion

This roadmap transforms the Tenable.sc MCP Server from a solid foundation into an **enterprise-grade platform** over 5 phases:

- **Phase 1 (v0.2.0)**: Foundation with caching - **40-70% token reduction**
- **Phase 2 (v0.3.0)**: Performance & reliability - **10x faster batch operations**
- **Phase 3 (v0.4.0)**: Enterprise features - **Multi-tenancy, auth, audit**
- **Phase 4 (v1.0.0)**: Advanced capabilities - **GraphQL, ML, SIEM**
- **Phase 5 (v2.0.0)**: Scale & innovation - **1000+ req/s, distributed**

**Immediate Next Steps:**
1. Review and approve this roadmap
2. Start Phase 1 implementation
3. Set up GitHub Pages
4. Begin caching layer development
5. Expand test suite

**Timeline Summary:**
- **Phase 1**: 4-6 weeks
- **Phase 2**: 4-6 weeks
- **Phase 3**: 6-8 weeks
- **Phase 4**: 8-10 weeks
- **Phase 5**: 10-12 weeks

**Total**: ~8-10 months to v1.0.0

This roadmap is ambitious but achievable with focused execution. Each phase delivers tangible value and can be shipped independently.

---

**Document Status**: Ready for Review  
**Next Review**: After Phase 1 completion  
**Maintained By**: Project Maintainers  
**Last Updated**: June 5, 2026

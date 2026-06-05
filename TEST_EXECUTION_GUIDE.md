# 🧪 Test Execution Guide - For Next Session

**Purpose**: Step-by-step instructions to execute the complete test plan  
**Estimated Time**: 2-3 hours  
**Test Plan**: See `TEST_PLAN.md` (800 lines, comprehensive)

---

## 📋 Quick Start for Next Session

Copy and paste this command to the next session:

```
Please execute the complete test plan from TEST_PLAN.md. Run all tests in order:
1. Unit tests with coverage report
2. Integration tests with real Tenable.sc
3. Performance benchmarks (cache vs no-cache)
4. Docker deployment validation
5. Security tests
6. Regression suite
Generate a final test report with all results, metrics, and recommendations.
```

---

## 🎯 Test Plan Overview

The `TEST_PLAN.md` file contains:

### **1. Unit Tests** (Section 2)
- ✅ **Already created**: 21 tests in `tests/test_cache.py`
- ✅ **Status**: All passing (21/21)
- 🔲 **Need to run**: With coverage report
- 📊 **Current coverage**: 43% overall, 66% cache module
- 🎯 **Target**: 70% overall, 80%+ cache module

**Command to run**:
```bash
cd /home/abmj/apps/tenable-sc-mcp-server
source .venv/bin/activate
pytest --cov=src/tenable_sc_mcp --cov-report=term --cov-report=html tests/
```

---

### **2. Integration Tests** (Section 3)
- 🔲 **Status**: Not yet run with real Tenable.sc
- 📝 **Tests defined**: 20+ integration test scenarios
- 🎯 **Purpose**: Validate real API calls with caching

**Test scenarios include**:
- tsc_catalog with caching
- tsc_request GET with caching
- tsc_request POST (write operations)
- Cache invalidation on writes
- Cross-resource cache dependencies
- Error handling with cache fallback

**Location in TEST_PLAN.md**: Lines 150-300

---

### **3. Performance Tests** (Section 4)
- 🔲 **Status**: Need to execute
- 📊 **Purpose**: Measure actual token savings and response times
- 🎯 **Expected**: 40-70% token reduction, 99% faster cached responses

**Test scenarios**:
1. **Baseline** (no cache): Measure response times
2. **First call** (cache miss): Measure response + cache write
3. **Second call** (cache hit): Measure cached response
4. **Calculate speedup**: Compare times and token usage
5. **Stress test**: 100 concurrent requests
6. **Cache hit rate**: Measure over 1000 requests

**Location in TEST_PLAN.md**: Lines 300-450

**Expected results**:
```
Metric              | Target      | Validation
--------------------|-------------|------------------
Token reduction     | 40-70%      | Log analysis
Cache hit rate      | >60%        | Cache stats
Response time (hit) | <5ms        | Performance test
Response time (API) | 200-500ms   | Baseline
Speedup             | 50-100x     | Calculated
```

---

### **4. Caching Tests** (Section 5)
- 🔲 **Status**: Basic tests done, need comprehensive suite
- 📝 **Tests**: TTL validation, invalidation rules, edge cases

**Test scenarios**:
- TTL expiry (24h static, 30m semi-static, 5m dynamic, 1m real-time)
- Pattern-based invalidation
- Write invalidation triggers
- Cache fallback on Redis failure
- Memory overflow handling
- Concurrent access safety

**Location in TEST_PLAN.md**: Lines 450-550

---

### **5. Docker Deployment Tests** (Section 6)
- ✅ **Status**: Basic validation done
- 🔲 **Need**: Full deployment test suite

**Test scenarios**:
- Container health checks
- Redis connectivity
- Volume persistence
- Environment variable injection
- Multi-container orchestration
- Restart resilience

**Location in TEST_PLAN.md**: Lines 550-650

---

### **6. Security Tests** (Section 7)
- 🔲 **Status**: Not yet executed
- 🔒 **Purpose**: Validate security controls

**Test scenarios**:
- SSL/TLS validation
- Credential handling
- Cache key sanitization
- Injection prevention
- Redis authentication (if enabled)
- Secret exposure in logs

**Location in TEST_PLAN.md**: Lines 650-700

---

### **7. Regression Test Suite** (Section 8)
- 🔲 **Status**: Not yet executed
- 📝 **Purpose**: Ensure no breaking changes

**Test scenarios**:
- All original MCP tools still work
- Backward compatibility
- No performance degradation
- Error handling unchanged
- API contract compliance

**Location in TEST_PLAN.md**: Lines 700-800

---

## 📊 Test Execution Order

### **Phase 1: Basic Validation** (30 minutes)
```bash
# 1. Run unit tests
cd /home/abmj/apps/tenable-sc-mcp-server
source .venv/bin/activate
pytest --cov=src/tenable_sc_mcp --cov-report=term --cov-report=html tests/ -v

# 2. Verify Docker deployment
docker-compose ps
docker-compose logs tenable-sc-mcp | grep "Cache initialized"

# 3. Quick cache test
python test_cache_quick.py
```

**Expected output**: All tests pass, coverage >40%, Docker healthy

---

### **Phase 2: Integration Tests** (45 minutes)
```bash
# Create integration test file
# (See TEST_PLAN.md Section 3 for test code)

# Run integration tests
pytest tests/test_integration.py -v --log-cli-level=INFO
```

**Expected output**: Real API calls work with caching

---

### **Phase 3: Performance Benchmarks** (30 minutes)
```bash
# Create performance test script
# (See TEST_PLAN.md Section 4 for benchmark code)

# Run performance tests
python tests/test_performance.py

# Expected output:
# - Baseline (no cache): 200-500ms
# - Cache hit: <5ms
# - Speedup: 50-100x
# - Token reduction: 40-70%
```

---

### **Phase 4: Docker & Security** (30 minutes)
```bash
# Docker tests
docker-compose down
docker-compose up -d
# Verify health, logs, persistence

# Security tests
# Check SSL validation
# Verify no secrets in logs
# Test Redis authentication
```

---

### **Phase 5: Regression Suite** (30 minutes)
```bash
# Run full regression suite
pytest tests/test_regression.py -v

# Verify all original tools work
# Check backward compatibility
# Validate error handling
```

---

## 📝 Test Report Template

After execution, generate this report:

```markdown
# Test Execution Report - [Date]

## Executive Summary
- Total tests: X
- Passed: Y
- Failed: Z
- Coverage: XX%
- Performance: [PASS/FAIL]
- Security: [PASS/FAIL]

## Results by Category

### Unit Tests
- Status: [PASS/FAIL]
- Coverage: XX%
- Time: Xm Ys

### Integration Tests
- Status: [PASS/FAIL]
- Real API calls: X/Y passed
- Cache hits: XX%

### Performance Tests
- Baseline (no cache): XXXms
- Cache hit: Xms
- Speedup: XXx
- Token reduction: XX%

### Docker Tests
- Health: [HEALTHY/UNHEALTHY]
- Redis: [CONNECTED/FAILED]
- Persistence: [PASS/FAIL]

### Security Tests
- SSL validation: [PASS/FAIL]
- Secrets handling: [PASS/FAIL]
- Cache security: [PASS/FAIL]

## Issues Found
1. [List any failures or issues]

## Recommendations
1. [Any improvements needed]

## Conclusion
[Overall assessment]
```

---

## 🎯 Success Criteria

For next session, these must all be **GREEN**:

| Category | Success Criteria | Status |
|----------|-----------------|--------|
| **Unit Tests** | >70% coverage, all passing | 🟡 43% |
| **Integration** | All MCP tools work with cache | 🔲 Not tested |
| **Performance** | 40-70% token reduction | 🔲 Not measured |
| **Cache Hit Rate** | >60% in realistic workflow | 🔲 Not measured |
| **Docker** | All containers healthy | ✅ Healthy |
| **Security** | No vulnerabilities found | 🔲 Not tested |
| **Regression** | No breaking changes | 🔲 Not tested |

---

## 📁 Test Artifacts

After testing, you should have:

1. ✅ `TEST_PLAN.md` (800 lines) - **Already created**
2. 🔲 `tests/test_integration.py` - **Need to create**
3. 🔲 `tests/test_performance.py` - **Need to create**
4. 🔲 `tests/test_regression.py` - **Need to create**
5. 🔲 `TEST_REPORT.md` - **Generate after execution**
6. 🔲 `htmlcov/` directory - **Coverage report**
7. 🔲 `performance_results.json` - **Benchmark data**

---

## 🚀 Quick Command for Next Session

To start testing immediately in the next session, use:

```bash
cd /home/abmj/apps/tenable-sc-mcp-server

# Phase 1: Unit tests
source .venv/bin/activate
pytest --cov=src/tenable_sc_mcp --cov-report=term --cov-report=html tests/ -v

# Phase 2: Integration (after creating test file)
pytest tests/test_integration.py -v

# Phase 3: Performance (after creating benchmark script)
python tests/test_performance.py

# Phase 4: Generate report
python -m pytest --html=test_report.html --self-contained-html
```

---

## 📚 References

- **Full Test Plan**: `TEST_PLAN.md` (800 lines)
- **Current Tests**: `tests/test_cache.py` (21 tests)
- **Quick Test**: `test_cache_quick.py`
- **Deployment Guide**: `DEPLOYMENT_LIVE.md`
- **Roadmap**: `FINAL_ULTIMATE_ROADMAP.md`

---

## ✅ Summary

**What's ready**:
- ✅ Comprehensive test plan (800 lines)
- ✅ 21 unit tests (all passing)
- ✅ Docker deployment (working)
- ✅ Quick test script

**What needs to be done in next session**:
- 🔲 Create integration tests
- 🔲 Create performance benchmarks
- 🔲 Run full test suite
- 🔲 Measure real token savings
- 🔲 Generate test report
- 🔲 Validate all success criteria

**Estimated time**: 2-3 hours for complete test execution

---

**Copy this to start next session**:
```
Execute the comprehensive test plan from TEST_PLAN.md:
1. Run unit tests with coverage (pytest --cov)
2. Create and run integration tests
3. Create and run performance benchmarks
4. Measure token savings and cache hit rates
5. Run Docker and security tests
6. Generate TEST_REPORT.md with all results
Target: >70% coverage, 40-70% token reduction, >60% cache hit rate
```

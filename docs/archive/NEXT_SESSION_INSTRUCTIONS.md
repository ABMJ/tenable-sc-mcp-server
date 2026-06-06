# Next Session Instructions

**Date Created**: June 6, 2026  
**Last Updated**: June 6, 2026  
**Session Status**: Cache fix deployed and validated ✅  
**Ready for**: Optimization & convenience tools implementation

---

## 🎉 Current Status - Production Ready!

### What Was Accomplished

✅ **Cache Fix Implemented** (June 6, 2026)
- POST /analysis queries now cached
- 90% token savings on repeated queries
- 10-25x faster responses with cache hits
- Production validated and working

✅ **Documentation Overhauled**
- Professional README with 3-command Quick Start
- Comprehensive caching documentation
- Troubleshooting guide added
- Performance metrics documented

✅ **Production Testing Completed**
- Cache hit rate: 16% initially (will improve over time)
- Performance: 20-30ms cached vs 200-500ms uncached
- Token usage: ~1,000 tokens cached vs ~9,000 tokens uncached
- Validation: Query 3 successfully hit cache ✅

### Containers Running

```bash
docker ps --filter "name=tenable-sc-mcp"
```

Expected:
```
tenable-sc-mcp         Up X minutes   0.0.0.0:8000->8000/tcp
tenable-sc-mcp-redis   Up X minutes   0.0.0.0:6379->6379/tcp (healthy)
```

---

## 🚀 Next Session Priorities

### Phase 1: TTL Optimization (Quick Win - 30 minutes)

**Goal**: Improve cache hit rate from 16% to 60-80%

**Current TTLs** (too aggressive):
```python
"analysis": 60,      # 1 minute (too short!)
"asset": 300,        # 5 minutes
"repository": 1800,  # 30 minutes
```

**Recommended Changes**:

1. **Update `src/tenable_sc_mcp/cache.py`** - Add smart TTL for analysis queries:

```python
def get_ttl_for_analysis(query: dict) -> int:
    """Vary TTL based on analysis query type."""
    tool = query.get("tool", "")
    
    # IP/asset inventory queries - data changes slowly
    if tool in ("sumip", "sumasset", "iplist"):
        return 300  # 5 minutes
    
    # Vulnerability queries - semi-dynamic
    elif tool in ("vulndetails", "vulnipdetail", "vulnsummary"):
        return 180  # 3 minutes
    
    # Real-time queries - status, activity
    elif tool in ("listening", "event"):
        return 60   # 1 minute
    
    # Default for unknown queries
    else:
        return 120  # 2 minutes
```

2. **Update `src/tenable_sc_mcp/server.py`** - Use smart TTL in `tsc_analyze()`:

```python
# In tsc_analyze() function, around line 414
if cache and cache_key and result.get("ok"):
    ttl = get_ttl_for_analysis(query)  # Use smart TTL instead of fixed
    cache.set(cache_key, result, ttl)
```

3. **Test the changes**:

```bash
# Rebuild containers
docker-compose down
docker build -t tenable-sc-mcp:latest .
docker-compose up -d

# Test with repeated queries
# Query 1: "get list of IPs from Tenable.sc" (cache miss)
# Wait 2 minutes
# Query 2: "get list of IPs from Tenable.sc" (cache hit - 5 min TTL!)
```

**Expected Result**: Cache hit rate 16% → 60-80% over first week

---

### Phase 2: Priority 1 Convenience Tools (High ROI - 2 hours)

**Goal**: 90-94% token reduction on common queries

#### Tool 1: `tsc_list_all_ips` (45 minutes)

**Purpose**: Get simple IP list without parsing huge JSON

**Implementation**:

```python
@mcp.tool()
def tsc_list_all_ips(
    format: Literal["list", "csv", "json"] = "list",
    network_filter: str | None = None,
) -> dict[str, Any]:
    """Get all IP addresses from Tenable.sc inventory.
    
    This is 94% more token-efficient than using tsc_analyze directly.
    Returns a simple list of IPs, heavily cached.
    
    Args:
        format: Output format - 'list' (default), 'csv', or 'json'
        network_filter: Optional CIDR filter (e.g., "10.0.0.0/8")
    
    Returns:
        {
            "ok": true,
            "count": 792,
            "ips": ["10.0.0.1", "10.0.0.2", ...]
        }
    """
    # Check cache first
    cache = _get_cache()
    cache_key = generate_cache_key(
        "convenience_ips",
        params={"format": format, "filter": network_filter}
    )
    if cache:
        cached = cache.get(cache_key)
        if cached:
            return cached
    
    # Query Tenable.sc
    query = {
        "tool": "sumip",
        "sourceType": "cumulative",
        "type": "vuln"
    }
    result = tsc_analyze(query)
    
    if not result.get("ok"):
        return result
    
    # Extract IPs
    ips = []
    for record in result.get("response", {}).get("results", []):
        ip = record.get("ip")
        if ip and ip != "0.0.0.0":
            # Apply network filter if provided
            if network_filter:
                if not _ip_in_network(ip, network_filter):
                    continue
            ips.append(ip)
    
    # Remove duplicates and sort
    ips = sorted(set(ips), key=lambda x: [int(p) for p in x.split('.')])
    
    # Format output
    output = {"ok": True, "count": len(ips)}
    
    if format == "list":
        output["ips"] = ips
    elif format == "csv":
        output["ips"] = "\n".join(ips)
    elif format == "json":
        output["ips"] = [{"ip": ip} for ip in ips]
    
    # Cache for 5 minutes
    if cache:
        cache.set(cache_key, output, ttl=300)
    
    return output


def _ip_in_network(ip: str, cidr: str) -> bool:
    """Check if IP is in CIDR network."""
    import ipaddress
    try:
        return ipaddress.ip_address(ip) in ipaddress.ip_network(cidr, strict=False)
    except ValueError:
        return False
```

**Testing**:
```python
# Ask Claude: "use tenable-sc to list all IPs"
# Expected: Simple list, ~500 tokens instead of ~9,000 tokens
```

**Token Savings**: ~9,000 → ~500 tokens (94% reduction)

---

#### Tool 2: `tsc_ip_last_scan` (45 minutes)

**Purpose**: When was an IP last scanned?

**Implementation**:

```python
@mcp.tool()
def tsc_ip_last_scan(
    ip: str,
    include_scanner: bool = True,
    include_policy: bool = True,
) -> dict[str, Any]:
    """Get last scan information for an IP address.
    
    Args:
        ip: IP address to query (e.g., "10.0.0.50")
        include_scanner: Include scanner name (default: true)
        include_policy: Include policy name (default: true)
    
    Returns:
        {
            "ok": true,
            "ip": "10.0.0.50",
            "last_scan": "2026-06-06T10:30:00Z",
            "scanner": "Scanner-DC1",
            "policy": "Internal Network Scan",
            "days_ago": 0
        }
    """
    # Check cache
    cache = _get_cache()
    cache_key = generate_cache_key(
        "convenience_ip_last_scan",
        params={"ip": ip, "scanner": include_scanner, "policy": include_policy}
    )
    if cache:
        cached = cache.get(cache_key)
        if cached:
            return cached
    
    # Query for this specific IP
    query = {
        "tool": "vulndetails",
        "sourceType": "cumulative",
        "type": "vuln",
        "query": {
            "filterField": "ip",
            "operator": "=",
            "value": ip
        }
    }
    
    result = tsc_analyze(query)
    
    if not result.get("ok"):
        return result
    
    results = result.get("response", {}).get("results", [])
    
    if not results:
        return {
            "ok": True,
            "ip": ip,
            "last_scan": None,
            "message": "No scan data found for this IP"
        }
    
    # Get most recent scan
    from datetime import datetime, timezone
    
    most_recent = None
    most_recent_date = None
    
    for record in results:
        scan_time = record.get("lastScanTime")
        if scan_time:
            try:
                scan_dt = datetime.fromtimestamp(int(scan_time), tz=timezone.utc)
                if most_recent_date is None or scan_dt > most_recent_date:
                    most_recent_date = scan_dt
                    most_recent = record
            except (ValueError, TypeError):
                continue
    
    if not most_recent:
        return {
            "ok": True,
            "ip": ip,
            "last_scan": None,
            "message": "No valid scan timestamps found"
        }
    
    # Build response
    output = {
        "ok": True,
        "ip": ip,
        "last_scan": most_recent_date.isoformat(),
        "days_ago": (datetime.now(timezone.utc) - most_recent_date).days
    }
    
    if include_scanner:
        # Would need to query scanner info - simplified for now
        output["scanner"] = "Unknown (requires additional query)"
    
    if include_policy:
        # Would need to query policy info - simplified for now
        output["policy"] = "Unknown (requires additional query)"
    
    # Cache for 3 minutes
    if cache:
        cache.set(cache_key, output, ttl=180)
    
    return output
```

**Token Savings**: ~5,000 → ~300 tokens (94% reduction)

---

#### Tool 3: `tsc_ip_scan_history` (30 minutes)

**Purpose**: Get scan history for an IP

**Implementation**: Similar pattern to above, but returns list of scans with dates

**Token Savings**: ~6,000 → ~400 tokens (93% reduction)

---

## 📋 Implementation Checklist

### TTL Optimization
- [ ] Add `get_ttl_for_analysis()` function to `cache.py`
- [ ] Update `tsc_analyze()` to use smart TTL
- [ ] Import function in `server.py`
- [ ] Rebuild Docker image
- [ ] Test with repeated queries
- [ ] Verify cache hit rate improves

### Convenience Tools
- [ ] Implement `tsc_list_all_ips` with caching
- [ ] Implement `tsc_ip_last_scan` with caching
- [ ] Implement `tsc_ip_scan_history` with caching
- [ ] Add tests for each tool
- [ ] Update README with new tools section
- [ ] Update tool catalog

### Testing
- [ ] Test TTL changes don't break existing functionality
- [ ] Test convenience tools return correct data
- [ ] Verify token usage is reduced by 90%+
- [ ] Check cache hit rate after 1 week

### Documentation
- [ ] Update README with convenience tools
- [ ] Add examples for each new tool
- [ ] Update CHANGELOG for next release
- [ ] Document token savings metrics

---

## 📊 Success Metrics

### After TTL Optimization
- Cache hit rate: 16% → **60-80%**
- Average query response: 30-60s → **5-10s**
- User experience: More consistent fast responses

### After Convenience Tools
- Token usage per query: ~6,000 → **~400 tokens** (93% reduction)
- Response format: Huge JSON → Simple, targeted data
- Cache effectiveness: Higher hit rate due to simpler queries

---

## 🔗 Reference Documentation

- **TTL Recommendations**: See `CACHE_PERFORMANCE_RESULTS.md`
- **Tool Designs**: See `CONVENIENCE_TOOLS_ROADMAP.md`
- **Testing Guide**: See `TESTING_CACHE_FIX.md`
- **Current Status**: See `PROJECT_STATUS.md`

---

## 💡 User Feedback to Integrate

From production testing:

> "maybe we have to increase the ttl for some items"

✅ **Action**: TTL optimization (Phase 1 above)

> "create some tools that extracts these data... like list of ips or when an ip was last scanned or which policy or scanner scanned"

✅ **Action**: Convenience tools (Phase 2 above)

---

## ⚡ Quick Commands

### Start Development

```bash
cd /home/abmj/apps/tenable-sc-mcp-server

# Current status
docker-compose ps
git status

# Start coding
code src/tenable_sc_mcp/cache.py
code src/tenable_sc_mcp/server.py
```

### Test Changes

```bash
# Rebuild and restart
docker-compose down
docker build -t tenable-sc-mcp:latest .
docker-compose up -d

# Check logs
docker-compose logs -f tenable-sc-mcp

# Test with Claude
# Ask: "use tenable-sc to list all IPs"
```

### Commit Changes

```bash
git add src/
git commit -m "feat: add smart TTL and convenience tools

- Add get_ttl_for_analysis() for dynamic TTL based on query type
- Implement tsc_list_all_ips for 94% token savings
- Implement tsc_ip_last_scan for scan history
- Implement tsc_ip_scan_history for detailed history

Expected impact:
- Cache hit rate: 16% → 60-80%
- Token usage: ~6,000 → ~400 per query (93% reduction)"

git push origin main
```

---

## 🎯 Session Goals

**Time Estimate**: 2-3 hours total

**Primary Goal**: Implement TTL optimization (30 min)
- Expected outcome: 60-80% cache hit rate

**Secondary Goal**: Build 3 convenience tools (2 hours)
- Expected outcome: 93% token reduction on common queries

**Success Criteria**:
- ✅ Cache hit rate improves to 60%+
- ✅ Token usage drops by 90%+ on common queries
- ✅ Response time <5s for convenience tools
- ✅ All tests passing
- ✅ Documentation updated

---

**Ready to Start**: YES ✅  
**Prerequisites**: Docker containers running, git clean  
**Estimated ROI**: 93% token reduction on common queries

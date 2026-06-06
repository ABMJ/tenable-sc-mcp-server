# Convenience Tools Roadmap

**Purpose**: High-ROI tools that save massive token usage by wrapping common queries  
**Expected Impact**: 90-94% token reduction per query  
**Target Audience**: Security teams, compliance auditors, incident responders

---

## Design Philosophy

### Why Convenience Tools?

**Problem**: Raw analysis queries return huge JSON payloads
- Example: `tsc_analyze` for IP list returns ~9,000 tokens
- Claude must parse, filter, and format the data
- User sees long processing times

**Solution**: Purpose-built tools that return only what's needed
- Example: `tsc_list_all_ips` returns simple IP list in ~500 tokens
- Pre-filtered, pre-formatted data
- Instant responses from cache

### Key Principles

1. **Single Responsibility** - Each tool does one thing well
2. **Minimal Output** - Return only requested data
3. **Heavy Caching** - Longer TTLs for stable data
4. **Consistent Interface** - Similar parameter patterns across tools

---

## Priority 1: IP Management Tools

### `tsc_list_all_ips`

**Description**: Get all IP addresses from Tenable.sc inventory

**Parameters**:
- `format` (optional): Output format - `list` (default), `csv`, `json`
- `include_offline` (optional, default false): Include offline hosts
- `network_filter` (optional): CIDR filter (e.g., "10.0.0.0/8")

**Returns**:
```json
{
  "ok": true,
  "count": 792,
  "ips": [
    "10.0.0.1",
    "10.0.0.2",
    ...
  ]
}
```

**Cache TTL**: 300s (5 minutes)

**Implementation**:
```python
@mcp.tool()
def tsc_list_all_ips(
    format: Literal["list", "csv", "json"] = "list",
    include_offline: bool = False,
    network_filter: str | None = None,
) -> dict[str, Any]:
    """Get all IP addresses from Tenable.sc inventory.
    
    Returns a simple list of IPs, heavily cached for performance.
    This is 90-94% more token-efficient than using tsc_analyze directly.
    """
    # Check cache first
    cache = _get_cache()
    cache_key = generate_cache_key(
        "convenience_ips",
        params={"format": format, "offline": include_offline, "filter": network_filter}
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
    
    # Extract and filter IPs
    if not result.get("ok"):
        return result
    
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
    output = {
        "ok": True,
        "count": len(ips),
    }
    
    if format == "list":
        output["ips"] = ips
    elif format == "csv":
        output["ips"] = "\n".join(ips)
    elif format == "json":
        output["ips"] = [{"ip": ip} for ip in ips]
    
    # Cache result
    if cache:
        cache.set(cache_key, output, ttl=300)  # 5 minutes
    
    return output
```

**Token Savings**: ~9,000 → ~500 tokens (94% reduction)

---

### `tsc_ip_last_scan`

**Description**: Get last scan information for an IP address

**Parameters**:
- `ip` (required): IP address to query
- `include_scanner` (optional, default true): Include scanner name
- `include_policy` (optional, default true): Include policy name

**Returns**:
```json
{
  "ok": true,
  "ip": "10.0.0.50",
  "last_scan": "2026-06-06T10:30:00Z",
  "scanner": "Scanner-DC1",
  "policy": "Internal Network Scan",
  "days_ago": 0
}
```

**Cache TTL**: 180s (3 minutes)

**Token Savings**: ~5,000 → ~300 tokens (94% reduction)

---

### `tsc_ip_scan_history`

**Description**: Get scan history for an IP address

**Parameters**:
- `ip` (required): IP address to query
- `days` (optional, default 30): Number of days of history
- `limit` (optional, default 10): Max number of scans to return

**Returns**:
```json
{
  "ok": true,
  "ip": "10.0.0.50",
  "scan_count": 15,
  "scans": [
    {
      "date": "2026-06-06T10:30:00Z",
      "scanner": "Scanner-DC1",
      "policy": "Internal Network Scan",
      "scan_id": 123,
      "vulnerabilities": 25
    },
    ...
  ]
}
```

**Cache TTL**: 300s (5 minutes)

**Token Savings**: ~6,000 → ~400 tokens (93% reduction)

---

## Priority 2: Scanner & Policy Tools

### `tsc_list_active_scanners`

**Description**: Get all active scanners with status

**Parameters**:
- `include_stats` (optional, default true): Include scan statistics

**Returns**:
```json
{
  "ok": true,
  "count": 5,
  "scanners": [
    {
      "id": 1,
      "name": "Scanner-DC1",
      "status": "running",
      "ip": "10.1.1.10",
      "last_scan": "2026-06-06T10:30:00Z",
      "scans_today": 12
    },
    ...
  ]
}
```

**Cache TTL**: 600s (10 minutes)

**Token Savings**: ~3,000 → ~200 tokens (93% reduction)

---

### `tsc_list_scan_policies`

**Description**: Get all scan policies with usage statistics

**Parameters**:
- `include_usage` (optional, default true): Include usage counts
- `active_only` (optional, default false): Only active policies

**Returns**:
```json
{
  "ok": true,
  "count": 8,
  "policies": [
    {
      "id": 1,
      "name": "Internal Network Scan",
      "description": "Weekly internal scan",
      "scans_using": 15,
      "last_used": "2026-06-06T10:30:00Z"
    },
    ...
  ]
}
```

**Cache TTL**: 1800s (30 minutes) - policies rarely change

**Token Savings**: ~4,000 → ~300 tokens (92% reduction)

---

### `tsc_scans_by_policy`

**Description**: Get all scans using a specific policy

**Parameters**:
- `policy_id` (optional): Policy ID
- `policy_name` (optional): Policy name (alternative to ID)
- `status` (optional): Filter by status (`running`, `completed`, etc.)

**Returns**:
```json
{
  "ok": true,
  "policy": "Internal Network Scan",
  "scan_count": 45,
  "scans": [
    {
      "id": 123,
      "name": "Weekly DC1 Scan",
      "status": "completed",
      "last_run": "2026-06-06T10:30:00Z",
      "targets": 250
    },
    ...
  ]
}
```

**Cache TTL**: 180s (3 minutes)

**Token Savings**: ~5,000 → ~400 tokens (92% reduction)

---

## Priority 3: Vulnerability Intelligence Tools

### `tsc_critical_vulns_summary`

**Description**: Get count of critical/high vulnerabilities by category

**Parameters**:
- `severity` (optional, default "critical,high"): Comma-separated severity levels
- `group_by` (optional, default "family"): Group by `family`, `plugin`, or `host`

**Returns**:
```json
{
  "ok": true,
  "total_vulns": 1543,
  "breakdown": [
    {
      "category": "Windows",
      "critical": 45,
      "high": 123,
      "total": 168
    },
    {
      "category": "Web Servers",
      "critical": 12,
      "high": 89,
      "total": 101
    },
    ...
  ]
}
```

**Cache TTL**: 300s (5 minutes)

**Token Savings**: ~8,000 → ~600 tokens (92% reduction)

---

### `tsc_top_vulnerable_hosts`

**Description**: Get top N hosts by vulnerability count

**Parameters**:
- `limit` (optional, default 10): Number of hosts to return
- `severity` (optional, default "critical,high"): Filter by severity
- `include_details` (optional, default false): Include vuln details

**Returns**:
```json
{
  "ok": true,
  "hosts": [
    {
      "ip": "10.0.0.50",
      "hostname": "webserver01",
      "critical": 15,
      "high": 45,
      "medium": 123,
      "total": 183
    },
    ...
  ]
}
```

**Cache TTL**: 180s (3 minutes)

**Token Savings**: ~6,000 → ~500 tokens (91% reduction)

---

## Priority 4: Compliance & Reporting Tools

### `tsc_compliance_summary`

**Description**: Get compliance status by audit type

**Returns**: Compliance percentage by audit policy

**Cache TTL**: 600s (10 minutes)

---

### `tsc_recent_changes`

**Description**: Get recent asset/vulnerability changes

**Parameters**: `days` (default 7)

**Returns**: Summary of what changed recently

**Cache TTL**: 180s (3 minutes)

---

## Implementation Strategy

### Phase 1: Core IP Tools (Session 1, ~2 hours)
1. `tsc_list_all_ips` - 45 min
2. `tsc_ip_last_scan` - 45 min
3. `tsc_ip_scan_history` - 30 min

### Phase 2: Scanner/Policy Tools (Session 2, ~2 hours)
4. `tsc_list_active_scanners` - 45 min
5. `tsc_list_scan_policies` - 45 min
6. `tsc_scans_by_policy` - 30 min

### Phase 3: Vulnerability Intelligence (Session 3, ~2 hours)
7. `tsc_critical_vulns_summary` - 60 min
8. `tsc_top_vulnerable_hosts` - 60 min

### Phase 4: Polish & Testing (Session 4, ~2 hours)
9. Add comprehensive tests
10. Update documentation
11. Performance benchmarking
12. User acceptance testing

---

## Expected Overall Impact

### Token Efficiency
- **Average query**: ~6,000 tokens → ~400 tokens (93% reduction)
- **Per-user savings**: ~200K tokens/month → ~15K tokens/month
- **Cost savings**: Significant reduction in Claude API costs

### Performance
- **Response time**: 30-60s → <5s (10x faster)
- **Cache hit rate**: Will exceed 80% for common queries
- **User satisfaction**: Instant responses, clear outputs

### Developer Experience
- **Simpler queries**: "list all IPs" instead of complex JSON
- **Consistent interface**: Similar patterns across tools
- **Better documentation**: Clear examples for each tool

---

## User Feedback Integration

**From user**:
> "tools that extract these data would save time and token usage... like list of ips or when an ip was last scanned or which policy or scanner scanned etc"

**Roadmap addresses**:
- ✅ `tsc_list_all_ips` - Direct IP list extraction
- ✅ `tsc_ip_last_scan` - Last scan date/scanner
- ✅ `tsc_ip_scan_history` - Scanner + policy history
- ✅ `tsc_scans_by_policy` - Scans using specific policy
- ✅ Extensible architecture for more tools

**Additional ideas to explore**:
- Vulnerability trending over time
- Asset group membership queries
- Plugin family breakdowns
- Scan schedule viewer
- Target list management

---

**Status**: Design complete, ready for implementation  
**Next Action**: Implement Phase 1 tools in next session  
**Success Metric**: 90%+ token reduction on common queries

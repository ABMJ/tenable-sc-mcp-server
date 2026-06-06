# Tenable.sc MCP Tools - User Guide

**Last Updated**: 2026-06-06  
**Status**: 3 Tools Available (Production Ready)

---

## Available Tools

### Tool 1: Efficient IP Profile (`tsc_profile_ip_efficient`)

**Status**: ✅ Production Ready  
**Token Efficiency**: 83-90% savings (~2,500 tokens vs ~15,000 raw API)  
**Cache TTL**: 180-300 seconds

**What It Does:**
Provides a comprehensive security profile for an IP address using optimized multi-query approach. Returns host identity, vulnerability summary, scan information, software inventory, running services, and asset group membership.

**Usage:**
```
use tenable-sc to profile IP 10.1.20.10 efficiently, then show me cache stats
```

**What You'll Get:**
- **Host Identity**: Hostname, NetBIOS name, MAC address, ACR score
- **Vulnerability Summary**: Count by severity (critical/high/medium/low/info)
- **Last Scan Info**: Scan name, policy, timestamp, credential status, duration
- **Software Packages**: Top 50 installed applications
- **Running Services**: Active services with ports/protocols
- **Asset Groups**: Group membership (up to 46 groups)

**Best For:**
- Initial security assessment
- Quarterly audits
- Asset inventory verification
- Credential validation

---

### Tool 2a: Vulnerability Summary (`tsc_list_vulns_by_ip_summary`)

**Status**: ✅ Production Ready  
**Token Efficiency**: 88-92% savings (~700 tokens vs ~6,000 raw API)  
**Cache TTL**: 180 seconds

**What It Does:**
Returns aggregated vulnerability counts by severity for quick overview. Lightweight and fast.

**Usage:**
```
use tenable-sc to get vulnerability summary for IP 10.1.20.10 with severity critical, then show me cache stats
```

**What You'll Get:**
- Total vulnerability count
- Breakdown by severity level
- Applied filter summary

**Supported Filters:**
- Severity (critical/high/medium/low/info or 0-4)
- Exploit availability (Yes/No)
- First/last seen dates (epoch timestamp)
- Plugin family
- VPR score
- Plugin ID
- CVE ID
- Port number
- Protocol (TCP/UDP)

**Best For:**
- Quick security posture check
- Dashboard views
- Determining if detailed investigation is needed
- High-level reporting

---

### Tool 2b: Full Vulnerability Details (`tsc_list_vulns_by_ip_full`)

**Status**: ✅ Production Ready (Fixed 2026-06-06)  
**Token Efficiency**: 58-75% savings (~5,000 tokens vs ~12,000 raw API)  
**Cache TTL**: 180 seconds  
**Pagination**: 10-200 records per query

**What It Does:**
Returns complete vulnerability details with all fields for in-depth investigation and remediation planning.

**Usage:**
```
use tenable-sc to list all critical vulnerabilities for IP 10.1.20.10 using tsc_list_vulns_by_ip_full, show first 10 records, then show me cache stats
```

**What You'll Get Per Vulnerability:**
- Plugin ID and name
- Severity (name and numeric)
- Plugin family
- Port and protocol
- CVSS v3 base score
- VPR score (Vulnerability Priority Rating)
- EPSS score (Exploit Prediction Scoring System)
- Exploit availability and frameworks
- CVE IDs
- First seen / last seen timestamps
- Synopsis (truncated to 200 chars)
- Solution (truncated to 200 chars)

**Pagination:**
- Default: 0-50 records
- Maximum: 0-200 records per query
- Use `start_offset` and `end_offset` parameters

**Supported Filters (15 total):**
- All filters from summary tool PLUS:
- CVSS v3 base score
- EPSS score
- Patch published date
- Vulnerability published date
- Mitigation status

**Best For:**
- Remediation planning
- Detailed investigation
- Compliance reporting
- Vulnerability prioritization
- Export to SIEM/ticketing systems

---

## Testing Status

| Tool | Status | Tests Passed | Last Tested |
|------|--------|--------------|-------------|
| Tool 1 (IP Profile) | ✅ Production | All | 2026-06-06 |
| Tool 2a (Vuln Summary) | ✅ Production | All | 2026-06-06 |
| Tool 2b (Vuln Full) | ✅ Production | All | 2026-06-06 |

**Test Environment:**
- Target IP: 10.1.20.10 (Windows 7 desktop)
- Vulnerabilities: 389 total (78 critical, 109 high, 40 medium, 3 low, 159 info)
- Cache: Redis backend, 57%+ hit rate achieved
- No errors encountered

---

## Usage Patterns

### Pattern 1: Quick Security Check
```
1. use tenable-sc to get vulnerability summary for IP X.X.X.X with severity critical
2. Review count
3. If high count, proceed to Pattern 2
```

### Pattern 2: Detailed Investigation
```
1. use tenable-sc to profile IP X.X.X.X efficiently
2. use tenable-sc to list all critical vulnerabilities for IP X.X.X.X using tsc_list_vulns_by_ip_full, show first 20 records
3. Filter by exploit_available=Yes if needed
```

### Pattern 3: Filtered Search
```
use tenable-sc to list vulnerabilities for IP X.X.X.X with:
- severity critical
- exploits available
- VPR score >= 7.0
```

### Pattern 4: Compliance Audit
```
1. use tenable-sc to profile IP X.X.X.X (verify credentials)
2. use tenable-sc to get vulnerability summary by severity
3. Export results for audit report
```

---

## Performance Expectations

### Response Times

| Query Type | First Call | Cached Call | Speedup |
|------------|-----------|-------------|---------|
| IP Profile | 2-3 seconds | <5ms | 400-600x |
| Vuln Summary | 500ms | <5ms | 100x |
| Vuln Full (10) | 1-2 seconds | <5ms | 200-400x |

### Cache Hit Rates

**Expected Progression:**
- First query: 0% (cache miss - expected)
- Repeat query: 50-100% (cache hit!)
- Multiple repeats: 60-80% sustained

**Test Results (2026-06-06):**
- Query 1: 0% (cold start)
- Query 2: 33% (first hit)
- Query 3: 50% (improving)
- Query 4-6: 50-57% (sustained)

### Token Savings

| Tool | First Call | Cached | vs Raw API | Savings |
|------|-----------|--------|------------|---------|
| IP Profile | ~2,500 | ~1,500 | ~15,000 | 83-90% |
| Vuln Summary | ~700 | ~500 | ~6,000 | 88-92% |
| Vuln Full (50) | ~5,000 | ~3,000 | ~12,000 | 58-75% |

---

## Common Filters Reference

### Severity Values
- **Text**: `critical`, `high`, `medium`, `low`, `info`
- **Numeric**: `4`, `3`, `2`, `1`, `0`

Both formats accepted, case-insensitive.

### Date Filters
Use Unix epoch timestamps:
- `first_seen`: When vulnerability was first detected
- `last_seen`: When vulnerability was last detected
- `patch_published`: When vendor released patch
- `vuln_published`: When vulnerability was publicly disclosed

### Score Filters
- **VPR Score**: 0.0-10.0 (Tenable's priority rating)
- **CVSS v3**: 0.0-10.0 (industry standard)
- **EPSS Score**: 0.0-1.0 (exploit prediction probability)

Use operators: `>=7.0`, `<=3.0`, `=9.5`

### Exploit Availability
- `exploit_available`: `Yes` or `No`
- Returns vulnerabilities with public exploits

### Pagination
- `start_offset`: Starting record (0-indexed)
- `end_offset`: Ending record (exclusive, max 200)
- Example: `start_offset=0, end_offset=10` returns first 10 records

---

## Best Practices

### 1. Always Monitor Cache Performance
```
... then show me cache stats
```
Append to every query to track cache hit rate and token savings.

### 2. Use Summary Before Full
Start with summary view to understand scope, then use full details only if needed. This optimizes token usage.

**Good:**
```
1. Get summary (78 critical vulns found)
2. Decide: Need details? Yes → Use full with limit=10
```

**Wasteful:**
```
1. Get full details for all 78 vulns (7,000+ tokens)
2. Realize you only needed the count
```

### 3. Apply Filters Early
Don't fetch everything then filter locally. Apply filters in the query to reduce API load and token usage.

**Good:**
```
List vulnerabilities with severity critical and exploits available
```

**Wasteful:**
```
List all vulnerabilities (fetch 389 vulns), then manually filter
```

### 4. Use Pagination Wisely
- Start with 10-20 records for initial review
- Increase to 50-100 if building reports
- Never exceed 200 (API limit)

### 5. Leverage Cache
Run identical queries within 3 minutes (180s TTL) to hit cache for instant responses.

### 6. New Chat After Container Rebuild
After rebuilding Docker containers, start a new OpenCode chat for clean connection.

---

## Error Handling

### Invalid IP Address
**Input:** `999.999.999.999`  
**Error:** "Invalid IP address format: '999.999.999.999'"  
**Suggestion:** "Use tsc_list_ips() to find valid IP addresses"

### Invalid Severity
**Input:** `severity="bogus"`  
**Error:** "Invalid severity: 'bogus'"  
**Valid values:** "0, 1, 2, 3, 4, info, low, medium, high, critical"

### Pagination Exceeded
**Input:** `end_offset=500`  
**Error:** "end_offset cannot exceed 200 (requested: 500)"  
**Suggestion:** "Use pagination by setting start_offset/end_offset in multiple queries"

### No Data Found
**Result:** Empty results array  
**Meaning:** IP exists but no vulnerabilities match filters  
**Action:** Try broader filters or verify IP address

---

## Troubleshooting

### Tool Returns No Data
1. **Verify IP exists**: Use `tsc_list_ips` or check Tenable.sc UI
2. **Check filters**: Remove severity/CVE filters to see all results
3. **Verify scan coverage**: Use Tool 1 to check last scan date
4. **Check permissions**: Ensure API user has repository access

### Cache Not Hitting
1. **Check cache backend**: Use `show me cache statistics`
2. **Verify TTL hasn't expired**: Cache TTL is 180-300 seconds
3. **Ensure identical query**: Parameters must match exactly
4. **Check Redis health**: `docker ps --filter "name=redis"`

### Slow Response Times
1. **First query is slow**: Expected (API call + caching)
2. **All queries slow**: Check network latency to Tenable.sc
3. **Cache disabled**: Verify `TSC_CACHE_ENABLED=true` in config
4. **Large result sets**: Use pagination to limit results

### Container Issues
1. **Connection refused**: Rebuild containers with `docker-compose up -d --build`
2. **Authentication errors**: Check API keys in `.env` file
3. **OpenCode can't connect**: Verify port 8000 exposed and `--allow-remote-hosts` set

---

## Next Tools (Coming Soon)

### Week 1 Remaining
- **Tool 3**: `tsc_list_ips` - IP discovery with subnet/asset/tag filters
- **Tool 4**: `tsc_list_missing_patches_windows` - MS patch gap analysis
- **Tool 5**: `tsc_scan_status` - Real-time scan monitoring

### Week 2 Planned
- Compliance reporting tools
- Admin monitoring (resources, licenses, plugin updates)
- Port/service enumeration
- Credential audit reporting
- Asset group management

See TEST_PROMPTS.md for detailed usage examples and test cases.

---

## Support

**Documentation:**
- Usage Examples: [TEST_PROMPTS.md](TEST_PROMPTS.md)
- Caching Details: [CACHING_DEEP_DIVE.md](CACHING_DEEP_DIVE.md)
- Session Notes: [week1_session_3_2026-06-06_1415.md](week1_session_3_2026-06-06_1415.md)

**Issues:**
Report bugs or request features at the GitHub repository issue tracker.

**Version:** Week 1 Session 3 (2026-06-06)

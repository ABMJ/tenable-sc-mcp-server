# Test Prompts for Tenable.sc MCP Server

Use these prompts to test the tools and verify functionality.

## Tool 1: IP Profile (tsc_profile_ip_efficient)

### Basic Profile Test
```
Profile IP 10.1.20.10 using Tenable.sc show me a summary of cache performance on tenable.sc and token utilization for each query
```

**Expected Output:**
- Hostname and OS information
- Vulnerability counts by severity
- Last scan timestamp
- ACR score and source

**Token Efficiency:** ~2,500 tokens (vs ~15,000 raw API)

---

### Full Profile with All Details
```
Get comprehensive profile for 10.1.20.10 including software, services, scan info, and asset groups, using Tenable.sc show me a summary of cache performance on tenable.sc and token utilization for each query

```

**Expected Output:**
- Basic host info + vulnerabilities
- Top 50 installed software packages
- Running services (ports/protocols)
- Last scan details (policy, scanner, credentials)
- Asset group membership

**Token Efficiency:** ~5,000 tokens (vs ~30,000 raw API)

---

## Tool 2: Vulnerability Lists (tsc_list_vulns_by_ip)

### Summary View (Efficient)
```
List all critical vulnerabilities for IP 10.1.20.10 using Tenable.sc show me a summary of cache performance on tenable.sc and token utilization for each query
```

**Expected Output:**
- Vulnerability counts grouped by plugin
- Severity distribution
- Compact format for quick overview

**Token Efficiency:** ~1,000 tokens (88-92% savings)

---

### Full Details View
```
Show detailed vulnerabilities for 10.1.20.10 with severity high or critical, limit to 10 results using Tenable.sc show me a summary of cache performance on tenable.sc and token utilization for each query
```

**Expected Output:**
- Full vulnerability details per occurrence
- CVSS/VPR scores, CVE IDs
- Exploit availability
- Port/protocol information
- Plugin descriptions

**Token Efficiency:** ~3,000 tokens for 10 vulns (58-75% savings)

---

### Filtered Search
```
Find all vulnerabilities on 10.1.20.10 with available exploits using Tenable.sc show me a summary of cache performance on tenable.sc and token utilization for each query
```

**Expected Output:**
- Only vulnerabilities with exploit_available=true
- Full details including exploit frameworks
- Prioritized by severity

---

## Cache Testing

### Check Cache Performance
```
Show me cache statistics for the Tenable.sc MCP server
```

**Expected Output:**
- Hit rate percentage
- Total keys cached
- Memory usage
- Performance metrics

---

### Test Cache Efficiency
```
Profile IP 10.1.20.10 twice and compare response times
```

**Expected Behavior:**
- First call: ~500ms (API query)
- Second call: <10ms (cached response)
- 50-100x speed improvement

---

## Advanced Queries

### Multi-Filter Vulnerability Search
```
Find vulnerabilities on 10.1.20.10 with:
- Severity: critical
- VPR score > 7.0
- Exploits available
- Published in last 90 days
```

---

### Asset Investigation
```
Investigate 10.1.20.10: show me the host profile, then list critical vulnerabilities with exploits available
```

**Expected Behavior:**
- Two tool calls (profile + vuln list)
- Comprehensive security posture
- Actionable remediation data

---

## Token Efficiency Verification

### Compare Raw API vs Tools
```
Compare token usage:
1. Get IP profile for 10.1.20.10 using the efficient tool
2. Show me how many tokens this saved vs raw API calls
```

**Expected Savings:**
- Tool 1 (basic): 83-90% savings
- Tool 2 (summary): 88-92% savings
- Tool 2 (full): 58-75% savings

---

## Cache Management

### Clear Cache
```
Clear all Tenable.sc cache entries
```

### Clear Specific Pattern
```
Clear cache for all vulnerability queries
```

**Pattern:** `"analysis:*"` or `"vuln*"`

---

## Error Handling Tests

### Invalid IP
```
Profile IP 999.999.999.999
```

**Expected:** Clear validation error message

### Non-existent IP
```
Profile IP 192.168.1.1
```

**Expected:** "No data found for IP" with helpful suggestion

---

## Notes

- All timestamps are Unix epoch (e.g., 1683211119 = 2023-05-04 14:38:39)
- Use `include_scan_info=true` to get scan metadata from plugin 19506
- Default pagination: 50 results (max 200)
- Cache TTLs: 60s-600s depending on data type

# Tool 2 Test Queries & Prompts

Quick reference guide for testing `tsc_list_vulns_by_ip_summary` and `tsc_list_vulns_by_ip_full` tools.

---

## Prerequisites

Replace `10.1.20.10` with an actual IP address from your Tenable.sc environment that has vulnerability data.

To find a valid IP address, first run:
```
Show me a list of IPs from my Tenable.sc environment
```

---

## Basic Usage Tests

### 1. Simple Summary Query
Get quick vulnerability counts by severity:

```
Show me a vulnerability summary for IP 10.1.20.10
```

**What you'll see:**
- Total vulnerability count
- Breakdown by severity (critical, high, medium, low, info)
- Minimal token usage (~700 tokens)

---

### 2. Simple Full Details Query
Get complete vulnerability details:

```
Show me all vulnerabilities for IP 10.1.20.10
```

**What you'll see:**
- First 50 vulnerabilities (default)
- Full details: plugin ID, name, severity, CVSS scores, exploit info
- CVE IDs, ports, protocols
- Synopsis and solution (truncated to 200 chars)

---

## Filtering Tests

### 3. Critical Vulnerabilities Only (Summary)
```
Show me critical vulnerabilities for IP 10.1.20.10
```

or more explicitly:
```
Get vulnerability summary for 10.1.20.10 filtered by critical severity
```

**Expected:** Only critical vulnerabilities counted

---

### 4. Critical Vulnerabilities Only (Full Details)
```
Show me detailed critical vulnerabilities for IP 10.1.20.10
```

or:
```
List all critical severity vulnerabilities on 10.1.20.10 with full details
```

**Expected:** Complete records for critical vulnerabilities only

---

### 5. Exploitable Vulnerabilities
```
Show me all exploitable vulnerabilities on 10.1.20.10
```

or:
```
Get vulnerabilities with available exploits for IP 10.1.20.10
```

**Expected:** Only vulnerabilities with exploit_available="Yes"

---

### 6. High VPR Score Vulnerabilities
```
Show me vulnerabilities with VPR score 7.0 or higher on 10.1.20.10
```

**Expected:** High-priority vulnerabilities based on Tenable's VPR scoring

---

### 7. Specific Port Vulnerabilities
```
Show me all vulnerabilities on port 443 for IP 10.1.20.10
```

or:
```
What vulnerabilities exist on HTTPS port for 10.1.20.10?
```

**Expected:** Only vulnerabilities affecting port 443

---

### 8. Specific Plugin Family
```
Show me all web server vulnerabilities for IP 10.1.20.10
```

or:
```
List vulnerabilities in the "Web Servers" family for 10.1.20.10
```

**Expected:** Only vulnerabilities in specified plugin family

---

### 9. CVE-Specific Query
```
Does IP 10.1.20.10 have CVE-2024-1234?
```

or:
```
Show me vulnerability details for CVE-2024-1234 on 10.1.20.10
```

**Expected:** Results only if that CVE affects the IP

---

## Multi-Filter Combinations

### 10. Critical + Exploitable
```
Show me critical exploitable vulnerabilities on 10.1.20.10
```

**Expected:** Intersection of critical severity AND exploit available

---

### 11. High Severity + Web Servers + Port 443
```
Show me high severity web server vulnerabilities on port 443 for IP 10.1.20.10
```

**Expected:** Highly targeted result set with all three filters applied

---

### 12. High VPR + High CVSS v3
```
Show me vulnerabilities with VPR >= 7.0 and CVSS v3 >= 7.0 for 10.1.20.10
```

**Expected:** Vulnerabilities meeting both scoring thresholds

---

## Pagination Tests

### 13. First 10 Records
```
Show me the first 10 vulnerabilities for IP 10.1.20.10
```

**Expected:** Exactly 10 records, sorted by severity (critical first)

---

### 14. Records 50-100
```
Show me vulnerabilities 50 through 100 for IP 10.1.20.10
```

or:
```
Get the next 50 vulnerabilities for 10.1.20.10 starting at offset 50
```

**Expected:** 50 records starting from position 50

---

### 15. Check for More Results
After getting initial results, ask:
```
Are there more vulnerabilities beyond what you just showed?
```

**Expected:** Tool should indicate if has_more is true in the response

---

## Error Handling Tests

### 16. Invalid IP Address
```
Show me vulnerabilities for IP invalid.address
```

**Expected:** Clear error message:
- "Invalid IP address format: 'invalid.address'"
- Suggestion to use valid IPv4/IPv6 format
- Reference to tsc_list_ips() tool

---

### 17. Invalid Severity
```
Show me vulnerabilities with severity "super-critical" for IP 10.1.20.10
```

**Expected:** Clear error message:
- "Invalid severity: 'super-critical'"
- List of valid values: 0, 1, 2, 3, 4, info, low, medium, high, critical

---

### 18. Pagination Exceeds Limit
```
Show me vulnerabilities 0 through 500 for IP 10.1.20.10
```

**Expected:** Error message:
- "end_offset cannot exceed 200"
- Suggestion to use multiple queries with pagination

---

## Performance & Caching Tests

### 19. Repeated Query (Cache Test)
First run:
```
Show me vulnerabilities for IP 10.1.20.10
```

Then immediately run again:
```
Show me vulnerabilities for IP 10.1.20.10
```

**Expected:** 
- First query: ~5,000 tokens, ~500-1000ms
- Second query: ~3,000 tokens, <2ms (cached)
- Identical results

---

### 20. Different Pagination, Same Data (Cache Test)
First:
```
Show me vulnerabilities 0-50 for IP 10.1.20.10
```

Then:
```
Show me vulnerabilities 50-100 for IP 10.1.20.10
```

**Expected:**
- Both queries use same cache entry (pagination normalized)
- Second query also fast due to cache hit

---

## Real-World Scenarios

### 21. Quick Triage
```
Give me a quick security overview for IP 10.1.20.10
```

**Expected:** Summary mode with counts - perfect for rapid assessment

---

### 22. Detailed Investigation
```
I need to investigate IP 10.1.20.10 in detail, show me all critical and high vulnerabilities with exploit information
```

**Expected:** Full details mode with severity and exploit filters applied

---

### 23. Compliance Reporting
```
Show me all vulnerabilities with CVSS v3 score above 7.0 on 10.1.20.10
```

**Expected:** Filtered results suitable for compliance documentation

---

### 24. Remediation Planning
```
Show me the top 20 most severe vulnerabilities on 10.1.20.10 sorted by severity
```

**Expected:** Critical vulnerabilities first, ready for remediation prioritization

---

### 25. Specific Vulnerability Hunt
```
Does 10.1.20.10 have any SMB vulnerabilities?
```

**Expected:** Filter by family="SMB" or search for SMB-related plugins

---

## Comparison Tests

### 26. Summary vs Full Comparison
First run summary:
```
Show me a vulnerability summary for IP 10.1.20.10
```

Note the counts, then run full:
```
Now show me the full vulnerability details for the same IP
```

**Expected:**
- Summary shows counts (e.g., "critical: 15")
- Full shows 15 actual critical vulnerability records
- Counts should match

---

## Edge Cases

### 27. IP with No Vulnerabilities
```
Show me vulnerabilities for IP 172.16.1.1
```
(Use an IP that exists but has zero vulnerabilities)

**Expected:**
- ok: true
- total: 0
- Empty results array

---

### 28. Non-Existent IP
```
Show me vulnerabilities for IP 192.168.255.254
```
(Use an IP that doesn't exist in your environment)

**Expected:**
- May return empty results or error depending on implementation
- Should not crash

---

## Token Efficiency Demonstrations

### 29. Minimal Token Usage
```
Just tell me how many critical vulnerabilities are on 10.1.20.10
```

**Expected:** Uses summary mode, returns only count, ~700 tokens

---

### 30. Maximum Detail
```
Show me every detail about every vulnerability on 10.1.20.10 including CVE, CVSS, VPR, exploit info, and solutions
```

**Expected:** Uses full mode, rich detail, ~5,000 tokens for 50 records

---

## Integration with Tool 1

### 31. Full IP Profile + Vulnerabilities
```
Profile IP 10.1.20.10 and then show me its critical vulnerabilities
```

**Expected:** 
1. Tool 1 runs: tsc_profile_ip_efficient
2. Tool 2 runs: tsc_list_vulns_by_ip_full with severity="critical"

---

## Command-Style Queries

If you prefer direct tool invocation format:

### 32. Direct Summary Call
```
Call tsc_list_vulns_by_ip_summary with ip="10.1.20.10"
```

---

### 33. Direct Full Call with Filters
```
Call tsc_list_vulns_by_ip_full with ip="10.1.20.10", severity="critical", exploit_available="Yes", end_offset=20
```

---

## Natural Language Examples

These should all work with the MCP server:

- "How bad is 10.1.20.10?"
- "What are the security issues on 10.1.20.10?"
- "Give me the vuln report for 10.1.20.10"
- "Is 10.1.20.10 exploitable?"
- "What's the risk level of 10.1.20.10?"
- "Show me the attack surface of 10.1.20.10"
- "What needs patching on 10.1.20.10?"

---

## Tips for Best Results

1. **Start with summary** - Get counts first, then drill into details if needed
2. **Use filters** - Narrow down large result sets (severity, exploit, port)
3. **Leverage caching** - Repeated queries are nearly instant
4. **Paginate large sets** - Don't try to get 500+ records at once
5. **Combine with Tool 1** - Get full IP context before diving into vulnerabilities

---

## Expected Performance

| Query Type | Token Count | Response Time (First) | Response Time (Cached) |
|------------|-------------|----------------------|----------------------|
| Summary | ~700 | 200-500ms | <1ms |
| Full (50 records) | ~5,000 | 500-1000ms | <2ms |
| Filtered (20 records) | ~2,500 | 300-700ms | <2ms |

---

## Troubleshooting

**"No data found for IP"**
- IP may not exist in Tenable.sc inventory
- Try running `tsc_list_ips` first to find valid IPs

**"Invalid IP address format"**
- Use format like `10.1.20.10` or `2001:db8::1`
- No hostnames, must be IP address

**"end_offset cannot exceed 200"**
- Use multiple queries: 0-200, then 200-400, etc.
- Or use summary mode if you just need counts

**Results seem stale**
- Cache TTL is 180 seconds (3 minutes)
- Wait 3 minutes or use `tsc_cache_clear` if you need fresh data

---

## Quick Reference Card

```
SUMMARY MODE (lightweight, ~700 tokens):
- "Show me vulnerability summary for [IP]"
- "How many vulnerabilities on [IP]?"
- "Quick security check on [IP]"

FULL MODE (detailed, ~5000 tokens):
- "Show me all vulnerabilities for [IP]"
- "Detailed vulnerability report for [IP]"
- "What's vulnerable on [IP]?"

FILTERS:
- severity: critical, high, medium, low, info
- exploit_available: Yes, No
- family: "Web Servers", "Windows", etc.
- port: 443, 22, 3389, etc.
- cve: CVE-2024-1234

PAGINATION:
- "First 10 vulnerabilities on [IP]"
- "Next 50 vulnerabilities on [IP] starting at 50"
- Max 200 records per query
```

---

**Happy testing! 🎯**

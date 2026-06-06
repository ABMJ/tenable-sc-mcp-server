# Tenable.sc MCP Tools Documentation

Complete reference for all Tenable.sc MCP server tools - your AI assistant's gateway to vulnerability intelligence.

> **Quick Start**: Jump to [Convenience Tools](#convenience-tools-high-level) for the most powerful, token-efficient tools designed for AI assistants.

---

## Table of Contents

1. [Overview](#overview)
2. [Tool Categories](#tool-categories)
3. [Convenience Tools (High-Level)](#convenience-tools-high-level)
   - [IP & Asset Intelligence](#ip--asset-intelligence)
   - [Vulnerability Analysis](#vulnerability-analysis)
4. [Core Tools (Generic)](#core-tools-generic)
5. [Specialized Tools](#specialized-tools)
6. [Cache Management](#cache-management)
7. [Quick Reference](#quick-reference)

---

## Overview

The Tenable.sc MCP server provides **three tiers of tools**:

### 🌟 **Tier 1: Convenience Tools** (Recommended)
**Purpose**: High-level, purpose-built tools optimized for AI assistants  
**Benefits**: 75-94% token savings, intelligent caching, helpful validation  
**When to use**: Default choice for all common operations

### ⚙️ **Tier 2: Core Tools** (Generic Access)
**Purpose**: Direct access to any Tenable.sc resource  
**Benefits**: Flexible, covers all API endpoints  
**When to use**: When convenience tools don't fit your exact need

### 🔧 **Tier 3: Specialized Tools** (Advanced)
**Purpose**: Expert-level operations (downloads, file uploads, raw analysis)  
**Benefits**: Complete control, advanced features  
**When to use**: Complex workflows, non-standard operations

---

## Tool Categories

| Category | Tools | Best For |
|----------|-------|----------|
| **IP Intelligence** | `tsc_profile_ip_efficient` | Complete IP security profile |
| **Vulnerability Analysis** | `tsc_list_vulns_by_ip_summary`<br>`tsc_list_vulns_by_ip_full` | Finding, filtering, and investigating vulnerabilities |
| **Resource Catalog** | `tsc_catalog`<br>`tsc_resource_docs` | Discovering available API resources |
| **Generic CRUD** | `tsc_resource_action`<br>`tsc_list`, `tsc_get`, etc. | Accessing any Tenable.sc resource |
| **Analysis** | `tsc_analyze` | Running custom analysis queries |
| **Cache** | `tsc_cache_stats`<br>`tsc_cache_clear` | Performance monitoring and optimization |
| **Advanced** | `tsc_request`<br>`tsc_download`<br>`tsc_upload_file` | Expert-level operations |

---

## Convenience Tools (High-Level)

These are **optimized for AI assistants** with massive token savings, intelligent caching, and helpful error messages.

### IP & Asset Intelligence

#### 🎯 `tsc_profile_ip_efficient`

**Purpose**: Get complete security profile for an IP address in one call

**Token Efficiency**: ~2,500 tokens (vs ~15,000 raw API)  
**Savings**: 83% first call, 90%+ cached  
**Cache TTL**: 180-600 seconds (component-specific)

**What You Get**:
- ✅ Basic info (hostname, OS, MAC, repository)
- ✅ Vulnerability summary by severity
- ✅ Last scan metadata (credentialed, duration, policy)
- ✅ Installed software (top 50)
- ✅ Running services (top 50)
- ✅ Asset groups membership
- ✅ ACR score (source: Tenable vs Manual)
- ✅ Asset Exposure Score (AES)
- ✅ First/Last seen timestamps

**Usage**:
```python
# Simple usage
profile = tsc_profile_ip_efficient("10.1.20.10")

# Customize what to include
profile = tsc_profile_ip_efficient(
    ip="10.1.20.10",
    include_software=True,      # Default: True
    include_services=True,      # Default: True
    include_scan_info=True,     # Default: True
    include_asset_groups=True   # Default: True
)
```

**Example Prompts**:
- "Profile IP 10.1.20.10"
- "Give me a complete security overview of 10.1.20.10"
- "What do we know about 10.1.20.10?"

**Return Structure**:
```json
{
  "ok": true,
  "ip": "10.1.20.10",
  "summary": {
    "hostname": "webserver01.domain.com",
    "os": "Windows Server 2019",
    "repository": "Production",
    "first_seen": "1640000000",
    "last_seen": "1680000000",
    "acr_score": "8",
    "acr_source": "Manually Adjusted",
    "last_scan": "2026-06-06T10:30:00Z",
    "credentialed": "yes",
    "vulnerabilities": {
      "critical": 5,
      "high": 23,
      "medium": 67,
      "low": 12,
      "info": 34
    },
    "software_count": 142,
    "services_count": 18,
    "asset_groups_count": 3,
    "asset_exposure_score": "742"
  },
  "data": {
    "basic_info": { ... },
    "vulnerabilities": { ... },
    "last_scan": { ... },
    "software": { ... },
    "services": { ... },
    "asset_groups": { ... }
  }
}
```

**Pro Tips**:
- 🚀 Start here for any IP investigation
- 💰 Most token-efficient way to get comprehensive IP data
- 🎯 Each component cached separately for maximum reuse
- 📊 Perfect for dashboards, reports, and quick assessments

---

### Vulnerability Analysis

#### 📊 `tsc_list_vulns_by_ip_summary`

**Purpose**: Quick vulnerability counts by severity (lightweight, dashboard-friendly)

**Token Efficiency**: ~700 tokens (vs ~6,000 raw API)  
**Savings**: 88% first call, 92% cached  
**Cache TTL**: 180 seconds

**Best For**:
- ✅ Quick security posture check
- ✅ Dashboard widgets
- ✅ Initial triage
- ✅ Comparing multiple IPs
- ✅ "How many critical vulns?" questions

**Parameters**:
```python
tsc_list_vulns_by_ip_summary(
    ip="10.1.20.10",              # Required: IP address
    severity=None,                # Filter: critical, high, medium, low, info
    exploit_available=None,       # Filter: "Yes" or "No"
    first_seen=None,              # Filter: Unix epoch timestamp
    last_seen=None,               # Filter: Unix epoch timestamp
    family=None,                  # Filter: Plugin family name
    vpr_score=None,               # Filter: VPR score (e.g., ">=7.0")
    plugin_id=None,               # Filter: Specific plugin ID
    cve=None,                     # Filter: CVE ID
    port=None,                    # Filter: Port number
    protocol=None                 # Filter: TCP/UDP
)
```

**Example Prompts**:
- "How many vulnerabilities on 10.1.20.10?"
- "Show me critical vuln counts for 10.1.20.10"
- "Quick security check on 10.1.20.10"
- "What's the vuln breakdown for 10.1.20.10?"

**Return Structure**:
```json
{
  "ok": true,
  "ip": "10.1.20.10",
  "summary": {
    "total": 183,
    "by_severity": {
      "critical": 15,
      "high": 45,
      "medium": 123,
      "low": 0,
      "info": 0
    }
  },
  "filters_applied": { ... }
}
```

---

#### 📋 `tsc_list_vulns_by_ip_full`

**Purpose**: Complete vulnerability details with all fields (investigation-grade)

**Token Efficiency**: ~5,000 tokens for 50 records (vs ~12,000 raw API)  
**Savings**: 58% first call, 75% cached  
**Cache TTL**: 180 seconds

**Best For**:
- ✅ Deep vulnerability investigation
- ✅ Remediation planning
- ✅ Compliance reporting
- ✅ Export to external systems
- ✅ "What exactly is vulnerable?" questions

**Parameters**:
```python
tsc_list_vulns_by_ip_full(
    ip="10.1.20.10",              # Required: IP address
    # Same 10 filters as summary mode, PLUS:
    cvss_v3_base_score=None,      # Filter: CVSS v3 score
    epss_score=None,              # Filter: EPSS score
    patch_published=None,         # Filter: Patch publication date
    vuln_published=None,          # Filter: Vulnerability publication date
    mitigated_status=None,        # Filter: Mitigation status
    # Pagination (max 200 records per query)
    start_offset=0,               # Starting record (0-indexed)
    end_offset=50                 # Ending record (exclusive, default: 50)
)
```

**Example Prompts**:
- "Show me all vulnerabilities on 10.1.20.10"
- "What are the critical exploitable vulns on 10.1.20.10?"
- "List vulnerabilities with CVSS > 7.0 on 10.1.20.10"
- "Give me the top 20 most severe vulns on 10.1.20.10"

**Return Structure**:
```json
{
  "ok": true,
  "ip": "10.1.20.10",
  "summary": {
    "total_records": 183,
    "returned_records": 50,
    "start_offset": 0,
    "end_offset": 50,
    "has_more": true
  },
  "vulnerabilities": [
    {
      "plugin_id": "98765",
      "name": "Critical RCE Vulnerability",
      "severity": "Critical",
      "severity_id": "4",
      "port": 443,
      "protocol": "TCP",
      "family": "Web Servers",
      "cvss_v3_base_score": "9.8",
      "vpr_score": "9.2",
      "epss_score": "0.95",
      "exploit_available": "Yes",
      "exploit_frameworks": "Metasploit",
      "cve": "CVE-2024-1234",
      "first_seen": "1640000000",
      "last_seen": "1680000000",
      "synopsis": "A critical remote code execution...",
      "solution": "Apply the security patch..."
    },
    ...
  ],
  "filters_applied": { ... }
}
```

**Pro Tips**:
- 🎯 **Start with summary** → Get counts first, then drill into details if needed
- 🔍 **Use filters aggressively** → Narrow 500 vulns to 20 critical ones
- 📄 **Paginate large sets** → Get 0-50, then 50-100, etc. (max 200 per query)
- ⚡ **Leverage cache** → Repeated queries <2ms, even with different pagination
- 🤝 **Combine with Tool 1** → Profile first, then investigate specific vulnerabilities

---

## Core Tools (Generic)

Direct access to **any Tenable.sc resource** using standard CRUD operations.

### `tsc_resource_action`

**Purpose**: Unified interface for list, get, create, update, delete operations

**Why Use This**: One tool handles all CRUD operations instead of 5 separate tools

**Actions**: `list`, `get`, `create`, `update`, `delete`

**Usage**:
```python
# List all repositories
tsc_resource_action(action="list", resource="repository")

# Get specific scan
tsc_resource_action(action="get", resource="scan", object_id="12")

# Create new asset group
tsc_resource_action(
    action="create",
    resource="asset",
    body={
        "name": "Critical Servers",
        "type": "static",
        "definedIPs": "10.1.20.0/24"
    }
)

# Update scan policy
tsc_resource_action(
    action="update",
    resource="scanPolicy",
    object_id="5",
    body={"name": "Updated Policy Name"}
)

# Delete credential
tsc_resource_action(action="delete", resource="credential", object_id="8")
```

**Common Resources**:
- `repository`, `scan`, `scanResult`, `scanPolicy`
- `asset`, `credential`, `query`
- `user`, `group`, `role`
- `plugin`, `pluginFamily`
- `alert`, `dashboard`, `report`

**Example Prompts**:
- "List all scan policies"
- "Get details for scan 12"
- "Create a new asset group for production servers"
- "Update repository 5's name to 'DMZ Hosts'"

---

### Legacy Aliases (Deprecated but still work)

These convenience shortcuts call `tsc_resource_action` under the hood:

- `tsc_list(resource)` → `tsc_resource_action(action="list", resource)`
- `tsc_get(resource, object_id)` → `tsc_resource_action(action="get", ...)`
- `tsc_create(resource, body)` → `tsc_resource_action(action="create", ...)`
- `tsc_update(resource, object_id, body)` → `tsc_resource_action(action="update", ...)`
- `tsc_delete(resource, object_id)` → `tsc_resource_action(action="delete", ...)`

**Recommendation**: Use `tsc_resource_action` for new code.

---

## Specialized Tools

Advanced operations for power users.

### 🔍 `tsc_catalog`

**Purpose**: Browse available Tenable.sc resources and endpoints

**Usage**:
```python
# List all resources
catalog = tsc_catalog()

# Search for specific resources
catalog = tsc_catalog(query="scan")

# Get compact output (names only)
catalog = tsc_catalog(compact=True)

# Include admin-only resources
catalog = tsc_catalog(include_admin_or_director=True)
```

**Example Prompts**:
- "What resources are available?"
- "Show me all scan-related resources"
- "List Tenable.sc API endpoints"

---

### 📖 `tsc_resource_docs`

**Purpose**: Get documentation for a specific resource

**Usage**:
```python
# Get docs for repository resource
docs = tsc_resource_docs(resource="repository")

# Compact format (summary only)
docs = tsc_resource_docs(resource="scan", compact=True)
```

**Example Prompts**:
- "How do I use the scan resource?"
- "Show me documentation for repositories"
- "What operations are available for assets?"

---

### 👤 `tsc_current_user`

**Purpose**: Verify API user identity and permissions

**Usage**:
```python
user = tsc_current_user()
```

**Example Prompts**:
- "Who am I authenticated as?"
- "Show me my Tenable.sc user info"
- "What are my permissions?"

---

### 🔬 `tsc_analyze`

**Purpose**: Run custom analysis queries against Tenable.sc data

**⚠️ Advanced**: This is a low-level tool. Convenience tools use this internally.

**Usage**:
```python
# Run vulnerability analysis query
result = tsc_analyze({
    "tool": "vulndetails",
    "type": "vuln",
    "sourceType": "cumulative",
    "query": {
        "tool": "vulndetails",
        "filters": [
            {"filterName": "ip", "operator": "=", "value": "10.1.20.10"},
            {"filterName": "severity", "operator": "=", "value": "4"}
        ]
    },
    "sortField": "severity",
    "sortDir": "DESC"
})
```

**When to Use**:
- Custom queries not covered by convenience tools
- Advanced filtering combinations
- Specialized reporting needs

**When NOT to Use**:
- Anything covered by convenience tools (use those instead)
- Standard IP profiling (use `tsc_profile_ip_efficient`)
- Vulnerability listing (use `tsc_list_vulns_by_ip_*`)

---

### 📥 `tsc_download`

**Purpose**: Download binary/text content from Tenable.sc

**Usage**:
```python
# Download scan result
result = tsc_download(
    path="/scanResult/123/download",
    params={"format": "nessus"}
)

# Download report
result = tsc_download(
    path="/report/456/download",
    method="POST",
    body={"format": "pdf"}
)
```

**Returns**: Base64-encoded content

---

### 📤 `tsc_upload_file`

**Purpose**: Upload files to Tenable.sc (audit files, tailoring files)

**Usage**:
```python
# Upload audit file
result = tsc_upload_file(
    file_path="/path/to/audit.audit",
    context="auditfile"
)
```

**Contexts**: `auditfile`, `tailoringfile`

---

### 🔧 `tsc_request`

**Purpose**: Direct access to any Tenable.sc endpoint (escape hatch)

**⚠️ Expert Level**: Use only when other tools don't fit your need

**Usage**:
```python
# GET request
result = tsc_request(
    method="GET",
    path="/repository",
    params={"fields": "id,name"}
)

# POST request
result = tsc_request(
    method="POST",
    path="/scan/12/launch",
    body={"targets": "10.1.20.0/24"}
)
```

---

## Cache Management

### 📊 `tsc_cache_stats`

**Purpose**: View cache performance metrics

**Usage**:
```python
stats = tsc_cache_stats()
```

**Returns**:
```json
{
  "ok": true,
  "backend": "redis",
  "hit_rate": 92.5,
  "total_requests": 1000,
  "hits": 925,
  "misses": 75,
  "total_keys": 342,
  "avg_ttl": 280
}
```

**Example Prompts**:
- "Show me cache statistics"
- "What's the cache hit rate?"
- "How many items are cached?"

---

### 🗑️ `tsc_cache_clear`

**Purpose**: Clear cache entries (all or by pattern)

**Usage**:
```python
# Clear all cache
tsc_cache_clear()

# Clear specific pattern
tsc_cache_clear(pattern="repository:*")
tsc_cache_clear(pattern="scan:12")
```

**Example Prompts**:
- "Clear the cache"
- "Clear repository cache entries"
- "Invalidate cache for scan 12"

**When to Use**:
- Need fresh data immediately (can't wait for TTL)
- After making changes to Tenable.sc (create/update/delete)
- Troubleshooting stale data

---

## Quick Reference

### Decision Tree: Which Tool Should I Use?

```
Need to...

├─ Profile an IP?
│  └─ Use: tsc_profile_ip_efficient()
│     🎯 Most comprehensive, best token efficiency
│
├─ Get vulnerability counts?
│  └─ Use: tsc_list_vulns_by_ip_summary()
│     📊 Lightweight, perfect for dashboards
│
├─ Investigate vulnerabilities in detail?
│  └─ Use: tsc_list_vulns_by_ip_full()
│     📋 Complete records, filterable, paginated
│
├─ Access other Tenable.sc resources?
│  └─ Use: tsc_resource_action()
│     ⚙️ Unified CRUD interface
│
├─ Discover what's available?
│  └─ Use: tsc_catalog() or tsc_resource_docs()
│     🔍 Browse resources and endpoints
│
├─ Run custom analysis?
│  └─ Use: tsc_analyze()
│     🔬 Advanced queries
│
└─ Everything else?
   └─ Use: tsc_request()
      🔧 Direct API access (expert level)
```

---

### Token Efficiency Comparison

| Operation | Without Tools | With Convenience Tools | Savings |
|-----------|--------------|----------------------|---------|
| IP Profile | ~15,000 tokens | ~2,500 tokens | **83%** |
| Vuln Summary | ~6,000 tokens | ~700 tokens | **88%** |
| Vuln Details (50) | ~12,000 tokens | ~5,000 tokens | **58%** |
| Cached Queries | Same | ~3,000 tokens | **75%** |

**Average Savings**: **75% first call, 85%+ with caching**

---

### Cache TTL Reference

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| Static (plugins, families) | 24 hours | Rarely changes |
| Semi-static (repos, policies, users) | 30 minutes | Occasional updates |
| Dynamic (assets, queries) | 10 minutes | Regular changes |
| Real-time (scans, scan results) | 1-5 minutes | Frequent updates |
| **IP profiles** | **180-600s** | **Component-specific** |
| **Vulnerability data** | **180s** | **Semi-dynamic** |

---

### Filter Support

All convenience tools support **55+ Tenable.sc analysis filters**:

| Category | Examples |
|----------|----------|
| **Asset** | `ip`, `dns_name`, `repository`, `asset_criticality` |
| **Vulnerability** | `plugin_id`, `severity`, `family`, `port`, `protocol` |
| **CVE/Compliance** | `cve`, `cce_id`, `iavm_id`, `ms_bulletin_id` |
| **Scoring** | `vpr_score`, `cvss_v3_base_score`, `epss_score` |
| **Threat** | `exploit_available`, `exploit_frameworks` |
| **Temporal** | `first_seen`, `last_seen`, `vuln_published` |
| **Risk** | `mitigated_status`, `accept_risk_status` |

**Full list**: See [convenience_tools.py:COMMON_FILTERS](../src/tenable_sc_mcp/convenience_tools.py)

---

### Common Patterns

**Pattern 1: Quick Triage**
```
1. Profile IP → tsc_profile_ip_efficient()
2. Get vuln summary → tsc_list_vulns_by_ip_summary()
3. If critical > 0 → tsc_list_vulns_by_ip_full(severity="critical")
```

**Pattern 2: Compliance Reporting**
```
1. Get all high CVSS → tsc_list_vulns_by_ip_full(cvss_v3_base_score=">=7.0")
2. Export results
3. Generate report
```

**Pattern 3: Remediation Planning**
```
1. Get exploitable vulns → tsc_list_vulns_by_ip_full(exploit_available="Yes")
2. Filter by VPR → vpr_score=">=7.0"
3. Sort by severity (automatic)
4. Prioritize top 20
```

---

## Best Practices

### ✅ Do's

- ✅ **Start with convenience tools** - They're optimized for AI assistants
- ✅ **Use summary before full** - Get counts first, then drill down
- ✅ **Apply filters** - Narrow results to what you need
- ✅ **Leverage caching** - Repeated queries are nearly instant
- ✅ **Paginate large results** - Don't try to get 500+ records at once
- ✅ **Check error messages** - They include helpful suggestions

### ❌ Don'ts

- ❌ **Don't use raw API when convenience tools exist** - Wastes tokens
- ❌ **Don't fetch full details for "just need counts"** - Use summary mode
- ❌ **Don't exceed pagination limits** - Max 200 records per query
- ❌ **Don't ignore cache stats** - Monitor performance
- ❌ **Don't use `tsc_request` as default** - It's for edge cases

---

## Troubleshooting

### "No data found for IP"
**Problem**: IP doesn't exist in Tenable.sc or has no scan results  
**Solution**: Use `tsc_resource_action(action="list", resource="repository")` to find valid IPs first

### "Invalid IP address format"
**Problem**: IP format is incorrect  
**Solution**: Use format like `10.1.20.10` or `2001:db8::1` (no hostnames)

### "end_offset cannot exceed 200"
**Problem**: Trying to get too many records at once  
**Solution**: Use multiple queries with pagination (0-200, 200-400, etc.)

### Stale Results
**Problem**: Cached data is outdated  
**Solution**: Wait for TTL (3 minutes) or use `tsc_cache_clear()` for immediate refresh

### High Token Usage
**Problem**: Response is too large  
**Solution**: 
- Use summary mode instead of full
- Apply more filters to narrow results
- Reduce pagination window (50 instead of 200)

---

## Additional Resources

- **[README.md](../README.md)** - Installation, deployment, quick start
- **[TOOL2_TEST_QUERIES.md](../TOOL2_TEST_QUERIES.md)** - 30+ test queries for Tool 2
- **[CONVENIENCE_TOOLS_ROADMAP.md](../CONVENIENCE_TOOLS_ROADMAP.md)** - Future tools (24 total planned)
- **[CACHING_DEEP_DIVE.md](../CACHING_DEEP_DIVE.md)** - Cache architecture details
- **[Tenable.sc API Docs](https://docs.tenable.com/security-center/api/index.htm)** - Official API reference

---

## Need Help?

- 💬 **Ask your AI assistant**: "How do I [task]?"
- 📖 **Read the docs**: Check tool descriptions above
- 🧪 **Try examples**: Use test queries from TOOL2_TEST_QUERIES.md
- 🐛 **Report issues**: [GitHub Issues](https://github.com/ABMJ/tenable-sc-mcp-server/issues)

---

**Version**: 0.2.0  
**Last Updated**: 2026-06-06  
**Status**: ✅ Tool 1 & 2 Complete, 22 more coming in Weeks 1-3

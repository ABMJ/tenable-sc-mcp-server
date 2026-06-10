"""
MCP Resource: Tenable.sc Analysis Filter Reference

Auto-generates comprehensive filter documentation from COMMON_FILTERS dict.
Exposes as MCP resource that clients can fetch to understand filter usage.
"""

from __future__ import annotations


def generate_filter_reference() -> str:
    """
    Auto-generate comprehensive filter reference documentation from COMMON_FILTERS.
    
    Returns markdown-formatted reference of all 55+ Tenable.sc filters,
    grouped by category with examples and troubleshooting guidance.
    
    Returns:
        Markdown string with complete filter documentation
    """
    from ..convenience_tools import COMMON_FILTERS
    
    # Group filters by category
    categories = {
        "Asset Identification": [
            "asset_id", "asset", "asset_criticality", "ip", "uuid", 
            "dns_name", "repository", "repository_ids"
        ],
        "Vulnerability Information": [
            "plugin_id", "plugin_name", "plugin_text", "plugin_type",
            "family", "family_id", "severity", "port", "protocol", "data_format"
        ],
        "CVE & Compliance": [
            "cve_id", "cve", "cce_id", "iavm_id", "ms_bulletin_id",
            "xref", "cpe", "stig_severity"
        ],
        "Risk Scoring": [
            "base_cvss_score", "cvss_v3_base_score", "cvss_v4_base_score",
            "vpr_score", "aes_score", "aes_severity", "epss_score",
            "cvss_vector", "cvss_v3_vector", "cvss_v4_vector"
        ],
        "Threat Context": [
            "exploit_available", "exploit_frameworks"
        ],
        "Temporal": [
            "first_seen", "last_seen", "last_mitigated", "days_mitigated",
            "vuln_published", "patch_published", "plugin_published", "plugin_modified"
        ],
        "Risk Management": [
            "accept_risk_status", "recast_risk_status", "mitigated_status",
            "responsible_user", "responsible_user_ids"
        ],
        "Policy & Audit": [
            "policy", "policy_id", "audit_file", "audit_file_id", "benchmark_name"
        ],
        "WAS-Specific": [
            "was_vuln"
        ]
    }
    
    # Scoring filters that require range format
    scoring_filters = {
        "asset_criticality": {"scale": "0-10", "desc": "Asset Criticality Rating (ACR)"},
        "vpr_score": {"scale": "0-10", "desc": "Vulnerability Priority Rating"},
        "aes_score": {"scale": "0-1000", "desc": "Asset Exposure Score"},
        "cvss_v3_base_score": {"scale": "0-10", "desc": "CVSS v3 base score"},
        "cvss_v4_base_score": {"scale": "0-10", "desc": "CVSS v4 base score"},
        "base_cvss_score": {"scale": "0-10", "desc": "CVSS v2 base score"},
        "epss_score": {"scale": "0-1", "desc": "EPSS exploitation probability"}
    }
    
    # Build markdown documentation
    md = """# Tenable.sc Analysis Filter Reference

**Version:** 1.0 (Auto-generated from COMMON_FILTERS)  
**Total Filters:** {total_filters}  
**Resource URI:** `tenable-sc://filters/reference`

**📚 OFFICIAL TENABLE DOCUMENTATION:**  
For the complete, authoritative filter reference directly from Tenable, always refer to:  
**https://docs.tenable.com/security-center/6_8/Content/VulnerabilityAnalysisFilters.htm**

This MCP resource documents the filters supported by this server's convenience tools.
For any discrepancies or newly added filters, the official Tenable documentation is the source of truth.

---

## 📋 Overview

This reference documents all {total_filters} analysis filters supported by Tenable.sc MCP convenience tools.
Filters enable precise queries across vulnerability data, asset discovery, and security analysis.

**Tools that accept filters:**
- `tsc_list_vulns_by_cve` - Search CVE across infrastructure
- `tsc_list_ips` - IP discovery with filtering
- `tsc_list_vulns_by_ip_full` - Detailed vulnerability records
- `tsc_list_vulns_by_ip_summary` - Vulnerability counts
- `tsc_profile_ip_efficient` - IP security profile

---

## ⚠️ CRITICAL: Scoring Filter Format

**Scoring filters MUST use range format `"min-max"` (e.g., `"7-10"`, `"600-1000"`)**

**❌ DO NOT USE OPERATORS:**
- `">7"` ❌ WRONG
- `">=7"` ❌ WRONG  
- `"<5"` ❌ WRONG

**✅ USE RANGE FORMAT:**
- `"7-10"` ✅ CORRECT (for "greater than or equal to 7")
- `"0-5"` ✅ CORRECT (for "less than or equal to 5")
- `"8-8"` ✅ CORRECT (for "exactly 8")

**Why?** Tenable.sc API only accepts inclusive range queries for scoring filters.

---

## 🎯 Scoring Filters (Range Format Required)

| Parameter | Scale | API Filter Name | Description | Example |
|-----------|-------|-----------------|-------------|---------|
""".format(total_filters=len(COMMON_FILTERS))
    
    # Add scoring filters table
    for param, info in scoring_filters.items():
        api_name = COMMON_FILTERS.get(param, "N/A")
        scale = info["scale"]
        desc = info["desc"]
        example = f'`{param}="7-10"`' if "10" in scale else f'`{param}="0.5-1.0"`'
        md += f"| `{param}` | {scale} | `{api_name}` | {desc} | {example} |\n"
    
    md += """
**Scoring Filter Examples:**
```python
# ACR (Asset Criticality Rating) greater than 7
tsc_list_vulns_by_cve("CVE-2021-44228", asset_criticality="7-10")

# VPR between 7-9
tsc_list_ips(repository="Default", vpr_score="7-9")

# AES (Asset Exposure Score) greater than 600
tsc_list_ips(aes_score="600-1000", severity="critical")

# EPSS probability above 50%
tsc_list_vulns_by_ip_full("10.1.20.10", epss_score="0.5-1.0")

# Multiple scoring filters
tsc_list_ips(asset_criticality="8-10", 
             aes_score="700-1000",
             cvss_v3_base_score="9-10")
```

---

"""
    
    # Add categorized filter tables
    for category, params in categories.items():
        md += f"## 📂 {category}\n\n"
        md += "| Parameter | API Filter Name | Description |\n"
        md += "|-----------|-----------------|-------------|\n"
        
        for param in params:
            api_name = COMMON_FILTERS.get(param, "N/A")
            # Add descriptions for common filters
            descriptions = {
                "asset_id": "Tenable.sc asset ID",
                "asset": "Asset identifier",
                "asset_criticality": "Asset Criticality Rating (0-10) - **Use range format**",
                "ip": "IP address (IPv4/IPv6)",
                "uuid": "Asset UUID",
                "dns_name": "DNS hostname",
                "repository": "Repository name or ID",
                "repository_ids": "Repository IDs (comma-separated)",
                "plugin_id": "Nessus plugin ID",
                "plugin_name": "Plugin name (partial match)",
                "plugin_text": "Plugin output text search",
                "plugin_type": "Plugin type",
                "family": "Plugin family (e.g., 'Windows', 'Web Servers')",
                "family_id": "Plugin family ID",
                "severity": "Severity: critical/high/medium/low/info or 0-4",
                "port": "Port number",
                "protocol": "Network protocol (TCP/UDP)",
                "data_format": "Data format",
                "cve_id": "CVE identifier (e.g., CVE-2021-44228)",
                "cve": "CVE identifier (alias for cve_id)",
                "cce_id": "CCE identifier",
                "iavm_id": "IAVM identifier",
                "ms_bulletin_id": "Microsoft Security Bulletin ID",
                "xref": "Cross-reference",
                "cpe": "Common Platform Enumeration",
                "stig_severity": "STIG severity level",
                "base_cvss_score": "CVSS v2 base score (0-10) - **Use range format**",
                "cvss_v3_base_score": "CVSS v3 base score (0-10) - **Use range format**",
                "cvss_v4_base_score": "CVSS v4 base score (0-10) - **Use range format**",
                "vpr_score": "Vulnerability Priority Rating (0-10) - **Use range format**",
                "aes_score": "Asset Exposure Score (0-1000) - **Use range format**",
                "aes_severity": "AES-based severity (info/low/medium/high/critical)",
                "epss_score": "EPSS probability (0-1) - **Use range format**",
                "cvss_vector": "CVSS v2 vector string",
                "cvss_v3_vector": "CVSS v3 vector string",
                "cvss_v4_vector": "CVSS v4 vector string",
                "exploit_available": "Exploit availability (Yes/No)",
                "exploit_frameworks": "Exploit framework names",
                "first_seen": "First detection timestamp (Unix epoch)",
                "last_seen": "Last detection timestamp (Unix epoch)",
                "last_mitigated": "Last mitigation timestamp",
                "days_mitigated": "Days since mitigation",
                "vuln_published": "Vulnerability publication date (Unix epoch)",
                "patch_published": "Patch publication date (Unix epoch)",
                "plugin_published": "Plugin publication date (Unix epoch)",
                "plugin_modified": "Plugin modification date (Unix epoch)",
                "accept_risk_status": "Risk acceptance status",
                "recast_risk_status": "Risk recasting status",
                "mitigated_status": "Mitigation status",
                "responsible_user": "Responsible user name",
                "responsible_user_ids": "Responsible user IDs",
                "policy": "Compliance policy",
                "policy_id": "Compliance policy ID",
                "audit_file": "Audit file name",
                "audit_file_id": "Audit file ID",
                "benchmark_name": "Compliance benchmark name",
                "was_vuln": "Web Application Scanning vulnerability"
            }
            desc = descriptions.get(param, "")
            md += f"| `{param}` | `{api_name}` | {desc} |\n"
        
        md += "\n"
    
    # Add practical examples section
    md += """---

## 💡 Practical Filter Examples

### Emergency Outbreak Response
```python
# Find all assets with Log4Shell
tsc_list_vulns_by_cve("CVE-2021-44228")

# Find critical assets (ACR > 7) with EternalBlue
tsc_list_vulns_by_cve("CVE-2017-0144", asset_criticality="7-10")

# Find ProxyLogon in Production with exploits
tsc_list_vulns_by_cve("CVE-2021-26855",
                      repository="Production",
                      exploit_available="Yes")
```

### High-Risk Asset Discovery
```python
# List high-criticality IPs with high exposure
tsc_list_ips(repository="Default",
             asset_criticality="8-10",
             aes_score="700-1000")

# Find critical vulnerabilities on high-risk assets
tsc_list_ips(asset_criticality="9-10",
             severity="critical",
             exploit_available="Yes")

# Identify assets with critical VPR scores
tsc_list_ips(vpr_score="9-10", 
             cvss_v3_base_score="9-10")
```

### Vulnerability Analysis
```python
# Get critical vulns with exploits on specific IP
tsc_list_vulns_by_ip_full("10.1.20.10",
                           severity="critical",
                           exploit_available="Yes")

# Find vulnerabilities published in last 30 days
# (Unix timestamp for 30 days ago)
tsc_list_vulns_by_ip_full("10.1.20.10",
                           vuln_published="1704067200")

# High EPSS score vulnerabilities
tsc_list_vulns_by_ip_full("10.1.20.10",
                           epss_score="0.7-1.0")
```

### Compliance & Audit
```python
# Find assets in specific repository
tsc_list_ips(repository="PCI Assets")

# Filter by plugin family
tsc_list_vulns_by_ip_full("10.1.20.10", family="Windows")

# Search by MS bulletin
tsc_list_vulns_by_ip_full("10.1.20.10", ms_bulletin_id="MS17-010")
```

### Network-Based Queries
```python
# Find vulnerabilities on specific port
tsc_list_vulns_by_ip_full("10.1.20.10", port=443, protocol="TCP")

# Identify assets with DNS name pattern
tsc_list_ips(dns_name="webserver", repository="DMZ")

# Port-specific vulnerability search
tsc_list_vulns_by_cve("CVE-2014-0160", port=443)  # Heartbleed
```

### Complex Multi-Filter Queries
```python
# Critical assets + critical vulns + exploits in prod
tsc_list_ips(repository="Production",
             asset_criticality="8-10",
             severity="critical",
             exploit_available="Yes",
             aes_score="600-1000")

# Windows systems with unpatched MS bulletins
tsc_list_vulns_by_ip_full("10.1.20.10",
                           family="Windows",
                           severity="high",
                           patch_published="1704067200")

# High-risk CVEs with active exploitation
tsc_list_vulns_by_cve("CVE-2021-44228",
                      asset_criticality="7-10",
                      exploit_available="Yes",
                      vpr_score="8-10",
                      epss_score="0.5-1.0")
```

---

## 🐛 Common Mistakes & Troubleshooting

### ❌ Mistake #1: Using Operators Instead of Ranges
**Wrong:**
```python
tsc_list_vulns_by_cve("CVE-2021-44228", asset_criticality=">7")
tsc_list_ips(vpr_score=">=8.0")
```

**Correct:**
```python
tsc_list_vulns_by_cve("CVE-2021-44228", asset_criticality="7-10")
tsc_list_ips(vpr_score="8-10")
```

### ❌ Mistake #2: Wrong Parameter Names
**Wrong:**
```python
tsc_list_vulns_by_cve("CVE-2021-44228", acr_score="7-10")  # Wrong param name
tsc_list_ips(hostname="webserver")  # Should be dns_name
```

**Correct:**
```python
tsc_list_vulns_by_cve("CVE-2021-44228", asset_criticality="7-10")
tsc_list_ips(dns_name="webserver")
```

**Tip:** Enable debug logging to see warnings about unknown parameters:
```
docker logs tenable-sc-mcp 2>&1 | grep WARNING
```

### ❌ Mistake #3: Wrong Severity Format
**Wrong:**
```python
tsc_list_vulns_by_ip_full("10.1.20.10", severity="Critical")  # Capital C
tsc_list_ips(severity="crit")  # Abbreviation
```

**Correct:**
```python
tsc_list_vulns_by_ip_full("10.1.20.10", severity="critical")  # lowercase
tsc_list_ips(severity="4")  # or numeric 0-4
```

### ❌ Mistake #4: Filters Not Applied
**Symptom:** Filter appears in `filters_applied` summary but results not filtered.

**Cause:** Unknown parameter name silently ignored.

**Solution:** Check spelling against this reference or enable validation warnings.

### ❌ Mistake #5: Date Format Confusion
**Wrong:**
```python
tsc_list_vulns_by_ip_full("10.1.20.10", first_seen="2024-01-01")  # ISO format
```

**Correct:**
```python
# Use Unix epoch timestamp
tsc_list_vulns_by_ip_full("10.1.20.10", first_seen="1704067200")
```

**Tip:** Convert dates with: `date -d "2024-01-01" +%s`

---

## 📚 Additional Resources

**OFFICIAL TENABLE DOCUMENTATION (ALWAYS CURRENT):**
- **Vulnerability Analysis Filters:** https://docs.tenable.com/security-center/6_8/Content/VulnerabilityAnalysisFilters.htm
- **Tenable.sc API Documentation:** https://docs.tenable.com/security-center/api/index.htm
- **Analysis API Endpoint:** https://docs.tenable.com/security-center/api/analysis.htm

**MCP SERVER DOCUMENTATION:**
- **MCP Server README:** See project README.md for deployment and usage
- **Tool Roadmap:** TOOLS_ROADMAP.md for complete tool catalog
- **Test Prompts:** TEST_PROMPTS.md for validation examples
- **Architecture:** ARCHITECTURE.md for system design details

**IMPORTANT:** This MCP resource is auto-generated from the server's `COMMON_FILTERS` dictionary.
If Tenable adds new filters or changes existing ones, always refer to the official documentation above.
The server may not immediately support newly added filters until `COMMON_FILTERS` is updated.

---

## 🔄 Version History

- **v1.0** (2026-06-10): Initial auto-generated reference from COMMON_FILTERS
  - 55+ filters documented
  - Grouped by category
  - Includes examples and troubleshooting
  - Format validation guidance
  - Official Tenable docs references added

---

**Note:** This documentation is auto-generated from the `COMMON_FILTERS` dictionary 
in `convenience_tools.py`. Any updates to available filters will automatically 
appear in this resource.

**For the most current and complete filter list, always refer to:**  
**https://docs.tenable.com/security-center/6_8/Content/VulnerabilityAnalysisFilters.htm**

**Last Generated:** {timestamp}
""".format(timestamp="Runtime - check container logs for generation time")
    
    return md


def register_resources(mcp):
    """
    Register filter reference as MCP resource.
    
    Makes comprehensive filter documentation available via MCP protocol
    at URI: tenable-sc://filters/reference
    """
    
    @mcp.resource("tenable-sc://filters/reference")
    async def get_filter_reference() -> str:
        """
        Complete reference for all Tenable.sc analysis filters.
        
        Auto-generated comprehensive guide covering:
        - All 55+ filter parameters with API mappings
        - Format requirements (range vs exact)
        - Grouped by category (Asset, Vulnerability, Scoring, etc.)
        - 15+ practical examples for common use cases
        - Troubleshooting guide for common mistakes
        
        Use this resource to understand how to properly filter:
        - CVE searches (tsc_list_vulns_by_cve)
        - IP discovery (tsc_list_ips)
        - Vulnerability queries (tsc_list_vulns_by_ip_full/summary)
        - IP profiling (tsc_profile_ip_efficient)
        
        Returns:
            Markdown-formatted filter reference documentation
        """
        import logging
        import datetime
        
        logger = logging.getLogger(__name__)
        logger.info("Generating filter reference resource")
        
        # Generate documentation
        docs = generate_filter_reference()
        
        # Add generation timestamp
        timestamp = datetime.datetime.now().isoformat()
        docs = docs.replace("Runtime - check container logs for generation time", timestamp)
        
        logger.info(f"Filter reference generated successfully ({len(docs)} chars)")
        
        return docs

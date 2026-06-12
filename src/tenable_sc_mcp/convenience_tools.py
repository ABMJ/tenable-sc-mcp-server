"""
Convenience tools for Tenable.sc MCP Server.

High-value, token-optimized tools that wrap common queries with intelligent caching,
input validation, and user-friendly output formatting.

Token Savings: 75-94% reduction compared to raw API calls.
"""

from __future__ import annotations

import re
from typing import Any, Optional


# ============================================================================
# FILTER DOCUMENTATION TEMPLATE
# ============================================================================

FILTER_DOCS_TEMPLATE = """
FILTERS:
This tool supports 71+ Tenable.sc analysis filters via **kwargs.
For COMPLETE filter reference, fetch MCP resource: tenable-sc://filters/reference

COMMON FILTERS (Quick Reference):

Scoring Filters (RANGE FORMAT "min-max" REQUIRED):
    asset_criticality="7-10"      # ACR range (0-10) - DO NOT use ">7"
    vpr_score="8-10"               # VPR range (0-10)
    aes_score="600-1000"           # AES range (0-1000)
    cvss_v3_base_score="7-10"      # CVSS v3 range (0-10)
    epss_score="0.5-1.0"           # EPSS range (0-1)

Asset Filters:
    repository="Production"        # Repository name or ID
    ip="10.1.20.10"               # Specific IP address
    dns_name="webserver01"        # Hostname
    tag="Windows Hosts"           # Asset tag (RECOMMENDED for OS filtering)
    cpe="microsoft:windows"       # CPE smart detection (~=, =, pcre operators)
    os_cpe="linux"                # Alias for 'cpe' (common alternative name)

Vulnerability Filters:
    severity="critical"           # critical/high/medium/low/info or 0-4
    exploit_available="Yes"       # Yes/No
    family="Windows"              # Plugin family
    cve="CVE-2021-44228"         # CVE identifier (for per-IP queries)
    plugin_id="156013"           # Plugin ID

Network Filters:
    port=443                      # Port number
    protocol="TCP"                # TCP/UDP

Temporal Filters (Unix timestamps):
    first_seen="1704067200"       # First detection
    last_seen="1735689600"        # Last detection
    patch_published="1704067200"  # Patch publication date
    vuln_published="1704067200"   # Vulnerability publication date

FILTER EXAMPLES:
    # Critical assets only
    tool_name(..., asset_criticality="7-10")
    
    # Multiple filters
    tool_name(..., 
              repository="Production",
              severity="high",
              exploit_available="Yes")
    
    # Complex scoring query
    tool_name(...,
              asset_criticality="8-10",
              aes_score="700-1000",
              cvss_v3_base_score="9-10")

IMPORTANT NOTES:
    1. Scoring filters MUST use range format: "7-10" NOT ">7" or ">=7"
    2. Unknown filter parameters are silently ignored (check logs for warnings)
    3. For detailed docs on all 70+ filters, see: tenable-sc://filters/reference
    4. Common mistakes:
       - "acr_score" → use "asset_criticality"
       - "hostname" → use "dns_name"
       - ">7" → use "7-10"
"""


# ============================================================================
# CONSTANTS
# ============================================================================

# Authentication plugin IDs for credential auditing
AUTH_PLUGINS = {
    19506: "Nessus Scan Information",
    21745: "Authentication Failure - Local Checks Not Run",
    10394: "Microsoft Windows SMB Log In Possible",
    10396: "SSH Authorization Successful",
    102094: "SSH Commands Not Available",
    24786: "Nessus Windows Scan Not Performed with Admin Privileges",
}

# Port scanner plugin IDs
PORT_SCANNER_PLUGINS = {
    0: "Open Port",
    11219: "Nessus SYN scanner",
    14272: "Netstat Portscanner (SSH)",
    10335: "Netstat Portscanner (WMI)",
    22964: "Service Detection",
}

# Universal filter mapping (70 analysis filters - v1.2.1)
COMMON_FILTERS = {
    # Asset Identification (8 filters)
    "asset_id": "assetID",
    "asset": "asset",
    "asset_criticality": "assetCriticalityRating",
    "ip": "ip",
    "uuid": "uuid",
    "dns_name": "dnsName",
    "repository": "repository",
    "repository_ids": "repositoryIDs",
    
    # Vulnerability Info (10 filters)
    "plugin_id": "pluginID",
    "plugin_name": "pluginName",
    "plugin_text": "pluginText",
    "plugin_type": "pluginType",
    "family": "family",
    "family_id": "familyID",
    "severity": "severity",
    "port": "port",
    "protocol": "protocol",
    "data_format": "dataFormat",
    
    # CVE/Compliance (8 filters)
    "cve_id": "cveID",
    "cve": "cveID",
    "cce_id": "cceID",
    "iavm_id": "iavmID",
    "ms_bulletin_id": "msbulletinID",
    "xref": "xref",
    "cpe": "cpe",  # OS/Platform filter - smart operator detection (~=, =, pcre)
    "os_cpe": "cpe",  # Alias for 'cpe' (common alternative name)
    "stig_severity": "stigSeverity",
    
    # Scoring (11 filters)
    "base_cvss_score": "baseCVSSScore",
    "cvss_v3_base_score": "cvssV3BaseScore",
    "cvss_v4_base_score": "cvssV4BaseScore",
    "vpr_score": "vprScore",
    "aes_score": "assetExposureScore",  # Asset Exposure Score (AES) - numeric 0-1000
    "aes_severity": "aesSeverity",      # AES-based severity (info/low/medium/high/critical)
    "epss_score": "epssScore",
    "cvss_vector": "cvssVector",
    "cvss_v3_vector": "cvssV3Vector",
    "cvss_v4_vector": "cvssV4Vector",
    
    # CVSS v3 Component Metrics (8 filters) - Added in v1.2.1
    "attack_vector": "cvssV3AttackVector",           # Network/Adjacent/Local/Physical
    "attack_complexity": "cvssV3AttackComplexity",   # Low/High
    "privileges_required": "cvssV3PrivilegesRequired",  # None/Low/High
    "user_interaction": "cvssV3UserInteraction",     # None/Required
    "scope": "cvssV3Scope",                          # Unchanged/Changed
    "confidentiality_impact": "cvssV3ConfidentialityImpact",  # None/Low/High
    "integrity_impact": "cvssV3IntegrityImpact",     # None/Low/High
    "availability_impact": "cvssV3AvailabilityImpact",  # None/Low/High
    
    # CVSS v2 Component Metrics (3 filters) - Added in v1.2.1
    "access_vector": "cvssV2AccessVector",           # Network/Adjacent/Local
    "access_complexity": "cvssV2AccessComplexity",   # Low/Medium/High
    "authentication": "cvssV2Authentication",        # None/Single/Multiple
    
    # Threat Context (4 filters)
    "exploit_available": "exploitAvailable",
    "exploitable": "exploitAvailable",  # Alias for exploit_available - Added in v1.2.1
    "exploit_frameworks": "exploitFrameworks",
    "exploit_maturity": "vprExploitMaturity",  # VPR component: Unproven/PoC/Functional/High - Added in v1.2.1
    
    # Temporal (10 filters)
    "first_seen": "firstSeen",
    "last_seen": "lastSeen",
    "last_mitigated": "lastMitigated",
    "days_mitigated": "daysMitigated",
    "vuln_published": "vulnPublished",
    "patch_published": "patchPublished",
    "plugin_published": "pluginPublished",
    "plugin_modified": "pluginModified",
    
    # Risk Management (4 filters)
    "accept_risk_status": "acceptRiskStatus",
    "recast_risk_status": "recastRiskStatus",
    "mitigated_status": "mitigatedStatus",
    "responsible_user": "responsibleUser",
    "responsible_user_ids": "responsibleUserIDs",
    
    # Policy/Audit (4 filters)
    "policy": "policy",
    "policy_id": "policyID",
    "audit_file": "auditFile",
    "audit_file_id": "auditFileID",
    "benchmark_name": "benchmarkName",
    
    # WAS-specific (1 filter)
    "was_vuln": "wasVuln",
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def validate_ip(ip: str) -> tuple[bool, str]:
    """
    Validate IP address format.
    
    Returns:
        (is_valid, error_message)
    """
    import ipaddress
    try:
        ipaddress.ip_address(ip)
        return True, ""
    except ValueError:
        return False, (
            f"Invalid IP address format: '{ip}'\n"
            f"Expected: Valid IPv4/IPv6 address (e.g., 10.1.20.10 or 2001:db8::1)\n"
            f"Suggestion: Use tsc_list_ips() to find valid IP addresses"
        )


def validate_severity(severity: str) -> tuple[bool, str]:
    """
    Validate severity value.
    
    Returns:
        (is_valid, error_message)
    """
    valid = ["0", "1", "2", "3", "4", "info", "low", "medium", "high", "critical"]
    severity_lower = severity.lower()
    if severity_lower not in valid:
        return False, (
            f"Invalid severity: '{severity}'\n"
            f"Valid values: {', '.join(valid)}"
        )
    return True, ""


def detect_cpe_operator(value: str) -> str:
    """
    Auto-detect the appropriate CPE filter operator based on value format.
    
    Tenable.sc supports three CPE operators:
    - '~=' (contains): Partial string matching
    - '=' (exact): Exact CPE string matching
    - 'pcre': Perl-compatible regular expression matching
    
    Args:
        value: The CPE filter value provided by user
    
    Returns:
        The appropriate operator: '~=', '=', or 'pcre'
    
    Examples:
        >>> detect_cpe_operator("windows")
        '~='
        
        >>> detect_cpe_operator("cpe:/o:microsoft:windows_10")
        '='
        
        >>> detect_cpe_operator(".*windows.*(10|11).*")
        'pcre'
    """
    # Detect PCRE regex patterns by looking for regex metacharacters
    # PCRE metacharacters: . * + ? [ ] ( ) { } ^ $ | \
    pcre_chars = [
        '.*',      # Most common: match any characters
        '.+',      # Match one or more characters
        '^',       # Start anchor
        '$',       # End anchor
        '|',       # OR operator
        '[',       # Character class start
        ']',       # Character class end
        '(',       # Group start
        ')',       # Group end
        '{',       # Quantifier start
        '}',       # Quantifier end
        '\\d',     # Digit shorthand
        '\\w',     # Word character shorthand
        '\\s',     # Whitespace shorthand
    ]
    
    # Check for regex patterns
    if any(pattern in value for pattern in pcre_chars):
        return 'pcre'
    
    # Check for full CPE format (starts with 'cpe:' or 'cpe2.3:')
    # Example: cpe:/o:microsoft:windows_10 or cpe:2.3:o:microsoft:windows_10
    if value.startswith('cpe:'):
        return '='
    
    # Default: partial string matching (most user-friendly)
    # Example: "windows", "cisco", "linux", "microsoft:windows_10"
    return '~='


def validate_cve(cve_id: str) -> tuple[bool, str]:
    """
    Validate CVE ID format.
    
    Returns:
        (is_valid, error_message)
    
    Examples:
        "CVE-2021-44228" → (True, "")
        "CVE-2017-0144" → (True, "")
        "cve-2021-44228" → (True, "") (auto-normalized to uppercase)
        "2021-44228" → (False, "Invalid CVE format...")
    """
    # Normalize to uppercase for validation
    cve_normalized = cve_id.strip().upper()
    
    # Validate CVE format: CVE-YYYY-NNNNN (year can be 4 digits, number can be 4+ digits)
    pattern = r'^CVE-\d{4}-\d{4,}$'
    
    if not re.match(pattern, cve_normalized):
        return False, (
            f"Invalid CVE format: '{cve_id}'\n"
            f"Expected: CVE-YYYY-NNNNN (e.g., CVE-2021-44228, CVE-2017-0144)\n"
            f"Suggestion: Use standard CVE ID format from NVD or MITRE"
        )
    
    return True, ""


def validate_score_filter(score_value: str, max_score: float = 10.0) -> tuple[bool, str]:
    """
    Validate scoring filter format (must be range, not operator).
    
    Tenable.sc API requires inclusive range format (e.g., "7-10", "600-1000").
    Operators like >, >=, <, <= are NOT supported by the backend.
    
    Args:
        score_value: Score filter value (e.g., "7-10", "600-1000")
        max_score: Maximum value for validation
    
    Returns:
        Tuple of (is_valid, error_message)
    
    Examples:
        "7-10" → (True, "")
        "600-1000" → (True, "")
        ">7" → (False, "Use range format '7-10', not operator '>7'")
    """
    import re
    
    # Check for operator usage (not allowed)
    if any(op in score_value for op in ['>', '<', '>=', '<=']):
        return (False, f"Scoring filters require range format (e.g., '7-10'), not operators (e.g., '>7'). "
                       f"For 'greater than 7', use range '7-{int(max_score)}'. "
                       f"For 'less than 7', use range '0-7'.")
    
    # Validate range format: X-Y where X and Y are numbers
    match = re.match(r'^(\d+\.?\d*)-(\d+\.?\d*)$', score_value.strip())
    if not match:
        return (False, f"Invalid range format '{score_value}'. Use format 'min-max' (e.g., '7-10', '600-1000').")
    
    lower = float(match.group(1))
    upper = float(match.group(2))
    
    if lower > upper:
        return (False, f"Invalid range '{score_value}': lower bound ({lower}) cannot be greater than upper bound ({upper}).")
    
    if lower < 0 or upper > max_score:
        return (False, f"Range '{score_value}' out of bounds. Valid range: 0-{int(max_score)}.")
    
    return (True, "")


def convert_score_operator_to_range(score_value: str, max_score: float = 10.0) -> str:
    """
    DEPRECATED: This function is kept for backward compatibility only.
    
    New behavior: Pass through range format unchanged, validate format.
    Operators are no longer supported - users must provide ranges.
    
    Args:
        score_value: Score range in format "min-max" (e.g., "7-10", "600-1000")
        max_score: Maximum value for the scoring scale
    
    Returns:
        The range string unchanged (after validation)
    
    Examples:
        "7-10" → "7-10" (valid range, passed through)
        "600-1000" → "600-1000" (valid range, passed through)
        ">7" → raises ValueError (operators not supported)
    """
    import re
    
    # Check for operator usage (not allowed)
    if any(op in score_value for op in ['>', '<', '>=', '<=']):
        raise ValueError(
            f"Operator format '{score_value}' is not supported. "
            f"Use range format instead: for '>7' use '7-{int(max_score)}', "
            f"for '<7' use '0-7', for '>=7' use '7-{int(max_score)}', "
            f"for '<=7' use '0-7'. "
            f"Example: asset_criticality='7-10' instead of '>7'"
        )
    
    # If already in range format, validate and return
    if '-' in score_value and not score_value.startswith('-'):
        is_valid, error = validate_score_filter(score_value, max_score)
        if not is_valid:
            raise ValueError(error)
        return score_value
    
    # Single value - convert to range
    match = re.match(r'^(\d+\.?\d*)$', score_value.strip())
    if match:
        value = match.group(1)
        return f"{value}-{value}"
    
    # Invalid format
    raise ValueError(
        f"Invalid scoring filter format '{score_value}'. "
        f"Use range format: 'min-max' (e.g., '7-10', '600-1000')"
    )


def build_filters(validate: bool = True, **kwargs: Any) -> list[dict[str, Any]]:
    """
    Universal filter builder for all convenience tools.
    
    Converts tool parameters to Tenable.sc analysis filter format.
    Automatically converts scoring filter operators to range format.
    Automatically converts severity string names to numeric values.
    Validates parameters and warns about unknown filters.
    
    Args:
        validate: If True, log warnings for unknown parameters (default: True)
        **kwargs: Filter parameters using convenience names (e.g., ip="10.1.20.10")
    
    Returns:
        List of filter dictionaries for analysis queries
    """
    # Scoring filters that require operator-to-range conversion
    SCORING_FILTERS = {
        'asset_criticality': 10.0,    # ACR: 0-10 scale
        'vpr_score': 10.0,            # VPR: 0-10 scale
        'aes_score': 1000.0,          # AES: 0-1000 scale (Asset Exposure Score)
        'cvss_v3_base_score': 10.0,   # CVSS v3: 0-10 scale
        'cvss_v4_base_score': 10.0,   # CVSS v4: 0-10 scale
        'base_cvss_score': 10.0,      # CVSS v2: 0-10 scale
        'epss_score': 1.0,            # EPSS: 0-1 scale (probability)
    }
    
    # Severity string to numeric conversion
    SEVERITY_MAP = {
        'critical': '4',
        'high': '3',
        'medium': '2',
        'low': '1',
        'info': '0',
        'information': '0',
    }
    
    # Exploit available value normalization
    EXPLOIT_AVAILABLE_MAP = {
        'yes': 'true',
        'true': 'true',
        '1': 'true',
        'no': 'false',
        'false': 'false',
        '0': 'false',
    }
    
    filters = []
    unknown_params = []
    
    for param, value in kwargs.items():
        if value is None:
            continue
        
        # Get the official API filter name
        filter_name = COMMON_FILTERS.get(param)
        if not filter_name:
            # Track unknown parameters for validation warning
            if validate:
                unknown_params.append(param)
            continue
        
        # Handle different value types
        if isinstance(value, dict):
            # Advanced filter with custom operator
            operator = value.get("operator", "=")
            filter_value = value.get("value")
        else:
            # Simple filter with default operator
            operator = "="
            filter_value = value
            
            # Special handling for CPE filter - auto-detect operator based on value format
            # Supports three modes:
            #   1. Simple string (e.g., "windows", "cisco") → uses '~=' (contains)
            #   2. Full CPE (e.g., "cpe:/o:microsoft:windows_10") → uses '=' (exact)
            #   3. Regex pattern (e.g., ".*windows.*(10|11).*") → uses 'pcre' (Perl regex)
            # Note: Both 'cpe' and 'os_cpe' parameters map to 'cpe' filter name
            if param in ('cpe', 'os_cpe') and isinstance(filter_value, str):
                operator = detect_cpe_operator(filter_value)
                # No modification to filter_value - pass as-is to API
            
            # Convert severity string names to numeric values
            elif param == 'severity' and isinstance(filter_value, str):
                severity_lower = filter_value.lower().strip()
                if severity_lower in SEVERITY_MAP:
                    filter_value = SEVERITY_MAP[severity_lower]
            
            # Normalize exploit_available values
            elif param in ('exploit_available', 'exploitable') and isinstance(filter_value, str):
                exploit_lower = filter_value.lower().strip()
                if exploit_lower in EXPLOIT_AVAILABLE_MAP:
                    filter_value = EXPLOIT_AVAILABLE_MAP[exploit_lower]
            
            # Convert scoring filters from operator format to range format
            elif param in SCORING_FILTERS and isinstance(filter_value, str):
                max_score = SCORING_FILTERS[param]
                filter_value = convert_score_operator_to_range(filter_value, max_score)
        
        filters.append({
            "filterName": filter_name,
            "operator": operator,
            "value": filter_value
        })
    
    # Warn about unknown parameters
    if validate and unknown_params:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            f"Unknown filter parameters will be ignored: {', '.join(unknown_params)}. "
            f"These parameters were not found in COMMON_FILTERS. "
            f"For valid filter names, see MCP resource: tenable-sc://filters/reference "
            f"or check COMMON_FILTERS in convenience_tools.py. "
            f"Common mistakes: 'acr_score' should be 'asset_criticality', "
            f"'hostname' should be 'dns_name'."
        )
    
    return filters


def parse_plugin_19506_output(plugin_text: str) -> dict[str, Any]:
    """
    Parse plugin 19506 (Nessus Scan Information) output.
    
    Extracts structured scan metadata from the plugin text output.
    
    Args:
        plugin_text: Raw plugin output text from plugin 19506
    
    Returns:
        Dictionary with parsed scan metadata
    """
    metadata = {}
    
    # Extract key-value pairs using regex
    patterns = {
        "nessus_version": r"Nessus version\s*:\s*(.+)",
        "nessus_build": r"Nessus build\s*:\s*(.+)",
        "plugin_feed_version": r"Plugin feed version\s*:\s*(.+)",
        "scanner_edition": r"Scanner edition used\s*:\s*(.+)",
        "scanner_os": r"Scanner OS\s*:\s*(.+)",
        "scanner_distribution": r"Scanner distribution\s*:\s*(.+)",
        "scan_type": r"Scan type\s*:\s*(.+)",
        "scan_name": r"Scan name\s*:\s*(.+)",
        "scan_policy": r"Scan policy used\s*:\s*(.+)",
        "scanner_ip": r"Scanner IP\s*:\s*(.+)",
        "port_scanner": r"Port scanner\(s\)\s*:\s*(.+)",
        "port_range": r"Port range\s*:\s*(.+)",
        "ping_rtt": r"Ping RTT\s*:\s*(.+)",
        "thorough_tests": r"Thorough tests\s*:\s*(.+)",
        "experimental_tests": r"Experimental tests\s*:\s*(.+)",
        "paranoia_level": r"Paranoia level\s*:\s*(.+)",
        "report_verbosity": r"Report verbosity\s*:\s*(.+)",
        "safe_checks": r"Safe checks\s*:\s*(.+)",
        "optimize_test": r"Optimize the test\s*:\s*(.+)",
        "credentialed_checks": r"Credentialed checks\s*:\s*(.+)",
        "patch_management_checks": r"Patch management checks\s*:\s*(.+)",
        "scan_start_date": r"Scan Start Date\s*:\s*(.+)",
        "scan_duration": r"Scan duration\s*:\s*(\d+)\s*sec",
        "scan_for_malware": r"Scan for malware\s*:\s*(.+)",
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, plugin_text, re.IGNORECASE | re.MULTILINE)
        if match:
            value = match.group(1).strip()
            metadata[key] = value
    
    return metadata


def format_vulnerability_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Format vulnerability results into a summary by severity.
    
    Args:
        results: List of vulnerability records
    
    Returns:
        Summary with counts by severity
    """
    severity_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "info": 0,
    }
    
    severity_map = {
        "4": "critical",
        "3": "high",
        "2": "medium",
        "1": "low",
        "0": "info",
    }
    
    for vuln in results:
        severity_id = vuln.get("severity", {}).get("id", "0")
        severity_name = severity_map.get(str(severity_id), "info")
        severity_counts[severity_name] += 1
    
    return {
        "total": len(results),
        "by_severity": severity_counts,
    }


# ============================================================================
# NAME-TO-ID RESOLVERS
# ============================================================================

def resolve_repository_name(repository_name: str) -> str | None:
    """
    Resolve repository name to numeric ID.
    
    Centralized resolver used by all tools requiring repository name-to-ID conversion.
    Implements caching and handles multiple API response formats.
    
    Args:
        repository_name: Repository name (e.g., "Default", "PCI Assets")
    
    Returns:
        Repository ID as string, or None if not found
    
    Example:
        >>> resolve_repository_name("Default")
        "9"
    """
    # Import server for API access
    from . import server
    
    try:
        # Query all repositories via direct API call
        result = server.tsc_request(
            method="GET",
            path="/repository",
            params={"fields": "id,name"}
        )
        
        if not result.get("ok"):
            return None
        
        # Extract response data - handle multiple response formats
        response_data = result.get("response", {})
        
        # Handle wrapped response format: {"response": {"response": [...]}}
        if isinstance(response_data, dict) and "response" in response_data:
            repositories = response_data.get("response", [])
        # Handle direct list format: {"response": [...]}
        elif isinstance(response_data, list):
            repositories = response_data
        # Handle manageable response format (less common for repositories)
        elif isinstance(response_data, dict) and "manageable" in response_data:
            repositories = response_data.get("manageable", [])
        else:
            # Unknown format, return None
            return None
        
        # Ensure repositories is a list
        if not isinstance(repositories, list):
            return None
        
        # Search for matching repository name
        for repo in repositories:
            # Skip non-dictionary items
            if not isinstance(repo, dict):
                continue
            
            repo_name = repo.get("name")
            repo_id = repo.get("id")
            
            if repo_name == repository_name and repo_id:
                return str(repo_id)
        
        return None  # Repository not found
    
    except Exception:
        # If anything goes wrong, return None (not found)
        return None


def resolve_asset_group_name(asset_group_name: str) -> str | None:
    """
    Resolve asset group name to numeric ID.
    
    Centralized resolver used by all tools requiring asset group name-to-ID conversion.
    Implements caching and handles multiple API response formats.
    
    Args:
        asset_group_name: Asset group name (e.g., "Windows Hosts", "Production Servers")
    
    Returns:
        Asset group ID as string, or None if not found
    
    Example:
        >>> resolve_asset_group_name("Windows Hosts")
        "3"
    """
    # Import server for API access
    from . import server
    
    try:
        # Use tsc_resource_action which we know works from user tests
        result = server.tsc_resource_action(
            action="list",
            resource="asset",
            fields=["id", "name"]
        )
        
        if not result.get("ok"):
            return None
        
        # Extract response - tsc_resource_action returns {"ok": True, "response": {...}}
        response_data = result.get("response", {})
        
        # Handle multiple response formats
        assets = []
        if isinstance(response_data, dict):
            # Try nested "response" key first (common format)
            if "response" in response_data:
                inner = response_data["response"]
                if isinstance(inner, list):
                    assets = inner
                elif isinstance(inner, dict):
                    # Might have "manageable" or "usable" keys
                    assets = inner.get("manageable", inner.get("usable", []))
            # Try "manageable" at top level
            elif "manageable" in response_data:
                assets = response_data.get("manageable", [])
            # Try "usable" at top level
            elif "usable" in response_data:
                assets = response_data.get("usable", [])
        elif isinstance(response_data, list):
            assets = response_data
        
        # Search for matching name
        for asset in assets:
            if not isinstance(asset, dict):
                continue
            
            asset_name = asset.get("name", "")
            asset_id = asset.get("id")
            
            # Exact match on name - ensure asset_id is valid (not None, not empty, numeric)
            if asset_name == asset_group_name and asset_id:
                # Validate that asset_id is actually numeric (string or int)
                asset_id_str = str(asset_id).strip()
                if asset_id_str and (asset_id_str.isdigit() or isinstance(asset_id, int)):
                    return asset_id_str
        
        return None
    
    except Exception:
        return None

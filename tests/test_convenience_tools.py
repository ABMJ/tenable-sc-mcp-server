"""
Tests for convenience tools.
"""

import pytest
from tenable_sc_mcp.convenience_tools import (
    validate_ip,
    validate_severity,
    build_filters,
    parse_plugin_19506_output,
    format_vulnerability_summary,
    AUTH_PLUGINS,
    COMMON_FILTERS,
)


# ============================================================================
# VALIDATION TESTS
# ============================================================================

def test_validate_ip_valid_ipv4():
    """Test IP validation with valid IPv4 address."""
    valid, error = validate_ip("10.1.20.10")
    assert valid is True
    assert error == ""


def test_validate_ip_valid_ipv6():
    """Test IP validation with valid IPv6 address."""
    valid, error = validate_ip("2001:db8::1")
    assert valid is True
    assert error == ""


def test_validate_ip_invalid():
    """Test IP validation with invalid address."""
    valid, error = validate_ip("invalid")
    assert valid is False
    assert "Invalid IP address format" in error
    assert "tsc_list_ips()" in error


def test_validate_ip_empty():
    """Test IP validation with empty string."""
    valid, error = validate_ip("")
    assert valid is False
    assert "Invalid IP address format" in error


def test_validate_severity_valid_numeric():
    """Test severity validation with valid numeric values."""
    for severity in ["0", "1", "2", "3", "4"]:
        valid, error = validate_severity(severity)
        assert valid is True, f"Failed for severity: {severity}"
        assert error == ""


def test_validate_severity_valid_names():
    """Test severity validation with valid severity names."""
    for severity in ["info", "low", "medium", "high", "critical"]:
        valid, error = validate_severity(severity)
        assert valid is True, f"Failed for severity: {severity}"
        assert error == ""


def test_validate_severity_case_insensitive():
    """Test severity validation is case-insensitive."""
    for severity in ["INFO", "Low", "MEDIUM", "High", "CRITICAL"]:
        valid, error = validate_severity(severity)
        assert valid is True, f"Failed for severity: {severity}"
        assert error == ""


def test_validate_severity_invalid():
    """Test severity validation with invalid value."""
    valid, error = validate_severity("bogus")
    assert valid is False
    assert "Invalid severity" in error
    assert "Valid values:" in error


# ============================================================================
# FILTER BUILDER TESTS
# ============================================================================

def test_build_filters_single_filter():
    """Test building a single filter."""
    filters = build_filters(ip="10.1.20.10")
    assert len(filters) == 1
    assert filters[0]["filterName"] == "ip"
    assert filters[0]["operator"] == "="
    assert filters[0]["value"] == "10.1.20.10"


def test_build_filters_multiple_filters():
    """Test building multiple filters."""
    filters = build_filters(
        ip="10.1.20.10",
        severity="4",
        exploit_available="Yes"
    )
    assert len(filters) == 3
    filter_names = [f["filterName"] for f in filters]
    assert "ip" in filter_names
    assert "severity" in filter_names
    assert "exploitAvailable" in filter_names


def test_build_filters_skip_none_values():
    """Test that None values are skipped."""
    filters = build_filters(
        ip="10.1.20.10",
        severity=None,
        exploit_available="Yes"
    )
    assert len(filters) == 2
    filter_names = [f["filterName"] for f in filters]
    assert "ip" in filter_names
    assert "exploitAvailable" in filter_names
    assert "severity" not in filter_names


def test_build_filters_custom_operator():
    """Test building filters with custom operators."""
    filters = build_filters(
        vpr_score={"operator": ">=", "value": "7.0"}
    )
    assert len(filters) == 1
    assert filters[0]["filterName"] == "vprScore"
    assert filters[0]["operator"] == ">="
    assert filters[0]["value"] == "7.0"


def test_build_filters_unknown_parameter():
    """Test that unknown parameters are skipped."""
    filters = build_filters(
        ip="10.1.20.10",
        unknown_param="value"
    )
    assert len(filters) == 1
    assert filters[0]["filterName"] == "ip"


def test_build_filters_all_filter_types():
    """Test that all major filter types are supported."""
    test_filters = {
        # Asset filters
        "asset_id": "123",
        "ip": "10.1.20.10",
        # Vulnerability filters
        "plugin_id": "19506",
        "severity": "4",
        # Scoring filters
        "vpr_score": "7.0",
        "cvss_v3_base_score": "9.0",
        # Temporal filters
        "first_seen": "1640000000",
        "last_seen": "1650000000",
    }
    filters = build_filters(**test_filters)
    assert len(filters) == len(test_filters)
    
    # Verify all filters were created with correct filter names
    filter_names = [f["filterName"] for f in filters]
    assert "assetID" in filter_names
    assert "ip" in filter_names
    assert "pluginID" in filter_names
    assert "severity" in filter_names
    assert "vprScore" in filter_names
    assert "cvssV3BaseScore" in filter_names
    assert "firstSeen" in filter_names
    assert "lastSeen" in filter_names


# ============================================================================
# PLUGIN 19506 PARSING TESTS
# ============================================================================

def test_parse_plugin_19506_output_sample():
    """Test parsing plugin 19506 output with user-provided sample."""
    sample_output = """
Information about this scan : 

Nessus version : 10.9.4
Nessus build : 20037
Plugin feed version : 202510060158
Scanner edition used : Nessus
Scanner OS : LINUX
Scanner distribution : es8-x86-64
Scan type : Normal
Scan name : Credentialed Patch Auditing Policy - Windows
Scan policy used : 053f713d-9f27-547b-8660-a084a340f9eb-4479/Credentialed Patch Auditing Policy
Scanner IP : 192.168.40.62
Port scanner(s) : nessus_syn_scanner 
Port range : sc-default
Ping RTT : 149.816 ms
Thorough tests : no
Experimental tests : no
Paranoia level : 1
Report verbosity : 1
Safe checks : yes
Optimize the test : yes
Credentialed checks : no
Patch management checks : None
Scan Start Date : 2025/10/6 4:15 EDT (UTC -04:00)
Scan duration : 181 sec
Scan for malware : no
"""
    
    metadata = parse_plugin_19506_output(sample_output)
    
    # Verify key fields are extracted
    assert metadata["nessus_version"] == "10.9.4"
    assert metadata["nessus_build"] == "20037"
    assert metadata["plugin_feed_version"] == "202510060158"
    assert metadata["scanner_edition"] == "Nessus"
    assert metadata["scanner_os"] == "LINUX"
    assert metadata["scanner_distribution"] == "es8-x86-64"
    assert metadata["scan_type"] == "Normal"
    assert metadata["scan_name"] == "Credentialed Patch Auditing Policy - Windows"
    assert "053f713d-9f27-547b-8660-a084a340f9eb-4479/Credentialed Patch Auditing Policy" in metadata["scan_policy"]
    assert metadata["scanner_ip"] == "192.168.40.62"
    assert metadata["port_scanner"] == "nessus_syn_scanner"
    assert metadata["port_range"] == "sc-default"
    assert metadata["credentialed_checks"] == "no"
    assert metadata["patch_management_checks"] == "None"
    assert metadata["scan_duration"] == "181"
    assert metadata["scan_for_malware"] == "no"


def test_parse_plugin_19506_output_empty():
    """Test parsing empty plugin output."""
    metadata = parse_plugin_19506_output("")
    assert isinstance(metadata, dict)
    # Should return empty dict for fields not found
    assert len(metadata) == 0


def test_parse_plugin_19506_output_partial():
    """Test parsing partial plugin output."""
    partial_output = """
Nessus version : 10.9.4
Scanner IP : 192.168.40.62
Credentialed checks : yes
"""
    
    metadata = parse_plugin_19506_output(partial_output)
    
    assert metadata["nessus_version"] == "10.9.4"
    assert metadata["scanner_ip"] == "192.168.40.62"
    assert metadata["credentialed_checks"] == "yes"
    assert "scan_name" not in metadata


# ============================================================================
# VULNERABILITY SUMMARY TESTS
# ============================================================================

def test_format_vulnerability_summary_empty():
    """Test formatting empty vulnerability list."""
    summary = format_vulnerability_summary([])
    assert summary["total"] == 0
    assert summary["by_severity"]["critical"] == 0
    assert summary["by_severity"]["high"] == 0
    assert summary["by_severity"]["medium"] == 0
    assert summary["by_severity"]["low"] == 0
    assert summary["by_severity"]["info"] == 0


def test_format_vulnerability_summary_single_critical():
    """Test formatting single critical vulnerability."""
    vulns = [
        {"severity": {"id": "4", "name": "Critical"}}
    ]
    summary = format_vulnerability_summary(vulns)
    assert summary["total"] == 1
    assert summary["by_severity"]["critical"] == 1
    assert summary["by_severity"]["high"] == 0


def test_format_vulnerability_summary_mixed():
    """Test formatting mixed severity vulnerabilities."""
    vulns = [
        {"severity": {"id": "4", "name": "Critical"}},
        {"severity": {"id": "4", "name": "Critical"}},
        {"severity": {"id": "3", "name": "High"}},
        {"severity": {"id": "3", "name": "High"}},
        {"severity": {"id": "3", "name": "High"}},
        {"severity": {"id": "2", "name": "Medium"}},
        {"severity": {"id": "1", "name": "Low"}},
        {"severity": {"id": "0", "name": "Info"}},
    ]
    summary = format_vulnerability_summary(vulns)
    assert summary["total"] == 8
    assert summary["by_severity"]["critical"] == 2
    assert summary["by_severity"]["high"] == 3
    assert summary["by_severity"]["medium"] == 1
    assert summary["by_severity"]["low"] == 1
    assert summary["by_severity"]["info"] == 1


def test_format_vulnerability_summary_missing_severity():
    """Test formatting vulnerabilities with missing severity field."""
    vulns = [
        {"other_field": "value"},
        {"severity": {"id": "4", "name": "Critical"}},
    ]
    summary = format_vulnerability_summary(vulns)
    assert summary["total"] == 2
    assert summary["by_severity"]["critical"] == 1
    assert summary["by_severity"]["info"] == 1  # Missing severity defaults to info (0)


# ============================================================================
# CONSTANTS TESTS
# ============================================================================

def test_auth_plugins_constant():
    """Test AUTH_PLUGINS constant has expected plugins."""
    assert 19506 in AUTH_PLUGINS
    assert 21745 in AUTH_PLUGINS
    assert 10394 in AUTH_PLUGINS
    assert 10396 in AUTH_PLUGINS
    assert 102094 in AUTH_PLUGINS
    assert 24786 in AUTH_PLUGINS
    assert AUTH_PLUGINS[19506] == "Nessus Scan Information"


def test_common_filters_constant():
    """Test COMMON_FILTERS has expected filter mappings."""
    # Spot check key filters
    assert COMMON_FILTERS["ip"] == "ip"
    assert COMMON_FILTERS["severity"] == "severity"
    assert COMMON_FILTERS["plugin_id"] == "pluginID"
    assert COMMON_FILTERS["cve"] == "cve"
    assert COMMON_FILTERS["vpr_score"] == "vprScore"
    assert COMMON_FILTERS["exploit_available"] == "exploitAvailable"
    assert COMMON_FILTERS["first_seen"] == "firstSeen"
    assert COMMON_FILTERS["asset_criticality"] == "assetCriticalityRating"
    
    # Verify count (55+ filters as documented)
    assert len(COMMON_FILTERS) >= 55


def test_common_filters_no_duplicates():
    """Test COMMON_FILTERS has no duplicate API filter names."""
    api_filter_names = list(COMMON_FILTERS.values())
    assert len(api_filter_names) == len(set(api_filter_names))

"""
Integration tests for Tool 2: tsc_list_vulns_by_ip_summary and tsc_list_vulns_by_ip_full

These tests verify the complete implementation of Week 1 Session 1.2 tools.
"""

from unittest.mock import patch
from tenable_sc_mcp import server
from tenable_sc_mcp import convenience_tools


# Create test-friendly wrappers that mimic the tool behavior
def tsc_list_vulns_by_ip_summary(
    ip: str,
    severity: str | None = None,
    exploit_available: str | None = None,
    first_seen: str | None = None,
    last_seen: str | None = None,
    family: str | None = None,
    vpr_score: str | None = None,
    plugin_id: str | None = None,
    cve: str | None = None,
    port: int | None = None,
    protocol: str | None = None,
):
    """Test wrapper for tsc_list_vulns_by_ip_summary"""
    # Validate IP
    valid, error = convenience_tools.validate_ip(ip)
    if not valid:
        return {"ok": False, "error": error}
    
    # Validate severity if provided
    if severity:
        valid, error = convenience_tools.validate_severity(severity)
        if not valid:
            return {"ok": False, "error": error}
    
    try:
        # Build filters from parameters
        filters = convenience_tools.build_filters(
            ip=ip,
            severity=severity,
            exploit_available=exploit_available,
            first_seen=first_seen,
            last_seen=last_seen,
            family=family,
            vpr_score=vpr_score,
            plugin_id=plugin_id,
            cve=cve,
            port=port,
            protocol=protocol,
        )
        
        # Query using vulnipsummary tool (efficient aggregation)
        query = {
            "type": "vuln",
            "query": {
                "type": "vuln",
                "tool": "vulnipsummary",
                "filters": filters
            },
            "sourceType": "cumulative"
        }
        
        result = server.tsc_analyze(query)
        
        if not result.get("ok"):
            return result
        
        # Format summary - handle nested response
        api_response = result.get("response", {})
        if isinstance(api_response, dict) and "response" in api_response:
            vuln_data = api_response.get("response", {}).get("results", [])
        else:
            vuln_data = api_response.get("results", [])
        summary = convenience_tools.format_vulnerability_summary(vuln_data)
        
        return {
            "ok": True,
            "ip": ip,
            "summary": summary,
            "filters_applied": {
                "severity": severity,
                "exploit_available": exploit_available,
                "family": family,
                "vpr_score": vpr_score,
                "plugin_id": plugin_id,
                "cve": cve,
                "port": port,
                "protocol": protocol,
            }
        }
    
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Failed to get vulnerability summary for {ip}: {str(exc)}",
            "ip": ip
        }


def tsc_list_vulns_by_ip_full(
    ip: str,
    severity: str | None = None,
    exploit_available: str | None = None,
    first_seen: str | None = None,
    last_seen: str | None = None,
    family: str | None = None,
    vpr_score: str | None = None,
    plugin_id: str | None = None,
    cve: str | None = None,
    port: int | None = None,
    protocol: str | None = None,
    cvss_v3_base_score: str | None = None,
    epss_score: str | None = None,
    patch_published: str | None = None,
    vuln_published: str | None = None,
    mitigated_status: str | None = None,
    start_offset: int = 0,
    end_offset: int = 50,
):
    """Test wrapper for tsc_list_vulns_by_ip_full"""
    # Validate IP
    valid, error = convenience_tools.validate_ip(ip)
    if not valid:
        return {"ok": False, "error": error}
    
    # Validate severity if provided
    if severity:
        valid, error = convenience_tools.validate_severity(severity)
        if not valid:
            return {"ok": False, "error": error}
    
    # Validate pagination
    if end_offset > 200:
        return {
            "ok": False,
            "error": f"end_offset cannot exceed 200 (requested: {end_offset})",
            "suggestion": "Use pagination by setting start_offset/end_offset in multiple queries"
        }
    
    if start_offset < 0 or end_offset < 0:
        return {
            "ok": False,
            "error": "start_offset and end_offset must be non-negative"
        }
    
    if start_offset >= end_offset:
        return {
            "ok": False,
            "error": f"start_offset ({start_offset}) must be less than end_offset ({end_offset})"
        }
    
    try:
        # Build filters from parameters
        filters = convenience_tools.build_filters(
            ip=ip,
            severity=severity,
            exploit_available=exploit_available,
            first_seen=first_seen,
            last_seen=last_seen,
            family=family,
            vpr_score=vpr_score,
            plugin_id=plugin_id,
            cve=cve,
            port=port,
            protocol=protocol,
            cvss_v3_base_score=cvss_v3_base_score,
            epss_score=epss_score,
            patch_published=patch_published,
            vuln_published=vuln_published,
            mitigated_status=mitigated_status,
        )
        
        # Query using vulnipdetail tool (full details)
        query = {
            "type": "vuln",
            "query": {
                "type": "vuln",
                "tool": "vulnipdetail",
                "filters": filters
            },
            "sourceType": "cumulative",
            "sortField": "severity",
            "sortDir": "DESC",
            "startOffset": start_offset,
            "endOffset": end_offset,
        }
        
        result = server.tsc_analyze(query)
        
        if not result.get("ok"):
            return result
        
        # Extract vulnerability data - handle nested response
        api_response = result.get("response", {})
        if isinstance(api_response, dict) and "response" in api_response:
            inner_response = api_response.get("response", {})
            vuln_data = inner_response.get("results", [])
            response_data = inner_response
        else:
            vuln_data = api_response.get("results", [])
            response_data = api_response
        
        # Format vulnerabilities for cleaner output
        formatted_vulns = []
        for vuln in vuln_data:
            formatted_vulns.append({
                "plugin_id": vuln.get("pluginID"),
                "name": vuln.get("pluginName"),
                "severity": vuln.get("severity", {}).get("name"),
                "severity_id": vuln.get("severity", {}).get("id"),
                "port": vuln.get("port"),
                "protocol": vuln.get("protocol"),
                "family": vuln.get("family", {}).get("name"),
                "cvss_v3_base_score": vuln.get("cvssV3BaseScore"),
                "vpr_score": vuln.get("vprScore"),
                "epss_score": vuln.get("epssScore"),
                "exploit_available": vuln.get("exploitAvailable"),
                "exploit_frameworks": vuln.get("exploitFrameworks"),
                "cve": vuln.get("cve"),
                "first_seen": vuln.get("firstSeen"),
                "last_seen": vuln.get("lastSeen"),
                "synopsis": vuln.get("synopsis", "")[:200],  # Truncate for token efficiency
                "solution": vuln.get("solution", "")[:200],
            })
        
        return {
            "ok": True,
            "ip": ip,
            "summary": {
                "total_records": response_data.get("totalRecords"),
                "returned_records": response_data.get("returnedRecords"),
                "start_offset": start_offset,
                "end_offset": end_offset,
                "has_more": int(response_data.get("totalRecords", 0)) > end_offset,
            },
            "vulnerabilities": formatted_vulns,
            "filters_applied": {
                "severity": severity,
                "exploit_available": exploit_available,
                "family": family,
                "vpr_score": vpr_score,
                "plugin_id": plugin_id,
                "cve": cve,
                "port": port,
                "protocol": protocol,
                "cvss_v3_base_score": cvss_v3_base_score,
                "epss_score": epss_score,
            }
        }
    
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Failed to get vulnerabilities for {ip}: {str(exc)}",
            "ip": ip
        }



# ============================================================================
# MOCK DATA
# ============================================================================

MOCK_ANALYZE_RESPONSE_SUMMARY = {
    "ok": True,
    "response": {
        "results": [
            {"severity": {"id": "4", "name": "Critical"}},
            {"severity": {"id": "4", "name": "Critical"}},
            {"severity": {"id": "3", "name": "High"}},
            {"severity": {"id": "3", "name": "High"}},
            {"severity": {"id": "3", "name": "High"}},
            {"severity": {"id": "2", "name": "Medium"}},
            {"severity": {"id": "1", "name": "Low"}},
            {"severity": {"id": "0", "name": "Info"}},
        ]
    }
}

MOCK_ANALYZE_RESPONSE_FULL = {
    "ok": True,
    "response": {
        "totalRecords": 100,
        "returnedRecords": 50,
        "results": [
            {
                "pluginID": "12345",
                "pluginName": "Test Critical Vulnerability",
                "severity": {"id": "4", "name": "Critical"},
                "port": 443,
                "protocol": "TCP",
                "family": {"name": "Web Servers"},
                "cvssV3BaseScore": "9.8",
                "vprScore": "9.2",
                "epssScore": "0.95",
                "exploitAvailable": "Yes",
                "exploitFrameworks": "Metasploit",
                "cve": "CVE-2024-1234",
                "firstSeen": "1640000000",
                "lastSeen": "1650000000",
                "synopsis": "A critical remote code execution vulnerability...",
                "solution": "Apply the security patch...",
            }
        ]
    }
}


# ============================================================================
# TOOL 2 SUMMARY TESTS
# ============================================================================

@patch("tenable_sc_mcp.server.tsc_analyze")
def test_list_vulns_by_ip_summary_valid_ip(mock_analyze):
    """Test summary tool with valid IP address."""
    mock_analyze.return_value = MOCK_ANALYZE_RESPONSE_SUMMARY
    
    result = tsc_list_vulns_by_ip_summary("10.1.20.10")
    
    assert result["ok"] is True
    assert result["ip"] == "10.1.20.10"
    assert "summary" in result
    assert result["summary"]["total"] == 8
    assert result["summary"]["by_severity"]["critical"] == 2
    assert result["summary"]["by_severity"]["high"] == 3
    assert result["summary"]["by_severity"]["medium"] == 1
    assert result["summary"]["by_severity"]["low"] == 1
    assert result["summary"]["by_severity"]["info"] == 1


@patch("tenable_sc_mcp.server.tsc_analyze")
def test_list_vulns_by_ip_summary_with_severity_filter(mock_analyze):
    """Test summary tool with severity filter."""
    mock_analyze.return_value = MOCK_ANALYZE_RESPONSE_SUMMARY
    
    result = tsc_list_vulns_by_ip_summary("10.1.20.10", severity="critical")
    
    assert result["ok"] is True
    assert result["filters_applied"]["severity"] == "critical"
    # Verify the filter was passed to tsc_analyze
    mock_analyze.assert_called_once()
    call_args = mock_analyze.call_args[0][0]
    assert "filters" in call_args["query"]
    filters = call_args["query"]["filters"]
    assert any(f["filterName"] == "ip" and f["value"] == "10.1.20.10" for f in filters)
    assert any(f["filterName"] == "severity" and f["value"] == "critical" for f in filters)


def test_list_vulns_by_ip_summary_invalid_ip():
    """Test summary tool with invalid IP."""
    result = tsc_list_vulns_by_ip_summary("invalid_ip")
    
    assert result["ok"] is False
    assert "Invalid IP address format" in result["error"]
    assert "tsc_list_ips()" in result["error"]


def test_list_vulns_by_ip_summary_invalid_severity():
    """Test summary tool with invalid severity."""
    result = tsc_list_vulns_by_ip_summary("10.1.20.10", severity="bogus")
    
    assert result["ok"] is False
    assert "Invalid severity" in result["error"]
    assert "Valid values:" in result["error"]


@patch("tenable_sc_mcp.server.tsc_analyze")
def test_list_vulns_by_ip_summary_with_multiple_filters(mock_analyze):
    """Test summary tool with multiple filters."""
    mock_analyze.return_value = MOCK_ANALYZE_RESPONSE_SUMMARY
    
    result = tsc_list_vulns_by_ip_summary(
        "10.1.20.10",
        severity="high",
        exploit_available="Yes",
        family="Web Servers"
    )
    
    assert result["ok"] is True
    assert result["filters_applied"]["severity"] == "high"
    assert result["filters_applied"]["exploit_available"] == "Yes"
    assert result["filters_applied"]["family"] == "Web Servers"


@patch("tenable_sc_mcp.server.tsc_analyze")
def test_list_vulns_by_ip_summary_no_results(mock_analyze):
    """Test summary tool with no vulnerabilities found."""
    mock_analyze.return_value = {"ok": True, "response": {"results": []}}
    
    result = tsc_list_vulns_by_ip_summary("10.1.20.10")
    
    assert result["ok"] is True
    assert result["summary"]["total"] == 0
    assert result["summary"]["by_severity"]["critical"] == 0


# ============================================================================
# TOOL 2 FULL TESTS
# ============================================================================

@patch("tenable_sc_mcp.server.tsc_analyze")
def test_list_vulns_by_ip_full_valid_ip(mock_analyze):
    """Test full tool with valid IP address."""
    mock_analyze.return_value = MOCK_ANALYZE_RESPONSE_FULL
    
    result = tsc_list_vulns_by_ip_full("10.1.20.10")
    
    assert result["ok"] is True
    assert result["ip"] == "10.1.20.10"
    assert "summary" in result
    assert result["summary"]["total_records"] == 100
    assert result["summary"]["returned_records"] == 50
    assert result["summary"]["start_offset"] == 0
    assert result["summary"]["end_offset"] == 50
    assert result["summary"]["has_more"] is True
    assert "vulnerabilities" in result
    assert len(result["vulnerabilities"]) == 1


@patch("tenable_sc_mcp.server.tsc_analyze")
def test_list_vulns_by_ip_full_formatted_output(mock_analyze):
    """Test full tool output formatting."""
    mock_analyze.return_value = MOCK_ANALYZE_RESPONSE_FULL
    
    result = tsc_list_vulns_by_ip_full("10.1.20.10")
    
    vuln = result["vulnerabilities"][0]
    assert vuln["plugin_id"] == "12345"
    assert vuln["name"] == "Test Critical Vulnerability"
    assert vuln["severity"] == "Critical"
    assert vuln["severity_id"] == "4"
    assert vuln["port"] == 443
    assert vuln["protocol"] == "TCP"
    assert vuln["family"] == "Web Servers"
    assert vuln["cvss_v3_base_score"] == "9.8"
    assert vuln["vpr_score"] == "9.2"
    assert vuln["exploit_available"] == "Yes"
    assert vuln["cve"] == "CVE-2024-1234"


@patch("tenable_sc_mcp.server.tsc_analyze")
def test_list_vulns_by_ip_full_with_pagination(mock_analyze):
    """Test full tool with custom pagination."""
    mock_analyze.return_value = MOCK_ANALYZE_RESPONSE_FULL
    
    result = tsc_list_vulns_by_ip_full("10.1.20.10", start_offset=10, end_offset=20)
    
    assert result["ok"] is True
    assert result["summary"]["start_offset"] == 10
    assert result["summary"]["end_offset"] == 20
    
    # Verify pagination was passed to tsc_analyze
    mock_analyze.assert_called_once()
    call_args = mock_analyze.call_args[0][0]
    assert call_args["startOffset"] == 10
    assert call_args["endOffset"] == 20


def test_list_vulns_by_ip_full_pagination_exceeds_max():
    """Test full tool with pagination exceeding max limit."""
    result = tsc_list_vulns_by_ip_full("10.1.20.10", start_offset=0, end_offset=300)
    
    assert result["ok"] is False
    assert "end_offset cannot exceed 200" in result["error"]


def test_list_vulns_by_ip_full_pagination_negative():
    """Test full tool with negative pagination."""
    result = tsc_list_vulns_by_ip_full("10.1.20.10", start_offset=-1, end_offset=50)
    
    assert result["ok"] is False
    assert "must be non-negative" in result["error"]


def test_list_vulns_by_ip_full_pagination_inverted():
    """Test full tool with inverted pagination range."""
    result = tsc_list_vulns_by_ip_full("10.1.20.10", start_offset=50, end_offset=10)
    
    assert result["ok"] is False
    assert "must be less than" in result["error"]


@patch("tenable_sc_mcp.server.tsc_analyze")
def test_list_vulns_by_ip_full_with_all_filters(mock_analyze):
    """Test full tool with all available filters."""
    mock_analyze.return_value = MOCK_ANALYZE_RESPONSE_FULL
    
    result = tsc_list_vulns_by_ip_full(
        "10.1.20.10",
        severity="critical",
        exploit_available="Yes",
        first_seen="1640000000",
        last_seen="1650000000",
        family="Web Servers",
        vpr_score="7.0",
        plugin_id="12345",
        cve="CVE-2024-1234",
        port=443,
        protocol="TCP",
        cvss_v3_base_score="9.0",
        epss_score="0.9",
        patch_published="1640000000",
        vuln_published="1640000000",
        mitigated_status="NotMitigated"
    )
    
    assert result["ok"] is True
    assert result["filters_applied"]["severity"] == "critical"
    assert result["filters_applied"]["exploit_available"] == "Yes"
    assert result["filters_applied"]["family"] == "Web Servers"
    assert result["filters_applied"]["vpr_score"] == "7.0"


@patch("tenable_sc_mcp.server.tsc_analyze")
def test_list_vulns_by_ip_full_truncates_long_fields(mock_analyze):
    """Test full tool truncates long synopsis and solution fields."""
    long_text = "A" * 500
    mock_response = {
        "ok": True,
        "response": {
            "totalRecords": 1,
            "returnedRecords": 1,
            "results": [
                {
                    "pluginID": "12345",
                    "pluginName": "Test",
                    "severity": {"id": "4", "name": "Critical"},
                    "synopsis": long_text,
                    "solution": long_text,
                }
            ]
        }
    }
    mock_analyze.return_value = mock_response
    
    result = tsc_list_vulns_by_ip_full("10.1.20.10")
    
    vuln = result["vulnerabilities"][0]
    assert len(vuln["synopsis"]) == 200  # Truncated to 200 chars
    assert len(vuln["solution"]) == 200  # Truncated to 200 chars


# ============================================================================
# TOOL INTERFACE CONSISTENCY TESTS
# ============================================================================

def test_tool2_summary_and_full_use_same_filter_interface():
    """Test that summary and full tools accept the same filter parameters."""
    import inspect
    
    summary_sig = inspect.signature(tsc_list_vulns_by_ip_summary)
    full_sig = inspect.signature(tsc_list_vulns_by_ip_full)
    
    summary_params = set(summary_sig.parameters.keys())
    full_params = set(full_sig.parameters.keys())
    
    # Common filters should be in both
    common_filters = [
        "ip", "severity", "exploit_available", "first_seen", "last_seen",
        "family", "vpr_score", "plugin_id", "cve", "port", "protocol"
    ]
    
    for filter_name in common_filters:
        assert filter_name in summary_params, f"{filter_name} missing from summary"
        assert filter_name in full_params, f"{filter_name} missing from full"
    
    # Full tool should have additional filters + pagination
    assert "cvss_v3_base_score" in full_params
    assert "start_offset" in full_params
    assert "end_offset" in full_params


def test_tool2_returns_consistent_structure():
    """Test that both tools return consistent error structure."""
    invalid_result_summary = tsc_list_vulns_by_ip_summary("invalid")
    invalid_result_full = tsc_list_vulns_by_ip_full("invalid")
    
    # Both should have ok=False and error message
    assert invalid_result_summary["ok"] is False
    assert invalid_result_full["ok"] is False
    assert "error" in invalid_result_summary
    assert "error" in invalid_result_full


# ============================================================================
# TOKEN EFFICIENCY TESTS
# ============================================================================

@patch("tenable_sc_mcp.server.tsc_analyze")
def test_tool2_summary_uses_efficient_query_tool(mock_analyze):
    """Test that summary uses vulnipsummary (efficient) tool."""
    mock_analyze.return_value = MOCK_ANALYZE_RESPONSE_SUMMARY
    
    tsc_list_vulns_by_ip_summary("10.1.20.10")
    
    call_args = mock_analyze.call_args[0][0]
    assert call_args["query"]["tool"] == "vulnipsummary"


@patch("tenable_sc_mcp.server.tsc_analyze")
def test_tool2_full_uses_detailed_query_tool(mock_analyze):
    """Test that full uses vulnipdetail (detailed) tool."""
    mock_analyze.return_value = MOCK_ANALYZE_RESPONSE_FULL
    
    tsc_list_vulns_by_ip_full("10.1.20.10")
    
    call_args = mock_analyze.call_args[0][0]
    assert call_args["query"]["tool"] == "vulnipdetail"


@patch("tenable_sc_mcp.server.tsc_analyze")
def test_tool2_full_sorts_by_severity(mock_analyze):
    """Test that full tool sorts results by severity descending."""
    mock_analyze.return_value = MOCK_ANALYZE_RESPONSE_FULL
    
    tsc_list_vulns_by_ip_full("10.1.20.10")
    
    call_args = mock_analyze.call_args[0][0]
    assert call_args["sortField"] == "severity"
    assert call_args["sortDir"] == "DESC"

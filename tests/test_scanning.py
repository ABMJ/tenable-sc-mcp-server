"""
Tests for scanning tools (Tool 7: Scan Status Monitoring).
"""

import time
import pytest
from unittest.mock import Mock, patch

from tenable_sc_mcp.tools.scanning import (
    parse_time_range,
    calculate_progress,
    check_import_status,
    format_timing,
    format_duration,
)


class TestHelperFunctions:
    """Test helper functions for scan status monitoring."""
    
    def test_parse_time_range_24h(self):
        """Test parsing 24h time range."""
        start, end = parse_time_range("24h")
        assert end - start == 86400
        assert end <= int(time.time()) + 1  # Allow 1 second tolerance
    
    def test_parse_time_range_7d(self):
        """Test parsing 7d time range."""
        start, end = parse_time_range("7d")
        assert end - start == 604800
    
    def test_parse_time_range_30d(self):
        """Test parsing 30d time range."""
        start, end = parse_time_range("30d")
        assert end - start == 2592000
    
    def test_parse_time_range_default(self):
        """Test parsing invalid time range defaults to 24h."""
        start, end = parse_time_range("invalid")
        assert end - start == 86400
    
    def test_calculate_progress_basic(self):
        """Test basic progress calculation."""
        result = {
            "completedIPs": "50",
            "totalIPs": "100",
            "completedChecks": "5000",
            "totalChecks": "10000",
            "startTime": str(int(time.time()) - 3600),  # 1 hour ago
        }
        
        progress = calculate_progress(result)
        
        assert progress["ips_completed"] == 50
        assert progress["ips_total"] == 100
        assert progress["percent"] == 50.0
        assert progress["checks_completed"] == 5000
        assert progress["checks_total"] == 10000
        assert progress["ips_per_hour"] is not None
        assert progress["ips_per_hour"] > 0
    
    def test_calculate_progress_zero_total(self):
        """Test progress calculation with zero total IPs."""
        result = {
            "completedIPs": "0",
            "totalIPs": "0",
            "completedChecks": "0",
            "totalChecks": "0",
            "startTime": str(int(time.time())),
        }
        
        progress = calculate_progress(result)
        
        assert progress["percent"] == 0.0
        assert progress["ips_per_hour"] is None
    
    def test_calculate_progress_not_started(self):
        """Test progress calculation for scan not yet started."""
        result = {
            "completedIPs": "0",
            "totalIPs": "100",
            "completedChecks": "0",
            "totalChecks": "10000",
            "startTime": "0",
        }
        
        progress = calculate_progress(result)
        
        assert progress["ips_completed"] == 0
        assert progress["ips_total"] == 100
        assert progress["percent"] == 0.0
        assert progress["ips_per_hour"] is None
    
    def test_calculate_progress_completed(self):
        """Test progress calculation for completed scan."""
        result = {
            "completedIPs": "200",
            "totalIPs": "200",
            "completedChecks": "10600",
            "totalChecks": "10600",
            "startTime": str(int(time.time()) - 7200),  # 2 hours ago
        }
        
        progress = calculate_progress(result)
        
        assert progress["percent"] == 100.0
        assert progress["estimated_remaining_seconds"] is None  # No time remaining
    
    def test_check_import_status_scan_complete_import_running(self):
        """Test import status alert when scan complete but import running."""
        result = {
            "status": "Completed",
            "importStatus": "Running",
            "importStart": str(int(time.time()) - 2700),  # 45 minutes ago
        }
        
        info = check_import_status(result)
        
        assert info["alert"] is True
        assert "still processing" in info["message"]
        assert info["import_elapsed_seconds"] > 2600
        assert "45m" in info["import_elapsed_formatted"] or "44m" in info["import_elapsed_formatted"]
    
    def test_check_import_status_import_error(self):
        """Test import status alert on import error."""
        result = {
            "status": "Completed",
            "importStatus": "Error",
            "importErrorDetails": "Database connection failed",
        }
        
        info = check_import_status(result)
        
        assert info["alert"] is True
        assert "failed" in info["message"].lower()
        assert "Database connection failed" in info["error_details"]
    
    def test_check_import_status_normal(self):
        """Test import status with no alerts."""
        result = {
            "status": "Completed",
            "importStatus": "Finished",
        }
        
        info = check_import_status(result)
        
        assert info["alert"] is False
    
    def test_format_timing_completed_scan(self):
        """Test timing formatting for completed scan."""
        start_time = int(time.time()) - 14400  # 4 hours ago
        finish_time = int(time.time()) - 120    # 2 minutes ago
        duration = 14280                         # 3h 58m
        
        result = {
            "startTime": str(start_time),
            "finishTime": str(finish_time),
            "scanDuration": str(duration),
        }
        
        timing = format_timing(result)
        
        assert "started" in timing
        assert "finished" in timing
        assert "duration" in timing
        assert "3h" in timing["duration"]
    
    def test_format_timing_running_scan(self):
        """Test timing formatting for running scan."""
        start_time = int(time.time()) - 7200  # 2 hours ago
        
        result = {
            "startTime": str(start_time),
            "finishTime": "-1",  # Not finished
            "scanDuration": "0",
        }
        
        timing = format_timing(result)
        
        assert "started" in timing
        assert "finished" not in timing
        assert "elapsed" in timing
        assert "h" in timing["elapsed"]
    
    def test_format_duration_hours_minutes(self):
        """Test duration formatting with hours and minutes."""
        assert format_duration(8100) == "2h 15m"
        assert format_duration(3600) == "1h 0m"
        assert format_duration(7380) == "2h 3m"
    
    def test_format_duration_minutes_only(self):
        """Test duration formatting with minutes only."""
        assert format_duration(900) == "15m"
        assert format_duration(60) == "1m"
        assert format_duration(30) == "0m"


class TestScanStatusTool:
    """Test tsc_scan_status tool with mocked API."""
    
    @patch("tenable_sc_mcp.tools.scanning._client")
    @patch("tenable_sc_mcp.tools.scanning._get_cache")
    def test_scan_status_list_running(self, mock_cache, mock_client):
        """Test listing running scans."""
        # Mock client response
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.get.return_value = {
            "response": {
                "usable": [
                    {
                        "id": "123",
                        "name": "Test Scan",
                        "status": "Running",
                        "totalIPs": "100",
                        "completedIPs": "50",
                        "completedChecks": "5000",
                        "totalChecks": "10000",
                        "startTime": str(int(time.time()) - 3600),
                        "finishTime": "-1",
                        "scanDuration": "0",
                        "importStatus": "No Results",
                        "importStart": "-1",
                        "importFinish": "-1",
                        "importDuration": "-1",
                        "errorDetails": "",
                        "importErrorDetails": "",
                        "scan": {"id": "1", "name": "Weekly Scan"},
                        "repository": {"id": "9", "name": "Default"},
                        "initiator": {"username": "admin"},
                    }
                ]
            }
        }
        
        # Mock cache
        mock_cache.return_value = None
        
        # Import and call tool
        from tenable_sc_mcp.tools.scanning import register_tools
        from mcp.server.fastmcp import FastMCP
        
        mcp = FastMCP("test")
        register_tools(mcp)
        
        # Get the registered tool
        tool_func = None
        for tool in mcp._tools.values():
            if tool.name == "tsc_scan_status":
                tool_func = tool.function
                break
        
        assert tool_func is not None, "tsc_scan_status tool not registered"
        
        # Call tool
        result = tool_func(status="running", time_range="24h")
        
        assert result["ok"] is True
        assert result["active_scans"] == 1
        assert result["total_results"] == 1
        assert len(result["scan_results"]) == 1
        assert result["scan_results"][0]["status"] == "Running"
        assert result["scan_results"][0]["progress"]["percent"] == 50.0
    
    @patch("tenable_sc_mcp.tools.scanning._client")
    @patch("tenable_sc_mcp.tools.scanning._get_cache")
    def test_scan_status_import_alert(self, mock_cache, mock_client):
        """Test scan status with import alert."""
        # Mock client response
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.get.return_value = {
            "response": {
                "usable": [
                    {
                        "id": "124",
                        "name": "Completed Scan",
                        "status": "Completed",
                        "totalIPs": "100",
                        "completedIPs": "100",
                        "completedChecks": "10000",
                        "totalChecks": "10000",
                        "startTime": str(int(time.time()) - 7200),
                        "finishTime": str(int(time.time()) - 3600),
                        "scanDuration": "3600",
                        "importStatus": "Running",
                        "importStart": str(int(time.time()) - 3600),
                        "importFinish": "-1",
                        "importDuration": "-1",
                        "errorDetails": "",
                        "importErrorDetails": "",
                        "scan": {"id": "2", "name": "Full Scan"},
                        "repository": {"id": "9", "name": "Default"},
                        "initiator": {"username": "scheduler"},
                    }
                ]
            }
        }
        
        # Mock cache
        mock_cache.return_value = None
        
        # Import and call tool
        from tenable_sc_mcp.tools.scanning import register_tools
        from mcp.server.fastmcp import FastMCP
        
        mcp = FastMCP("test")
        register_tools(mcp)
        
        # Get the registered tool
        tool_func = None
        for tool in mcp._tools.values():
            if tool.name == "tsc_scan_status":
                tool_func = tool.function
                break
        
        # Call tool
        result = tool_func()
        
        assert result["ok"] is True
        assert result["completed_scans"] == 1
        assert result["scan_results"][0]["import_info"]["alert"] is True
        assert "still processing" in result["scan_results"][0]["note"]
    
    @patch("tenable_sc_mcp.tools.scanning._client")
    @patch("tenable_sc_mcp.tools.scanning._get_cache")
    def test_scan_status_specific_scan(self, mock_cache, mock_client):
        """Test getting status for specific scan ID."""
        # Mock client response
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.get.return_value = {
            "response": {
                "id": "125",
                "name": "Specific Scan",
                "status": "Running",
                "totalIPs": "200",
                "completedIPs": "150",
                "completedChecks": "15000",
                "totalChecks": "20000",
                "startTime": str(int(time.time()) - 5400),
                "finishTime": "-1",
                "scanDuration": "0",
                "importStatus": "No Results",
                "importStart": "-1",
                "importFinish": "-1",
                "importDuration": "-1",
                "errorDetails": "",
                "importErrorDetails": "",
                "scan": {"id": "3", "name": "PCI Scan"},
                "repository": {"id": "10", "name": "Production"},
                "initiator": {"username": "admin"},
                "progress": {
                    "completedIPs": "150",
                    "totalIPs": "200",
                    "scannedIPs": "150",
                    "completedChecks": "15000",
                    "totalChecks": "20000",
                },
            }
        }
        
        # Mock cache
        mock_cache.return_value = None
        
        # Import and call tool
        from tenable_sc_mcp.tools.scanning import register_tools
        from mcp.server.fastmcp import FastMCP
        
        mcp = FastMCP("test")
        register_tools(mcp)
        
        # Get the registered tool
        tool_func = None
        for tool in mcp._tools.values():
            if tool.name == "tsc_scan_status":
                tool_func = tool.function
                break
        
        # Call tool
        result = tool_func(scan_id=125, include_progress=True)
        
        assert result["ok"] is True
        assert result["total_results"] == 1
        assert result["scan_results"][0]["id"] == "125"
        assert result["scan_results"][0]["progress"]["percent"] == 75.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

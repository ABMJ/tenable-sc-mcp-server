"""
Scanning tools for Tenable.sc MCP Server.

This module provides real-time scan execution monitoring using the scanResult API.
"""

import time
from datetime import datetime
from typing import Any

from mcp.server import Server

from ..cache import generate_cache_key
from ..server import _client, _get_cache


def parse_time_range(time_range: str) -> tuple[int, int]:
    """
    Parse time range string to epoch timestamps.
    
    Args:
        time_range: Time range string (24h, 7d, 30d)
    
    Returns:
        Tuple of (start_epoch, end_epoch)
    """
    now = int(time.time())
    
    if time_range == "24h":
        return (now - 86400, now)
    elif time_range == "7d":
        return (now - 604800, now)
    elif time_range == "30d":
        return (now - 2592000, now)
    else:
        # Default to 24h
        return (now - 86400, now)


def calculate_progress(result: dict[str, Any]) -> dict[str, Any]:
    """
    Calculate scan progress metrics.
    
    Args:
        result: Scan result dictionary from API
    
    Returns:
        Progress metrics including percent, IPs/hour, estimated time
    """
    completed = int(result.get("completedIPs", 0))
    total = int(result.get("totalIPs", 1))
    percent = (completed / total * 100) if total > 0 else 0
    
    # Time estimation
    start = int(result.get("startTime", 0))
    now = int(time.time())
    elapsed = now - start if start > 0 else 0
    
    ips_per_hour = (completed / elapsed * 3600) if elapsed > 0 else 0
    remaining_ips = total - completed
    estimated_seconds = (remaining_ips / ips_per_hour * 3600) if ips_per_hour > 0 else 0
    
    return {
        "ips_completed": completed,
        "ips_total": total,
        "percent": round(percent, 1),
        "checks_completed": int(result.get("completedChecks", 0)),
        "checks_total": int(result.get("totalChecks", 0)),
        "ips_per_hour": round(ips_per_hour, 1) if ips_per_hour > 0 else None,
        "estimated_remaining_seconds": int(estimated_seconds) if estimated_seconds > 0 else None,
    }


def check_import_status(result: dict[str, Any]) -> dict[str, Any]:
    """
    Check for import issues and alert on scan completed but import still running.
    
    Args:
        result: Scan result dictionary from API
    
    Returns:
        Import status info with alert flag
    """
    scan_status = result.get("status", "")
    import_status = result.get("importStatus", "")
    
    # Key insight: scan can be completed but import still running
    if scan_status == "Completed" and import_status == "Running":
        import_start = int(result.get("importStart", 0))
        elapsed = int(time.time()) - import_start if import_start > 0 else 0
        
        return {
            "alert": True,
            "message": "Scan completed but import still processing",
            "import_elapsed_seconds": elapsed,
            "import_elapsed_formatted": format_duration(elapsed),
        }
    elif import_status == "Error":
        return {
            "alert": True,
            "message": "Import failed",
            "error_details": result.get("importErrorDetails", "Unknown error"),
        }
    
    return {"alert": False}


def format_timing(result: dict[str, Any]) -> dict[str, Any]:
    """
    Format timing information from scan result.
    
    Args:
        result: Scan result dictionary from API
    
    Returns:
        Formatted timing information
    """
    start = int(result.get("startTime", 0))
    finish = int(result.get("finishTime", -1))
    duration = int(result.get("scanDuration", 0))
    
    timing: dict[str, Any] = {}
    
    if start > 0:
        timing["started"] = datetime.fromtimestamp(start).isoformat()
    
    if finish > 0:
        timing["finished"] = datetime.fromtimestamp(finish).isoformat()
        timing["duration"] = format_duration(duration)
    elif start > 0:
        elapsed = int(time.time()) - start
        timing["elapsed"] = format_duration(elapsed)
    
    return timing


def format_duration(seconds: int) -> str:
    """
    Format seconds to human-readable duration.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted duration string (e.g., "2h 15m")
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def register_tools(mcp: Server) -> None:
    """Register scanning tools with the MCP server."""

    @mcp.tool()
    def tsc_scan_status(
        scan_id: int | None = None,
        status: str | None = None,
        time_range: str | None = "24h",
        include_progress: bool = False,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Monitor scan execution status with progress tracking.
        
        Tracks scan status, import status, and performance metrics using the
        scanResult API. Supports filtering by status, time range, and custom filters.
        
        WHEN TO USE THIS TOOL:
        - User asks "show me all running scans"
        - User asks "did last night's scans complete?"
        - User asks "why can't I see scan data?" (import status check)
        - User asks "how long until PCI scan finishes?"
        - User asks "which scans failed this week?"
        - User asks "what's the scanning rate?" (IPs/hour)
        
        KEY FEATURES:
        - Dual status tracking (scan status + import status)
        - Progress calculation (percent, IPs/hour, ETA)
        - Time range helpers (24h, 7d, 30d)
        - Detailed progress per-scan (optional)
        - Import status alerts (scan complete but data not available)
        
        CRITICAL API INSIGHTS:
        1. Time filtering searches createdTime by default, NOT finishTime
        2. Detailed progress only available on GET /{id}, not list
        3. Import status must be tracked separately from scan status
        4. API returns string booleans ("true"/"false"), not actual booleans
        
        Args:
            scan_id: Specific scan result ID for detailed view
            status: Filter by status (running/completed/error/stopped/paused)
            time_range: Time range filter (24h/7d/30d). Default: 24h
            include_progress: Get detailed progress (requires per-scan query). Default: False
            filters: Additional filters dict. Supported keys:
                - start_time: Custom start time (ISO format or epoch)
                - end_time: Custom end time (ISO format or epoch)
                - time_compare_field: "finishTime" or "createdTime" (default: createdTime)
        
        Returns:
            Scan status with progress, timing, and import status:
            {
                "ok": True,
                "total_results": 15,
                "active_scans": 3,
                "completed_scans": 10,
                "failed_scans": 2,
                "scan_results": [
                    {
                        "id": "123",
                        "name": "Weekly PCI Scan",
                        "status": "Running",
                        "progress": {
                            "ips_completed": 450,
                            "ips_total": 500,
                            "percent": 90.0,
                            "checks_completed": 125000,
                            "checks_total": 135000,
                            "ips_per_hour": 200.0,
                            "estimated_remaining_seconds": 900
                        },
                        "timing": {
                            "started": "2026-06-24T10:00:00",
                            "elapsed": "2h 15m"
                        },
                        "import_status": "No Results",
                        "import_info": {"alert": False},
                        "scan": {"id": "45", "name": "PCI Quarterly"},
                        "repository": {"id": "9", "name": "Production"},
                        "initiator": {"username": "scheduler"}
                    }
                ],
                "filters_applied": {
                    "time_range": "24h",
                    "status": "all"
                }
            }
        
        Example:
            >>> tsc_scan_status(status="running")
            # Returns all running scans
            
            >>> tsc_scan_status(status="completed", time_range="24h")
            # Returns scans completed in last 24 hours
            
            >>> tsc_scan_status(scan_id=123, include_progress=True)
            # Returns detailed progress for scan 123
            
            >>> tsc_scan_status(filters={
            ...     "start_time": "2026-06-20",
            ...     "end_time": "2026-06-24",
            ...     "time_compare_field": "finishTime"
            ... })
            # Returns scans that finished between June 20-24
        """
        client = _client()
        cache = _get_cache()
        
        # Parse time range
        if time_range:
            start_epoch, end_epoch = parse_time_range(time_range)
        else:
            start_epoch, end_epoch = parse_time_range("24h")
        
        # Build query parameters
        params: dict[str, Any] = {
            "fields": "id,name,status,totalIPs,completedIPs,completedChecks,totalChecks,startTime,finishTime,scanDuration,importStatus,importStart,importFinish,importDuration,errorDetails,importErrorDetails,scan,repository,initiator",
            "startTime": str(start_epoch),
            "endTime": str(end_epoch),
        }
        
        # Add status filter
        if status:
            if status == "running":
                params["running"] = "true"
            elif status == "completed":
                params["completed"] = "true"
        
        # Apply custom filters
        filter_dict = filters or {}
        if "time_compare_field" in filter_dict:
            params["timeCompareField"] = filter_dict["time_compare_field"]
        
        # Generate cache key
        cache_key = generate_cache_key("scan_status", params=params)
        
        # Check cache (skip for specific scan queries)
        if cache and not scan_id:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
        
        # Query API
        if scan_id:
            # Single scan with detailed progress
            response = client.request(
                "GET",
                f"/rest/scanResult/{scan_id}",
                params={"fields": params["fields"] + ",progress"}
            )
            results = [response.get("response", {})]
        else:
            # List all matching scans
            response = client.request(
                "GET",
                "/rest/scanResult",
                params=params
            )
            results = response.get("response", {}).get("usable", [])
        
        # Process results
        scan_results = []
        active_scans = 0
        completed_scans = 0
        failed_scans = 0
        
        for result in results:
            status_val = result.get("status", "")
            
            # Count by status
            if status_val == "Running":
                active_scans += 1
            elif status_val == "Completed":
                completed_scans += 1
            elif status_val in ["Error", "Stopped"]:
                failed_scans += 1
            
            # Calculate progress
            progress = calculate_progress(result)
            
            # Check import status
            import_info = check_import_status(result)
            
            # Format timing
            timing = format_timing(result)
            
            scan_result: dict[str, Any] = {
                "id": result.get("id"),
                "name": result.get("name"),
                "status": status_val,
                "progress": progress,
                "timing": timing,
                "import_status": result.get("importStatus"),
                "import_info": import_info,
                "scan": result.get("scan", {}),
                "repository": result.get("repository", {}),
                "initiator": result.get("initiator", {}),
            }
            
            # Add note for import alerts
            if import_info.get("alert"):
                scan_result["note"] = import_info.get("message", "")
            
            scan_results.append(scan_result)
        
        result_data = {
            "ok": True,
            "total_results": len(scan_results),
            "active_scans": active_scans,
            "completed_scans": completed_scans,
            "failed_scans": failed_scans,
            "scan_results": scan_results,
            "filters_applied": {
                "time_range": time_range or "24h",
                "status": status or "all",
            },
        }
        
        # Cache result (skip for specific scan queries)
        if cache and not scan_id:
            cache.set(cache_key, result_data, ttl_seconds=60)
        
        return result_data

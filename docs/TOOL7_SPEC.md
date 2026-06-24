# Tool 7 FINAL Specification - Scan Result Status

## Official Tenable.sc API Documentation Summary

### GET /rest/scanResult - Available Fields

**Core Status Fields:**
- `status`: Running | Completed | Error | Stopped | Paused | Partial
- `importStatus`: Finished | Running | Error | Partial | "No Results"
- `running`: "true" | "false" (string boolean)

**Progress Fields:**
- `totalIPs`: Total target count
- `completedIPs`: IPs scanned so far
- `scannedIPs`: Count of scanned IPs (different from completed?)
- `completedChecks`: Plugins executed
- `totalChecks`: Total plugins to execute

**Timing Fields:**
- `startTime`: Unix epoch timestamp
- `finishTime`: Unix epoch (-1 if not finished)
- `createdTime`: When result was created
- `scanDuration`: Duration in seconds
- `importStart`: Unix epoch when import began (-1 if not started)
- `importFinish`: Unix epoch when import finished (-1 if not finished)
- `importDuration`: Import duration in seconds (-1 if not finished)

**Metadata Fields:**
- `id`: Scan result ID
- `name`: Scan result name
- `description`: Description
- `details`: Policy name/details
- `errorDetails`: Error message if failed
- `importErrorDetails`: Import error message
- `dataFormat`: "IPv4" | "IPv6" | "agent"
- `resultType`: "active" | "passive"
- `resultSource`: "internal" | "external"
- `downloadAvailable`: "true" | "false"
- `downloadFormat`: "v2" (Nessus format)

**Relationship Fields:**
- `scan`: {id, name, description, type}
- `repository`: {id, name, description, type, dataFormat, uuid}
- `owner`: {id, username, firstname, lastname, uuid}
- `initiator`: {id, username, firstname, lastname, uuid} (who launched it)
- `ownerGroup`: {id, name, description}
- `job`: {id} (scheduled job that launched it)

**Special Field - progress (only on GET /{id}):**
```json
"progress": {
    "completedIPs": "200",
    "completedChecks": "10600",
    "totalChecks": "10600",
    "checksPerHost": "53",
    "totalIPs": "200",
    "runState": "Stopped",
    "scanningIPs": "192.168.1.50",
    "scanningSize": 1,
    "scannedIPs": "192.168.0.0",
    "scannedSize": 29,
    "awaitingDownloadIPs": "",
    "awaitingDownloadSize": 0,
    "distributedSize": 200,
    "status": "Completed",
    "deadHostSize": 171,
    "deadHostIPs": "192.168.0.0",
    "scanners": [...]  // Per-scanner breakdown
}
```

### Filter Parameters
- `usable` - Returns only usable scan results
- `manageable` - Returns only manageable scan results  
- `running` - Returns only running scans
- `completed` - Returns only completed scans
- `optimizeCompletedScans` - Skip progress fields for completed scans (performance)
- `timeCompareField` - "finishTime" or "createdTime" (for time filtering)
- `startTime` - Unix epoch (default: now-30 days) - uses createdTime
- `endTime` - Unix epoch (default: now) - uses createdTime

### Key Insights

1. **Time Filtering Confusion:**
   - `startTime`/`endTime` params search against `createdTime`, NOT `finishTime`
   - Need `timeCompareField` param to search by finishTime
   - API default: last 30 days of created results

2. **Progress Field Limitation:**
   - `progress` field ONLY available on GET /{id}, NOT on list
   - Must query each scan individually for detailed progress
   - List view only has: completedIPs, completedChecks, totalChecks

3. **Import vs Scan Status:**
   - `status` = scan execution status
   - `importStatus` = result import status
   - Both must be tracked separately!

4. **String Booleans:**
   - `running`, `downloadAvailable` are strings: "true" or "false"
   - NOT actual booleans

5. **Optimization Flag:**
   - `optimizeCompletedScans` skips progress fields for speed
   - Use this when listing many historical results

## Tool 7 Implementation Specification

### Tool Name: `tsc_scan_status`

**Status:** ⏳ Next Priority  
**Time Estimate:** 2.5-3h  
**Token Budget:** 2,000-4,000  
**Cache TTL:** 60s  
**Module:** `tools/scanning.py` (new file)

### Function Signature

```python
@mcp.tool()
def tsc_scan_status(
    scan_id: int | None = None,           # Specific scan result ID
    status: str | None = None,            # running/completed/error/stopped/paused
    time_range: str | None = "24h",       # 24h/7d/30d or custom
    include_progress: bool = False,       # Get detailed progress (requires per-scan query)
    filters: dict[str, Any] | None = None # Additional filters
) -> dict[str, Any]:
```

### Features to Implement

#### 1. List Scan Results with Filters (Core - 1h)
```python
# Basic listing with status filter
tsc_scan_status(status="running")

# Time range filtering
tsc_scan_status(time_range="24h", status="completed")

# Custom time range
tsc_scan_status(filters={
    "start_time": "2026-06-20",
    "end_time": "2026-06-24",
    "time_compare_field": "finishTime"  # Search by finish time, not created
})
```

**Returns:**
- List of scan results
- Basic progress: completedIPs, totalIPs, percent
- Status and timing info
- Import status (critical!)

#### 2. Detailed Progress for Specific Scan (Enhancement - 0.5h)
```python
# Get detailed progress for one scan
tsc_scan_status(scan_id=123, include_progress=True)
```

**Returns:**
- Full progress object with per-scanner breakdown
- Current scanning IPs
- Dead host detection
- Checks per host
- Scanner load distribution

#### 3. Import Status Tracking (Core - 0.5h)
```python
# Identify scans with import issues
{
    "scan_name": "Full Network",
    "scan_status": "Completed",
    "scan_duration": "4h 23m",
    "import_status": "Running",      # ← Still importing!
    "import_duration": "45m",
    "note": "Scan complete but import still processing"
}
```

#### 4. Performance Metrics (Enhancement - 0.5h)
- IPs per hour calculation
- Scan duration comparison
- Identify slow scans
- Import performance

### Response Structure

```json
{
    "ok": true,
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
                "percent": 90,
                "checks_completed": 125000,
                "checks_total": 135000
            },
            "timing": {
                "started": "2026-06-24 10:00:00",
                "elapsed": "2h 15m",
                "estimated_remaining": "15m",
                "ips_per_hour": 200
            },
            "import_status": "No Results",  // Not started yet
            "scan": {"id": 45, "name": "PCI Quarterly"},
            "repository": {"id": 9, "name": "Production"},
            "initiator": {"username": "scheduler"}
        },
        {
            "id": "122",
            "name": "Full Network Scan",
            "status": "Completed",
            "progress": {
                "ips_completed": 1000,
                "ips_total": 1000,
                "percent": 100
            },
            "timing": {
                "started": "2026-06-24 06:00:00",
                "finished": "2026-06-24 10:23:00",
                "duration": "4h 23m"
            },
            "import_status": "Running",  // ← KEY: Still importing!
            "import_timing": {
                "started": "2026-06-24 10:23:00",
                "elapsed": "45m"
            },
            "note": "Scan completed but import in progress"
        },
        {
            "id": "121",
            "name": "Database Servers",
            "status": "Error",
            "error_details": "Scanner lost connectivity to host",
            "progress": {
                "ips_completed": 15,
                "ips_total": 50,
                "percent": 30
            },
            "timing": {
                "started": "2026-06-24 08:00:00",
                "failed_at": "2026-06-24 08:45:00",
                "duration_before_failure": "45m"
            }
        }
    ],
    "filters_applied": {
        "time_range": "24h",
        "status": "all"
    }
}
```

### Implementation Notes

1. **API Query Pattern:**
```python
# Basic list (fast)
results = client.get("/rest/scanResult", params={
    "fields": "id,name,status,totalIPs,completedIPs,completedChecks,totalChecks,startTime,finishTime,scanDuration,importStatus,importStart,importFinish,importDuration,errorDetails,scan,repository,initiator",
    "startTime": start_epoch,
    "endTime": end_epoch,
    "running": "true"  # or "completed", etc.
})

# Detailed progress (slower - one at a time)
if include_progress:
    detailed = client.get(f"/rest/scanResult/{scan_id}", params={
        "fields": "progress"
    })
```

2. **Time Range Helpers:**
```python
def parse_time_range(time_range: str) -> tuple[int, int]:
    now = int(time.time())
    if time_range == "24h":
        return (now - 86400, now)
    elif time_range == "7d":
        return (now - 604800, now)
    elif time_range == "30d":
        return (now - 2592000, now)
```

3. **Progress Calculation:**
```python
def calculate_progress(result: dict) -> dict:
    completed = int(result.get("completedIPs", 0))
    total = int(result.get("totalIPs", 1))
    percent = (completed / total * 100) if total > 0 else 0
    
    # Time estimation
    start = int(result["startTime"])
    now = int(time.time())
    elapsed = now - start
    ips_per_hour = (completed / elapsed * 3600) if elapsed > 0 else 0
    remaining_ips = total - completed
    estimated_seconds = (remaining_ips / ips_per_hour * 3600) if ips_per_hour > 0 else 0
    
    return {
        "ips_completed": completed,
        "ips_total": total,
        "percent": round(percent, 1),
        "elapsed_seconds": elapsed,
        "estimated_remaining_seconds": estimated_seconds,
        "ips_per_hour": round(ips_per_hour, 1)
    }
```

4. **Import Status Helper:**
```python
def check_import_status(result: dict) -> dict:
    scan_status = result["status"]
    import_status = result["importStatus"]
    
    # Key insight: scan can be completed but import still running
    if scan_status == "Completed" and import_status == "Running":
        return {
            "alert": True,
            "message": "Scan completed but import still processing",
            "import_elapsed": calculate_duration(result["importStart"])
        }
    return {"alert": False}
```

### Use Cases Covered

1. ✅ "Show me all running scans"
2. ✅ "Did last night's scans complete?"
3. ✅ "Why can't I see scan data?" (import status check)
4. ✅ "How long until PCI scan finishes?"
5. ✅ "Which scans failed this week?"
6. ✅ "What's the scanning rate?" (IPs/hour)

### Testing Plan

1. Test with running scan (progress tracking)
2. Test with completed scan (import status)
3. Test with failed scan (error details)
4. Test time range filters (24h, 7d, 30d)
5. Test status filters (running, completed, error)
6. Test detailed progress query (scan_id specific)

### Cache Strategy

- **TTL**: 60 seconds (real-time data)
- **Key**: Status filter + time range (not scan_id)
- **Invalidation**: Short TTL handles changing data

### Token Budget

- Basic list (10 scans): ~2,000 tokens
- With detailed progress: ~4,000 tokens
- Historical query (30d, 50 scans): ~8,000 tokens

## Conclusion

Tool 7 should be a **2.5-3h implementation** with these priorities:

**MUST HAVE (2h):**
1. List scan results with filters ✅
2. Progress tracking (basic) ✅
3. Import status tracking ✅
4. Time range helpers ✅

**NICE TO HAVE (+1h):**
5. Detailed progress (per-scanner) ✅
6. Performance metrics ✅
7. Historical trending

**Defer to Later:**
- Scanner health (different tool)
- Scan scheduling validation
- License tracking


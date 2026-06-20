# Tenable.sc MCP Server - Tools Roadmap

**Status**: v1.3.0.1 Released (OS Filtering & Plugin Family Validation Complete)  
**Last Updated**: 2026-06-20  
**Next Phase**: v1.4.0 Planning (TBD)

---

## 📋 Completed Tools (v1.3.0.1)

### Core Convenience Tools ✅
1. **`tsc_profile_ip_efficient`** - Complete IP security profile with OS, software, services
2. **`tsc_list_vulns_by_ip_summary`** - Quick vulnerability counts by severity  
3. **`tsc_list_vulns_by_ip_full`** - Detailed vulnerability records with remediation
4. **`tsc_list_ips`** - IP discovery with OS filtering (multi-query support)
5. **`tsc_list_vulns_by_cve`** - CVE search across infrastructure

### Helper Tools ✅
6. **`tsc_list_operating_systems`** - Discover valid OS names for filtering (300s cache)
7. **`tsc_list_plugin_families`** - Discover plugin families with IDs (24h cache)

### Filter Architecture ✅
- **74 total filters** - Including OS aliases and plugin family smart lookup
- **Unified filters dict pattern** - All tools use `filters={}` parameter
- **Smart lookups** - Automatic name→ID resolution for OS and families
- **Validation** - Proper error handling for invalid filter values

---

## 🎯 v1.4.0 Planning (Future Work)

### Potential Feature Areas

#### 1. Scan Management
- Launch scans with custom targets
- Pause/resume/stop running scans
- Schedule recurring scans
- Check scan status and progress
- Retrieve scan history

**Use Cases:**
- Automate scan workflows
- Emergency response scans for specific CVEs
- Integrate scanning into CI/CD pipelines

---

#### 2. Remediation Tracking
- Track remediation progress over time
- Generate remediation reports
- Compare vulnerability states across time periods
- Track patch deployment effectiveness

**Use Cases:**
- Measure remediation SLAs
- Generate executive reports
- Validate patch deployment success

---

#### 3. Custom Dashboard Management
- Create custom dashboards from templates
- Add/remove widgets from dashboards
- Apply context filters to dashboards
- Export dashboard data

**Use Cases:**
- Automate dashboard creation for teams
- Apply filters programmatically (e.g., by tag)
- Generate consistent reporting views

---

#### 4. Report Generation
- Generate reports from templates
- Schedule report generation
- Download report output (PDF, HTML, CSV)
- Track report generation status

**Use Cases:**
- Automate compliance reporting
- Generate executive summaries
- Export data for external analysis

---

#### 5. Enhanced Tag Management
- Create tags with dynamic filters
- Bulk tag assets by query criteria
- Remove tags from assets
- Search tags and filter assets by tags

**Use Cases:**
- Auto-tag assets by subnet (e.g., "PCI Assets")
- Bulk categorization for reporting
- Integration with external CMDBs

---

#### 6. Compliance Scanning
- Retrieve compliance scan results
- Filter by compliance standard (PCI, HIPAA, etc.)
- Generate compliance summary reports
- Track compliance status over time

**Use Cases:**
- Automated compliance reporting
- Audit trail generation
- Continuous compliance monitoring

---

#### 7. Asset Intelligence
- Software inventory across assets
- Service discovery and enumeration
- Open port analysis
- Credential audit results

**Use Cases:**
- Software license management
- Attack surface analysis
- Credential hygiene monitoring

---

#### 8. Advanced Querying
- Bulk IP profiling (profile multiple IPs in parallel)
- Asset criticality (ACR) risk scoring queries
- Advanced filtering combinations
- Custom analysis tool queries

**Use Cases:**
- Large-scale asset analysis
- Risk-based prioritization
- Custom security queries

---

## 🔧 Development Guidelines for v1.4.0

### Architecture Principles

**1. Unified Filters Pattern**
```python
# All tools use filters dict parameter
def tool_name(
    required_param: str,
    filters: dict[str, Any] | None = None
) -> dict[str, Any]:
    filter_dict = filters or {}
    filter_list, os_names = build_filters(client=_client(), **filter_dict)
```

**2. Smart Lookups**
- Use cached helper functions for name→ID resolution
- Validate inputs before API calls
- Return helpful error messages for invalid values

**3. Token Efficiency**
- Target 60-90% token reduction vs raw API
- Use caching with appropriate TTLs
- Return compact summaries with optional detail levels

**4. Error Handling**
```python
try:
    # Tool logic
    filter_list, os_names = build_filters(...)
except ValueError as e:
    # Invalid filter parameter
    return {"ok": False, "error": str(e)}
except Exception as e:
    # Unexpected error
    return {"ok": False, "error": f"Failed: {str(e)}"}
```

### Testing Requirements

**For Each New Tool:**
1. Create test prompts in TEST_PROMPTS.md
2. Include formatting instructions for cache/token reporting
3. Test error handling with invalid inputs
4. Verify results against Tenable.sc UI
5. Measure token efficiency vs raw API

### Documentation Requirements

**For Each Release:**
1. Update CHANGELOG.md with version notes
2. Update TEST_PROMPTS.md with test cases
3. Update version in pyproject.toml and __init__.py
4. Update filter reference if new filters added
5. Create GitHub release with release notes

---

## 📚 Reference Documentation

### User Facing
- `README.md` - Quick start and overview
- `TEST_PROMPTS.md` - Test cases for all tools
- `CHANGELOG.md` - Version history
- `FILTER_FORMAT_REFERENCE.md` - Complete filter syntax guide

### Developer Facing
- `.private/HANDOFF.md` - Session handoff document
- `.private/TOOLS_ROADMAP.md` - This file
- `DESIGN_PRINCIPLES.md` - Architecture patterns
- `src/tenable_sc_mcp/convenience_tools.py` - Core filter building logic

### MCP Resources (Exposed to LLM)
- `tenable-sc://filters/reference` - Compact filter reference (74 filters)
- `tenable-sc://filters/format-reference` - Detailed format guide with examples

---

## 💡 Lessons Learned (v1.3.0.1)

### What Works Well

1. **Unified Filters Dict** - Clean API, easy to extend
2. **Smart Lookups** - Name→ID resolution makes tools user-friendly
3. **Multi-Query Pattern** - Handles API limitations (no OR logic) elegantly
4. **Comprehensive Testing** - TEST_PROMPTS.md catches bugs early
5. **LLM Orchestration** - Simple tools + LLM workflows > complex single tools

### Common Pitfalls

1. **Docker Caching** - Always use `--no-cache` when debugging Python changes
2. **API Format Variations** - Different tools need different filter structures
3. **Validation Required** - Always validate user inputs to prevent unfiltered results
4. **Multi-OS Entries** - Handle ambiguous detections (comma-separated) specially
5. **Token Efficiency** - Balance between detail and conciseness

### Best Practices

1. **Cache Strategy**
   - Static data (plugin families): 24 hours
   - Semi-static (OS names): 5 minutes
   - Dynamic (vulnerabilities): 3 minutes

2. **Error Messages**
   - Include hint pointing to discovery tool
   - Show what was searched for
   - Suggest valid alternatives

3. **Response Format**
   ```python
   {
       "ok": True/False,
       "error": "...",  # if ok=False
       "data": {...},   # actual results
       "summary": {...}, # metadata (counts, pagination)
       "filters_applied": {...}  # what filters were used
   }
   ```

---

## 🚀 Next Steps for v1.4.0

1. **Requirements Gathering**
   - Discuss priorities with user
   - Identify most valuable features
   - Estimate implementation effort

2. **Design Phase**
   - Create detailed specifications for chosen features
   - Define API endpoints and data structures
   - Plan testing strategy

3. **Implementation**
   - Follow established patterns from v1.3.0.1
   - Write tests first (TEST_PROMPTS.md)
   - Document as you go

4. **Testing & Release**
   - Comprehensive testing with real data
   - Update all documentation
   - Create GitHub release

---

**End of Roadmap**  
**Next Developer:** Discuss v1.4.0 priorities with user before starting implementation

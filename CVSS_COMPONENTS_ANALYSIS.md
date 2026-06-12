# CVSS Component Filters - Implementation Complete

**Status:** ✅ IMPLEMENTED in v1.2.1 (2026-06-12)

Based on user demand from Docker logs:
```
Unknown filter parameters will be ignored: exploitable, attack_vector, exploit_maturity, attack_complexity, os
```

## Implementation Summary

### ✅ What We Now Support (v1.2.1)

#### CVSS Vector Strings (Already Supported)
```python
COMMON_FILTERS = {
    # CVSS Vector Strings (full vectors)
    "cvss_vector": "cvssVector",        # CVSS v2 vector (e.g., "AV:N/AC:L/Au:N/C:P/I:P/A:P")
    "cvss_v3_vector": "cvssV3Vector",   # CVSS v3 vector (e.g., "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")
    "cvss_v4_vector": "cvssV4Vector",   # CVSS v4 vector
}
```

#### CVSS Component Metrics (NEW in v1.2.1)

These are **individual components** of CVSS vectors that Tenable.sc supports as separate filters:

These are **individual components** of CVSS vectors now supported as separate filters:

**Added to COMMON_FILTERS in `convenience_tools.py`:**

```python
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

# VPR/Exploit Component (1 filter) - Added in v1.2.1
"exploit_maturity": "vprExploitMaturity",  # Unproven/PoC/Functional/High
```

**Total:** 12 new CVSS/VPR component filters added

## Research Summary

### 1. Verified Filter Names
Based on Tenable.sc naming conventions and CVSS standard terminology:
- CVSS v3 filters follow pattern: `cvssV3{ComponentName}` (camelCase)
- CVSS v2 filters follow pattern: `cvssV2{ComponentName}` (camelCase)
- VPR filters follow pattern: `vpr{ComponentName}` (camelCase)

### 2. Use Cases (NOW SUPPORTED)

**Why users would want these filters:**

```python
# Find vulnerabilities exploitable over the network with low complexity
filters = {
    "attack_vector": "Network",
    "attack_complexity": "Low",
    "exploit_maturity": "Functional"
}

# Find high-impact vulnerabilities requiring no privileges
filters = {
    "attack_vector": "Network",
    "privileges_required": "None",
    "confidentiality_impact": "High",
    "integrity_impact": "High"
}

# Critical path analysis (easy to exploit, high impact)
filters = {
    "attack_vector": "Network",
    "attack_complexity": "Low",
    "user_interaction": "None",
    "exploit_maturity": "Functional",
    "severity": "critical"
}
```

}
```

## Benefits of CVSS Component Filters

**More Granular Filtering:**
- Filter by specific attack characteristics (network vs local, low vs high complexity)
- Target vulnerabilities based on impact severity (high confidentiality/integrity/availability)
- Prioritize based on exploit maturity (PoC vs functional exploits)

**Better Threat Prioritization:**
- Focus on easily exploitable vulnerabilities (network + low complexity + no privileges)
- Identify high-impact vulnerabilities (high C/I/A impact)
- Critical path analysis for incident response

**Advanced Security Use Cases:**
- "Show me network-accessible vulnerabilities with low attack complexity"
- "Find high-impact vulnerabilities requiring no user interaction"
- "List functional exploits with network attack vector"

## Files Updated in v1.2.1

1. **`src/tenable_sc_mcp/convenience_tools.py`**
   - Added 12 CVSS component filters to `COMMON_FILTERS` dict
   - No changes to helper functions (they work with any filter in COMMON_FILTERS)

2. **`CVSS_COMPONENTS_ANALYSIS.md`** (this file)
   - Documented implementation details
   - Updated from "investigation" to "complete" status

3. **`FILTER_FORMAT_REFERENCE.md`**
   - Added CVSS component filter section with examples
   - Documented valid values for each component

4. **`src/tenable_sc_mcp/resources/filter_reference.py`**
   - MCP resource auto-generates from COMMON_FILTERS
   - No manual updates needed (by design)

## Testing Notes

Users were already trying to use these filters (from Docker logs):
```
Unknown filter parameters: attack_vector, exploit_maturity, attack_complexity
```

After v1.2.1, these warnings will disappear and filters will work correctly.

## Version History

- **v1.2.0** (2026-06-10): CVSS vector strings supported (full vectors only)
- **v1.2.1** (2026-06-12): CVSS component filters added (12 new filters)

---

**Created:** 2026-06-10  
**Updated:** 2026-06-12  
**Status:** ✅ IMPLEMENTED  
**Priority:** Complete (user demand addressed)

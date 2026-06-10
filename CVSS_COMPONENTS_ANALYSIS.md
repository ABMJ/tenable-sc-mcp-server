# CVSS Component Filters - Missing Support Analysis

Based on the warning message:
```
Unknown filter parameters will be ignored: exploitable, attack_vector, exploit_maturity, attack_complexity, os
```

## Current Status

### ✅ What We Support (CVSS Vectors)
```python
COMMON_FILTERS = {
    # CVSS Vector Strings (full vectors)
    "cvss_vector": "cvssVector",        # CVSS v2 vector (e.g., "AV:N/AC:L/Au:N/C:P/I:P/A:P")
    "cvss_v3_vector": "cvssV3Vector",   # CVSS v3 vector (e.g., "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")
    "cvss_v4_vector": "cvssV4Vector",   # CVSS v4 vector
}
```

### ❌ What We're Missing (CVSS Components)

These are **individual components** of CVSS vectors that Tenable.sc supports as separate filters:

#### CVSS v2 Components
- `attack_vector` (or `access_vector`) - Network/Adjacent/Local/Physical
- `attack_complexity` (or `access_complexity`) - Low/Medium/High
- `authentication` - None/Single/Multiple
- `confidentiality_impact` - None/Partial/Complete
- `integrity_impact` - None/Partial/Complete
- `availability_impact` - None/Partial/Complete

#### CVSS v3 Components
- `attack_vector` - Network/Adjacent/Local/Physical
- `attack_complexity` - Low/High
- `privileges_required` - None/Low/High
- `user_interaction` - None/Required
- `scope` - Unchanged/Changed
- `confidentiality_impact` - None/Low/High
- `integrity_impact` - None/Low/High
- `availability_impact` - None/Low/High

#### VPR/Exploit Components
- `exploit_maturity` - Unproven/Proof of Concept/Functional/High
- `exploitable` - Might be same as `exploit_available` (need to verify)

## Investigation Needed

### 1. Check Tenable.sc API Documentation
Need to verify the exact filter names and formats:
- Official docs: https://docs.tenable.com/security-center/6_8/Content/VulnerabilityAnalysisFilters.htm
- API endpoint: `GET /rest/analysis` (check available filters)

### 2. Common Use Cases

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

### 3. Filter Name Mapping

Need to determine Tenable.sc API filter names:

```python
# Likely mappings (need to verify):
CVSS_COMPONENT_FILTERS = {
    # CVSS v3 Attack Vector
    "attack_vector": "attackVector",  # or "cvssV3AttackVector"?
    "access_vector": "accessVector",  # CVSS v2 equivalent
    
    # CVSS v3 Attack Complexity
    "attack_complexity": "attackComplexity",  # or "cvssV3AttackComplexity"?
    "access_complexity": "accessComplexity",  # CVSS v2 equivalent
    
    # CVSS v3 Privileges Required
    "privileges_required": "privilegesRequired",
    
    # CVSS v3 User Interaction
    "user_interaction": "userInteraction",
    
    # CVSS v3 Scope
    "scope": "scope",
    
    # Impact metrics
    "confidentiality_impact": "confidentialityImpact",
    "integrity_impact": "integrityImpact",
    "availability_impact": "availabilityImpact",
    
    # VPR Exploit Maturity
    "exploit_maturity": "exploitMaturity",  # or "vprExploitMaturity"?
    
    # Exploitable flag
    "exploitable": "exploitable",  # might be duplicate of "exploit_available"
}
```

## Recommendation

### Option 1: Add CVSS Component Filters (Recommended)
**Benefits:**
- More granular filtering capabilities
- Better alignment with CVSS scoring methodology
- Enables critical path analysis (network + low complexity + no privileges)
- Supports advanced security use cases

**Effort:**
- Add ~15-20 new filters to `COMMON_FILTERS`
- Document in `FILTER_FORMAT_REFERENCE.md`
- Test with Tenable.sc API to verify exact names
- Add examples to tool docstrings

**Priority:** Medium-High
- Users are already trying to use these filters (shown in warning logs)
- CVSS components are standard security metrics
- Enables advanced threat prioritization

### Option 2: Document Limitations (Current Approach)
**Status Quo:**
- CVSS vector strings are supported (users can parse components themselves)
- Warning message helps users understand unsupported filters
- No breaking changes

**Drawbacks:**
- Less user-friendly (requires vector string parsing)
- Misses advanced use cases
- Users expect component-level filtering

## Next Steps

1. **Verify filter names** - Query Tenable.sc API for exact filter names
2. **Add to COMMON_FILTERS** - Extend with CVSS component filters
3. **Update documentation** - Add examples to FILTER_FORMAT_REFERENCE.md
4. **Test** - Validate with real Tenable.sc queries
5. **Release as v1.2.1** - Minor version bump (additive change)

## Example Implementation

```python
# Add to COMMON_FILTERS in convenience_tools.py
COMMON_FILTERS = {
    # ... existing filters ...
    
    # CVSS v3 Components (8 filters) - NEW
    "attack_vector": "cvssV3AttackVector",
    "attack_complexity": "cvssV3AttackComplexity",
    "privileges_required": "cvssV3PrivilegesRequired",
    "user_interaction": "cvssV3UserInteraction",
    "scope": "cvssV3Scope",
    "confidentiality_impact": "cvssV3ConfidentialityImpact",
    "integrity_impact": "cvssV3IntegrityImpact",
    "availability_impact": "cvssV3AvailabilityImpact",
    
    # VPR Components (1 filter) - NEW
    "exploit_maturity": "vprExploitMaturity",
    
    # ... rest of filters ...
}
```

---

**Created:** 2026-06-10  
**Status:** Investigation needed  
**Priority:** Medium-High (user demand evident from logs)

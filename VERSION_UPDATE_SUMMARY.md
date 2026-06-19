# Version 1.2.1 - Verification and Update Summary

**Date:** 2026-06-19  
**Status:** ✅ Version Confirmed and Updated

---

## Verification Results

### Git Tags
```
v0.1.0  - Initial release (2026-04-30)
v1.2.0  - Unified filters dict pattern (2026-06-10)
v1.2.1  - CPE/OS filtering + MCP fixes (2026-06-12)
```

### Version Consistency Check

| Location | Before | After | Status |
|----------|--------|-------|--------|
| pyproject.toml | 0.1.0 ❌ | 1.2.1 ✅ | Updated |
| src/tenable_sc_mcp/__init__.py | 0.1.0 ❌ | 1.2.1 ✅ | Updated |
| HANDOFF.md | 1.2.1 ✅ | 1.2.1 ✅ | Correct |
| DESIGN_PRINCIPLES.md | 1.2.1 ✅ | 1.2.1 ✅ | Correct |
| Git tag | v1.2.1 ✅ | v1.2.1 ✅ | Exists |
| GitHub release | v0.1.0 ❌ | - | **Needs update** |

---

## What is v1.2.1?

### Release Date
**June 12, 2026** (according to HANDOFF.md and DESIGN_PRINCIPLES.md)

### Key Features

1. **CPE/OS Filtering with Smart Operator Detection**
   - Auto-detects operator based on pattern:
     - Simple string → `~=` (contains): `"windows"`
     - Full CPE → `=` (exact): `"cpe:/o:microsoft:..."`
     - Regex pattern → `pcre`: `".*windows.*(10|11).*"`
   - Added `cpe` and `os_cpe` filters (71 total filters)

2. **MCP Resource Documentation Fix**
   - Fixed brace escaping in filter reference examples
   - Resource `tenable-sc://filters/reference` now loads correctly
   - Renders 14,985 characters of documentation

3. **Enhanced Documentation**
   - Added "Common Regex Pitfalls" section to FILTER_FORMAT_REFERENCE.md
   - Best practices for CPE filtering
   - Boundary techniques to avoid false positives

4. **Verified Features**
   - Severity string-to-numeric conversion working ("critical" → "4")
   - All 5 tools functional with CPE support
   - Token efficiency maintained (58-92% reduction)

### Files Modified in v1.2.1

**Core Implementation:**
- `src/tenable_sc_mcp/convenience_tools.py` - Added `detect_cpe_operator()` function
- `src/tenable_sc_mcp/resources/filter_reference.py` - Fixed brace escaping

**Documentation:**
- `FILTER_FORMAT_REFERENCE.md` - Added regex pitfall guidance
- `DESIGN_PRINCIPLES.md` - Added v1.2.1 version history entry
- `HANDOFF.md` - Complete rewrite for v1.2.1 session

---

## What Changed in This Update

### Commits Applied

1. **4ab5f5a** - `chore: Bump version to 1.2.1`
   - Updated `pyproject.toml` from 0.1.0 to 1.2.1
   - Updated `src/tenable_sc_mcp/__init__.py` from 0.1.0 to 1.2.1
   - Aligns code version with git tag and documentation

2. **16baf6b** - `docs: Remove QUICK_RULESET_SETUP.md`
   - Removed redundant branch protection guide

3. **cbd1727** - `docs: Clean up documentation and update branch protection guide`
   - Updated DESIGN_PRINCIPLES.md with GitHub Rulesets instructions
   - Removed outdated documentation files
   - Added LICENSE (GPL-3.0)
   - Updated .gitignore

---

## Current Repository Status

### Branch Status
- **main:** 3 commits ahead of origin/main
- **develop:** Up to date with origin/develop

### Unpushed Commits
1. chore: Bump version to 1.2.1 (4ab5f5a)
2. docs: Remove QUICK_RULESET_SETUP.md (16baf6b)
3. docs: Clean up documentation and update branch protection guide (cbd1727)

### Protection Status
- ✅ Main branch protected via GitHub Ruleset
- ⚠️ Develop branch not yet protected (recommended)

---

## Next Steps

### Immediate (This Session)
- [x] Verify version consistency across all files
- [x] Update pyproject.toml to 1.2.1
- [x] Update __init__.py to 1.2.1
- [x] Commit version updates
- [ ] **Push to GitHub** (user decision)
- [ ] **Create GitHub Release for v1.2.1** (recommended)

### Recommended GitHub Release

If creating a release for v1.2.1, use this content:

**Title:** `v1.2.1 - CPE/OS Filtering & Documentation Fixes`

**Release Notes:**
```markdown
## What's New in v1.2.1

### Features
- **Smart CPE/OS Filtering**: Auto-detects operators (contains/exact/regex) based on input pattern
- Added `cpe` and `os_cpe` filter parameters (71 total filters)
- Zero-configuration operator detection for intuitive filtering

### Bug Fixes
- Fixed MCP resource documentation generation (brace escaping)
- Resource `tenable-sc://filters/reference` now loads correctly

### Documentation
- Added comprehensive regex pitfall guidance
- Enhanced FILTER_FORMAT_REFERENCE.md with best practices
- Updated branch protection instructions for GitHub Rulesets

### Technical Details
- Token efficiency maintained: 58-92% reduction vs raw API
- All 5 tools functional with CPE support
- Severity string conversion verified working

### Files Changed
- Core: `convenience_tools.py`, `filter_reference.py`
- Docs: Multiple documentation updates
- Version: Bumped to 1.2.1 across all files

**Full Changelog**: https://github.com/ABMJ/tenable-sc-mcp-server/compare/v1.2.0...v1.2.1
```

---

## Version Roadmap

### Released
- ✅ **v0.1.0** (2026-04-30) - Initial release
- ✅ **v1.2.0** (2026-06-10) - Unified filters dict pattern
- ✅ **v1.2.1** (2026-06-12) - CPE/OS filtering + fixes

### Planned
- 🚧 **v1.3.0** (Planned) - OS exact matching & plugin family fix
  - See OS_AND_PLUGIN_FAMILY_FIX.md for details
  - Adds `operating_system` filter (zero false positives)
  - Fixes plugin family filter (name→ID lookup)
  - Helper tools: `tsc_list_operating_systems`, `tsc_list_plugin_families`
  - 71 → 74 filters

---

## Summary

**Status:** Version 1.2.1 is now correctly reflected across:
- ✅ Git tag (v1.2.1 exists)
- ✅ pyproject.toml (updated)
- ✅ __init__.py (updated)
- ✅ Documentation (HANDOFF.md, DESIGN_PRINCIPLES.md)

**Needs Attention:**
- ⚠️ GitHub release still shows v0.1.0 (outdated)
- ⚠️ 3 commits unpushed to origin/main

**Recommendation:** Push commits and create GitHub release for v1.2.1 to sync remote repository.

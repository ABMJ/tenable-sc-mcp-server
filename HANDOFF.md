# Tenable.sc MCP Server - Handoff Document

**Last Updated:** 2026-06-20 21:00  
**Project Status:** ✅ v1.3.0.1 Released  
**Next Session Priority:** v1.4.0 - Multi-Client API Key Support  
**Current Version:** 1.3.0.1

---

## 📋 Quick Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Current Version** | ✅ v1.3.0.1 | OS filtering & plugin family validation fixed |
| **Completed Tools** | 7/27 (26%) | Core tools + 2 helper tools |
| **Filter Count** | 74 filters | Universal filter framework |
| **Next Release** | v1.4.0 | Multi-client API key support |
| **Pending Tools** | Tools 6-27 | See TOOLS_ROADMAP.md |

### v1.3.0.1 Highlights (Completed)

- ✅ **OS Filtering**: Word-boundary matching, 74 filters, 4 OS aliases
- ✅ **Plugin Family**: Smart name→ID resolution, 123 families
- ✅ **Helper Tools**: `tsc_list_operating_systems`, `tsc_list_plugin_families`
- ✅ **Testing**: 8/8 tests passed
- ✅ **Documentation**: CHANGELOG.md, TEST_PROMPTS.md, filter reference updated

---

## 🚀 Next Priority: v1.4.0 - Multi-Client API Key Support

**CRITICAL:** Read **[MULTI_CLIENT_API_KEYS.md](MULTI_CLIENT_API_KEYS.md)** before starting implementation!

**What:** Transform MCP server from single-tenant to multi-tenant architecture  
**Estimated Time:** 4-5 hours  
**Breaking Changes:** None (backward compatible with .env mode)  
**Status:** Ready to implement

### Quick Summary

**Current Problem:**
- MCP server loads ONE set of API keys from `.env` at startup
- ALL clients share the SAME credentials
- No per-client RBAC enforcement
- Cannot support multiple users with different permission levels

**Solution:**
- Add FastMCP `Context` parameter to all 15+ tools for session tracking
- Store per-session `TenableScClient` instances with separate credentials
- Add `initialize_credentials` tool for clients to provide API keys
- Implement per-client cache isolation to prevent data leakage
- Support BOTH legacy `.env` mode and new per-client mode (backward compatible)

**Impact:**
- ✅ Proper multi-user support with RBAC enforcement
- ✅ Each client sees only data they're authorized to access
- ✅ Maintains backward compatibility with existing deployments
- ✅ Foundation for future session management and audit logging

### Implementation Phases

**Phase 1 (2h):** Core Session Management
- Add session storage: `_CLIENTS`, `_CACHE_PER_CLIENT` dicts
- Implement `_client_for_session(session_id)` (replaces singleton `_client()`)
- Implement `_register_client(session_id, config)` for registration
- Implement `_cleanup_session(session_id)` for disconnect handling
- Add `initialize_credentials` tool
- Thread-safe with `Lock()`

**Phase 2 (1.5h):** Update All Tools
- Add `from mcp.server.fastmcp import Context` import
- Add `ctx: Context` as first parameter to all 15+ tools:
  - Core API: `tsc_request`, `tsc_analyze`, `tsc_resource_action`
  - CRUD: `tsc_list`, `tsc_get`, `tsc_create`, `tsc_update`, `tsc_delete`
  - Docs: `tsc_catalog`, `tsc_resource_docs`
  - File ops: `tsc_download`, `tsc_upload_file`
  - Convenience: `tsc_profile_ip_efficient`, `tsc_list_ips`, etc.
- Replace `_client()` → `_client_for_session(ctx.session_id)`
- Replace `_get_cache()` → `_get_cache_for_tool(ctx)`

**Phase 3 (1h):** Testing & Validation
- Unit tests: session storage, cleanup, cache isolation
- Integration tests: multiple clients with different credentials
- Backward compatibility: `.env` fallback works
- Concurrent requests from multiple clients

**Phase 4 (1h):** Documentation
- Update README.md with multi-client usage examples
- Update tool docstrings
- Write migration guide

### Key Code Changes

**File:** `src/tenable_sc_mcp/server.py`

```python
from mcp.server.fastmcp import Context
from threading import Lock

# Replace singleton with session storage
_CLIENTS: dict[str, TenableScClient] = {}
_CLIENTS_LOCK = Lock()
_CACHE_PER_CLIENT: dict[str, Cache] = {}

def _client_for_session(session_id: str) -> TenableScClient:
    """Get or create client for this session."""
    with _CLIENTS_LOCK:
        if session_id in _CLIENTS:
            return _CLIENTS[session_id]
        
        # Fallback to .env for backward compatibility
        try:
            config = TenableScConfig.from_env()
            _CLIENTS[session_id] = TenableScClient(config=config)
            return _CLIENTS[session_id]
        except TenableScConfigError:
            raise TenableScConfigError(
                f"No credentials for session {session_id}. "
                "Call initialize_credentials first."
            )

@mcp.tool()
def initialize_credentials(
    ctx: Context,
    base_url: str,
    access_key: str,
    secret_key: str,
    verify_ssl: bool = True,
) -> dict[str, Any]:
    """Initialize Tenable.sc credentials for this session."""
    config = TenableScConfig(
        base_url=base_url,
        access_key=access_key,
        secret_key=secret_key,
        verify_ssl=verify_ssl,
    )
    _register_client(ctx.session_id, config)
    
    # Verify credentials work
    client = _client_for_session(ctx.session_id)
    client.request("GET", "/rest/system")
    
    return {
        "ok": True,
        "session_id": ctx.session_id,
        "base_url": base_url
    }
```

**Tool Pattern (apply to all tools):**

```python
# Before:
@mcp.tool()
def tsc_request(method: str, path: str, ...) -> dict[str, Any]:
    client = _client()
    cache = _get_cache()
    ...

# After:
@mcp.tool()
def tsc_request(ctx: Context, method: str, path: str, ...) -> dict[str, Any]:
    client = _client_for_session(ctx.session_id)
    cache = _get_cache_for_tool(ctx)
    ...
```

### Deliverables

- [ ] Session management infrastructure (`_CLIENTS`, `_CACHE_PER_CLIENT`, `_CLIENTS_LOCK`)
- [ ] `_client_for_session(session_id)` function
- [ ] `_register_client(session_id, config)` function
- [ ] `_cleanup_session(session_id)` function
- [ ] `initialize_credentials` tool
- [ ] All 15+ tools updated with `ctx: Context` parameter
- [ ] Per-client cache isolation
- [ ] Backward compatibility with `.env` mode
- [ ] Unit tests for session management
- [ ] Integration tests for multi-client scenarios
- [ ] Documentation updates (README.md, migration guide)
- [ ] Version bumped to 1.4.0
- [ ] Release published

**Start Here:** [MULTI_CLIENT_API_KEYS.md](MULTI_CLIENT_API_KEYS.md) - Complete implementation guide

---

## 📚 Key Documentation Files

**User Documentation:**
- `README.md` - Quick start and feature overview
- `TEST_PROMPTS.md` - Comprehensive test prompts for all tools
- `CHANGELOG.md` - Version history and release notes

**Developer Documentation:**
- `TOOLS_ROADMAP.md` - Future feature planning (Tools 6-27)
- `HANDOFF.md` - Session handoff notes (this file)
- `DESIGN_PRINCIPLES.md` - Architecture patterns and decisions
- `FILTER_FORMAT_REFERENCE.md` - Complete filter syntax guide
- `MULTI_CLIENT_API_KEYS.md` - v1.4.0 implementation guide

**MCP Resources (exposed to LLM):**
- `tenable-sc://filters/reference` - Interactive filter documentation
- `tenable-sc://resources/catalog` - Available API resources
- `tenable-sc://server/info` - Server configuration and OpenAPI metadata

---

## 🔧 Quick Development Setup

```bash
# Clone repository
git clone https://github.com/ABMJ/tenable-sc-mcp-server.git
cd tenable-sc-mcp-server

# Install dependencies
uv sync

# Configure credentials
cp .env.example .env
# Edit .env with your Tenable.sc credentials

# Build Docker container
docker build -t tenable-sc-mcp:latest .

# Run container
docker run -d --name tenable-sc-mcp \
  --env-file .env \
  -p 8080:8080 \
  tenable-sc-mcp:latest

# Run tests (after v1.4.0 implementation)
pytest tests/ -v
```

---

## 🎯 Development Workflow

1. **Create feature branch:** `git checkout -b feature/multi-client-support`
2. **Implement changes:** Follow MULTI_CLIENT_API_KEYS.md guide
3. **Test thoroughly:** Unit tests + integration tests
4. **Update docs:** README.md, tool docstrings, migration guide
5. **Merge to develop:** `git checkout develop && git merge feature/multi-client-support`
6. **Create release branch:** `git checkout -b release/1.4.0`
7. **Version bump:** Update `pyproject.toml` and `__init__.py`
8. **Merge to main:** Create PR, review, merge
9. **Tag release:** `git tag v1.4.0 && git push origin v1.4.0`
10. **Publish GitHub release:** Draft release notes from CHANGELOG.md

---

## 🚨 Critical Notes for v1.4.0

1. **Backward Compatibility:** `.env` mode MUST continue working for existing deployments
2. **Cache Isolation:** Per-client caches prevent data leakage between sessions
3. **Thread Safety:** Use `Lock()` for all session storage operations
4. **Error Handling:** Clear error messages when credentials not initialized
5. **Testing:** Test both `.env` fallback mode AND per-client credential mode
6. **Documentation:** Migration guide for existing users

---

## 📊 Project Statistics

- **Total Tools:** 7 implemented, 20 planned (27 total)
- **Total Filters:** 74 (universal across all tools)
- **Token Efficiency:** 83-90% reduction vs raw API
- **Cache Strategy:** Per-tool TTLs (60s-24h depending on data volatility)
- **Test Coverage:** 8 test cases for v1.3.0.1 (all passing)
- **GitHub Stars:** 1 (as of v1.3.0.1 release)

---

**For next session:** Read MULTI_CLIENT_API_KEYS.md and begin Phase 1 implementation

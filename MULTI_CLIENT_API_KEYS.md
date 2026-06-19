# v1.4.0 Implementation Plan - Multi-Client API Key Support

**Version:** v1.4.0  
**Created:** 2026-06-19  
**Status:** Ready for Implementation  
**Estimated Time:** 4-5 hours total  
**Breaking Changes:** None (backward compatible with .env file mode)

---

## 🎯 Executive Summary

This release transforms the MCP server from single-tenant to multi-tenant architecture, allowing multiple clients to connect with different API keys and receive data according to their individual Tenable.sc RBAC permissions.

**Current Problem:**
- MCP server loads ONE set of API keys from `.env` file at startup
- ALL clients connecting to the server share the SAME credentials
- No per-client RBAC enforcement - everyone sees the same data
- Cannot support multiple users with different permission levels

**Solution Strategy:**
- Add FastMCP `Context` parameter to all tools for session tracking
- Store per-session `TenableScClient` instances with separate credentials
- Add `initialize_credentials` tool for clients to provide their API keys
- Implement per-client cache isolation to prevent data leakage
- Support BOTH legacy `.env` mode and new per-client mode for backward compatibility

**Impact:** 
- Proper multi-user support with RBAC enforcement
- Each client sees only data they're authorized to access
- Maintains backward compatibility with existing deployments
- Foundation for future session management and audit logging

---

## 📊 Current Architecture Analysis

### Single-Tenant Flow (v1.2.2)

```
MCP Server Startup:
  1. Read TSC_URL, TSC_ACCESS_KEY, TSC_SECRET_KEY from .env
  2. Create singleton TenableScClient instance
  3. Initialize global cache

Client A connects:
  → Uses global TenableScClient
  → Sees data per .env credentials

Client B connects:
  → Uses SAME global TenableScClient
  → Sees SAME data as Client A
  
Problem: No per-client isolation!
```

**Code Location:**
- `server.py:37-38` - `_client()` function returns singleton
- `server.py:23-24` - Global `_CLIENT_ENV_PREFIX`, `_CLIENT_ENV_FILE`
- `client.py:73-136` - `TenableScConfig.from_env()` reads .env

**All Tools Use Singleton:**
```python
@mcp.tool()
def tsc_request(method: str, path: str, ...) -> dict[str, Any]:
    client = _client()  # ❌ Returns same instance for all clients
    result = client.request(method, path, ...)
    return result
```

---

## 🎯 Target Architecture - Multi-Tenant

### Per-Session Flow (v1.4.0)

```
MCP Server Startup:
  1. Initialize empty session storage: _CLIENTS = {}
  2. No credentials loaded at startup

Client A connects (Session ID: abc123):
  → Calls initialize_credentials(url, key_A, secret_A)
  → Server creates TenableScClient_A for session abc123
  → Client A sees data per key_A permissions

Client B connects (Session ID: xyz789):
  → Calls initialize_credentials(url, key_B, secret_B)
  → Server creates TenableScClient_B for session xyz789
  → Client B sees data per key_B permissions

All tool calls include Context:
  @mcp.tool()
  def tsc_request(ctx: Context, method: str, path: str, ...):
      client = _client_for_session(ctx.session_id)  # ✅ Per-client
      ...
```

**Benefits:**
- ✅ Each client isolated with own credentials
- ✅ Tenable.sc RBAC enforced per-client
- ✅ No shared cache data between clients
- ✅ Support multiple concurrent users
- ✅ Credentials never stored on disk

---

## 📋 Implementation Phases

### Phase 1: Core Session Management (2 hours)

#### 1.1 Add Session Storage (30 minutes)

**File:** `src/tenable_sc_mcp/server.py`

**Add at top of file after imports:**
```python
from mcp.server.fastmcp import Context
from threading import Lock

# Replace singleton with session-based storage
_CLIENTS: dict[str, TenableScClient] = {}
_CLIENTS_LOCK = Lock()
_CACHE_PER_CLIENT: dict[str, Cache] = {}
```

**Replace `_client()` function:**
```python
# OLD (remove):
def _client() -> TenableScClient:
    return TenableScClient(env_prefix=_CLIENT_ENV_PREFIX, env_file=_CLIENT_ENV_FILE)

# NEW (add):
def _client_for_session(session_id: str) -> TenableScClient:
    """
    Get TenableScClient for a specific session.
    
    Returns cached client if exists, otherwise attempts to initialize
    from environment variables for backward compatibility.
    
    Raises:
        TenableScConfigError: If no credentials found for session
    """
    with _CLIENTS_LOCK:
        # Check if client already exists for this session
        if session_id in _CLIENTS:
            return _CLIENTS[session_id]
        
        # Legacy mode: Try to initialize from .env for backward compatibility
        try:
            config = TenableScConfig.from_env(
                env_prefix=_CLIENT_ENV_PREFIX, 
                env_file=_CLIENT_ENV_FILE
            )
            client = TenableScClient(config=config)
            _CLIENTS[session_id] = client
            
            # Initialize cache for this client
            if _CACHE:
                _CACHE_PER_CLIENT[session_id] = _CACHE
            
            return client
        except TenableScConfigError:
            raise TenableScConfigError(
                f"No credentials configured for session {session_id}. "
                "Either set TSC_* environment variables or call initialize_credentials tool."
            )

def _register_client(session_id: str, config: TenableScConfig) -> None:
    """Register a new client session with credentials."""
    with _CLIENTS_LOCK:
        _CLIENTS[session_id] = TenableScClient(config=config)
        
        # Initialize per-client cache
        if config.cache_enabled:
            if config.cache_backend == "redis":
                try:
                    backend = RedisCache(
                        host=config.cache_redis_host,
                        port=config.cache_redis_port,
                        db=config.cache_redis_db,
                        password=config.cache_redis_password,
                    )
                    _CACHE_PER_CLIENT[session_id] = initialize_cache(backend)
                except Exception as e:
                    print(f"Failed to initialize Redis cache for session {session_id}: {e}")
                    _CACHE_PER_CLIENT[session_id] = initialize_cache(InMemoryCache())
            else:
                _CACHE_PER_CLIENT[session_id] = initialize_cache(InMemoryCache())
        else:
            _CACHE_PER_CLIENT[session_id] = None

def _get_cache_for_session(session_id: str) -> Cache | None:
    """Get cache instance for a specific session."""
    return _CACHE_PER_CLIENT.get(session_id)

def _cleanup_session(session_id: str) -> None:
    """Clean up when client disconnects."""
    with _CLIENTS_LOCK:
        if session_id in _CLIENTS:
            print(f"Cleaning up session: {session_id}")
            del _CLIENTS[session_id]
        
        if session_id in _CACHE_PER_CLIENT:
            cache = _CACHE_PER_CLIENT[session_id]
            if cache and isinstance(cache.backend, RedisCache):
                try:
                    cache.backend.client.close()
                except Exception as e:
                    print(f"Error closing Redis connection for session {session_id}: {e}")
            del _CACHE_PER_CLIENT[session_id]
```

**Testing:**
```python
# Test session storage
assert len(_CLIENTS) == 0  # Empty at start
config = TenableScConfig(base_url="https://test", access_key="key", secret_key="secret")
_register_client("test-session", config)
assert "test-session" in _CLIENTS
client = _client_for_session("test-session")
assert client.config.access_key == "key"
_cleanup_session("test-session")
assert "test-session" not in _CLIENTS
```

---

#### 1.2 Add Credential Initialization Tool (30 minutes)

**File:** `src/tenable_sc_mcp/server.py`

**Add new tool after existing tools:**
```python
@mcp.tool()
def initialize_credentials(
    ctx: Context,
    base_url: str,
    access_key: str,
    secret_key: str,
    verify_ssl: bool = True,
    cache_enabled: bool = True,
    cache_backend: str = "memory",
) -> dict[str, Any]:
    """
    Initialize Tenable.sc credentials for this session.
    
    This tool enables multi-client support by allowing each MCP client to
    provide their own API credentials. Each session is isolated with separate
    credentials, cache, and RBAC permissions.
    
    **Multi-Client Architecture:**
    - Each client connecting to the MCP server gets a unique session ID
    - Credentials are stored per-session in memory (not on disk)
    - All subsequent tool calls use the credentials for that session
    - Tenable.sc RBAC is enforced per-client based on their API keys
    
    **Security:**
    - Credentials are only stored in server memory
    - Each session is isolated - Client A cannot access Client B's data
    - Cache is per-session to prevent data leakage
    - Sessions are cleaned up when client disconnects
    
    **Backward Compatibility:**
    - If you don't call this tool, server falls back to TSC_* env vars
    - Existing deployments using .env file continue to work
    
    Args:
        ctx: MCP context (automatically provided)
        base_url: Tenable.sc URL (e.g., "https://tsc.company.com:8443")
        access_key: Tenable.sc API access key
        secret_key: Tenable.sc API secret key
        verify_ssl: Verify SSL certificates (default: True)
        cache_enabled: Enable caching for this session (default: True)
        cache_backend: Cache backend - "memory" or "redis" (default: "memory")
    
    Returns:
        Success confirmation with session info
    
    Raises:
        TenableScConfigError: If base_url is invalid
        TenableScApiError: If credentials are invalid (verified on first API call)
    
    Example:
        >>> initialize_credentials(
        ...     base_url="https://tsc.company.com:8443",
        ...     access_key="abcd1234...",
        ...     secret_key="xyz789...",
        ...     verify_ssl=False  # For self-signed certs
        ... )
        {
            "ok": True,
            "session_id": "abc123...",
            "base_url": "https://tsc.company.com:8443",
            "cache_enabled": True,
            "message": "Credentials initialized successfully"
        }
    """
    try:
        # Validate URL format
        if not base_url.startswith(("https://", "http://")):
            return {
                "ok": False,
                "error": "base_url must start with https:// or http://",
                "error_type": "TenableScConfigError"
            }
        
        # Create config for this session
        config = TenableScConfig(
            base_url=base_url.strip().rstrip("/"),
            access_key=access_key.strip(),
            secret_key=secret_key.strip(),
            verify_ssl=verify_ssl,
            cache_enabled=cache_enabled,
            cache_backend=cache_backend,
        )
        
        # Register client for this session
        _register_client(ctx.session_id, config)
        
        # Verify credentials work by making a test API call
        client = _client_for_session(ctx.session_id)
        try:
            # Test call to /rest/system - requires valid credentials
            test_result = client.request("GET", "/rest/system")
            if test_result.get("error_code"):
                # Cleanup failed session
                _cleanup_session(ctx.session_id)
                return {
                    "ok": False,
                    "error": "Invalid credentials - authentication failed",
                    "error_type": "TenableScApiError",
                    "details": test_result.get("error_msg", "Unknown error")
                }
        except TenableScApiError as e:
            # Cleanup failed session
            _cleanup_session(ctx.session_id)
            return {
                "ok": False,
                "error": f"Credential verification failed: {e}",
                "error_type": "TenableScApiError",
                "status_code": e.status_code
            }
        
        return {
            "ok": True,
            "session_id": ctx.session_id,
            "base_url": config.base_url,
            "cache_enabled": config.cache_enabled,
            "cache_backend": config.cache_backend,
            "message": "Credentials initialized successfully. You can now use all Tenable.sc tools."
        }
        
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "error_type": type(e).__name__
        }
```

**Test Cases:**
1. Valid credentials → Success
2. Invalid URL format → Error with clear message
3. Invalid credentials → Error with authentication failure
4. Multiple clients with different credentials → Isolated sessions
5. Session cleanup → No memory leaks

---

#### 1.3 Update Cache Functions (30 minutes)

**File:** `src/tenable_sc_mcp/server.py`

**Replace `_get_cache()` function:**
```python
# OLD (remove):
def _get_cache() -> Cache | None:
    """Get cache instance if enabled."""
    return _CACHE

# NEW (add):
def _get_cache_for_tool(ctx: Context | None = None) -> Cache | None:
    """
    Get cache instance for current session.
    
    Args:
        ctx: MCP context (if available)
    
    Returns:
        Per-session cache if ctx provided, global cache otherwise
    """
    if ctx and ctx.session_id in _CACHE_PER_CLIENT:
        return _CACHE_PER_CLIENT[ctx.session_id]
    
    # Fallback to global cache for backward compatibility
    return _CACHE
```

**Update all tools that use cache:**

Pattern to find:
```python
cache = _get_cache()
```

Replace with:
```python
cache = _get_cache_for_tool(ctx)
```

---

### Phase 2: Update All Tools (1.5 hours)

#### 2.1 Core API Tools (30 minutes)

**Pattern:** Add `ctx: Context` as first parameter, update `_client()` calls

**Tools to update (15 tools):**

1. **tsc_request** (line ~127):
```python
# Before:
@mcp.tool()
def tsc_request(
    method: str,
    path: str,
    ...
) -> dict[str, Any]:
    client = _client()
    cache = _get_cache()
    ...

# After:
@mcp.tool()
def tsc_request(
    ctx: Context,
    method: str,
    path: str,
    ...
) -> dict[str, Any]:
    client = _client_for_session(ctx.session_id)
    cache = _get_cache_for_tool(ctx)
    ...
```

2. **tsc_analyze** (line ~176)
3. **tsc_resource_action** (line ~261)
4. **tsc_list** (line ~301)
5. **tsc_get** (line ~320)
6. **tsc_create** (line ~341)
7. **tsc_update** (line ~347)
8. **tsc_delete** (line ~353)
9. **tsc_catalog** (line ~387)
10. **tsc_resource_docs** (line ~425)
11. **tsc_download** (line ~462)
12. **tsc_upload_file** (line ~484)

**Automated approach using sed (optional):**
```bash
# Add ctx: Context as first parameter to all @mcp.tool() functions
# Manual is safer for this refactor
```

---

#### 2.2 Convenience Tools (45 minutes)

**File:** `src/tenable_sc_mcp/convenience_tools.py`

All convenience tools call `_client()` and `_get_cache()` internally.

**Update pattern:**

```python
# Before:
def tsc_profile_ip_efficient(
    ip: str,
    include_software: bool = True,
    ...
) -> dict[str, Any]:
    """Profile an IP address."""
    client = _client()
    cache = _get_cache()
    ...

# After:
def tsc_profile_ip_efficient(
    ctx: Context,
    ip: str,
    include_software: bool = True,
    ...
) -> dict[str, Any]:
    """Profile an IP address."""
    client = _client_for_session(ctx.session_id)
    cache = _get_cache_for_tool(ctx)
    ...
```

**Tools to update:**
- `tsc_profile_ip_efficient`
- `tsc_list_ips`
- `tsc_list_vulns_by_ip_summary`
- `tsc_list_vulns_by_ip_full`
- `tsc_list_vulns_by_cve`

**Note:** These are registered as tools in convenience_tools.py, so they need Context parameter.

---

#### 2.3 Import Context (15 minutes)

**Files to update:**
1. `src/tenable_sc_mcp/server.py` - Add import at top
2. `src/tenable_sc_mcp/convenience_tools.py` - Add import at top

```python
from mcp.server.fastmcp import Context
```

**Also need to pass Context to convenience tools:**

In `server.py`, when convenience tools are imported and registered:
```python
from .convenience_tools import (
    tsc_profile_ip_efficient,
    tsc_list_ips,
    ...
)

# These are already registered as @mcp.tool() in convenience_tools.py
# Just need to ensure Context is imported there
```

---

### Phase 3: Testing & Validation (1 hour)

#### 3.1 Unit Tests (30 minutes)

**File:** `tests/test_multi_client.py` (new file)

```python
"""Tests for multi-client session management."""

import pytest
from mcp.server.fastmcp import Context
from src.tenable_sc_mcp.server import (
    _register_client,
    _client_for_session,
    _cleanup_session,
    _get_cache_for_tool,
)
from src.tenable_sc_mcp.client import TenableScConfig, TenableScConfigError


def test_session_storage():
    """Test basic session storage and retrieval."""
    config = TenableScConfig(
        base_url="https://test.local",
        access_key="test_key",
        secret_key="test_secret"
    )
    
    _register_client("session1", config)
    
    client = _client_for_session("session1")
    assert client.config.access_key == "test_key"
    assert client.config.base_url == "https://test.local"
    
    _cleanup_session("session1")


def test_multiple_sessions():
    """Test isolation between multiple sessions."""
    config1 = TenableScConfig(
        base_url="https://tsc1.local",
        access_key="key1",
        secret_key="secret1"
    )
    config2 = TenableScConfig(
        base_url="https://tsc2.local",
        access_key="key2",
        secret_key="secret2"
    )
    
    _register_client("session1", config1)
    _register_client("session2", config2)
    
    client1 = _client_for_session("session1")
    client2 = _client_for_session("session2")
    
    assert client1.config.access_key == "key1"
    assert client2.config.access_key == "key2"
    assert client1 is not client2
    
    _cleanup_session("session1")
    _cleanup_session("session2")


def test_missing_session():
    """Test error when session not found."""
    with pytest.raises(TenableScConfigError) as exc_info:
        _client_for_session("nonexistent-session")
    
    assert "No credentials configured" in str(exc_info.value)


def test_cache_isolation():
    """Test that cache is isolated per session."""
    config1 = TenableScConfig(
        base_url="https://test.local",
        access_key="key1",
        secret_key="secret1",
        cache_enabled=True,
        cache_backend="memory"
    )
    
    _register_client("session1", config1)
    _register_client("session2", config1)
    
    ctx1 = Context(session_id="session1")
    ctx2 = Context(session_id="session2")
    
    cache1 = _get_cache_for_tool(ctx1)
    cache2 = _get_cache_for_tool(ctx2)
    
    # Should be separate instances
    assert cache1 is not cache2
    
    _cleanup_session("session1")
    _cleanup_session("session2")
```

Run tests:
```bash
pytest tests/test_multi_client.py -v
```

---

#### 3.2 Integration Tests (30 minutes)

**Manual testing with two Claude Desktop instances:**

**Setup:**
1. Start MCP server: `uv run tenable-sc-mcp`
2. Configure two Claude Desktop clients (different machines or browsers)

**Test Case 1: Different Credentials**
```
Claude A:
> Initialize Tenable.sc with URL https://tsc.local:8443, 
  access key ADMIN_KEY, secret ADMIN_SECRET

> List repositories
Expected: See all repositories (admin access)

Claude B:
> Initialize Tenable.sc with URL https://tsc.local:8443,
  access key READONLY_KEY, secret READONLY_SECRET

> List repositories
Expected: See only repositories with read-only access

Verify: Results should be different based on RBAC
```

**Test Case 2: Same Credentials**
```
Claude A & B: Use same credentials
Expected: Both see same data, but sessions are isolated
```

**Test Case 3: Cache Isolation**
```
Claude A:
> Profile IP 10.1.20.10
(Data cached for session A)

Claude B:
> Profile IP 10.1.20.10
Expected: Makes fresh API call (not using A's cache)
```

**Test Case 4: Backward Compatibility**
```
# Don't call initialize_credentials
# Server should fall back to .env file
> List repositories
Expected: Works with TSC_* env vars
```

---

### Phase 4: Documentation (1 hour)

#### 4.1 Update README.md (30 minutes)

**Add new section after "Installation":**

```markdown
## Multi-Client Support

v1.4.0+ supports multiple clients with different API credentials connecting to the same MCP server instance.

### Option 1: Per-Client Credentials (Recommended for Multi-User)

Each client provides their own credentials at runtime:

**Claude Desktop Configuration:**
```json
{
  "mcpServers": {
    "tenable-sc": {
      "command": "uv",
      "args": ["run", "tenable-sc-mcp"]
    }
  }
}
```

**First-Time Usage:**
```
You: Initialize Tenable.sc with URL https://tsc.company.com:8443,
     access key abc123..., secret key xyz789...
Claude: [Calls initialize_credentials tool]
✅ Credentials initialized successfully.

You: List all scans
Claude: [Returns scans visible to abc123 credentials]
```

**Benefits:**
- ✅ Each user sees only data they're authorized to access (RBAC enforced)
- ✅ Support multiple users with different permission levels
- ✅ Credentials stored in memory only (not on disk)
- ✅ Sessions automatically cleaned up on disconnect

### Option 2: Single Credential (.env file)

For single-user deployments, continue using the `.env` file approach:

**Claude Desktop Configuration:**
```json
{
  "mcpServers": {
    "tenable-sc": {
      "command": "uv",
      "args": ["run", "tenable-sc-mcp"],
      "env": {
        "TSC_URL": "https://tsc.company.com:8443",
        "TSC_ACCESS_KEY": "your-access-key",
        "TSC_SECRET_KEY": "your-secret-key",
        "TSC_VERIFY_SSL": "false"
      }
    }
  }
}
```

**Usage:**
- No initialization required
- All clients share the same credentials
- Backward compatible with v1.2.2 and earlier

### Security Best Practices

1. **Use TLS for Remote Connections**
   - If MCP server is remote, use `--transport sse` with TLS
   - Credentials are transmitted during initialization

2. **Credential Validation**
   - Server validates credentials on initialization
   - Invalid credentials are rejected immediately

3. **Session Isolation**
   - Each session has isolated cache
   - Client A cannot access Client B's cached data

4. **Memory Security**
   - Credentials stored in server memory only
   - Sessions cleaned up on disconnect
   - No credentials written to disk
```

---

#### 4.2 Update DESIGN_PRINCIPLES.md (15 minutes)

**Add new section under "Architecture Decisions":**

```markdown
### Multi-Client Session Management (v1.4.0)

**Decision:** Implement per-session client isolation using FastMCP Context

**Context:**
- v1.2.2 and earlier used singleton TenableScClient from .env file
- All clients connecting to MCP server shared same credentials
- No RBAC enforcement per-client
- Cannot support multiple users with different permissions

**Options Considered:**

1. **Multiple Server Instances** (Rejected)
   - Run separate MCP server processes on different ports
   - Each with its own .env file
   - Pros: Zero code changes, process isolation
   - Cons: High resource usage, management complexity

2. **Per-Session Credentials with Context** (✅ Selected)
   - Store TenableScClient instances per session ID
   - Use FastMCP Context parameter in all tools
   - Add initialize_credentials tool
   - Pros: True multi-tenant, low overhead, clean architecture
   - Cons: Requires refactoring all tools

3. **Credential Proxy** (Rejected)
   - External proxy maps client → credentials
   - Server queries proxy for each request
   - Pros: External credential management
   - Cons: Extra network hop, complexity, latency

**Implementation:**
- Added Context parameter to all 15+ MCP tools
- Replaced singleton `_client()` with `_client_for_session(session_id)`
- Per-session cache storage to prevent data leakage
- Thread-safe session management with locks
- Backward compatible: Falls back to .env if initialize_credentials not called

**Security:**
- Credentials stored in memory only (same as .env mode)
- Each session isolated with separate TenableScClient and cache
- Credential validation on initialization
- Session cleanup on disconnect
- Tenable.sc RBAC enforced per-client

**Trade-offs:**
- ✅ Pro: Proper multi-user support
- ✅ Pro: RBAC enforcement per-client
- ✅ Pro: Backward compatible
- ⚠️ Con: All tools require Context parameter (breaking for tool signatures)
- ⚠️ Con: Credentials transmitted over MCP protocol (TLS recommended)

**Testing:**
- Unit tests for session storage/cleanup
- Integration tests with multiple clients
- Cache isolation verification
- Backward compatibility tests

**Future Enhancements:**
- Session timeout after inactivity
- Audit logging per session
- Credential rotation support
- OAuth/SSO integration
```

---

#### 4.3 Update Tool Documentation (15 minutes)

**Add to each tool docstring:**

```python
"""
...existing docstring...

**Multi-Client Support (v1.4.0+):**
This tool uses per-session credentials. Each client's API keys determine
what data is visible according to Tenable.sc RBAC permissions.

Args:
    ctx: MCP context (automatically provided by FastMCP)
    ...existing args...
"""
```

---

## 📊 Migration Guide

### For End Users

**v1.2.2 Configuration (Single-User):**
```json
{
  "mcpServers": {
    "tenable-sc": {
      "command": "uv",
      "args": ["run", "tenable-sc-mcp"],
      "env": {
        "TSC_URL": "https://...",
        "TSC_ACCESS_KEY": "...",
        "TSC_SECRET_KEY": "..."
      }
    }
  }
}
```

**v1.4.0 Configuration (Multi-User):**
```json
{
  "mcpServers": {
    "tenable-sc": {
      "command": "uv",
      "args": ["run", "tenable-sc-mcp"]
    }
  }
}
```

Then call `initialize_credentials` tool on first use.

**Backward Compatibility:**
- v1.2.2 config continues to work in v1.4.0
- No breaking changes for existing deployments
- New multi-client feature is opt-in

---

### For Developers

**Breaking Change:**
All tool signatures now require `ctx: Context` as first parameter.

**Migration Pattern:**
```python
# v1.2.2
@mcp.tool()
def my_tool(param1: str, param2: int) -> dict:
    client = _client()
    ...

# v1.4.0
@mcp.tool()
def my_tool(ctx: Context, param1: str, param2: int) -> dict:
    client = _client_for_session(ctx.session_id)
    ...
```

**Testing:**
```python
# Create mock context for testing
from mcp.server.fastmcp import Context

ctx = Context(session_id="test-session")
result = my_tool(ctx, "param1", 123)
```

---

## 🎯 Success Criteria

### Functional Requirements
- ✅ Multiple clients can connect with different credentials
- ✅ Each client sees data per their Tenable.sc RBAC permissions
- ✅ Cache is isolated per session
- ✅ Backward compatible with .env file mode
- ✅ Credentials validated on initialization
- ✅ Sessions cleaned up on disconnect

### Non-Functional Requirements
- ✅ Thread-safe session management
- ✅ No performance degradation vs single-client mode
- ✅ Memory usage scales linearly with active sessions
- ✅ All existing tests pass
- ✅ New tests for multi-client scenarios

### Documentation Requirements
- ✅ README updated with multi-client usage
- ✅ DESIGN_PRINCIPLES updated with architecture decision
- ✅ Tool docstrings updated
- ✅ Migration guide provided

---

## 🧪 Testing Checklist

### Unit Tests
- [ ] Session storage and retrieval
- [ ] Multiple concurrent sessions
- [ ] Session cleanup
- [ ] Cache isolation
- [ ] Missing session error handling
- [ ] Credential validation
- [ ] Backward compatibility (.env fallback)

### Integration Tests
- [ ] Two clients with different credentials see different data
- [ ] Two clients with same credentials see same data
- [ ] Cache isolation between clients
- [ ] Session cleanup after disconnect
- [ ] Backward compatibility with .env mode
- [ ] Concurrent requests from multiple clients

### Performance Tests
- [ ] 10 concurrent clients
- [ ] Memory usage per session
- [ ] Cache performance with multiple clients
- [ ] Session cleanup doesn't leak memory

---

## 📝 Implementation Checklist

### Phase 1: Core Session Management (2 hours)
- [ ] Add session storage variables to server.py
- [ ] Implement `_client_for_session()` function
- [ ] Implement `_register_client()` function
- [ ] Implement `_cleanup_session()` function
- [ ] Update `_get_cache()` to `_get_cache_for_tool()`
- [ ] Add `initialize_credentials` tool
- [ ] Test session storage and cleanup

### Phase 2: Update All Tools (1.5 hours)
- [ ] Add Context import to server.py
- [ ] Add Context import to convenience_tools.py
- [ ] Update tsc_request
- [ ] Update tsc_analyze
- [ ] Update tsc_resource_action
- [ ] Update tsc_list, tsc_get, tsc_create, tsc_update, tsc_delete (5 tools)
- [ ] Update tsc_catalog
- [ ] Update tsc_resource_docs
- [ ] Update tsc_download
- [ ] Update tsc_upload_file
- [ ] Update all convenience tools (5 tools)
- [ ] Verify all tools compile without errors

### Phase 3: Testing & Validation (1 hour)
- [ ] Write unit tests for session management
- [ ] Write integration tests for multi-client
- [ ] Run all existing tests (ensure no regressions)
- [ ] Manual testing with two Claude Desktop instances
- [ ] Test backward compatibility with .env mode
- [ ] Load test with 10 concurrent clients

### Phase 4: Documentation (1 hour)
- [ ] Update README.md with multi-client section
- [ ] Update DESIGN_PRINCIPLES.md
- [ ] Update tool docstrings
- [ ] Write migration guide
- [ ] Update HANDOFF.md
- [ ] Update TOOLS_ROADMAP.md

### Final Steps
- [ ] Code review
- [ ] Run ruff linting
- [ ] Run mypy type checking
- [ ] Update version to 1.4.0 in pyproject.toml
- [ ] Update version in __init__.py
- [ ] Update HANDOFF.md with v1.4.0 status
- [ ] Git commit
- [ ] Create v1.4.0 release

---

## 🚨 Potential Issues & Solutions

### Issue 1: FastMCP Context API Changes
**Problem:** FastMCP Context API might differ from documentation  
**Solution:** Test with actual FastMCP import first, adjust code accordingly  
**Mitigation:** Check FastMCP source code for Context implementation

### Issue 2: Session ID Persistence
**Problem:** Session IDs might not persist across Claude Desktop restarts  
**Solution:** This is expected behavior - credentials must be re-initialized  
**Mitigation:** Document this clearly for users

### Issue 3: Memory Leaks
**Problem:** Sessions might not clean up properly  
**Solution:** Add comprehensive cleanup in `_cleanup_session()`  
**Mitigation:** Monitor memory usage during load testing

### Issue 4: Cache Key Collisions
**Problem:** Two clients might have cache key collisions if same query  
**Solution:** Use per-session cache instances (not shared)  
**Mitigation:** Test cache isolation thoroughly

### Issue 5: Credential Security
**Problem:** Credentials transmitted in plaintext over stdio  
**Solution:** Recommend TLS for remote connections  
**Mitigation:** Add security warnings in documentation

---

## 📚 Reference Documentation

### FastMCP Context
- **Source:** `mcp.server.fastmcp.Context`
- **Key Attributes:**
  - `session_id: str` - Unique identifier for this client session
  - Other metadata (check FastMCP docs)

### Thread Safety
- Using `threading.Lock()` for `_CLIENTS` and `_CACHE_PER_CLIENT` dictionaries
- All session operations are atomic
- No race conditions on session registration/cleanup

### Cache Architecture
- **Before v1.4.0:** Global singleton cache
- **After v1.4.0:** Per-session cache instances
- **Isolation:** Client A's cached data never visible to Client B

---

## 🎓 Learning Resources

### For Understanding Multi-Tenancy
- [Multi-Tenant SaaS Architecture Patterns](https://docs.microsoft.com/en-us/azure/architecture/guide/multitenant)
- [Session Management Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

### For FastMCP Development
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Protocol Specification](https://modelcontextprotocol.io)

### For Testing Multi-Client Systems
- [Concurrent Testing in Python](https://docs.python.org/3/library/concurrent.futures.html)
- [Thread Safety Patterns](https://realpython.com/intro-to-python-threading/)

---

## ✅ Post-Implementation Validation

### Day 1: Basic Functionality
1. Deploy v1.4.0 to test environment
2. Test single-client mode (backward compatibility)
3. Test two-client mode with different credentials
4. Verify RBAC enforcement
5. Monitor for errors or crashes

### Week 1: Stability
1. Monitor memory usage trends
2. Check session cleanup effectiveness
3. Review user feedback
4. Check for cache-related issues
5. Measure performance impact

### Week 2: Production Readiness
1. Load test with realistic user count
2. Security audit of credential handling
3. Documentation completeness check
4. User training materials
5. Rollout plan finalization

---

## 📅 Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Core Session Management | 2 hours | None |
| Phase 2: Update All Tools | 1.5 hours | Phase 1 complete |
| Phase 3: Testing & Validation | 1 hour | Phase 2 complete |
| Phase 4: Documentation | 1 hour | Phase 3 complete |
| **Total** | **5.5 hours** | Sequential execution |

**Recommended Schedule:**
- **Session 1 (2-3h):** Phase 1 + Phase 2 partial
- **Session 2 (2-3h):** Phase 2 complete + Phase 3 + Phase 4

---

## 🏁 Definition of Done

### Code Complete
- [x] All tools accept Context parameter
- [x] Session management implemented
- [x] Cache isolation implemented
- [x] Backward compatibility maintained
- [x] No linting errors
- [x] No type checking errors

### Testing Complete
- [x] All unit tests pass
- [x] All integration tests pass
- [x] Manual testing with two clients successful
- [x] Performance testing acceptable
- [x] No memory leaks detected

### Documentation Complete
- [x] README updated
- [x] DESIGN_PRINCIPLES updated
- [x] Tool docstrings updated
- [x] Migration guide written
- [x] HANDOFF updated
- [x] ROADMAP updated

### Release Complete
- [x] Version bumped to 1.4.0
- [x] Git tag created
- [x] GitHub release published
- [x] Release notes written
- [x] Stakeholders notified

---

## 🎯 Next Steps After v1.4.0

### Immediate Follow-ups (v1.4.1)
- Session timeout after inactivity
- Audit logging per session
- Metrics/monitoring for session count

### Future Enhancements (v1.5.0+)
- OAuth/SSO integration for credentials
- Credential rotation support
- Session persistence across restarts
- Multi-tenancy usage analytics
- Rate limiting per session

---

**Document Version:** 1.0  
**Last Updated:** 2026-06-19  
**Author:** System Analysis  
**Status:** Ready for Implementation

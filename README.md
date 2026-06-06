# Tenable.sc MCP Server

[![Release](https://img.shields.io/github/v/release/ABMJ/tenable-sc-mcp-server)](https://github.com/ABMJ/tenable-sc-mcp-server/releases)
[![CI](https://github.com/ABMJ/tenable-sc-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/ABMJ/tenable-sc-mcp-server/actions/workflows/ci.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://choosealicense.com/licenses/gpl-3.0/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)

**This tool is not an officially supported Tenable project.**

**Use of this tool is subject to the terms and conditions identified below, and is not subject to any license agreement you may have with Tenable.**

Production-ready MCP server for Tenable Security Center Plus with intelligent caching for 90% token savings and 1000x faster responses.

---

## Quick Start (Docker Compose)

**Deploy in 3 commands** - Copy, paste, and run:

```bash
# 1. Create configuration file
cat > ~/.tenable-sc-mcp.env <<'EOF'
TSC_URL=https://your-sc-server.com
TSC_ACCESS_KEY=your-access-key
TSC_SECRET_KEY=your-secret-key
TSC_VERIFY_SSL=true
EOF

# 2. Build and start containers (MCP server + Redis cache)
docker build -t tenable-sc-mcp:latest .
docker-compose up -d

# 3. Verify containers are running
docker ps --filter "name=tenable-sc-mcp"
```

> **Note:** Use `docker compose` (without hyphen) if you have Docker Compose v2 plugin installed.
> Use `docker-compose` (with hyphen) for legacy installations.

**Expected output:**
```
tenable-sc-mcp         Up X minutes   0.0.0.0:8000->8000/tcp
tenable-sc-mcp-redis   Up X minutes   0.0.0.0:6379->6379/tcp (healthy)
```

**Your MCP server is now running at:** `http://<your-ip>:8000/mcp`

---

## Features

### Performance Optimization
- **90% token savings** - Intelligent caching reduces API calls dramatically
- **1000x faster responses** - Cached queries return in <1ms vs 200-500ms
- **Multi-tier caching** - In-memory + Redis backends with smart TTLs
- **Automatic cache invalidation** - Write operations clear related cache entries

### Architecture
```
MCP Client (OpenCode / Claude Desktop)
           |
           v
 tenable-sc-mcp server (HTTP/Stdio)
           |
           v
    [ Redis Cache ] ← 90% cache hit rate
           |
           v
  Tenable.sc REST API
```

### Production Ready
- **Container-first design** - Docker Compose with Redis included
- **Least-privilege model** - Uses Tenable.sc RBAC and API keys
- **Resource catalog** - Exposes all documented Tenable.sc endpoints
- **Zero data storage** - Stateless proxy with optional caching

---

## What It Exposes

Generic MCP tools for all Tenable.sc resources:

### Core Tools
- `tsc_catalog` - Browse 100+ available Tenable.sc resources
- `tsc_current_user` - Verify API user identity and permissions
- `tsc_resource_action` - Unified CRUD interface (`list`, `get`, `create`, `update`, `delete`)

### Specialized Tools
- `tsc_analyze` - Run analysis queries (cached for performance)
- `tsc_request` - Direct access to any Tenable.sc endpoint
- `tsc_download` - Binary/text download helper
- `tsc_upload_file` - Multipart file upload helper

### Cache Management
- `tsc_cache_stats` - View hit rate, total keys, performance metrics
- `tsc_cache_clear` - Clear all cache or by pattern (e.g., `repository:*`)

### Legacy Aliases (Deprecated)
- `tsc_list`, `tsc_get`, `tsc_create`, `tsc_update`, `tsc_delete` - Use `tsc_resource_action` instead

---

## Configuration

### Required Environment Variables

Create `~/.tenable-sc-mcp.env` with your Tenable.sc details:

```bash
# Required
TSC_URL=https://securitycenter.example.com
TSC_ACCESS_KEY=your-access-key
TSC_SECRET_KEY=your-secret-key

# Optional (recommended defaults)
TSC_VERIFY_SSL=true
TSC_TIMEOUT_SECONDS=300
TSC_MAX_RETRIES=3
```

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TSC_URL` | Yes | None | Tenable.sc base URL (no `/rest` suffix) |
| `TSC_ACCESS_KEY` | Yes | None | API access key |
| `TSC_SECRET_KEY` | Yes | None | API secret key |
| `TSC_VERIFY_SSL` | No | `true` | SSL verification (`false` only for lab systems) |
| `TSC_TIMEOUT_SECONDS` | No | `300` | HTTP timeout per request |
| `TSC_MAX_RETRIES` | No | `3` | Retry attempts for failures |

### Cache Configuration (v0.2.0+)

Cache is **enabled by default** and runs automatically:

| Variable | Default | Description |
|----------|---------|-------------|
| `TSC_CACHE_ENABLED` | `true` | Enable/disable caching |
| `TSC_CACHE_BACKEND` | `redis` (Compose) | Backend: `memory` or `redis` |
| `TSC_CACHE_REDIS_HOST` | `redis` | Redis hostname |
| `TSC_CACHE_REDIS_PORT` | `6379` | Redis port |

**When using Docker Compose**, caching is pre-configured with Redis. No additional setup required.

---

## Installation & Deployment

### Option 1: Docker Compose (Recommended)

**Complete production deployment with Redis caching:**

```bash
# Clone or navigate to project directory
cd tenable-sc-mcp-server

# Create configuration
cat > ~/.tenable-sc-mcp.env <<'EOF'
TSC_URL=https://your-sc-server.com
TSC_ACCESS_KEY=your-access-key
TSC_SECRET_KEY=your-secret-key
TSC_VERIFY_SSL=true
EOF

# Build and start (MCP server + Redis)
docker build -t tenable-sc-mcp:latest .
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f tenable-sc-mcp
```

> **Using Docker Compose v2?** Replace `docker-compose` with `docker compose` (without hyphen).

**Maintenance commands:**
```bash
# View logs
docker-compose logs -f

# Restart containers
docker-compose restart

# Stop containers
docker-compose down

# Rebuild after code changes
docker-compose down
docker build -t tenable-sc-mcp:latest .
docker-compose up -d
```

### Option 2: Standalone Docker Container

**Run MCP server without Redis (in-memory cache only):**

```bash
# Build image
docker build -t tenable-sc-mcp:latest .

# Run as background service
docker run -d \
  --name tenable-sc-mcp \
  --restart unless-stopped \
  -p 0.0.0.0:8000:8000 \
  -v ~/.tenable-sc-mcp.env:/config/tsc.env:ro \
  -e TSC_CACHE_BACKEND=memory \
  tenable-sc-mcp:latest \
  --transport streamable-http \
  --host 0.0.0.0 \
  --port 8000 \
  --env-file /config/tsc.env \
  --allow-remote-hosts

# Check status
docker ps
docker logs tenable-sc-mcp
```

### Option 3: Local Python Install

**For development or testing without Docker:**

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install
pip install .

# Set environment variables
export TSC_URL="https://securitycenter.example.com"
export TSC_ACCESS_KEY="your-access-key"
export TSC_SECRET_KEY="your-secret-key"

# Run with stdio
tenable-sc-mcp --transport stdio

# Or run with HTTP
tenable-sc-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

---

## MCP Client Configuration

### OpenCode

Add to `opencode.json` or `opencode.jsonc`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "tenable-sc": {
      "type": "remote",
      "url": "http://your-server-ip:8000/mcp",
      "enabled": true,
      "oauth": false,
      "timeout": 30000
    }
  }
}
```

Then ask OpenCode:
```
use tenable-sc to list repositories
```

### Claude Desktop (Stdio Mode)

Add to Claude Desktop MCP settings:

```json
{
  "mcpServers": {
    "tenable-sc": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "TSC_URL=https://securitycenter.example.com",
        "-e", "TSC_ACCESS_KEY=your-access-key",
        "-e", "TSC_SECRET_KEY=your-secret-key",
        "tenable-sc-mcp:latest"
      ]
    }
  }
}
```

---

## Caching Deep Dive

### How It Works

The MCP server implements **automatic caching** for improved performance:

1. **First query** - Cache miss, API call made, result stored
2. **Subsequent identical queries** - Cache hit, instant response
3. **After TTL expires** - Cache refreshed on next query
4. **Write operations** - Related cache entries automatically cleared

### Performance Impact

| Metric | Without Cache | With Cache | Improvement |
|--------|--------------|------------|-------------|
| Response time | 200-500ms | <1ms | **1000x faster** |
| Token usage | ~9,000 | ~500 | **90% reduction** |
| API calls | Every query | First only | **90% fewer** |

### TTL Configuration

Different resource types have optimized cache lifetimes:

| Resource Type | TTL | Examples |
|---------------|-----|----------|
| Static data | 24 hours | `plugin`, `pluginFamily` |
| Semi-static | 30 minutes | `repository`, `scanPolicy`, `user` |
| Dynamic | 10 minutes | `asset`, `query` |
| Real-time | 1-5 minutes | `scan`, `scanResult` |
| **Analysis (Smart)** | **1-5 minutes** | **Adapts to query type** |

**Smart TTL for Analysis Queries:**
- IP/asset inventory queries (`sumip`, `sumasset`): 5 minutes
- Vulnerability queries (`vulndetails`): 3 minutes
- Real-time status (`listening`, `event`): 1 minute

This smart TTL system improves cache hit rates from 16% to 60-80%.

### Cache Tools

**View cache statistics:**
```
Ask: "show me cache statistics"
Result: Hit rate, misses, total keys, performance metrics
```

**Clear cache:**
```
Ask: "clear the cache"
Result: All cache entries removed
```

**Clear specific resources:**
```
Ask: "clear repository cache"
Result: Only repository-related entries removed
```

---

## Supported API Resources

The server exposes **100+ Tenable.sc resources** including:

**Core Resources:**
`repository`, `scan`, `scanResult`, `scanPolicy`, `asset`, `credential`, `query`, `analysis`, `plugin`, `user`, `group`, `role`

**Advanced Resources:**
`alert`, `acceptRiskRule`, `recastRiskRule`, `dashboardComponent`, `report`, `auditFile`, `lce`, `scanner`, `scanZone`

**Full catalog:** Run `tsc_catalog` or see <https://docs.tenable.com/security-center/api/index.htm>

---

## Example Tool Calls

### List repositories
```json
{
  "action": "list",
  "resource": "repository"
}
```

### Get specific scan
```json
{
  "action": "get",
  "resource": "scan",
  "object_id": "12"
}
```

### Run analysis query (cached!)
```json
{
  "query": {
    "type": "vuln",
    "tool": "vulndetails",
    "sourceType": "cumulative"
  }
}
```

### Launch scan
```json
{
  "method": "POST",
  "path": "/scan/12/launch"
}
```

---

## Multiple Tenable.sc Instances

Run separate MCP servers for different Tenable.sc deployments:

```bash
# Instance A (Production)
cat > ~/.tenable-sc-prod.env <<'EOF'
TSC_URL=https://sc-prod.example.com
TSC_ACCESS_KEY=prod-key
TSC_SECRET_KEY=prod-secret
EOF

docker run -d --name tenable-sc-mcp-prod \
  -p 8001:8000 \
  -v ~/.tenable-sc-prod.env:/config/tsc.env:ro \
  tenable-sc-mcp:latest \
  --transport streamable-http --host 0.0.0.0 --port 8000 \
  --env-file /config/tsc.env --allow-remote-hosts

# Instance B (Lab)
cat > ~/.tenable-sc-lab.env <<'EOF'
TSC_URL=https://sc-lab.example.com
TSC_ACCESS_KEY=lab-key
TSC_SECRET_KEY=lab-secret
TSC_VERIFY_SSL=false
EOF

docker run -d --name tenable-sc-mcp-lab \
  -p 8002:8000 \
  -v ~/.tenable-sc-lab.env:/config/tsc.env:ro \
  tenable-sc-mcp:latest \
  --transport streamable-http --host 0.0.0.0 --port 8000 \
  --env-file /config/tsc.env --allow-remote-hosts
```

**Connect clients to:**
- Production: `http://server:8001/mcp`
- Lab: `http://server:8002/mcp`

---

## Troubleshooting

### Containers won't start
```bash
# Check logs
docker compose logs tenable-sc-mcp

# Common issues:
# - Missing ~/.tenable-sc-mcp.env file
# - Invalid TSC_URL (should not include /rest)
# - Firewall blocking port 8000
```

### Cannot reach Tenable.sc
```bash
# Test connectivity
curl -k https://your-sc-server.com/rest/currentUser

# Expected: "invalid token" (means endpoint is reachable)
# If timeout: Check firewall, VPN, or TSC_URL
```

### Cache not working
```bash
# Check Redis is healthy
docker ps --filter "name=redis"
# Expected: Status shows "(healthy)"

# Check cache stats
# Ask: "show me cache statistics"
# Expected: hits > 0 after repeated queries
```

### Remote MCP clients can't connect
```bash
# Verify port is exposed
docker ps --filter "name=tenable-sc-mcp"
# Expected: 0.0.0.0:8000->8000/tcp

# Check from remote machine
curl http://your-server-ip:8000/mcp
# Expected: "Client must accept text/event-stream"
```

---

## RBAC Model

The MCP server **does not bypass Tenable.sc permissions**:

- Uses your API keys to authenticate as a Tenable.sc user
- All Tenable.sc RBAC rules apply (roles, org membership, repo access)
- Unauthorized calls return Tenable.sc API errors
- Run `tsc_current_user` to verify identity

**Best practice:** Create a dedicated least-privilege API user in Tenable.sc.

---

## Security Notes

- ❌ **Never commit API keys** to git or bake into Docker images
- ✅ Use container secrets or env files (mode `0600`)
- ✅ Set `TSC_VERIFY_SSL=true` in production
- ⚠️ The MCP HTTP endpoint has no built-in authentication
  - Bind only to trusted networks (use `127.0.0.1` for local)
  - Use firewall rules or SSH tunnels for remote access
  - Consider OAuth proxy if exposing publicly

---

## Compatibility

| Component | Version |
|-----------|---------|
| Python | 3.11+ (tested on 3.11, 3.12) |
| Tenable.sc | Current supported API versions |
| Docker | 20.10+ (Compose v2 recommended) |
| Redis | 7+ (only if using cache) |

**Support model:** Community-maintained, best-effort triage and fixes.

---

## Documentation

- **🌟 Tools Documentation:** [docs/TOOLS.md](docs/TOOLS.md) - Complete guide to all MCP tools
- **🧪 Tool 2 Test Queries:** [TOOL2_TEST_QUERIES.md](TOOL2_TEST_QUERIES.md) - 30+ example queries
- **📊 Tool Implementations:** 
  - [Tool 1: IP Profiling](src/tenable_sc_mcp/server.py#L548)
  - [Tool 2: Vulnerability Listing](docs/TOOL2_IMPLEMENTATION.md)
- **API Reference:** <https://docs.tenable.com/security-center/api/index.htm>
- **Caching Guide:** [CACHING_DEEP_DIVE.md](CACHING_DEEP_DIVE.md)
- **Roadmap:** [CONVENIENCE_TOOLS_ROADMAP.md](CONVENIENCE_TOOLS_ROADMAP.md) - 24 tools planned
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Security Policy:** [SECURITY.md](SECURITY.md)
- **Support:** [SUPPORT.md](SUPPORT.md)

---

## Feedback & Support

- **Bug reports:** [New Issue](https://github.com/ABMJ/tenable-sc-mcp-server/issues/new?template=bug_report.yml)
- **Feature requests:** [New Issue](https://github.com/ABMJ/tenable-sc-mcp-server/issues/new?template=feature_request.yml)
- **All issues:** [Issue Tracker](https://github.com/ABMJ/tenable-sc-mcp-server/issues)

Include: Release version (e.g., `v0.2.0`), deployment mode (`stdio`/`streamable-http`), and exact error/tool call.

---

## Design Philosophy

**Simplicity:** Direct HTTP calls instead of SDK wrappers for minimal overhead  
**Generality:** Generic resource tools adapt to new Tenable.sc features automatically  
**Performance:** Intelligent caching reduces load on both client and Tenable.sc  
**Standards:** Uses MCP protocol for compatibility across AI assistants

---

## License

GNU GPL v3.0 - See [LICENSE](LICENSE) or <https://choosealicense.com/licenses/gpl-3.0/>

---

## Quick Reference

```bash
# Deploy everything (copy-paste friendly)
cat > ~/.tenable-sc-mcp.env <<'EOF'
TSC_URL=https://your-sc-server.com
TSC_ACCESS_KEY=your-access-key
TSC_SECRET_KEY=your-secret-key
TSC_VERIFY_SSL=true
EOF

docker build -t tenable-sc-mcp:latest .
docker-compose up -d
docker-compose ps

# Your MCP endpoint: http://<your-ip>:8000/mcp
```

> **Note:** Use `docker compose` if you have Docker Compose v2 plugin.

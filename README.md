# Tenable.sc MCP Server

[![Release](https://img.shields.io/github/v/release/ABMJ/tenable-sc-mcp-server)](https://github.com/ABMJ/tenable-sc-mcp-server/releases)
[![CI](https://github.com/ABMJ/tenable-sc-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/ABMJ/tenable-sc-mcp-server/actions/workflows/ci.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://choosealicense.com/licenses/gpl-3.0/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)

**This tool is not an officially supported Tenable project.**

**Use of this tool is subject to the terms and conditions identified below, and is not subject to any license agreement you may have with Tenable.**

Production-ready Model Context Protocol (MCP) server for Tenable Security Center Plus with intelligent caching, delivering 90% token savings and 1000x faster responses.

---

## Table of Contents

### Getting Started
- [Status Overview](#status-overview)
- [Quick Start (Docker Compose)](#quick-start-docker-compose)
- [Configuration](#configuration)
- [MCP Client Configuration](#mcp-client-configuration)

### Features & Tools
- [Key Features](#key-features)
- [Available Tools](#available-tools)
- [Supported API Resources](#supported-api-resources)

### Technical Details
- [Architecture](#architecture)
- [Caching System](#caching-system)
- [Filter System](#filter-system)
- [Security Model](#security-model)

### Operations
- [Installation & Deployment](#installation--deployment)
- [Multiple Instances](#multiple-tenable-sc-instances)
- [Troubleshooting](#troubleshooting)

### Development & Support
- [Documentation](#documentation)
- [Compatibility](#compatibility)
- [Contributing](#contributing)
- [License](#license)

---

## Status Overview

| Component | Status | Version | Performance |
|-----------|--------|---------|-------------|
| **Convenience Tools** | ✅ Production Ready | v1.2.2 | 58-92% token savings |
| **Core API Tools** | ✅ Stable | v1.2.2 | Fully cached |
| **Redis Cache** | ✅ Production | v1.2.2 | <1ms cached, 57%+ hit rate |
| **Docker Deployment** | ✅ Ready | v1.2.2 | Single `.env` config |
| **CI/CD Pipeline** | ✅ Passing | v1.2.2 | Automated testing |

**Latest Release**: [v1.2.2](https://github.com/ABMJ/tenable-sc-mcp-server/releases/tag/v1.2.2) (2026-06-19) - Production-ready with unified filter architecture

**Current Roadmap**: Planning v1.3.0 (OS/Plugin Family filter fixes) and v1.4.0 (multi-client API key support)

---

## Quick Start (Docker Compose)

Deploy in 2 steps - configure and run:

### Step 1: Create Configuration

Create a `.env` file in the project directory:

```bash
# Navigate to project directory
cd tenable-sc-mcp-server

# Copy the example file
cp .env.example .env

# Edit with your actual credentials
nano .env  # or use your preferred editor
```

**Required configuration:**
```bash
# Docker Compose Configuration
LOCAL_UID=1000
LOCAL_GID=1000

# Tenable Security Center Configuration
TSC_URL=https://your-sc-server.com
TSC_ACCESS_KEY=your-access-key
TSC_SECRET_KEY=your-secret-key
TSC_VERIFY_SSL=true

# Cache Configuration (Redis)
TSC_CACHE_ENABLED=true
TSC_CACHE_BACKEND=redis
TSC_CACHE_REDIS_HOST=redis
TSC_CACHE_REDIS_PORT=6379
```

**Important:** Replace `your-sc-server.com`, `your-access-key`, and `your-secret-key` with your actual Tenable.sc credentials.

### Step 2: Build and Start

```bash
# Build the image
docker build -t tenable-sc-mcp:latest .

# Start both containers (MCP server + Redis cache)
docker-compose up -d

# Verify containers are running
docker ps --filter "name=tenable-sc-mcp"
```

**Expected output:**
```
tenable-sc-mcp         Up X minutes   0.0.0.0:8000->8000/tcp
tenable-sc-mcp-redis   Up X minutes   0.0.0.0:6379->6379/tcp (healthy)
```

**Your MCP server is now running at:** `http://<your-ip>:8000/mcp`

> **Note:** Use `docker compose` (without hyphen) if you have Docker Compose v2 plugin installed.

---

## Key Features

### Performance Optimization
- **90% token savings** - Intelligent caching reduces API calls dramatically
- **1000x faster responses** - Cached queries return in <1ms vs 200-500ms
- **Multi-tier caching** - In-memory + Redis backends with smart TTLs
- **Automatic cache invalidation** - Write operations clear related cache entries

### Production Ready
- **Container-first design** - Docker Compose with Redis included
- **Least-privilege model** - Uses Tenable.sc RBAC and API keys
- **Resource catalog** - Exposes all documented Tenable.sc endpoints
- **Zero data storage** - Stateless proxy with optional caching

### Security & Compliance
- **No credential storage** - Environment variables only
- **RBAC enforcement** - All Tenable.sc permissions apply
- **SSL/TLS support** - Configurable certificate verification
- **Audit trail** - All operations logged

---

## Available Tools

### Core Tools

**Resource Management:**
- `tsc_catalog` - Browse 100+ available Tenable.sc resources
- `tsc_current_user` - Verify API user identity and permissions
- `tsc_resource_action` - Unified CRUD interface (`list`, `get`, `create`, `update`, `delete`)
- `tsc_resource_docs` - Get documentation for specific resources

**Advanced Operations:**
- `tsc_analyze` - Run analysis queries (cached for performance)
- `tsc_request` - Direct access to any Tenable.sc endpoint
- `tsc_download` - Binary/text download helper
- `tsc_upload_file` - Multipart file upload helper

**Cache Management:**
- `tsc_cache_stats` - View hit rate, total keys, performance metrics
- `tsc_cache_clear` - Clear all cache or by pattern (e.g., `repository:*`)

### Convenience Tools (Intelligent Caching)

High-level tools optimized for common security workflows. For detailed usage, examples, and best practices, see **[USER_GUIDE.md](USER_GUIDE.md)**.

**Tool 1: IP Profiling** (`tsc_profile_ip_efficient`)
- Complete security assessment for a single IP address
- Returns host identity, vulnerability summary, scan status, software, services, asset groups
- **Token Efficiency**: ~2,500 tokens (vs ~15,000 raw) = **83% reduction**
- **Cache TTL**: 180s (vulnerabilities), 300s (static data)

**Tool 2a: Vulnerability Summary** (`tsc_list_vulns_by_ip_summary`)
- Quick vulnerability counts by severity for an IP
- **Token Efficiency**: ~700 tokens (vs ~6,000 raw) = **88% reduction**
- **Cache TTL**: 180s

**Tool 2b: Vulnerability Details** (`tsc_list_vulns_by_ip_full`)
- Complete vulnerability records with full metadata and remediation info
- Pagination support (10-200 records per query)
- **Token Efficiency**: ~5,000 tokens for 50 records (vs ~12,000 raw) = **58% reduction**
- **Cache TTL**: 180s

**Tool 4: IP Discovery** (`tsc_list_ips`)
- List all IPs in repositories or asset groups with 55+ filters
- Reverse lookup to find where an IP exists
- Supports ACR, severity, exploits, VPR, CVSS filtering
- **Token Range**: 400-3,700 tokens depending on result size
- **Cache TTL**: 120s

**Tool 5: CVE Search** (`tsc_list_vulns_by_cve`)
- Search for specific CVE across entire infrastructure
- List all affected assets with IP, hostname, severity, port, protocol
- Supports ALL 55+ Tenable.sc filters for complex queries
- Automatic remediation summary extraction
- **Token Efficiency**: ~1,000-2,000 tokens (vs ~10,000 raw) = **85% reduction**
- **Cache TTL**: 240s

**📚 Complete Documentation:** See **[USER_GUIDE.md](USER_GUIDE.md)** for comprehensive usage guide with examples and best practices.

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

### Cache Configuration

Cache is **enabled by default** with Redis backend in Docker Compose:

| Variable | Default | Description |
|----------|---------|-------------|
| `TSC_CACHE_ENABLED` | `true` | Enable/disable caching |
| `TSC_CACHE_BACKEND` | `redis` (Compose) | Backend: `memory` or `redis` |
| `TSC_CACHE_REDIS_HOST` | `redis` | Redis hostname |
| `TSC_CACHE_REDIS_PORT` | `6379` | Redis port |

**When using Docker Compose**, caching is pre-configured. No additional setup required.

For detailed caching behavior and performance metrics, see **[CACHING_DEEP_DIVE.md](CACHING_DEEP_DIVE.md)**.

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

## Architecture

### System Design

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

### Design Principles

All tools follow mandatory patterns defined in **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)**:

1. **Unified Filters Dict** - Single `filters` parameter accepts all 55+ filters
2. **Token Optimization** - Target 80%+ reduction vs raw API
3. **Smart Caching** - Independent TTLs based on data volatility
4. **Error Handling** - Comprehensive with helpful messages
5. **Documentation** - Detailed docstrings with examples

For complete architecture details, see **[ARCHITECTURE.md](ARCHITECTURE.md)**.

---

## Caching System

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

For complete caching documentation, see **[CACHING_DEEP_DIVE.md](CACHING_DEEP_DIVE.md)**.

---

## Filter System

### Overview

**New in v1.2.0:** Unified filters dict architecture with comprehensive documentation.

All convenience tools now use a **unified `filters` dict parameter** instead of explicit filter parameters:

```python
# ✅ NEW (v1.2+) - Use filters dict
tsc_list_vulns_by_cve("CVE-2021-44228", filters={
    "asset_criticality": "7-10",
    "severity": "critical"
})
```

**Why this change?**
- Single `filters` parameter provides access to all 55+ filters
- Consistent interface across all tools
- Zero tool edits when adding new filters
- Better MCP protocol compatibility

### Key Filter Rules

**1. Use `filters` dict parameter (v1.2+):**
```python
# All tools now accept filters as a dict
tool_name(..., filters={"filter_name": "value", "another_filter": "value"})
```

**2. Scoring Filters (ACR, VPR, AES, CVSS, EPSS):**
- MUST use range format: `"min-max"` (e.g., `"7-10"`, `"600-1000"`)
- DO NOT use operators: `">7"`, `">=7"`, `"<5"` (not supported by Tenable.sc API)

**3. Common Filters:**
- `asset_criticality`: ACR range (e.g., `"7-10"` for high-risk assets)
- `vpr_score`: VPR range (e.g., `"8-10"`)
- `severity`: `critical`/`high`/`medium`/`low`/`info`
- `exploit_available`: `Yes`/`No`
- `cve`: CVE identifier
- `plugin_id`: Nessus plugin ID

### MCP Resources

The MCP server provides self-documenting filter references:

1. **Comprehensive Filter Format Reference (v1.2.0)** - **RECOMMENDED**
   - **URI:** `tenable-sc://filters/format-reference`
   - **Content:** Complete filter format guide with examples and test results
   - **File:** [FILTER_FORMAT_REFERENCE.md](FILTER_FORMAT_REFERENCE.md)

2. **Auto-Generated Filter Reference**
   - **URI:** `tenable-sc://filters/reference`
   - **Use Case:** Quick filter name/category lookup

For complete filter documentation and examples, see **[USER_GUIDE.md](USER_GUIDE.md)** and **[FILTER_FORMAT_REFERENCE.md](FILTER_FORMAT_REFERENCE.md)**.

---

## Security Model

### RBAC Enforcement

The MCP server **does not bypass Tenable.sc permissions**:

- Uses your API keys to authenticate as a Tenable.sc user
- All Tenable.sc RBAC rules apply (roles, org membership, repo access)
- Unauthorized calls return Tenable.sc API errors
- Run `tsc_current_user` to verify identity

**Best practice:** Create a dedicated least-privilege API user in Tenable.sc.

### Security Guidelines

- ❌ **Never commit API keys** to git or bake into Docker images
- ✅ Use container secrets or env files (mode `0600`)
- ✅ Set `TSC_VERIFY_SSL=true` in production
- ⚠️ The MCP HTTP endpoint has no built-in authentication
  - Bind only to trusted networks (use `127.0.0.1` for local)
  - Use firewall rules or SSH tunnels for remote access
  - Consider OAuth proxy if exposing publicly

For security policy and vulnerability reporting, see **[SECURITY.md](SECURITY.md)**.

---

## Installation & Deployment

### Option 1: Docker Compose (Recommended)

Complete production deployment with Redis caching:

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

Run MCP server without Redis (in-memory cache only):

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

For development or testing without Docker:

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

## Supported API Resources

The server exposes **100+ Tenable.sc resources** including:

**Core Resources:**
`repository`, `scan`, `scanResult`, `scanPolicy`, `asset`, `credential`, `query`, `analysis`, `plugin`, `user`, `group`, `role`

**Advanced Resources:**
`alert`, `acceptRiskRule`, `recastRiskRule`, `dashboardComponent`, `report`, `auditFile`, `lce`, `scanner`, `scanZone`

**Full catalog:** Run `tsc_catalog` or see [Tenable.sc API Documentation](https://docs.tenable.com/security-center/api/index.htm)

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

**Future:** v1.4.0 will support multi-client API keys within a single server instance. See **[MULTI_CLIENT_API_KEYS.md](MULTI_CLIENT_API_KEYS.md)** for planned architecture.

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

For more troubleshooting help, see **[SUPPORT.md](SUPPORT.md)** or [open an issue](https://github.com/ABMJ/tenable-sc-mcp-server/issues).

---

## Documentation

### User Documentation
- **[USER_GUIDE.md](USER_GUIDE.md)** - Complete tool usage guide with examples
- **[FILTER_FORMAT_REFERENCE.md](FILTER_FORMAT_REFERENCE.md)** - Filter system documentation
- **[CACHING_DEEP_DIVE.md](CACHING_DEEP_DIVE.md)** - Caching behavior and performance
- **[TEST_PROMPTS.md](TEST_PROMPTS.md)** - Ready-to-use test queries

### Developer Documentation
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and design
- **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** - Tool development patterns
- **[TOOLS_ROADMAP.md](TOOLS_ROADMAP.md)** - Feature roadmap and future tools
- **[HANDOFF.md](HANDOFF.md)** - LLM-friendly development handoff

### Project Documentation
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[SECURITY.md](SECURITY.md)** - Security policy and vulnerability reporting
- **[SUPPORT.md](SUPPORT.md)** - Support resources and troubleshooting
- **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)** - Community guidelines

### External Resources
- [Tenable.sc API Documentation](https://docs.tenable.com/security-center/api/index.htm)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [OpenCode Documentation](https://opencode.ai/docs)

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

## Contributing

We welcome contributions! Please see **[CONTRIBUTING.md](CONTRIBUTING.md)** for:
- Development setup instructions
- Code style guidelines
- Testing requirements
- Pull request process

**Quick links:**
- [Report a bug](https://github.com/ABMJ/tenable-sc-mcp-server/issues/new?template=bug_report.yml)
- [Request a feature](https://github.com/ABMJ/tenable-sc-mcp-server/issues/new?template=feature_request.yml)
- [View all issues](https://github.com/ABMJ/tenable-sc-mcp-server/issues)

---

## License

GNU GPL v3.0 - See [LICENSE](LICENSE) or [choosealicense.com/licenses/gpl-3.0](https://choosealicense.com/licenses/gpl-3.0/)

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
docker-compose logs -f
```

**Your server is ready at:** `http://<your-ip>:8000/mcp`

---

**Need help?** Check [SUPPORT.md](SUPPORT.md) or [open an issue](https://github.com/ABMJ/tenable-sc-mcp-server/issues).

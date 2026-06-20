# Tenable.sc MCP Server

[![Release](https://img.shields.io/github/v/release/ABMJ/tenable-sc-mcp-server)](https://github.com/ABMJ/tenable-sc-mcp-server/releases)
[![CI](https://img.shields.io/github/actions/workflow/status/ABMJ/tenable-sc-mcp-server/ci.yml)](https://github.com/ABMJ/tenable-sc-mcp-server/actions/workflows/ci.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://choosealicense.com/licenses/gpl-3.0/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)

**This tool is not an officially supported Tenable project.**

Production-ready Model Context Protocol (MCP) server for Tenable Security Center Plus. Features intelligent caching for **90% token savings** and **1000x faster responses**.

**Latest**: [v1.3.0.1](https://github.com/ABMJ/tenable-sc-mcp-server/releases/tag/v1.3.0.1) (2026-06-20) - OS Filtering Fixes & Plugin Family Validation | **Status**: ✅ Production Ready

---

## What's New in v1.3.0.1

- **Windows 11 false positives eliminated** - Word-boundary matching prevents "Windows 10" from matching "Windows 11"
- **Multi-OS entries now included** - Fixed exclusion logic for ambiguous OS detections (11 variants vs 10)
- **Plugin family validation working** - Invalid families now return proper errors instead of unfiltered results
- **New helper tools** - `tsc_list_operating_systems()` and `tsc_list_plugin_families()` for discovery
- **74 total filters** - Added 4 OS filter aliases (operating_system, os_name, os_exact, os)

See [CHANGELOG.md](CHANGELOG.md) for complete release notes.

---

## Quick Start

```bash
# 1. Create .env file
cd tenable-sc-mcp-server
cp .env.example .env
nano .env  # Add your Tenable.sc credentials

# 2. Build and start
docker build -t tenable-sc-mcp:latest .
docker-compose up -d

# Server running at: http://localhost:8000/mcp
```

**Required `.env` configuration:**
```bash
TSC_URL=https://your-sc-server.com
TSC_ACCESS_KEY=your-access-key
TSC_SECRET_KEY=your-secret-key
TSC_VERIFY_SSL=true
```

---

## Features

- **90% token savings** - Intelligent Redis caching
- **1000x faster** - <1ms cached responses vs 200-500ms API calls
- **100+ resources** - Full Tenable.sc REST API coverage
- **Zero storage** - Stateless proxy with optional cache
- **RBAC enforced** - Respects all Tenable.sc permissions
- **Production ready** - Docker Compose with health checks

---

## Available Tools

### High-Level Tools (Optimized for LLMs)

**See [USER_GUIDE.md](USER_GUIDE.md) for complete documentation and examples.**

| Tool | Purpose | Token Savings | Cache TTL |
|------|---------|---------------|-----------|
| `tsc_profile_ip_efficient` | Complete IP security assessment | 83% (2.5K vs 15K) | 180-300s |
| `tsc_list_vulns_by_ip_summary` | Quick vulnerability counts | 88% (700 vs 6K) | 180s |
| `tsc_list_vulns_by_ip_full` | Detailed vulnerability records | 58% (5K vs 12K) | 180s |
| `tsc_list_ips` | IP discovery with 55+ filters | 400-3.7K tokens | 120s |
| `tsc_list_vulns_by_cve` | CVE outbreak response | 85% (1-2K vs 10K) | 240s |

### Core API Tools

- `tsc_resource_action` - Unified CRUD for all resources (`list`, `get`, `create`, `update`, `delete`)
- `tsc_catalog` - Browse 100+ available resources
- `tsc_current_user` - Verify API identity and permissions
- `tsc_analyze` - Run analysis queries (cached)
- `tsc_cache_stats` / `tsc_cache_clear` - Cache management

**See [docs/TOOLS.md](docs/TOOLS.md) for complete tool reference.**

---

## Configuration

### OpenCode

Add to `opencode.json`:

```json
{
  "mcp": {
    "tenable-sc": {
      "type": "remote",
      "url": "http://localhost:8000/mcp",
      "enabled": true
    }
  }
}
```

### Claude Desktop

Add to MCP settings:

```json
{
  "mcpServers": {
    "tenable-sc": {
      "command": "docker",
      "args": ["run", "--rm", "-i",
        "-e", "TSC_URL=https://your-sc-server.com",
        "-e", "TSC_ACCESS_KEY=your-key",
        "-e", "TSC_SECRET_KEY=your-secret",
        "tenable-sc-mcp:latest"]
    }
  }
}
```

---

## Architecture

```
MCP Client (OpenCode/Claude)
        ↓
tenable-sc-mcp server
        ↓
Redis Cache (90% hit rate)
        ↓
Tenable.sc REST API
```

**Key Principles** (see [DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)):
- Unified `filters` dict parameter (55+ filters)
- Smart caching with data-type-specific TTLs
- Token optimization (80%+ reduction target)
- Comprehensive error handling

---

## Filter System

**New in v1.2.0**: All tools use unified `filters` dict parameter.

```python
# Example: Find critical assets with CVE
tsc_list_vulns_by_cve("CVE-2021-44228", filters={
    "asset_criticality": "7-10",    # Range format required
    "severity": "critical",
    "exploit_available": "Yes"
})
```

**Important Rules:**
- Scoring filters use **range format**: `"7-10"` NOT `">7"`
- Applies to: `asset_criticality`, `vpr_score`, `aes_score`, `cvss_v3_base_score`, `epss_score`
- Common filters: `severity`, `exploit_available`, `cve`, `plugin_id`, `port`, `protocol`

**Documentation:**
- Complete reference: [FILTER_FORMAT_REFERENCE.md](FILTER_FORMAT_REFERENCE.md)
- MCP resource: `tenable-sc://filters/format-reference`
- Examples: [USER_GUIDE.md](USER_GUIDE.md)

---

## Deployment Options

### Docker Compose (Recommended)
```bash
docker build -t tenable-sc-mcp:latest .
docker-compose up -d
```

### Standalone Docker
```bash
docker run -d --name tenable-sc-mcp \
  -p 8000:8000 \
  -v ~/.tenable-sc-mcp.env:/config/tsc.env:ro \
  tenable-sc-mcp:latest \
  --transport streamable-http \
  --host 0.0.0.0 --port 8000 \
  --env-file /config/tsc.env
```

### Local Python
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
export TSC_URL="https://sc.example.com"
export TSC_ACCESS_KEY="key"
export TSC_SECRET_KEY="secret"
tenable-sc-mcp --transport stdio
```

---

## Troubleshooting

**Containers won't start:**
```bash
docker compose logs tenable-sc-mcp
# Check: Missing .env, invalid TSC_URL, firewall
```

**Can't reach Tenable.sc:**
```bash
curl -k https://your-sc-server.com/rest/currentUser
# Expected: "invalid token" (endpoint reachable)
```

**Cache not working:**
```bash
docker ps --filter "name=redis"  # Should show (healthy)
# Ask MCP: "show me cache statistics"
```

**Remote clients can't connect:**
```bash
docker ps --filter "name=tenable-sc-mcp"  # Should show 0.0.0.0:8000
curl http://your-server-ip:8000/mcp
```

See [SUPPORT.md](SUPPORT.md) for more help.

---

## Security

- **RBAC enforced** - Uses your Tenable.sc API keys, all permissions apply
- **No credential storage** - Environment variables only
- **SSL/TLS support** - Set `TSC_VERIFY_SSL=true` in production
- **No built-in auth** - Bind to trusted networks only (127.0.0.1 for local)

**Best practices:**
- ❌ Never commit API keys to git
- ✅ Use env files with mode `0600`
- ✅ Create dedicated least-privilege API user in Tenable.sc
- ✅ Use firewall rules or SSH tunnels for remote access

See [SECURITY.md](SECURITY.md) for vulnerability reporting.

---

## Documentation

### User Docs
- [USER_GUIDE.md](USER_GUIDE.md) - Complete tool usage guide
- [FILTER_FORMAT_REFERENCE.md](FILTER_FORMAT_REFERENCE.md) - Filter system reference
- [CACHING_DEEP_DIVE.md](CACHING_DEEP_DIVE.md) - Cache behavior and performance
- [TEST_PROMPTS.md](TEST_PROMPTS.md) - Ready-to-use test queries

### Developer Docs
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md) - Tool development patterns
- [TOOLS_ROADMAP.md](TOOLS_ROADMAP.md) - Feature roadmap (v1.3.0, v1.4.0)
- [HANDOFF.md](HANDOFF.md) - LLM-friendly development handoff

### Project
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [SECURITY.md](SECURITY.md) - Security policy
- [SUPPORT.md](SUPPORT.md) - Support resources

---

## Compatibility

| Component | Version |
|-----------|---------|
| Python | 3.11+ |
| Tenable.sc | Current API versions |
| Docker | 20.10+ (Compose v2) |
| Redis | 7+ |

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Quick links:**
- [Report a bug](https://github.com/ABMJ/tenable-sc-mcp-server/issues/new?template=bug_report.yml)
- [Request a feature](https://github.com/ABMJ/tenable-sc-mcp-server/issues/new?template=feature_request.yml)
- [View issues](https://github.com/ABMJ/tenable-sc-mcp-server/issues)

---

## License

GNU GPL v3.0 - See [LICENSE](LICENSE)

---

**Need help?** Check [SUPPORT.md](SUPPORT.md) or [open an issue](https://github.com/ABMJ/tenable-sc-mcp-server/issues).

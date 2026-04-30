# Tenable.sc MCP Server

[![Release](https://img.shields.io/github/v/release/ABMJ/tenable-sc-mcp-server)](https://github.com/ABMJ/tenable-sc-mcp-server/releases)
[![CI](https://github.com/ABMJ/tenable-sc-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/ABMJ/tenable-sc-mcp-server/actions/workflows/ci.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://choosealicense.com/licenses/gpl-3.0/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)

**This tool is not an officially supported Tenable project.**

**Use of this tool is subject to the terms and conditions identified below, and is not subject to any license agreement you may have with Tenable.**

Container-ready MCP server for Tenable Security Center Plus using direct REST API calls. It does not use `pyTenable`; the server talks to Tenable.sc over HTTP with the documented `x-apikey` header.

## Compatibility And Support Policy

- Python versions: tested on `3.11` and `3.12`.
- Tenable.sc versions: intended for current supported Tenable.sc API versions; behavior can vary across older deployments.
- Support model: community-maintained, best-effort triage and fixes.
- Security fixes: prioritized for the latest release.

## What It Exposes

The server exposes documented Tenable.sc resources through generic MCP tools:

- `tsc_catalog`: lists the built-in API resource catalog with REST paths and documentation links.
- `tsc_resource_docs`: returns docs metadata for one resource (`compact=true` for `{name,path,docs}` only).
- `tsc_current_user`: returns the configured API user's Tenable.sc identity details.
- `tsc_resource_action`: unified CRUD-style helper for resources (`list`, `get`, `create`, `update`, `delete`).
- `tsc_list`: `GET /rest/{resource}` for any catalog resource.
- `tsc_get`: `GET /rest/{resource}/{id}` for any catalog resource.
- `tsc_create`: `POST /rest/{resource}` for resources that support create.
- `tsc_update`: `PUT /rest/{resource}/{id}` for resources that support update.
- `tsc_delete`: `DELETE /rest/{resource}/{id}` for resources that support delete.
- `tsc_analyze`: convenience wrapper for `POST /rest/analysis`.
- `tsc_download`: binary/text download helper for endpoints such as `POST /scanResult/{id}/download`.
- `tsc_upload_file`: multipart upload helper for `POST /file/upload`.
- `tsc_request`: direct escape hatch for any Tenable.sc endpoint, sub-action, or method (`response_path`, `max_items`, `keys_only` for token-efficient shaping).

`tsc_list`, `tsc_get`, `tsc_create`, `tsc_update`, and `tsc_delete` remain available as compatibility aliases, but new clients should use `tsc_resource_action`.

Tenable.sc has many resource-specific actions, such as scan launch/import/export style operations. Use `tsc_request` for those documented paths, for example `POST /scan/{id}/launch` if supported by your Tenable.sc version.

## RBAC Model

The MCP server does not bypass or reimplement Tenable.sc RBAC. Tenable.sc remains the source of truth:

- The configured `TSC_ACCESS_KEY` and `TSC_SECRET_KEY` identify the API user.
- Tenable.sc roles, organization membership, repository access, object sharing, and administrator/director permissions determine what each tool can see or change.
- Unauthorized calls return Tenable.sc API errors through the MCP response.
- Run `tsc_current_user` first to verify which identity the server is using.

Use a dedicated least-privilege Tenable.sc service account for deployment.

## Supported API Resources

The built-in catalog follows the Tenable.sc API index at <https://docs.tenable.com/security-center/api/index.htm> and includes these resource paths:

`acceptRiskRule`, `agentGroup`, `agentResultsSync`, `agentScan`, `alert`, `analysis`, `arc`, `arcTemplate`, `asset`, `assetTemplate`, `attributeSet`, `auditFile`, `auditFileTemplate`, `bulk`, `configuration`, `configurationSection`, `credential`, `currentOrganization`, `currentUser`, `customPlugins`, `dashboardComponent`, `dashboardTab`, `dashboardTemplate`, `deviceInformation`, `directorInsights`, `directorOrganization`, `directorRepository`, `directorScan`, `directorScanner`, `directorScanPolicy`, `directorScanResult`, `directorScanZone`, `directorSystem`, `directorUser`, `feed`, `file`, `freezeWindow`, `group`, `hosts`, `job`, `lce`, `lceClient`, `lcePolicy`, `ldap`, `licenseInfo`, `lumin`, `mdm`, `notification`, `organization`, `organizationSecurityManager`, `organizationUser`, `passiveScanner`, `plugin`, `pluginFamily`, `publishingSite`, `query`, `recastRiskRule`, `report`, `reportDefinition`, `reportImage`, `reportTemplate`, `repository`, `role`, `saml`, `scanner`, `scan`, `scanPolicy`, `scanPolicyTemplate`, `scanResult`, `scanZone`, `sensorProxy`, `solutions`, `sshKey`, `status`, `style`, `styleFamily`, `system`, `tenableScInstance`, `tesAdminRoles`, `tesUserPermissions`, `ticket`, `token`, `user`, `wasScan`, and `wasScanner`.

Use `tsc_catalog` for the catalog. It returns compact results by default; use `compact=false` for full metadata. You can also use `query` and `limit`.

## Configuration

Set these environment variables (or place them in an env file and pass `--env-file`):

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `TSC_URL` | Yes | None | Base URL for Tenable.sc, for example `https://securitycenter.example.com`. |
| `TSC_ACCESS_KEY` | Yes | None | Tenable.sc API access key. |
| `TSC_SECRET_KEY` | Yes | None | Tenable.sc API secret key. |
| `TSC_VERIFY_SSL` | No | `true` | Set to `false` for lab systems with untrusted certificates. Prefer `true` in production. |
| `TSC_TIMEOUT_SECONDS` | No | `300` | HTTP timeout per request. |
| `TSC_MAX_RETRIES` | No | `3` | Retries for network failures and HTTP 429 responses. |
| `TSC_BACKOFF_SECONDS` | No | `1` | Base retry backoff in seconds. |

You can also run with a custom prefix using `--env-prefix` (for example `LAB1_TSC_`).
With `--env-prefix LAB1_TSC_`, the server reads `LAB1_TSC_URL`, `LAB1_TSC_ACCESS_KEY`, and so on.

Do not include `/rest` in `TSC_URL`. Use the same base URL you use to reach Tenable.sc in a browser, for example `https://sc.example.internal:8443` or `https://securitycenter.example.com`.

### Save Tenable.sc Details

For container deployments, keep Tenable.sc details in an env file on the machine that runs the MCP server:

```bash
nano ~/.tenable-sc-mcp.env
```

Example lab configuration:

```bash
TSC_URL=https://sc.example.internal:8443
TSC_ACCESS_KEY=your-access-key
TSC_SECRET_KEY=your-secret-key
TSC_VERIFY_SSL=false
```

Use `TSC_VERIFY_SSL=true` when Tenable.sc has a trusted certificate. Use `false` only for lab systems with self-signed or untrusted certificates.

You can verify the Tenable.sc URL is reachable before starting the MCP server:

```bash
curl -k https://sc.example.internal:8443/rest/currentUser
```

An `invalid token` response means the Tenable.sc API endpoint is reachable; the MCP server will authenticate with the configured API keys.

## Local Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install .
export TSC_URL="https://securitycenter.example.com"
export TSC_ACCESS_KEY="your-access-key"
export TSC_SECRET_KEY="your-secret-key"
tenable-sc-mcp --transport stdio
```

## Docker Install On Ubuntu

Install Docker if it is not already available:

```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
```

Log out and back in after adding your user to the `docker` group.

Install Docker Compose (recommended v2 plugin):

```bash
sudo apt update
sudo apt install -y docker-compose-plugin
docker compose version
```

If `docker compose` is unavailable on your host, install legacy Compose and use `docker-compose` commands:

```bash
sudo apt install -y docker-compose
docker-compose version
```

## Container Build

From the project directory on the machine that will run the MCP server:

```bash
docker build -t tenable-sc-mcp:latest .
```

## Run As A Background Service

Run the MCP server as a background Docker container using Streamable HTTP:

```bash
docker run -d \
  --name tenable-sc-mcp \
  --user "$(id -u):$(id -g)" \
  --restart unless-stopped \
  -p 0.0.0.0:8000:8000 \
  -v ~/.tenable-sc-mcp.env:/config/tsc.env:ro \
  tenable-sc-mcp:latest \
  --transport streamable-http \
  --host 0.0.0.0 \
  --port 8000 \
  --env-file /config/tsc.env \
  --allow-remote-hosts
```

Using `--user "$(id -u):$(id -g)"` runs the container process as the same UID/GID that launched the command. This is useful for bind-mounted file permissions.

## Run With Docker Compose

This repo includes `docker-compose.yml` with:

- `user: "${LOCAL_UID}:${LOCAL_GID}"` so it runs as the invoking user
- `restart: unless-stopped` so it survives host/container restarts
- the same port, env-file mount, and MCP arguments as the `docker run` example

Use detached mode (`up -d`) to start the container and return to your shell. Running `up` without `-d` attaches logs in the foreground.

If you are using Docker Compose v2 (`docker compose`), run:

```bash
export LOCAL_UID=$(id -u)
export LOCAL_GID=$(id -g)
docker compose up -d
docker compose ps
docker compose logs -f
docker compose down
```

If you are using legacy Docker Compose (`docker-compose`), run:

```bash
export LOCAL_UID=$(id -u)
export LOCAL_GID=$(id -g)
docker-compose up -d
docker-compose ps
docker-compose logs -f
docker-compose down
```

`--allow-remote-hosts` is required for remote MCP clients. Without it, the server can return `421 Misdirected Request` with `Invalid Host header` for non-local requests.

The remote MCP URL is:

```text
http://<mcp-server-ip>:8000/mcp
```

For example:

```text
http://sc-mcp-host.example.internal:8000/mcp
```

Check that the container is running and listening on all interfaces:

```bash
docker ps
```

The `PORTS` column should include:

```text
0.0.0.0:8000->8000/tcp
```

Opening `/mcp` in a browser may show a protocol error such as `Client must accept text/event-stream`. That still means the MCP server is reachable; connect with an MCP client such as OpenCode.

Useful maintenance commands:

```bash
docker logs tenable-sc-mcp
docker rm -f tenable-sc-mcp
```

## Run Multiple MCP Instances On One Machine

You can run multiple instances, each connected to a different Tenable.sc, without editing code.

Use one env file per instance and a different container name/host port:

```bash
# Instance A
cat > ~/.tenable-sc-mcp-a.env <<'EOF'
TSC_URL=https://sc-a.example.com
TSC_ACCESS_KEY=access-key-a
TSC_SECRET_KEY=secret-key-a
TSC_VERIFY_SSL=true
EOF

# Instance B
cat > ~/.tenable-sc-mcp-b.env <<'EOF'
TSC_URL=https://sc-b.example.com
TSC_ACCESS_KEY=access-key-b
TSC_SECRET_KEY=secret-key-b
TSC_VERIFY_SSL=true
EOF

docker run -d --name tenable-sc-mcp-a --restart unless-stopped \
  -p 0.0.0.0:8001:8000 \
  -v ~/.tenable-sc-mcp-a.env:/config/tsc.env:ro \
  tenable-sc-mcp:latest \
  --transport streamable-http --host 0.0.0.0 --port 8000 \
  --env-file /config/tsc.env --allow-remote-hosts

docker run -d --name tenable-sc-mcp-b --restart unless-stopped \
  -p 0.0.0.0:8002:8000 \
  -v ~/.tenable-sc-mcp-b.env:/config/tsc.env:ro \
  tenable-sc-mcp:latest \
  --transport streamable-http --host 0.0.0.0 --port 8000 \
  --env-file /config/tsc.env --allow-remote-hosts
```

Then connect MCP clients to:

- `http://<host>:8001/mcp` (Tenable.sc A)
- `http://<host>:8002/mcp` (Tenable.sc B)

## Local Stdio Container Run

For an MCP client that starts containers over stdio, configure the client to run:

```bash
docker run --rm -i \
  -e TSC_URL="https://securitycenter.example.com" \
  -e TSC_ACCESS_KEY="your-access-key" \
  -e TSC_SECRET_KEY="your-secret-key" \
  -e TSC_VERIFY_SSL="true" \
  tenable-sc-mcp:latest
```

## OpenCode Remote MCP Example

Add this to `opencode.json` or `opencode.jsonc` on the machine running OpenCode:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "tenable-sc": {
      "type": "remote",
      "url": "http://sc-mcp-host.example.internal:8000/mcp",
      "enabled": true,
      "oauth": false,
      "timeout": 30000
    }
  }
}
```

If you already have an OpenCode config, merge only the `mcp` block. Restart OpenCode after changing the config.

You can then ask OpenCode to use Tenable.sc, for example:

```text
use tenable-sc to call tsc_current_user
```

or:

```text
use tenable-sc to list repositories
```

## Claude Desktop Stdio Example

Add an MCP server entry similar to this:

```json
{
  "mcpServers": {
    "tenable-sc": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e",
        "TSC_URL=https://securitycenter.example.com",
        "-e",
        "TSC_ACCESS_KEY=your-access-key",
        "-e",
        "TSC_SECRET_KEY=your-secret-key",
        "tenable-sc-mcp:latest"
      ]
    }
  }
}
```

## Example Tool Calls

List repositories:

```json
{
  "resource": "repository"
}
```

Get scan ID `12`:

```json
{
  "resource": "scan",
  "object_id": "12"
}
```

Run an analysis query:

```json
{
  "query": {
    "type": "vuln",
    "sourceType": "cumulative",
    "query": {
      "tool": "vulndetails",
      "filters": []
    },
    "startOffset": 0,
    "endOffset": 50
  }
}
```

Call a resource-specific action with `tsc_request`:

```json
{
  "method": "POST",
  "path": "/scan/12/launch",
  "body": {}
}
```

Request only selected fields:

```json
{
  "resource": "asset",
  "fields": ["id", "name", "description"]
}
```

Request expansions:

```json
{
  "resource": "scan",
  "object_id": "12",
  "expand": ["credentials", "assets"]
}
```

## Feedback And Support

- Bug reports: <https://github.com/ABMJ/tenable-sc-mcp-server/issues/new?template=bug_report.yml>
- Feature requests: <https://github.com/ABMJ/tenable-sc-mcp-server/issues/new?template=feature_request.yml>
- General issues list: <https://github.com/ABMJ/tenable-sc-mcp-server/issues>
- Contribution guide: `CONTRIBUTING.md`
- Security policy: `SECURITY.md`
- Support policy: `SUPPORT.md`

When opening an issue, include the release version (for example `v0.1.0`), deployment mode (`stdio` or `streamable-http`), and the exact request or tool call that failed.

## API Documentation Sources

- Tenable.sc API reference: <https://docs.tenable.com/security-center/api/index.htm>
- Tenable.sc API best practices guide: <https://docs.tenable.com/security-center/best-practices/api/Content/PDF/Tenablesc_API_BestPracticesGuide.pdf>
- pyTenable SDK reference: <https://pytenable.readthedocs.io/en/stable/api/sc/index.html>

## Security Notes

- Do not bake API keys into the image.
- Prefer container/orchestrator secrets for `TSC_ACCESS_KEY` and `TSC_SECRET_KEY`.
- Use `TSC_VERIFY_SSL=true` in production.
- Use a dedicated least-privilege Tenable.sc API user.
- Be careful with `tsc_delete`, `tsc_update`, and `tsc_request` calls using mutating methods.
- The remote MCP HTTP endpoint does not add its own user authentication. Anyone who can reach it can use the configured Tenable.sc API identity through MCP tools. Bind it only to trusted networks, restrict it with firewall rules, or expose it through an SSH tunnel/VPN.

## Design Notes

This server intentionally uses direct HTTP instead of `pyTenable` to keep startup and call paths small. The generic resource tools avoid maintaining hundreds of brittle wrappers while still exposing the entire documented API catalog. When Tenable adds a new action under an existing resource, `tsc_request` can call it immediately.

## License

- GNU GPL v3.0: <https://choosealicense.com/licenses/gpl-3.0/>

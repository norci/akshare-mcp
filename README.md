# akshare-mcp

<p align="center">
  <strong>Complete MCP server for akshare - 100% API coverage</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/akshare-mcp/">
    <img src="https://img.shields.io/pypi/v/akshare-mcp" alt="PyPI Version">
  </a>
  <a href="https://pypi.org/project/akshare-mcp/">
    <img src="https://img.shields.io/pypi/pyversions/akshare-mcp" alt="Python Versions">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/pypi/l/akshare-mcp" alt="License: MIT">
  </a>
</p>

---

## Overview

`akshare-mcp` is a Model Context Protocol (MCP) server that provides **complete** access to all akshare APIs. Unlike other solutions that manually define a handful of tools, this project **dynamically generates** MCP tools from all 995+ akshare functions.

### Key Features

- **100% API Coverage** - All akshare functions become MCP tools automatically
- **Dynamic Generation** - No manual maintenance needed when akshare updates
- **Smart Parameter Handling** - Automatically extracts types, defaults, and documentation
- **Built-in Discovery** - Search and browse all available APIs

## Installation

### Using uv (Recommended)

```bash
# Local development (from project directory)
uvx --from .

# Or install and run
uv venv .venv
source .venv/bin/activate
uv pip install -e .
akshare-mcp
```

### Using pip

```bash
pip install akshare-mcp
```

### Using Docker

> Note: Docker image will be published after GitHub Actions is set up.

```bash
# Build locally
docker build -t akshare-mcp .

# Or pull from GitHub Container Registry (after CI is configured)
docker run -d -p 8000:8000 \
  --name akshare-mcp \
  ghcr.io/norci/akshare-mcp:latest
```

## Usage

### Standalone Server

```bash
akshare-mcp
# Or specify port
akshare-mcp --port 9000
```

### With MCP Clients

#### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "akshare-mcp": {
      "command": "path/to/.venv/bin/python",
      "args": ["-m", "akshare_mcp"]
    }
  }
}
```

#### OpenCode

Add to your OpenClaw agent skill:

```yaml
mcp:
  command: akshare-mcp
  port: 8000
```

## Available Tools

### Management Tools

| Tool | Description |
|------|-------------|
| `list_akshare_apis` | List all available APIs with optional category filter |
| `get_api_info` | Get detailed info about a specific API |
| `search_apis` | Search APIs by keyword |
| `get_time_info` | Get current time and trading calendar |

### Data Tools (Auto-generated)

All 995+ akshare functions are automatically available as tools:

- Stock data (A-share, H-share, US, etc.)
- Fund data (ETF, mutual funds, etc.)
- Futures and options
- Bond data
- Economic data (GDP, CPI, PMI, etc.)
- Currency and forex
- And much more...

## Examples

### List All Stock APIs

```
list_akshare_apis(category="stock", limit=20)
```

### Get Historical Data

```
stock_zh_a_hist(symbol="000001", start_date="20250101", end_date="20251231", adjust="qfq")
```

### Search for ETFs

```
search_apis(keyword="etf")
```

### Get API Details

```
get_api_info(api_name="stock_zh_a_hist")
```

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────┐
│   Client    │────▶│  akshare-mcp│────▶│  akshare │
│ (MCP SDK)   │     │  (Dynamic)  │     │ (995+ APIs)
└─────────────┘     └─────────────┘     └──────────┘
```

## Why This Project?

Existing akshare MCP servers only expose a handful of manually-defined tools (typically 5-10). This project solves that by:

1. **Introspecting akshare** at runtime using `inspect` module
2. **Extracting signatures** including types, defaults, and docs
3. **Generating tools** dynamically for each function
4. **Caching results** for performance

## License

MIT License - See [LICENSE](LICENSE) for details.

## Disclaimer

This project is for educational purposes. Financial data is provided by third-party sources and may have delays or inaccuracies. Use at your own risk.

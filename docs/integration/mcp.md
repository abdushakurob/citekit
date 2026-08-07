# MCP Integration

CiteKit implements the **Model Context Protocol (MCP)**, a standard open protocol that enables AI assistants to connect to data sources.

Because CiteKit is MCP-compliant, it works with **any** MCP client, including:
*   [Claude Desktop](https://claude.ai/download)
*   [Cline](https://github.com/cline/cline) (VS Code Extension)
*   Coming soon: JetBrains AI, Zed, and more.

## Installation & Setup

You do not need to install a separate "MCP Extension". The `citekit` package *is* the server.

### 1. Install CiteKit
Ensure you have CiteKit installed on your system.

```bash
# Python (Recommended)
pip install citekit

# Node.js
npm install citekit
```

### 2. Configure Your Client

#### Claude Desktop

Edit your configuration file:
*   **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
*   **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add the following:

::: code-group

```json [Python]
{
  "mcpServers": {
    "citekit": {
      "command": "citekit",
      "args": ["serve"],
      "env": {
        "GEMINI_API_KEY": "AIzaSy..."
      }
    }
  }
}
```

```json [Node.js]
{
  "mcpServers": {
    "citekit": {
      "command": "npx",
      "args": ["-y", "citekit", "serve"],
      "env": {
        "GEMINI_API_KEY": "AIzaSy..."
      }
    }
  }
}
```

:::

*Note: If `citekit` is not in your PATH, provide the full path to your python executable or use `uv run citekit serve`.*

#### Cline (VS Code)

1.  Open **Cline Settings**.
2.  Go to **MCP Servers**.
3.  Add a new server with:
    *   **Name**: `citekit`
    *   **Command**: `citekit` (or full path)
    *   **Args**: `serve`
    *   **Environment Variables**: `{"GEMINI_API_KEY": "..."}` (only required for the default Gemini mapper)

### Available Tools

| Tool | Description | Input |
| :--- | :--- | :--- |
| `listResources` | List all ingested resources. | `{}` |
| `getStructure` | Get the full JSON map of a resource. | `{ resource_id }` |
| `getNode` | Get metadata for a specific node. | `{ resource_id, node_id }` |
| `resolve` | Extract content (physical or virtual). | `{ resource_id, node_id, virtual? }` |

---

### See it in Action
Check out the [**Study Tool Example**](/guide/examples/study) to see how an AI agent uses these tools to help you study a lecture video.

## Troubleshooting

*   **"Command not found"**: Ensure `citekit` is installed in your PATH, or use absolute paths to your python executable.
*   **"Missing API Key"**: If you ingest with the default Gemini mapper, provide `GEMINI_API_KEY` in the `env` section of the config.

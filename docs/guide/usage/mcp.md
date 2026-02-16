# MCP Integration Guide

CiteKit implements the **Model Context Protocol (MCP)**, allowing AI agents (like **Claude Desktop** or **Cline**) to directly access your local library.

## 1. Prerequisites

-   **Claude Desktop App** (or any MCP-compliant client)
-   **Python 3.10+** (for Python Server) OR **Node.js 18+** (for JS Server)
-   **Gemini API Key** (for ingestion)

## 2. Configuration (`claude_desktop_config.json`)

To use CiteKit, you must add it to your MCP client's configuration file.

### 🐍 Python Server (Recommended)

Does not require installing the package globally if you use `uv`.

```json
{
  "mcpServers": {
    "citekit": {
      "command": "uvx",
      "args": ["citekit"],
      "env": {
        "GEMINI_API_KEY": "AIzaSy..."
      }
    }
  }
}
```

*Alternatively, if installed via pip:*
```json
    "citekit": {
      "command": "python",
      "args": ["-m", "citekit.mcp_server"],
      "env": { ... }
    }
```

### 📦 Node.js Server

```json
{
  "mcpServers": {
    "citekit-js": {
      "command": "npx",
      "args": ["-y", "@citekit/server"],
      "env": {
        "GEMINI_API_KEY": "AIzaSy..."
      }
    }
  }
}
```

## 3. Available Tools

Once connected, the Agent will have access to these tools:

| Tool | Arguments | Description |
| :--- | :--- | :--- |
| `listResources` | None | Lists all mapped resources in the library. |
| `getStructure` | `resource_id` | Returns the full JSON tree (Nodes) of a resource. |
| `getNode` | `resource_id`, `node_id` | Returns details (timestamps, text lines) for a specific node. |
| `resolve` | `resource_id`, `node_id` | Extracts the content to a local file. |

## 4. Example Workflow

Here is how a typical interaction looks:

1.  **User**: "Parse the `maintenance_manual.pdf` and find the safety procedures."
    *   *Agent calls `listResources()` to see file names.*
    *   *Agent calls `CiteKitClient.ingest()` if the file isn't listed (note: Agent usually asks user to run ingest).*

2.  **Agent**: "I see the manual. Let me check the structure."
    *   *Agent calls `getStructure("maintenance_manual")`.*

3.  **Agent**: "Found a 'Safety' section. Extracting it now."
    *   *Agent calls `resolve("maintenance_manual", "section_safety")`.*

4.  **CiteKit**:
    *   Creates `.citekit_output/maintenance_manual_section_safety.pdf`
    *   Returns the **absolute path** to the Agent.

5.  **Agent**: Reads the new PDF and answers your question.

## 5. Troubleshooting

**"Tool not found"**
- Restart Claude Desktop.
- Check logs: `tail -f ~/Library/Logs/Claude/mcp.log`

**"API Key Missing"**
- Ensure `GEMINI_API_KEY` is set in the `env` section of the config JSON.

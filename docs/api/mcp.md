# MCP Protocol Reference

CiteKit implements the **Model Context Protocol (MCP)** to allow AI agents to browse, understand, and extract multimodal evidence directly.

---

## Tools

The CiteKit MCP server exposes the following tools to the agent:

### `listResources`
Returns a list of all resource IDs currently available in the local CiteKit index.
-   **Input**: `{}`
-   **Output**: `{"resources": ["lecture_vid", "book_pdf", ...]}`

### `getStructure`
Retrieves the full semantic map (JSON) of a specific resource.
-   **Input**: `{"resource_id": "string"}`
-   **Output**: The full `ResourceMap` schema.
-   **Agent Usage**: Agents call this first to "see" what is inside a file without downloading it.

### `getNode`
Fetches metadata for a specific node ID.
-   **Input**: `{"resource_id": "string", "node_id": "string"}`
-   **Output**: The single `Node` object.
-   **Agent Usage**: Used for fast verification of a specific concept's location.

### `resolve`
The "Resolution" tool. Converts a node into evidence.
-   **Input**: 
    -   `resource_id`: (Required)
    -   `node_id`: (Required)
    -   `virtual`: (Optional, default: `False`)
-   **Output**: `ResolvedEvidence` object (contains absolute path to clip/slice).
-   **Agent Usage**: The final step. The agent takes the `output_path` and attaches it to the current chat context as grounded evidence.

---

## Internal Protocol Flow

1.  **Discovery**: User asks "What happens at 5 minutes in the video?".
2.  **Mapping**: Agent looks at `listResources`.
3.  **Selection**: Agent calls `getStructure(lecture_vid)`.
4.  **Pinpointing**: Agent finds a node with `id: "recursion_demo"` and `location: {start: 300, end: 360}`.
5.  **Resolution**: Agent calls `resolve(lecture_vid, "recursion_demo")`.
6.  **Grounding**: CiteKit extracts the 60s clip, returns the path, and the agent "sees" the video.

---

## Configuration

### Claude Desktop
Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "citekit": {
      "command": "python",
      "args": ["-m", "citekit.cli", "serve"]
    }
  }
}
```

### Cursor / Cline / Roo Code
See the [MCP Integration Guide](/integration/mcp) for specific IDE setup.

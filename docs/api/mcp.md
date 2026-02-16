# MCP Protocol Reference

Technical specification for the CiteKit Model Context Protocol (MCP) server.

## Overview

The CiteKit MCP server allows AI agents to interact with your local resource maps and resolve content slices automatically. It implements the standard [Model Context Protocol](https://modelcontextprotocol.io/).

## Tools

### `listResources`
Lists all available resource map IDs currently ingested in the storage directory.

**Arguments**: None.

**Response**:
```json
{
  "resources": ["lecture_1", "calculus_ch2"]
}
```

---

### `getStructure`
Retrieves the full structural index for a specific resource ID.

**Arguments**:
- `resource_id` (string): The ID of the resource to inspect.

**Response**:
Returns the full [Resource Map JSON](/api/models).

---

### `resolve`
Converts a node ID into extracted evidence (physical file or virtual pointer).

**Arguments**:
- `resource_id` (string): The parent resource ID.
- `node_id` (string): The ID of the node to resolve.
- `virtual` (boolean, optional): If `true`, CiteKit will skip physical file extraction and return metadata only.

**Response**:
Returns a [ResolvedEvidence](/api/models#resolved-evidence) object.

**Virtual Resolve Response**:
When `virtual: true` is provided, the tool returns:
- `modality`: string
- `address`: string (e.g., `video://lecture#t=180,210`)
- `node`: The node metadata object.
- `output_path`: `null` (Physical file skipping)

---

## Server Initialization

The server can be started using the `serve` command in both Python and Node.js.

### Python
```bash
python -m citekit.cli serve --storage-dir .resource_maps --output-dir .citekit_output
```

### Node.js
```bash
npx citekit serve
```

## Security & Environment

The MCP server requires the `GEMINI_API_KEY` to be passed as an environment variable for mapping tasks. It does **not** expose your API key to the client; all mapping logic happens server-side.

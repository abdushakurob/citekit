---
layout: home

hero:
  name: CiteKit
  text: Multimodal Context SDK
  tagline: Structural mapping and content extraction for AI agents.
  actions:
    - theme: brand
      text: Documentation
      link: /guide/
    - theme: alt
      text: MCP Setup
      link: /integration/mcp

features:
  - title: Context Mapping
    details: Generates hierarchical JSON maps of video, audio, PDF, and image content, enabling agents to understand file structure without consuming context tokens.
    link: /guide/concepts/resource-mapping
  - title: Zero-Copy Extraction
    details: extract specific segments (video clips, audio ranges, PDF pages, image crops) locally.
  - title: Local-First
    details: File processing occurs on the local filesystem. No data is sent to the cloud during the retrieval phase.
  - title: Model Context Protocol
    details: Includes a built-in MCP server for integration with Claude Desktop, Cline, and other compliant agents.
---

## Quick Install

::: code-group

```bash [Python]
pip install citekit
```

```bash [Node.js]
npm install citekit
```

```bash [MCP Server]
# Installs CLI tool for Claude/Cline
pip install citekit
```

:::

## Overview

CiteKit is a software development kit designed to solve the **Context Granularity Problem** in multimodal AI applications.

Traditional RAG (Retrieval Augmented Generation) approaches often rely on arbitrary chunking or full-file context loading. CiteKit employs a **Map-Reduce** strategy:

1.  **Map**: The file is analyzed once by a specific prompt to generate a structural index (JSON).
2.  **Reduce**: Agents query this index to select only relevant nodes.
3.  **Resolve**: The selected nodes are extracted as standalone files.

## Workflow

### 1. Ingestion
The file is processed to generate a `ResourceMap`.

```python
from citekit import CiteKitClient
client = CiteKitClient()
video_map = await client.ingest("lecture.mp4", "video")
```

### 2. Selection
The agent (or a human via MCP) selects a Node ID.

```json
{
  "id": "intro_sequence",
  "type": "section",
  "location": { "start": 0, "end": 45 }
}
```

### 3. Resolution
The specific segment is extracted locally.

```python
evidence = await client.resolve("lecture", "intro_sequence")
```

## MCP Support (Claude / Cline)

CiteKit has a built-in MCP server. No extra plugins required.

1.  **Install**: `pip install citekit`
2.  **Config**: Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "citekit": {
      "command": "citekit",
      "args": ["serve"],
      "env": { "GEMINI_API_KEY": "..." }
    }
  }
}
```

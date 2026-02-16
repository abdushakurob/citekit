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
  - title: Context Economics
    details: Pay the "Token Tax" once. CiteKit maps your file via Gemini API once to create a structural index, then allows agents to resolve evidence 100% locally from then on.
    link: /guide/concepts/resource-mapping
  - title: High-Fidelity Extraction
    details: Extract specific segments (video clips, audio ranges, PDF pages, image crops) locally without relying on proprietary cloud services.
  - title: Model Context Protocol
    details: Includes a built-in MCP server for integration with Claude Desktop, Cline, and other compliant agents.
  - title: Text Structure Analysis
    details: Native support for codebases and docs (`.txt`, `.md`, `.py`). Maps classes/functions and resolves specific line ranges.
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

## Quick Usage

CiteKit works the same way across all interfaces: **Ingest** to map, **Resolve** to extract.

::: code-group

```python [Python]
from citekit import CiteKitClient

# 1. Ingest (Map)
client = CiteKitClient()
video_map = await client.ingest("lecture.mp4", "video")

# 2. Resolve (Extract)
# Extracts exact clip from 10s to 20s
evidence = await client.resolve(video_map.resource_id, "intro_scene")
print(evidence.output_path)
```

```typescript [Node.js]
import { CiteKitClient } from 'citekit';

// 1. Ingest (Map)
const client = new CiteKitClient();
const map = await client.ingest('lecture.mp4', 'video');

// 2. Resolve (Extract)
const evidence = await client.resolve(map.resource_id, 'intro_scene');
console.log(evidence.output_path);
```

```bash [CLI]
# 1. Ingest
python -m citekit.cli ingest lecture.mp4 --type video

# 2. Resolve
python -m citekit.cli resolve lecture intro_scene
```

```json [MCP Config]
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

:::

## Overview

CiteKit is the high-fidelity orchestration layer for **Modern AI Architectures**. It solves the **Context Precision Problem** in multimodal applications (Agentic RAG, Long-Context reasoning, and Multi-Agent flows).

Instead of "fuzzy" context loading, CiteKit employs a **Semantic Indexing** strategy:

1.  **Map**: Files are analyzed to discover their "Structural DNA" (Topics, Scenes, Charts).
2.  **Orchestrate**: Agents use the Map to navigate and choose relevant logical units.
3.  **Resolve**: CiteKit extracts exactly those high-fidelity segments (Physical or Virtual).



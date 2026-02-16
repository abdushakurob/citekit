# CLI Reference

CiteKit provides Command Line Interfaces (CLIs) for both Python and Node.js.

## Overview

| Feature | Python CLI | Node.js CLI |
| :--- | :--- | :--- |
| **Command** | `python -m citekit.cli` | `citekit` |
| **Ingest Files** | Yes | No (API only) |
| **Resolve Nodes** | Yes | No (API only) |
| **MCP Server** | Yes (`serve`) | Yes (`serve`) |
| **Inspect Maps** | Yes | No |
| **Validate Maps** | Yes (`check-map`) | No |

## Python CLI

The Python CLI is a full-featured tool for managing your local CiteKit resources.

### Installation
```bash
pip install citekit
# This installs both the library and the CLI tool.
```

### Usage

**1. Ingest a file**
```bash
# Video with custom concurrency and retries
python -m citekit.cli ingest video.mp4 --type video --concurrency 2 --retries 5
```

*   `--type`, `-t`: One of `video`, `audio`, `document`, `image`, `text`.
*   `--concurrency`, `-c`: Max parallel mapper calls (default: 5).
*   `--retries`, `-r`: Max API retries (default: 3).

### `list`

Lists all ingested resources or inspects a specific resource.

```bash
# List all resources
python -m citekit.cli list

# List nodes in a specific resource
python -m citekit.cli list my_video
```

*   `node_id` (Optional): If provided without a resource ID, it tries to parse `resource_id.node_id`.

### `inspect`

View detailed metadata for a specific node without resolving it.

```bash
# Inspect a node
python -m citekit.cli inspect DataProcessor --resource test_code

# Shorthand
python -m citekit.cli inspect test_code.DataProcessor
```

**3. Resolve (Extract) content**
```bash
# Physical extraction (default)
python -m citekit.cli resolve lecture.intro
# Virtual resolution (metadata only)
python -m citekit.cli resolve lecture.intro --virtual
```

*   `--resource`, `-res`: Optional resource ID (if not provided in rid.nid format).
*   `--virtual`: If set, returns only timestamps/pages without file extraction.

### `check-map`

Validates a JSON map against the official schema. Useful for debugging or before sharing maps.

```bash
python -m citekit.cli check-map path/to/map.json
```

**4. Start MCP Server**
```bash
python -m citekit.cli serve
```
> **What is `serve`?**
> This starts the **Model Context Protocol (MCP)** server over stdio. It allows AI agents (like Claude Desktop or Cline) to "talk" to CiteKit. It sits silently waiting for agent commands and is **not** meant for human interaction.

## Node.js CLI

The Node.js CLI is primarily designed to run the **MCP Server**.

### Installation
```bash
npm install -g citekit
# Installs the `citekit` global command (MCP Server only).
```

### Usage

**Start MCP Server**
```bash
citekit serve
```
> **Purpose**: Connects this machine to an AI agent via MCP. Not for human use.

> **Note**: For programmatic ingestion and resolution in Node.js, use the SDK:
> ```typescript
> import { CiteKitClient } from 'citekit';
> const client = new CiteKitClient();
> await client.ingest('image.png', 'image');
> ```

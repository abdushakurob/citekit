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
# Video
python -m citekit.cli ingest video.mp4 --type video

# Image
python -m citekit.cli ingest chart.png --type image
```

*Supported types*: `video`, `audio`, `document`, `image`.

**2. List resources**
```bash
python -m citekit.cli list
```

**3. Resolve (Extract) content**
```bash
python -m citekit.cli resolve <node_id>
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

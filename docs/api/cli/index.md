# CLI Reference

The CiteKit CLI is the primary management tool for local-first multimodal workflows. It allows you to build maps, resolve evidence, and serve resources to AI agents without writing code.

## Quick Reference

| Command | Usage | Responsibility | link |
| :--- | :--- | :--- | :--- |
| **`ingest`** | `citekit ingest <file>` | Analyzing files and building semantic maps. | [Ingest API](/api/cli/ingest) |
| **`resolve`** | `citekit resolve <node>` | Extracting clips and slices from sources. | [Resolve API](/api/cli/resolve) |
| **`inspect`** | `citekit inspect <node>` | Viewing technical metadata for a pinpoint. | [Resolve API](/api/cli/resolve#inspect) |
| **`list`** | `citekit list` | Exploring the local index of resources. | [Management API](/api/cli/manage) |
| **`adapt`** | `citekit adapt <data>` | Converting external datasets (GraphRAG, etc). | [Adapter API](/api/cli/adapt) |
| **`serve`** | `citekit serve` | Starting the Model Context Protocol server. | [MCP Protocol](/api/mcp/) |

## Installation

The CLI is included automatically with the Python and Node.js SDKs.

### Python (Full Tools)
```bash
pip install citekit
python -m citekit.cli --help
```

### Node.js (MCP Only)
```bash
npm install -g citekit
citekit serve
```

---

## Global Options

The following flags apply to most interactive commands:

| Flag | Shorthand | Description |
| :--- | :--- | :--- |
| `--help` | `-h` | Display help for the command. |
| `--verbose` | `-v` | Enable detailed debug logging. |

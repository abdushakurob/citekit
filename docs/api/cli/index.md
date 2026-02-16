# CLI Reference

The CiteKit CLI is the primary management tool for local-first multimodal workflows. It allows you to build maps, resolve evidence, and serve resources to AI agents without writing code.

## Quick Reference

| Command | Usage | Responsibility | link |
| :--- | :--- | :--- | :--- |
| **`ingest`** | `python -m citekit.cli ingest <file>` or `citekit ingest <file>` | Analyzing files and building semantic maps. | [Ingest API](/api/cli/ingest) |
| **`resolve`** | `python -m citekit.cli resolve <node>` or `citekit resolve <node>` | Extracting clips and slices from sources. | [Resolve API](/api/cli/resolve) |
| **`inspect`** | `python -m citekit.cli inspect <node>` or `citekit inspect <node>` | Viewing technical metadata for a pinpoint. | [Resolve API](/api/cli/resolve#citekit-inspect) |
| **`list`** | `python -m citekit.cli list` or `citekit list` | Exploring the local index of resources. | [Management API](/api/cli/manage) |
| **`check-map`** | `python -m citekit.cli check-map <path>` or `citekit check-map <path>` | Validating external or edited maps. | [Management API](/api/cli/manage#citekit-check-map) |
| **`structure`** | `python -m citekit.cli structure <id>` or `citekit structure <id>` | Dumping a raw map JSON. | [Management API](/api/cli/manage#citekit-structure) |
| **`adapt`** | `python -m citekit.cli adapt <data>` or `citekit adapt <data>` | Converting external datasets (GraphRAG, etc). | [Adapter API](/api/cli/adapt) |
| **`serve`** | `python -m citekit.cli serve` or `citekit serve` | Starting the Model Context Protocol server. | [MCP Protocol](/api/mcp/) |

## Installation

The CLI is included automatically with both the Python and JavaScript SDKs. As of v0.1.8, both packages have full CLI parity.

### Python
```bash
pip install citekit
python -m citekit.cli --help
```

### JavaScript
```bash
npm install -g citekit
citekit --help
```

Both CLIs provide identical functionality. If you prefer not to install globally, use `npx citekit` instead.

---

## Global Options

The following flags apply to most interactive commands:

| Flag | Shorthand | Description |
| :--- | :--- | :--- |
| `--help` | `-h` | Display help for the command. |

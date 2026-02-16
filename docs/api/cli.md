# CLI Reference

CiteKit provides a command-line interface for managing the resource lifecycle, available in both Python and JavaScript (v0.1.8+).

```bash
# Python
python -m citekit.cli [COMMAND]

# JavaScript
citekit [COMMAND]
```

If you prefer not to install globally, use `npx citekit [COMMAND]` instead.

---

## Global Commands

### `ingest`
Generates a `ResourceMap` from a file.

```bash
# Python
python -m citekit.cli ingest <path> [OPTIONS]

# JavaScript
citekit ingest <path> [OPTIONS]
```

| Option | Shorthand | Default | Description |
| :--- | :--- | :--- | :--- |
| `--type` | `-t` | (auto) | `document`, `video`, `audio`, `image`, `text`. |
| `--concurrency` | `-c` | `5` | Max parallel LLM calls. |
| `--retries` | `-r` | `3` | Max API retries for rate limits or network issues. |
| `--mapper` | `-m` | (none) | Mapper name (`gemini`) or path to a custom `.py` mapper. |
| `--mapper-config` | | (none) | JSON string of kwargs for custom mapper initialization. |

**Pro Tip**: If you omit `--type`, CiteKit will infer it from the file extension (e.g., `.pdf` -> `document`).

---

### `resolve`
Extracts a specific node into a file (Physical) or URI (Virtual).

```bash
# Python
python -m citekit.cli resolve <node_id> [OPTIONS]

# JavaScript
citekit resolve <node_id> [OPTIONS]
```

| Option | Shorthand | Description |
| :--- | :--- | :--- |
| `--resource` | `-res` | Required if `<node_id>` isn't in `rid.nid` format. |
| `--virtual` | | Return metadata (URI/JSON) only. No FFmpeg/PDF work. |

**Example**:
```bash
# Python
python -m citekit.cli resolve lecture.intro --virtual

# JavaScript
citekit resolve lecture.intro --virtual
```

Output:
```
[RESOLVING] Node: intro
[SUCCESS] Virtual resolution successful.
	Modality: video
	Address: video://lecture#t=0-120
```

---

### `list`
Explores your indexed resources.

```bash
# Python
python -m citekit.cli list [resource_id]

# JavaScript
citekit list [resource_id]
```

-   **No ID**: Lists all IDs in `.resource_maps/`.
-   **With ID**: Lists the semantic tree (nodes and their titles).

---

### `inspect`
Shows full technical metadata for a node.

```bash
# Python
python -m citekit.cli inspect <node_id> --resource <rid>

# JavaScript
citekit inspect <node_id> --resource <rid>
```
Useful for checking `bbox` coordinates or page numbers without extracting.

---

### `check-map`
Validates a manual or adapted map against the schema.

```bash
# Python
python -m citekit.cli check-map path/to/map.json

# JavaScript
citekit check-map path/to/map.json
```
**Performs**: Pydantic validation + logical sanity checks (e.g., "map is type video but has pages in location").

---

### `adapt`
The "Universal Receiver" command.

```bash
# Python
python -m citekit.cli adapt <input> --adapter <adapter>

# JavaScript
citekit adapt <input> --adapter <adapter>
```

| Option | Shorthand | Description |
| :--- | :--- | :--- |
| `--adapter` | `-a` | `graphrag`, `llamaindex`, `generic`, or path to a `.py` script. |
| `--output` | `-o` | Where to save the CiteKit map. |

---

### `serve` (MCP)
Starts the stdio MCP server for AI communication.

```bash
# Python
python -m citekit.cli serve

# JavaScript
citekit serve
```
**Internal**: Connects your local resources to the agent's brain. Not interactive.

> **Note**: As of v0.1.8, both Python and JavaScript packages have full CLI parity.

---

## Exit Codes

CiteKit uses standard Unix exit codes:
-   `0`: Success.
-   `1`: Failure (File not found, API error, Invalid schema).
-   `130`: Interrupted (Ctrl+C).

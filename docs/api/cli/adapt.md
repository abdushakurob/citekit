# `citekit adapt`

The "Universal Bridge" command. It converts external data schemas (GraphRAG, LlamaIndex, Custom JSON) into standard CiteKit `ResourceMap` objects.

## Usage

```bash
python -m citekit.cli adapt <input_path> --adapter <adapter_type> [OPTIONS]
```

## Options

### `--adapter` (`-a`)
Specifies which adapter logic to use.
*   **Built-in**: `graphrag`, `generic`.
*   **Custom**: Path to a `.py` script (e.g., `./my_adapter.py`).

### `--output` (`-o`)
Explicit path for the generated map. Defaults to `.resource_maps/<input_id>.json`.

---

## Built-in Adapters

### GraphRAG Adapter
Maps GraphRAG entities (from `.parquet` or `.json` outputs) to CiteKit nodes. It automatically sets **Virtual Locations** since GraphRAG nodes often represent concepts rather than specific file slices.

### Generic Adapter
A fallback for simple JSON arrays. Expects an array of objects with at least an `id` and `title`.

---

## Custom Adapters (Python)

You can write your own adapter in Python and run it via the CLI. Your script must define an **`adapt(data)`** function or an **`Adapter`** class.

```python
# my_adapter.py
from citekit.models import ResourceMap, Node, Location

def adapt(input_path: str) -> ResourceMap:
    # 1. Read your custom format
    # 2. Map to CiteKit Nodes
    # 3. Return a ResourceMap
    return ResourceMap(...)
```

**Run it**:
```bash
python -m citekit.cli adapt data.csv --adapter ./my_adapter.py
```

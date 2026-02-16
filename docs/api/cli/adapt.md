# `citekit adapt` — Complete API Reference

The "Universal Bridge" command. It converts external data schemas (GraphRAG, LlamaIndex, Custom JSON) into standard CiteKit `ResourceMap` objects.

## Usage

```bash
python -m citekit.cli adapt <input_path> --adapter <adapter_type> [OPTIONS]
```

## Options

### `--adapter` (`-a`)
Specifies which adapter logic to use to transform the input data.

*   **Built-in Adapters**:
    - `graphrag` - Convert GraphRAG entity/community outputs
    - `llamaindex` - Convert LlamaIndex nodes
    - `generic` - Generic JSON array converter
*   **Custom Adapter**: Path to a `.py` script (e.g., `./my_adapter.py`)
*   **Example**: `--adapter graphrag` or `--adapter ./custom.py`

### `--output` (`-o`)
Explicit path for the generated map. 

*   **Default**: `.resource_maps/<input_id>.json`
*   **Example**: `--output /data/adapted_map.json`

---

## Built-in Adapters

### 1. GraphRAG Adapter

Converts GraphRAG entities/communities/relationships to CiteKit nodes.

**Input Format**: GraphRAG `.parquet` or `.json` output files

**Mapping**:
- **Entities** → Node with `type: "entity"`
- **Communities** → Node with `type: "community"`
- **Relationships** → Node hierarchy (parent → children)

**Location**: Always `modality: "virtual"` (GraphRAG is abstract, not file-based)

**Example**:

```bash
# Convert GraphRAG community detection output
python -m citekit.cli adapt entities_and_communities.parquet \
  --adapter graphrag
```

**Output**: `.resource_maps/research_graph.json` with nodes representing entities/communities

**CLI Flow**:
```
Input (parquet)
    ↓
GraphRAGAdapter.adapt()
    ↓
Parse entities/relationships
    ↓
Create hierarchical nodes
    ↓
ResourceMap with type="virtual"
    ↓
Output (JSON)
```

### 2. LlamaIndex Adapter

Converts LlamaIndex node structures to CiteKit nodes.

**Input Format**: LlamaIndex `.json` exports or node arrays

**Mapping**:
- **LlamaIndex Node** → CiteKit Node
- **Metadata** → Location (if available)
- **Text Content** → Summary

**Location**: Attempts to infer from metadata; falls back to `virtual`

**Example**:

```bash
# Convert LlamaIndex retrieval index
python -m citekit.cli adapt index_nodes.json \
  --adapter llamaindex
```

**Input JSON Format**:
```json
[
  {
    "id": "node_1",
    "text": "Node content here...",
    "metadata": {
      "file_name": "doc.pdf",
      "page": 5
    }
  }
]
```

**Output**: CiteKit `ResourceMap` with extracted nodes

### 3. Generic Adapter

Fallback converter for custom JSON structures.

**Input Format**: Simple JSON with required fields

**Mapping**:
- `id` (string) → Node ID
- `title` (string) → Node title
- `type` (string, optional) → Node type
- `summary` (string, optional) → Node summary
- `children` (array, optional) → Child nodes

**Location**: Defaults to `modality: "virtual"`

**Example Input**:
```json
{
  "title": "My Resource",
  "nodes": [
    {
      "id": "section_1",
      "title": "Section 1",
      "type": "section",
      "summary": "Overview section"
    },
    {
      "id": "section_2",
      "title": "Section 2",
      "type": "section",
      "children": [
        {
          "id": "section_2.subsection",
          "title": "Subsection",
          "type": "subsection"
        }
      ]
    }
  ]
}
```

**CLI Usage**:
```bash
python -m citekit.cli adapt custom_data.json --adapter generic
```

---

## Custom Adapters (Python)

Write your own adapter to convert any data format to CiteKit `ResourceMap`.

### Adapter Interface

Your adapter module **must export one of**:
- An `adapt(input_path: str) -> ResourceMap` function, OR
- An `Adapter` class with an `adapt(input_path: str)` method

### Example: CSV Adapter

```python
# csv_adapter.py
import csv
from pathlib import Path
from citekit.models import ResourceMap, Node, Location

def adapt(input_path: str) -> ResourceMap:
  """Convert a CSV file to CiteKit ResourceMap."""
    
  path = Path(input_path)
  resource_id = path.stem
    
    nodes = []
    with open(input_path, 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            nodes.append(Node(
                id=f"row_{i}",
                title=row.get("name", f"Row {i}"),
                type="row",
                summary=row.get("description", ""),
                location=Location(modality="virtual", virtual_address=str(i))
            ))
    
    return ResourceMap(
        resource_id=resource_id,
        type="virtual",
        title=f"Adapted CSV: {path.name}",
        source_path=str(path.resolve()),
        nodes=nodes
    )
```

**Usage**:
```bash
python -m citekit.cli adapt data.csv --adapter ./csv_adapter.py
```

### Example: Markdown Adapter

```python
# markdown_adapter.py
import re
from pathlib import Path
from citekit.models import ResourceMap, Node, Location

class MarkdownAdapter:
  def adapt(self, input_path: str) -> ResourceMap:
    """Convert Markdown file to CiteKit nodes based on headers."""
        
    path = Path(input_path)
    resource_id = path.stem
        content = path.read_text()
        
        nodes = []
        lines = content.split('\n')
        line_num = 1
        
        for i, line in enumerate(lines):
            if line.startswith('# '):
                title = line[2:].strip()
                nodes.append(Node(
                    id=f"h1_{len(nodes)}",
                    title=title,
                    type="heading1",
                    location=Location(
                        modality="text",
                        lines=(line_num, line_num + 10)
                    )
                ))
            line_num += 1
        
        return ResourceMap(
            resource_id=resource_id,
            type="text",
            title=f"Markdown: {path.name}",
            source_path=str(path.resolve()),
            nodes=nodes
        )
```

**Usage**:
```bash
python -m citekit.cli adapt README.md --adapter ./markdown_adapter.py
```

### Adapter Best Practices

```python
from citekit.models import ResourceMap, Node, Location
from pathlib import Path
import json

def adapt(input_path: str, resource_id: str = None) -> ResourceMap:
    # 1. Validate inputs
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    resource_id = resource_id or path.stem
    
    # 2. Parse/load your data format
    try:
        with open(input_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
    
    # 3. Map to CiteKit nodes
    nodes = []
    for item in data:
        # Validate required fields
        if 'id' not in item or 'title' not in item:
            continue  # Skip invalid items
        
        nodes.append(Node(
            id=str(item['id']),
            title=str(item['title']),
            type=item.get('type', 'item'),
            summary=item.get('description'),
            location=Location(
                modality="virtual",
                virtual_address=item.get('url')
            )
        ))
    
    # 4. Return ResourceMap
    return ResourceMap(
        resource_id=resource_id,
        type="virtual",
        title=f"Adapted from {path.name}",
        source_path=str(path.resolve()),
        nodes=nodes
    )
```

---

## Adapter Development Workflow

### 1. Create Adapter File

```bash
cat > my_adapter.py << 'EOF'
from citekit.models import ResourceMap, Node, Location

def adapt(input_path: str, resource_id: str = None) -> ResourceMap:
    # Your logic here
    pass
EOF
```

### 2. Test Locally

```python
# test_adapter.py
from my_adapter import adapt
import json

result = adapt("test_input.json", "test_resource")
print(json.dumps(result.model_dump(), indent=2))
```

### 3. Use with CLI

```bash
python -m citekit.cli adapt mydata.json --adapter ./my_adapter.py
```

### 4. Verify Output

```bash
python -m citekit.cli check-map .resource_maps/test_resource.json
python -m citekit.cli list test_resource
```

---

## Error Codes & Handling

### Success (Exit Code 0)
```
✓ Successfully adapted 'data.json' → .resource_maps/data.json
  Resource ID: data
  Nodes: 15
```

### Error: Input File Not Found (Exit Code 1)
```
✗ FileNotFoundError: Input file not found: nonexistent.json
  Did you provide the correct path?
```

**Solution**: Verify file path exists

### Error: Unknown Adapter (Exit Code 1)
```
✗ ValueError: Unknown adapter: 'xyz'
  Available: graphrag, llamaindex, generic
  Or pass custom: --adapter ./my_adapter.py
```

**Solution**: Use a valid built-in adapter or provide custom adapter path

### Error: Adapter Import Failed (Exit Code 1)
```
✗ ImportError: Cannot import adapter from ./my_adapter.py
  Error: ModuleNotFoundError: No module named 'external_dep'
```

**Solution**: Install missing dependencies in your adapter

### Error: Adapter Execution Failed (Exit Code 1)
```
✗ RuntimeError: Adapter.adapt() raised exception
  Error: ValueError: Missing required field 'id' in input row 5
```

**Solution**: Verify input file format matches adapter expectations

### Error: Invalid Output (Exit Code 1)
```
✗ ValidationError: Adapter output is not a valid ResourceMap
  Error: Field 'resource_id' is required
```

**Solution**: Ensure adapter returns proper `ResourceMap` object

### Error: Permission Denied (Exit Code 1)
```
✗ PermissionError: Cannot write output file: .resource_maps/data.json
  Check directory permissions
```

**Solution**: Verify `.resource_maps/` is writable

---

## Examples

### Adapt GraphRAG Output
```bash
python -m citekit.cli adapt entities.parquet \
  --adapter graphrag
```

### Adapt LlamaIndex Output
```bash
python -m citekit.cli adapt index_nodes.json \
  --adapter llamaindex \
  --output /data/rag_map.json
```

### Adapt Generic JSON
```bash
python -m citekit.cli adapt concepts.json \
  --adapter generic
```

### Adapt Custom Format
```bash
python -m citekit.cli adapt data.csv \
  --adapter ./csv_adapter.py
```

### Chain Adapters (Multiple Resources)
```bash
# Adapt multiple sources and combine
for file in *.parquet; do
  python -m citekit.cli adapt "$file" --adapter graphrag
done

# All now available for resolution
python -m citekit.cli list
```

---

## Data Model

```typescript
interface ResourceMap {
  resource_id: string;       // Adapter-defined (usually derived from input)
  type: string;              // Usually "virtual" for adapted data
  title: string;             // Auto-generated based on adapter
  source_path: string;       // Path to original input file
  nodes: Node[];             // Hierarchical nodes
  metadata?: {
    adapter_type: string;    // "graphrag", "llamaindex", etc.
    adapter_version: string;
    original_format: string;
    [key: string]: any;
  };
  created_at: string;        // ISO 8601 timestamp
}

interface Node {
  id: string;                // From adapter input
  title: string;             // From adapter input
  type: string;              // Adapter-defined type
  location: Location;        // Usually virtual
  summary?: string;          // From adapter metadata
  children?: Node[];         // Hierarchy if available
}
```

---

## Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| "Unknown adapter" | Typo in adapter name | Check available adapters: `graphrag`, `llamaindex`, `generic` |
| "Cannot import adapter" | Python import error | Ensure custom adapter file is valid Python and accessible |
| "Invalid output" | Adapter didn't return ResourceMap | Verify adapter returns `ResourceMap` object, not dict |
| "Permission denied" | Directory not writable | Check `.resource_maps/` permissions: `chmod 755 .resource_maps/` |
| Slow adaptation | Large input file | Process in chunks or use streaming if supported |
| Memory error | File too large | Reduce input size or adapt in batches |

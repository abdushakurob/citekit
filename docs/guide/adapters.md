# Map Adapters & Extensibility

CiteKit is designed to be the **Universal Receiver** for your knowledge. While it excels at generating its own maps from raw files, you often already have structured data from other tools like **GraphRAG**, **LlamaIndex**, or your own custom scrapers.

**Map Adapters** allow you to convert any external structure into a standard `citekit.ResourceMap` so it can be used by your agents.

## 1. Using Built-in Adapters

CiteKit comes with adapters for popular frameworks.

### GraphRAG
If you use Microsoft GraphRAG, you can import its entity and community reports.

```bash
citekit adapt output/artifacts/create_final_entities.parquet.json --adapter graphrag
```

**What it does:**
-   Maps `Components` -> `citekit.Node`
-   Maps `Descriptions` -> `Node Summary`
-   Creates `virtual` locations (since graph nodes don't always have a single physical file).

### Generic (JSON)
If you have a JSON file that already matches the Schema (or is close enough), use the generic adapter.

```bash
citekit adapt my_map.json --adapter generic
```

## 2. Custom Adapters (Extensibility)

You can write your own adapter in a simple Python script. This is powerful for converting:
-   CSV exports from databases.
-   Proprietary API responses.
-   Scraped websites.

### The Protocol
Create a python file (e.g., `my_converter.py`). It must export an `adapt(input_path)` function that returns a `citekit.models.ResourceMap` object.

```python
# my_converter.py
import json
from citekit.models import ResourceMap, Node, Location

def adapt(file_path, **kwargs):
    # 1. Read your custom format
    with open(file_path) as f:
        data = json.load(f)
    
    # 2. Transform to Nodes
    nodes = []
    for item in data['items']:
        nodes.append(Node(
            id=item['id'],
            title=item['name'],
            type="custom_item",
            location=Location(modality="virtual", virtual_address=f"custom://{item['id']}")
        ))
        
    # 3. Return Map
    return ResourceMap(
        resource_id="my_custom_import",
        type="custom",
        title="My Custom Data",
        nodes=nodes
    )
```

### Running Your Adapter

Simply pass the path to your script:

```bash
citekit adapt ./raw_data.json --adapter ./my_converter.py
```

CiteKit will dynamically load your script, run the transformation, and validate/save the result.

## 3. SDK Usage

You can also use adapters programmatically:

```python
from citekit.adapters import GraphRAGAdapter
from citekit.client import CiteKitClient

adapter = GraphRAGAdapter()
resource_map = adapter.adapt("graph_output.json")

# Now you can use it just like any ingested map
client.save_map(resource_map)
```

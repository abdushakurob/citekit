# Python SDK Guide

The Python SDK is designed for seamless integration into backend services, data pipelines, and AI agent frameworks. It provides programmatic access to the full CiteKit lifecycle.

## Initialization

The `CiteKitClient` is the main entry point. It manages the mapper (Gemini by default or a custom `MapperProvider`) and the local file system (for storage and resolution).

```python
from citekit import CiteKitClient

# Default Initialization
# Uses '.resource_maps' and '.citekit_output' in current dir
client = CiteKitClient()

# Custom Configuration
client = CiteKitClient(
    base_dir="./my_library",     # Root for relative paths
    storage_dir="./maps",        # Where JSON maps are stored
    output_dir="./media",        # Where resolved files go
    concurrency_limit=10,        # Max API calls
    api_key="AIzaSy..."          # Explicit API Key (default: env.GEMINI_API_KEY)
)
```

## 1. Ingestion (Mapping)

The `ingest` method analyzes a file and returns a `ResourceMap` object.

```python
async def analyze_file():
    # Returns a ResourceMap Pydantic model
    resource_map = await client.ingest(
        resource_path="lectures/cs101.mp4",
        resource_type="video",  # Optional: 'video', 'document', 'audio', 'image', 'text'
        resource_id="cs101_lec1" # Optional: Custom ID (default: filename)
    )
    
    print(f"Title: {resource_map.title}")
    print(f"Total Nodes: {len(resource_map.nodes)}")
```

**Error Handling:**
- `FileNotFoundError`: If the input file doesn't exist.
- `ValueError`: If the file type is unsupported or prompt fails.
- `Exception`: API connection errors (CiteKit handles retries automatically).

## 2. Inspection (Planning)

Once mapped, you can retrieve and inspect the structure without hitting the API. This is heavily used by Agents to "see" what's available.

```python
# Retrieve an existing map by ID
resource_map = client.get_map("cs101_lec1")

# Iterate through top-level nodes
for node in resource_map.nodes:
    print(f"[{node.id}] {node.title} ({node.type})")
    
    # Check if it has children (nested structure)
    if node.children:
        for child in node.children:
             print(f"  - {child.title}")
```

### Accessing Metadata
Nodes contain rich metadata about their location in the source file:

```python
node = resource_map.nodes[0]

# For Video/Audio
start_time = node.location.start  # Seconds
end_time = node.location.end      # Seconds

# For Documents (PDF)
pages = node.location.pages
```

## 3. Resolution (Extraction)

Resolution converts a logical `node_id` into a physical file or actionable metadata.

### Physical Resolution
Creates a new file on disk containing *only* the relevant content.

```python
evidence = client.resolve(
    resource_id="cs101_lec1", 
    node_id="intro_chapter"
)

# The path to the newly created clip/slice
print(f"Generated: {evidence.output_path}")
# e.g., ./media/cs101_lec1_intro_chapter.mp4
```

### Virtual Resolution
Returns valid addresses and metadata *without* running extraction tools (FFmpeg/PDF).

```python
evidence = client.resolve(
    resource_id="cs101_lec1", 
    node_id="intro_chapter",
    virtual=True
)

print(evidence.output_path) # None
print(evidence.address)     # video://cs101_lec1#t=645-1350
```

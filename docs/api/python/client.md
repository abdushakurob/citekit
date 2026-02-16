# Python Client API Reference

The `CiteKitClient` is the main entry point for the CiteKit Python SDK. It provides a single interface for ingesting resources, managing resource maps locally, and resolving specific content into extracted evidence.

## Constructor

```python
from citekit import CiteKitClient
from citekit.mapper.gemini import GeminiMapper

# Using default Gemini mapper
client = CiteKitClient(api_key="YOUR_GEMINI_API_KEY")

# Using custom mapper
from my_mapper import OllamaMapper
client = CiteKitClient(mapper=OllamaMapper(model="llama3"))

# Full options
client = CiteKitClient(
    mapper=None,  # Will auto-initialize GeminiMapper if api_key is provided
    base_dir=".",
    storage_dir=".resource_maps",
    output_dir=".citekit_output",
    concurrency_limit=5,
    api_key=None,  # Reads GEMINI_API_KEY env var if not provided
    model="gemini-2.0-flash",
    max_retries=3
)
```

### Constructor Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `mapper` | `MapperProvider \| None` | `None` | Custom mapper instance. If `None` and `api_key` is provided, auto-initializes `GeminiMapper`. |
| `base_dir` | `str` | `"."` | Root directory for all CiteKit operations. Useful for serverless environments. |
| `storage_dir`| `str` | `".resource_maps"` | Relative path (from `base_dir`) where resource maps are persisted as JSON files. |
| `output_dir` | `str` | `".citekit_output"` | Relative path (from `base_dir`) where resolved clips/extracts are written. |
| `concurrency_limit` | `int` | `5` | Maximum number of parallel mapper calls (ingestion). Prevents rate-limiting. |
| `api_key` | `str \| None` | `None` | Gemini API Key (only used if `mapper=None`). Falls back to `GEMINI_API_KEY` environment variable. |
| `model` | `str` | `"gemini-2.0-flash"` | Gemini model ID to use (only used if `mapper=None`). |
| `max_retries` | `int` | `3` | Retry attempts for failed mapper API calls (only used if `mapper=None`). |

### Raises

- **`RuntimeError`**: If neither `mapper` nor `api_key` (or `GEMINI_API_KEY` env) is provided when calling `ingest()`.

---

## Methods

### `async ingest(resource_path, resource_type, resource_id=None)`

Analyzes a file using the configured mapper and generates a `ResourceMap`. This is the primary entry point for structuring your resources.

```python
async def ingest(
    resource_path: str,
    resource_type: str,
    resource_id: str | None = None
) -> ResourceMap
```

#### Parameters

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `resource_path` | `str` | Absolute or relative path to the resource file (e.g., `"lecture.mp4"`, `"/data/paper.pdf"`). |
| `resource_type` | `str` | The resource modality: `"document"`, `"video"`, `"audio"`, `"image"`, or `"text"`. |
| `resource_id` | `str \| None` | Optional custom ID for the resource. If not provided, defaults to the filename stem (e.g., `"lecture"` from `"lecture.mp4"`). |

#### Returns

- **`ResourceMap`**: The generated resource structure containing nodes, metadata, and location data.

#### Ingestion Workflow

The ingestion process is **atomic and idempotent**:

1. **Path Normalization**: Converts the path to absolute.
2. **SHA-256 Hashing**: Computes a content hash for deduplication.
3. **Cache Lookup**: Scans `storage_dir` for an existing map with the same hash (skips LLM call if found).
4. **Concurrency Gate**: Waits for a semaphore slot (respects `concurrency_limit`).
5. **Mapper Generation**: Calls the configured `MapperProvider.generate_map()`.
6. **JSON Repair**: Automatically extracts and validates JSON from the LLM response.
7. **Persistence**: Saves the map as `<resource_id>.json` in `storage_dir`.
8. **Metadata Injection**: Adds `source_hash` and `source_size` to the map.

#### Examples

**Basic ingestion**:
```python
import asyncio
from citekit import CiteKitClient

async def main():
    client = CiteKitClient(api_key="YOUR_GEMINI_API_KEY")
    
    # Ingest a lecture video
    resource_map = await client.ingest("lecture_01.mp4", "video")
    print(f"Mapped '{resource_map.resource_id}' with {len(resource_map.nodes)} top-level nodes")

asyncio.run(main())
```

**Explicit type and custom ID**:
```python
async def main():
    client = CiteKitClient(api_key="YOUR_GEMINI_API_KEY")
    
    # Force modality and use custom ID
    resource_map = await client.ingest(
        resource_path="src/main.py",
        resource_type="text",
        resource_id="codebase_v2"
    )
    print(resource_map.resource_id)  # "codebase_v2"

asyncio.run(main())
```

**Using a custom mapper**:
```python
from my_mapper import OllamaMapper

async def main():
    client = CiteKitClient(mapper=OllamaMapper(model="llama3"))
    
    # Ingest with local LLM (no API calls)
    resource_map = await client.ingest("docs/README.md", "text")
    print(f"Mapped locally in {len(resource_map.nodes)} sections")

asyncio.run(main())
```

#### Raises

- **`FileNotFoundError`**: If `resource_path` does not exist.
- **`RuntimeError`**: If no mapper is configured.
- **`ValueError`**: If `resource_type` is not recognized.

---

### `resolve(resource_id, node_id, virtual=False)`

Resolves a node to extracted evidence. Extracts the physical segment from the resource (video clip, PDF pages, image crop, etc.) or returns a metadata-only reference.

```python
def resolve(
    resource_id: str,
    node_id: str,
    virtual: bool = False
) -> ResolvedEvidence
```

#### Parameters

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `resource_id` | `str` | The resource ID (from `ingest()` or `list_maps()`). |
| `node_id` | `str` | The node ID to resolve (e.g., `"chapter_1.scene_2"`). Use `get_map(resource_id).list_node_ids()` or `citekit list <resource_id>` to discover available nodes. |
| `virtual` | `bool` | If `True`, returns only metadata without extracting physical files (no FFmpeg/PDF library calls). Defaults to `False`. |

#### Returns

- **`ResolvedEvidence`**: An object containing:
  - `output_path` (str or None): Path to the extracted file (or None if `virtual=True`)
  - `address` (str): CiteKit URI address (e.g., `video://lecture_01#t=10-20`)
  - `modality` (str): The node's modality (e.g., "video", "document")
  - `node` (Node): The resolved node object
  - `resource_id` (str): The resource ID

#### Resolution Workflow

1. **Map Lookup**: Loads the resource map from `storage_dir`.
2. **Node Search**: Finds the node by ID in the hierarchical structure.
3. **Address Building**: Generates a CiteKit URI based on the node's location.
4. **Virtual Check**: If `virtual=True`, returns address without extraction.
5. **Modality Dispatch**: Selects the appropriate resolver (VideoResolver, DocumentResolver, etc.).
6. **Physical Extraction**: Resolver writes the extracted segment to `output_dir`.

#### Examples

**Virtual resolution** (metadata only):
```python
client = CiteKitClient(api_key="YOUR_GEMINI_API_KEY")

# Get address without extracting
evidence = client.resolve(
    "lecture_01",
    "chapter_1.intro",
    virtual=True
)

print(evidence.address)     # e.g. "video://lecture_01#t=145-285"
print(evidence.output_path) # None
```

**Physical resolution** (extracts file):
```python
client = CiteKitClient(api_key="YOUR_GEMINI_API_KEY")

# Extracts video segment to .citekit_output/
evidence = client.resolve("lecture_01", "chapter_1.intro")

print(evidence.output_path)  # e.g. ".citekit_output/lecture_01_chapter_1_intro.mp4"
print(evidence.modality)     # "video"
```

**Document page extraction**:
```python
evidence = client.resolve("textbook", "chapter_2.definition")
# Output: ".citekit_output/textbook_chapter_2_definition.pdf"
# Contains only pages 12-15 (as specified in the node's location)
```

#### Raises

- **`FileNotFoundError`**: If the resource map doesn't exist.
- **`ValueError`**: If the node ID is not found in the resource.
- **`RuntimeError`**: If no resolver is available for the node's modality.

---

### `get_map(resource_id)`

Loads a previously ingested resource map from local storage.

```python
def get_map(resource_id: str) -> ResourceMap
```

#### Parameters

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `resource_id` | `str` | The resource ID to retrieve. |

#### Returns

- **`ResourceMap`**: The deserialized resource structure.

#### Example

```python
client = CiteKitClient(api_key="YOUR_GEMINI_API_KEY")

# Load an existing map
resource_map = client.get_map("lecture_01")
print(f"Resource: {resource_map.title}")
print(f"Nodes: {len(resource_map.nodes)}")
```

#### Raises

- **`FileNotFoundError`**: If no map exists for the given `resource_id`.

---

### `list_maps()`

Returns all resource IDs (ingested maps) currently stored locally.

```python
def list_maps() -> list[str]
```

#### Returns

- **`list[str]`**: Array of resource IDs.

#### Example

```python
client = CiteKitClient(api_key="YOUR_GEMINI_API_KEY")

maps = client.list_maps()
print(f"Available resources: {maps}")
# Output: ['lecture_01', 'textbook', 'codebase_v2']
```

---

### `get_structure(resource_id)`

Retrieves a resource map as a plain dictionary (JSON-serializable). Commonly used by MCP servers and integrations.

```python
def get_structure(resource_id: str) -> dict
```

#### Parameters

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `resource_id` | `str` | The resource ID to retrieve. |

#### Returns

- **`dict`**: The resource map as a plain dictionary (Pydantic model in JSON mode).

#### Example

```python
client = CiteKitClient(api_key="YOUR_GEMINI_API_KEY")

structure = client.get_structure("lecture_01")
# Can be serialized directly to JSON
import json
json_str = json.dumps(structure)
```

#### Raises

- **`FileNotFoundError`**: If no map exists for the given `resource_id`.

---

### `save_map(resource_map)`

Manually persists a `ResourceMap` to local storage. Useful for programmatically constructed or modified maps.

```python
def save_map(self, resource_map: ResourceMap) -> None
```

#### Parameters

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `resource_map` | `ResourceMap` | The resource map to persist. |

#### Example

```python
from citekit.models import ResourceMap, Node, Location

client = CiteKitClient(api_key="YOUR_GEMINI_API_KEY")

# Create a custom map
custom_map = ResourceMap(
    resource_id="custom_resource",
    type="text",
    title="My Custom Map",
    source_path="/path/to/file.txt",
    nodes=[
        Node(
            id="intro",
            title="Introduction",
            type="section",
            location=Location(modality="text", lines=(1, 10))
        ),
        Node(
            id="body",
            title="Main Content",
            type="section",
            location=Location(modality="text", lines=(11, 50))
        )
    ]
)

client.save_map(custom_map)
print(f"Saved '{custom_map.resource_id}' to storage")
```

---

## Data Models

See [Core Data Models](/api/models.md) for unified definitions across all implementations.

**Quick Reference (Python):**

```python
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ResourceType = Literal["document", "video", "audio", "image", "text", "virtual"]

class Location(BaseModel):
    modality: ResourceType
    pages: list[int] | None = None  # Document (list of pages)
    lines: tuple[int, int] | None = None  # Text
    start: float | None = None  # Video/Audio start (seconds)
    end: float | None = None  # Video/Audio end (seconds)
    bbox: tuple[float, float, float, float] | None = None  # Image [x1, y1, x2, y2]
    virtual_address: str | None = None  # Virtual reference URI

class Node(BaseModel):
    id: str
    title: str | None = None
    type: str
    location: Location
    summary: str | None = None
    children: list["Node"] = Field(default_factory=list)

class ResourceMap(BaseModel):
    resource_id: str
    type: ResourceType
    title: str
    source_path: str
    metadata: dict[str, str | int | float | None] | None = None
    nodes: list[Node] = Field(default_factory=list)
    created_at: datetime

class ResolvedEvidence(BaseModel):
    output_path: str | None = None  # None if virtual
    modality: str
    address: str  # e.g., "video://lecture_01#t=145.5-285.0"
    node: Node
    resource_id: str
```

All field names use snake_case (e.g., `resource_id`, not `resourceId`) for consistency with JSON serialization.

---

## Error Handling

### Common Errors

**Missing mapper or API key:**
```python
try:
    client = CiteKitClient()  # No mapper, no api_key
    await client.ingest("file.mp4")
except RuntimeError as e:
    print(f"Error: {e}")  # "No mapper provider configured..."
```

**Resource not found:**
```python
try:
    resource_map = client.get_map("nonexistent")
except FileNotFoundError as e:
    print(f"Error: {e}")  # "No map found for resource 'nonexistent'..."
```

**Node not found:**
```python
try:
    evidence = client.resolve("lecture_01", "invalid.node.id")
except ValueError as e:
    print(f"Error: {e}")  # "Node 'invalid.node.id' not found..."
```

---

## Complete Example: Multi-Modal RAG Pipeline

```python
import asyncio
from citekit import CiteKitClient

async def rag_pipeline():
    # Initialize client
    client = CiteKitClient(api_key="YOUR_GEMINI_API_KEY")
    
    # 1. Ingest resources
    print("Ingesting lecture...")
    video_map = await client.ingest("lecture.mp4", "video", "lecture_01")
    
    print("Ingesting textbook...")
    doc_map = await client.ingest("textbook.pdf", "document", "textbook")
    
    # 2. List all resources
    all_resources = client.list_maps()
    print(f"Mapped resources: {all_resources}")
    
    # 3. Resolve specific nodes
    for node_id in ["chapter_1.intro", "chapter_1.definition"]:
        print(f"\nResolving {node_id}...")
        
        # Virtual resolution (metadata only)
        virtual_evidence = client.resolve("lecture_01", node_id, virtual=True)
        print(f"  Address: {virtual_evidence.address}")
        
        # Physical extraction
        physical_evidence = client.resolve("lecture_01", node_id, virtual=False)
        print(f"  Extracted to: {physical_evidence.output_path}")

asyncio.run(rag_pipeline())
```

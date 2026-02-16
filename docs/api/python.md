# Python SDK Reference

The `citekit` package exports a main client class `CiteKitClient`.

## Client

```python
from citekit import CiteKitClient

client = CiteKitClient(
    mapper: MapperProvider | None = None,
    base_dir: str = ".",
    storage_dir: str = ".resource_maps",
    output_dir: str = ".citekit_output",
    concurrency_limit: int = 5
)
```

*   `mapper`: The analysis provider (e.g., `GeminiMapper`).
*   `base_dir`: The root directory for storage. Set to `tempfile.gettempdir()` for serverless.
*   `storage_dir`: Relative path for maps.
*   `output_dir`: Relative path for extracted files.
*   `concurrency_limit`: Max parallel mapper calls.
*   `api_key`: Gemini API key (optional if `mapper` is provided or env is set).
*   `model`: Gemini model name (default: `"gemini-2.0-flash"`).
*   `max_retries`: Number of retries for API failures (default: `3`).

---

## methods

### `ingest`

Uploads file to LLM and generates a map.

```python
async def ingest(
    self, 
    source_path: str | Path, 
    modality: str
) -> ResourceMap
```

*   `source_path`: Path to local file.
*   `modality`: One of `"video"`, `"audio"`, `"document"` (PDF), `"image"`, `"text"`.
*   **Returns**: `ResourceMap` object.

### `get_structure`

Retrieves an existing map from local storage.

```python
def get_structure(self, resource_id: str) -> ResourceMap
```

*   `resource_id`: The ID of the resource (usually filename stem).
*   **Returns**: `ResourceMap` object.
*   **Raises**: `FileNotFoundError` if map doesn't exist.

### `resolve`

Extracts a specific node from the source file.

```python
def resolve(
    self, 
    resource_id: str, 
    node_id: str,
    virtual: bool = False
) -> ResolvedEvidence
```

*   `resource_id`: The ID of the resource.
*   `node_id`: The ID of the node to extract.
*   `virtual`: If `True`, returns metadata only without physical extraction.
*   **Returns**: `ResolvedEvidence` object.

---

## Utilities

### `GeminiMapper`

The default analyzer using Google Gemini.

```python
from citekit import GeminiMapper

mapper = GeminiMapper(
    api_key="...", 
    model="gemini-2.0-flash",
    max_retries=3
)
```

*   `max_retries`: Number of times to retry on API failures (e.g., 429). Uses exponential backoff.

### `create_agent_context`

Aggregates multiple ResourceMaps into a single string for LLM context.

```python
from citekit import create_agent_context

context = create_agent_context([map1, map2], format="markdown")
```

> [!IMPORTANT]
> Always pass a **list** of maps, even for a single resource: `create_agent_context([map])`.

---

## Data Models

### `ResourceMap`
```python
class ResourceMap(BaseModel):
    resource_id: str
    title: str
    source_path: str
    type: str # "video" | "audio" | "document" | "image" | "text"
    nodes: List[Node]
    metadata: Dict[str, Any]
```

### `Node`
```python
class Node(BaseModel):
    id: str
    title: str
    summary: str
    type: str
    location: Location
    children: List[Node] = []
```

### `ResolvedEvidence`
```python
class ResolvedEvidence(BaseModel):
    output_path: str | None
    modality: str
    address: str
    node: Node
    resource_id: str
```

### `Location`
```python
class Location(BaseModel):
    # For Video/Audio
    start: float | None = None
    end: float | None = None
    
    # For Documents
    pages: List[int] | None = None

    # For Text/Code
    lines: Tuple[int, int] | None = None
    
    # For Images [x1, y1, x2, y2]
    bbox: Tuple[float, float, float, float] | None = None
```

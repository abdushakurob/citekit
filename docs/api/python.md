# Python SDK Reference

The `citekit` package exports a main client class `CiteKitClient`.

## Client

```python
from citekit import CiteKitClient

client = CiteKitClient(
    api_key: str | None = None,
    model_name: str = "gemini-1.5-flash",
    dirs: DirectoryConfig | None = None
)
```

*   `api_key`: Gemini API key. Defaults to `os.environ["GEMINI_API_KEY"]`.
*   `model_name`: LLM model to use for ingestion. Defaults to `gemini-1.5-flash`.
*   `dirs`: Custom directory paths for storage.

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
*   `modality`: One of `"video"`, `"audio"`, `"document"` (PDF), `"image"`.
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
async def resolve(
    self, 
    resource_id: str, 
    node_id: str
) -> ResolvedEvidence
```

*   `resource_id`: The ID of the resource.
*   `node_id`: The ID of the node to extract (found in the map).
*   **Returns**: `ResolvedEvidence` object containing `output_path`.

---

## Data Models

### `ResourceMap`
```python
class ResourceMap(BaseModel):
    resource_id: str
    title: str
    source_path: str
    type: str # "video" | "audio" | "document" | "image"
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

### `Location`
```python
class Location(BaseModel):
    # For Video/Audio
    start: float | None = None
    end: float | None = None
    
    # For Documents
    pages: List[int] | None = None
    
    # For Images
    bbox: List[int] | None = None
```

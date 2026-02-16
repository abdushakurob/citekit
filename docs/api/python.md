# Python SDK Reference

The CiteKit Python SDK provides a high-level client for managing the lifecycle of multimodal resources.

```python
from citekit import CiteKitClient
```

---

## `CiteKitClient`

The main entry point for CiteKit. It manages local storage, concurrency, and resolver orchestration.

### Constructor

```python
def __init__(
    self,
    mapper: MapperProvider | None = None,
    base_dir: str = ".",
    storage_dir: str = ".resource_maps",
    output_dir: str = ".citekit_output",
    concurrency_limit: int = 5,
    api_key: str | None = None,
    model: str = "gemini-2.0-flash",
    max_retries: int = 3,
)
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `mapper` | `MapperProvider` | `None` | A custom mapper instance. If `None`, defaults to `GeminiMapper`. |
| `base_dir` | `str` | `"."` | The root directory for all CiteKit operations. |
| `storage_dir`| `str` | `".resource_maps"` | Where JSON maps are saved (relative to `base_dir`). |
| `output_dir` | `str` | `".citekit_output"` | Where resolved clips/slices are saved (relative to `base_dir`). |
| `concurrency_limit` | `int` | `5` | Max parallel calls to the `MapperProvider` (uses `asyncio.Semaphore`). |
| `api_key` | `str` | `None` | Gemini API Key. If `None`, checks `GEMINI_API_KEY` env var. |
| `model` | `str` | `"gemini-2.0-flash"` | The Gemini model to use for the default mapper. |
| `max_retries` | `int` | `3` | Number of times to retry failed mapping attempts. |

### Ingestion

#### `async ingest(...)`
Analyzes a file and generates a `ResourceMap`.

```python
async def ingest(
    self,
    resource_path: str,
    resource_type: str,
    resource_id: str | None = None
) -> ResourceMap
```

**Internal Logic:**
1.  **Hashing**: Computes a SHA-256 hash of the file content.
2.  **Caching**: Scans `storage_dir` for existing maps with a matching `source_hash` in metadata. If found, returns the cached map immediately.
3.  **Concurrency Control**: Enters a semaphore. Only `concurrency_limit` maps are generated in parallel.
4.  **Generation**: Calls `mapper.generate_map()`.
5.  **Persistence**: Saves the resulting map as `{resource_id}.json`.

---

### Resolution

#### `resolve(...)`
Converts a node into physical or virtual evidence.

```python
def resolve(
    self,
    resource_id: str,
    node_id: str,
    virtual: bool = False
) -> ResolvedEvidence
```

**Internal Logic:**
1.  **Lookup**: Loads the map for `resource_id`.
2.  **Address Building**: Generates a standard URI (e.g. `doc://book#pages=1-2`).
3.  **Virtual Flow**: If `virtual=True`, returns metadata only (no file processing).
4.  **Physical Flow**: Selects a `Resolver` based on modality (Document, Video, etc.) and executes extraction (FFmpeg, PyMuPDF, etc.).

---

### Map Management

#### `get_map(resource_id: str) -> ResourceMap`
Loads a map from disk. Raises `FileNotFoundError` if missing.

#### `list_maps() -> list[str]`
Returns all ingested resource IDs (filenames in `storage_dir`).

#### `get_structure(resource_id: str) -> dict`
Returns the map as a plain JSON-serializable dictionary.

---

## Data Models (Pydantic)

CiteKit uses Pydantic for strict schema validation.

### `ResourceMap`
| Field | Type | Description |
| :--- | :--- | :--- |
| `resource_id` | `str` | Unique slug for the resource. |
| `type` | `str` | `video`, `audio`, `document`, `image`, `text`. |
| `title` | `str` | Human-readable title. |
| `source_path` | `str` | Absolute path to the source file. |
| `nodes` | `List[Node]` | The semantic tree of content. |
| `metadata` | `dict` | Catch-all for hashes, timestamps, etc. |

### `Node`
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `str` | Dot-separated ID (e.g. `ch1.intro`). |
| `title` | `str` | Short title. |
| `type` | `str` | e.g., `section`, `explanation`, `clip`. |
| `location` | `Location` | The physical coordinates. |
| `children` | `List[Node]` | Nested sub-nodes. |

### `Location`
| Field | Type | Modality |
| :--- | :--- | :--- |
| `pages` | `list[int]` | Document (1-indexed) |
| `lines` | `tuple[int, int]` | Text (1-indexed inclusive) |
| `start`/`end` | `float` | Video/Audio (seconds) |
| `bbox` | `tuple[float, float, float, float]` | Image (x1, y1, x2, y2) |

---

## Protocols (For Contributors)

### `MapperProvider`
Any class implementing `generate_map`.

```python
class MyMapper(MapperProvider):
    async def generate_map(
        self, 
        resource_path: str, 
        resource_type: str, 
        resource_id: str | None = None
    ) -> ResourceMap:
        ...
```

### `MapAdapter`
Any class or script implementing `adapt`.

```python
class MyAdapter(MapAdapter):
    def adapt(self, input_data: Any, **kwargs) -> ResourceMap:
        ...
```

---

## Address Utilities

CiteKit uses a URI-style protocol to point to content.

#### `parse_address(address: str) -> tuple[str, Location]`
Parses `doc://book#pages=1-2` into `('book', Location(...))`.

#### `build_address(resource_id: str, location: Location) -> str`
Converts a Python object into a string URI.

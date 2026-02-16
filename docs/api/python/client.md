# Python Client

The `CiteKitClient` is the main entry point for the CiteKit Python SDK. It coordinates ingestion, logic, and resolution.

## Constructor

```python
from citekit import CiteKitClient

client = CiteKitClient(
    mapper=None,
    base_dir=".",
    storage_dir=".resource_maps",
    output_dir=".citekit_output",
    concurrency_limit=5,
    api_key=None,
    model="gemini-2.0-flash",
    max_retries=3
)
```

### Options

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `mapper` | `MapperProvider` | `None` | Custom mapper (defaults to `GeminiMapper`). |
| `base_dir` | `str` | `"."` | Root for all operations. |
| `storage_dir`| `str` | `".resource_maps"` | Where JSON maps are saved. |
| `output_dir` | `str` | `".citekit_output"` | Where resolved clips are saved. |
| `concurrency_limit` | `int` | `5` | Max parallel LLM calls. |
| `api_key` | `str` | `None` | Gemini API Key. |
| `model` | `str` | `"gemini-2.0-flash"` | The Gemini model to use. |
| `max_retries` | `int` | `3` | Attempts for failed mappings. |

---

## Methods

### `async ingest(...)`
Analyzes a file and generates a `ResourceMap`.

```python
async def ingest(
    resource_path: str,
    resource_type: str,
    resource_id: str | None = None
) -> ResourceMap
```

#### The Ingestion Lifecycle

CiteKit ingestion is designed to be **atomic and idempotent**. When you call `ingest`, the following sequence occurs:

1.  **Normalization**: The `resource_path` is converted to an absolute path.
2.  **Hashing**: A SHA-256 content hash is computed.
3.  **Cache Lookup**: The `storage_dir` is scanned. If a map with a matching `source_hash` metadata exists, it is returned immediately.
4.  **Concurrency Gate**: The call enters a semaphore. Parallel LLM calls are capped at `concurrency_limit` (default 5).
5.  **LLM Generation**: The assigned `MapperProvider` is called.
6.  **JSON Repair Engine**: The SDK automatically attempts to balance brackets and extract JSON blocks from the LLM's raw text response.
7.  **Persistence**: The map is saved as a JSON file, and the semaphore is released.

---

### Resolution

#### `resolve(...)`
Converts a node ID into physical or virtual evidence.

```python
def resolve(
    resource_id: str,
    node_id: str,
    virtual: bool = False
) -> ResolvedEvidence
```

**Internal Logic:**
-   **Virtual**: Returns a `CiteKit URI` address without touching the disk or media tools.
-   **Physical**: Executes the modality resolver (FFmpeg/PyMuPDF) and writes the result to `output_dir`.

### `get_map(resource_id: str)`
Loads a map from disk.

### `list_maps()`
Returns all ingested resource IDs.

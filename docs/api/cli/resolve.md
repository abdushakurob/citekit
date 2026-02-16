# `citekit resolve`

Converts a semantic node ID into a physical clip, slice, or virtual address.

## Usage

```bash
python -m citekit.cli resolve <resource_id>.<node_id> [OPTIONS]
```

## Options

### `--resource` (`-res`)
Explicitly specify the resource ID if you are not using the `id.node` shorthand.
*   **Example**: `python -m citekit.cli resolve intro --resource lecture`

### `--virtual`
Enable virtual resolution mode.
*   **Behavior**: Instead of extracting a file, it returns just the URI address (e.g., `video://lecture#t=10,120`) and metadata.
*   **Why?**: Faster for serverless apps or whenever the agent only needs the citation text, not the media.

---

## `citekit inspect`

View technical metadata for a node without performing any extraction or resolution.

```bash
python -m citekit.cli inspect <node_id> --resource <rid>
```

**Returns**:
-   **ID/Title**: The semantic identifier.
-   **Modality**: (video, doc, etc.)
-   **Location**: The raw coordinates (pages, timestamps, bbox).
-   **Summary**: The LLM-generated description of that segment.

---

## Technical Flow

When you call `resolve`:
1.  **Map Lookup**: Loads the JSON map from the local index.
2.  **Resolver Selection**: Spawns the appropriate worker (FFmpeg for video, PyMuPDF for documents).
3.  **Surgical Extraction**: Slices the exact segment and saves it to `.citekit_output/`.
4.  **Evidence Return**: Returns the absolute file path and the URI address.

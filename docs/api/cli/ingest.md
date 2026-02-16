# `citekit ingest`

Generates a `ResourceMap` by analyzing a multimodal file with an LLM (defaults to Gemini).

## Usage

```bash
python -m citekit.cli ingest <path/to/file> [OPTIONS]
```

## Options

### `--type` (`-t`)
Explicitly set the resource modality. If omitted, CiteKit infers the type from the file extension.

*   **Values**: `video`, `audio`, `document`, `image`, `text`
*   **Example**: `python -m citekit.cli ingest video.mp4 --type video`

### `--concurrency` (`-c`)
Sets the maximum number of parallel LLM calls allowed during batch ingestion.
*   **Default**: `5`
*   **Why?**: Prevents rate-limiting on your Gemini/LLM API key.

### `--retries` (`-r`)
Sets the maximum number of attempts for a failed mapping call.
*   **Default**: `3`
*   **Strategy**: Uses exponential backoff (starting at 1s, doubling per failure).

---

## Behavior

1.  **Checksum Check**: CiteKit generates a SHA-256 hash of the target file. If a map with the same hash exists in `.resource_maps/`, it returns the cached version immediately.
2.  **LLM Inversion**: The mapper builds a hierarchy (e.g., Chapters -> Scenes) and converts it to a standard `ResourceMap` JSON.
3.  **Persistence**: Saves the JSON to `.resource_maps/<filename>.json`.

---

## Examples

### Ingesting for RAG
```bash
# Analyze a research paper
python -m citekit.cli ingest paper.pdf --type document
```

### High-Concurrency Video Mapping
```bash
# Map a large video with minimal retries
python -m citekit.cli ingest lecture.mp4 -t video -c 2 -r 1
```

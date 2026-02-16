# `citekit ingest` — Complete API Reference

Generates a `ResourceMap` by analyzing a multimodal file with a mapper (Gemini by default).

## Usage

```bash
python -m citekit.cli ingest <path/to/file> [OPTIONS]
```

## Options

### `--type` (`-t`)
Explicitly set the resource modality. If omitted, CiteKit infers the type from the file extension.

*   **Values**: `video`, `audio`, `document`, `image`, `text`, `virtual`
*   **Default**: Auto-detect
*   **Example**: `python -m citekit.cli ingest lecture.mp4 --type video`

### `--concurrency` (`-c`)
Sets the maximum number of parallel LLM calls allowed during batch ingestion.
*   **Default**: `5`
*   **Range**: `1` - `20` (recommended)
*   **Why?**: Prevents rate-limiting on your mapper API key.
*   **Example**: `--concurrency 2`

### `--retries` (`-r`)
Sets the maximum number of attempts for a failed mapping call.
*   **Default**: `3`
*   **Strategy**: Uses exponential backoff (starting at 1s, doubling per failure).
*   **Example**: `--retries 5`

### `--mapper` (`-m`)
Use a custom mapper instead of Gemini. Accepts either a mapper name or path to a Python file.

*   **Values**: 
  - `gemini` (default)
  - `/path/to/mapper.py` (custom mapper file)
*   **How it works**: CiteKit looks for one of:
    - A `Mapper` class implementing `MapperProvider`
    - A `create_mapper(**kwargs)` factory function
    - A `mapper` instance of `MapperProvider`
*   **Example**: `--mapper ./my_ollama_mapper.py`

### `--mapper-config`
JSON string of keyword arguments to pass when initializing a custom mapper.
*   **Format**: `--mapper-config '{"model": "llama3", "base_url": "http://localhost:11434"}'`
*   **Usage**: Only applies if `--mapper` points to a custom mapper file.

---

## Behavior

### Step-by-Step Workflow

1.  **Checksum Validation**: CiteKit generates a SHA-256 hash of the target file. If a map with the same hash exists in `.resource_maps/`, it returns the cached version immediately (skips LLM call).
2.  **File Type Resolution**: Determines the resource type from file extension (if not explicitly provided with `--type`).
3.  **Mapper Initialization**: Loads the mapper (Gemini by default, or custom if `--mapper` specified).
4.  **LLM Inversion**: The mapper analyzes the file and builds a hierarchy (e.g., Chapters → Scenes → Examples).
5.  **JSON Repair**: Automatically extracts and validates JSON from the LLM response (handles markdown backticks, trailing commas, etc.).
6.  **Persistence**: Saves the `ResourceMap` JSON to `.resource_maps/<resource_id>.json`.
7.  **Metadata Injection**: Adds `source_hash` and `source_size` to the map for future deduplication.

### Cache Behavior

- **Cache Hit**: If a file with identical content already has a map, the CLI returns the cached version without calling the mapper.
- **Cache Invalidation**: Modifying the source file invalidates the cache (hash changes).
- **Cache Location**: `.resource_maps/` directory

## Examples

### Basic ingestion (auto-detect type):
```bash
python -m citekit.cli ingest lecture.mp4
```

**Output:**
```
[INFO] Ingesting lecture.mp4 as 'video'...
[SUCCESS] Map generated: lecture_01
   Title: Introduction to Machine Learning
   Nodes: 12
```

### Explicit type specification:
```bash
python -m citekit.cli ingest textbook.pdf --type document
```

**Output:**
```
[INFO] Ingesting textbook.pdf as 'document'...
[SUCCESS] Map generated: textbook
   Title: Advanced Algorithms
   Nodes: 45
```

### With custom mapper:
```bash
python -m citekit.cli ingest code.py --mapper ./ollama_mapper.py --mapper-config '{"model": "llama3"}'
```

**Output:**
```
[INFO] Ingesting code.py as 'text'...
[SUCCESS] Map generated: code_base
   Title: Python Application
   Nodes: 28
```

### Type auto-detection not possible:
```bash
python -m citekit.cli ingest unknown_file
```

**Output:**
```
[!] Could not infer type from extension ''. Please specify --type.
```

---

## Error Codes & Handling

### Success (Exit Code 0)
```
[INFO] Ingesting file.pdf as 'document'...
[SUCCESS] Map generated: file_id
   Title: Document Title
   Nodes: 25
```

### File Not Found (Exit Code 1)
```
[ERROR] File not found: nonexistent.pdf
```

### Type Cannot Be Inferred (Exit Code 1)
```
[!] Could not infer type from extension '.xyz'. Please specify --type.
```

### Invalid Mapper File (Exit Code 1)
```
[ERROR] Could not load custom mapper from /path/to/mapper.py
```

### Invalid Mapper Config (Exit Code 1)
```
[ERROR] Invalid --mapper-config JSON: Expecting value: line 1 column 1 (char 0)
```

### Mapper Initialization Error (Exit Code 1)
```
[ERROR] Custom mapper must export a Mapper class, create_mapper() factory, or mapper instance.
```

### API/LLM Error During Mapping (Exit Code 1)
```
[ERROR] {error message from mapper}
```

**Solution**: Verify the file path is correct and the file exists.

### Error: Unknown Resource Type (Exit Code 1)
```
✗ ValueError: Unknown resource type: 'xyz'
  Valid types: video, audio, document, image, text, virtual
```

**Solution**: Use a valid resource type or rely on auto-detection from file extension.

### Error: No Mapper Configured (Exit Code 1)
```
✗ RuntimeError: No mapper provider configured.
  Set GEMINI_API_KEY or use --mapper with a custom mapper.
```

**Solution**: 
- Set `GEMINI_API_KEY` environment variable, OR
- Pass `--mapper ./custom_mapper.py`

### Error: Mapper Initialization Failed (Exit Code 1)
```
✗ RuntimeError: Failed to initialize mapper from file: ./my_mapper.py
  Could not find Mapper class, create_mapper() function, or mapper instance.
```

**Solution**: Ensure your custom mapper file exports one of:
- A class named `Mapper` implementing `MapperProvider`
- A function named `create_mapper(**kwargs)`
- A module-level `mapper` instance

### Error: JSON Repair Failed (Exit Code 1)
```
✗ ValueError: Could not extract valid JSON from mapper response.
  Mapper returned malformed response. Check mapper logs.
```

**Solution**: 
- Check the mapper's output manually
- Increase `--retries` to allow more attempts
- Switch to a different mapper

### Error: API Rate Limiting (Exit Code 1)
```
✗ RateLimitError: Mapper API returned 429 Too Many Requests
  Retrying with exponential backoff... (Attempt 2/3)
```

**Solution**:
- Reduce `--concurrency` flag
- Increase `--retries` to allow more backoff attempts
- Wait and retry manually

---

## Examples

### Basic Ingestion (Auto-Detect Type)
```bash
python -m citekit.cli ingest lecture.mp4
```
Output: `.resource_maps/lecture.json`

### Forcing a Modality
```bash
# Treat a .md file as text (not auto-detected)
python -m citekit.cli ingest README.md --type text
```

### High-Concurrency Video Mapping
```bash
python -m citekit.cli ingest long_lecture.mp4 -t video -c 2 -r 1
```

### Using a Custom Local Mapper
```bash
python -m citekit.cli ingest code.py \
  --type text \
  --mapper ./ollama_mapper.py \
  --mapper-config '{"model": "llama3"}'
```

### Ingesting Multiple Files (Shell Loop)
```bash
for file in *.mp4; do
  python -m citekit.cli ingest "$file" -t video -c 3
done
```

### Specifying a Custom Resource ID
```bash
python -m citekit.cli ingest data.pdf --type document
# Automatically becomes: .resource_maps/data.json
# Access via: citekit list data
```

---

## Data Model

The ingested `ResourceMap` follows this structure:

```typescript
interface ResourceMap {
  resource_id: string;       // Derived from filename or --mapper-config
  type: string;              // "document", "video", "audio", "image", "text"
  title: string;             // Generated by mapper
  source_path: string;       // Absolute path to the ingested file
  nodes: Node[];             // Hierarchical semantic structure
  metadata: {
    source_hash: string;     // SHA-256 hash (for deduplication)
    source_size: number;     // File size in bytes
    [key: string]: any;      // Mapper-specific metadata
  };
  created_at: string;        // ISO 8601 timestamp
}

interface Node {
  id: string;                // e.g., "chapter_1.scene_2"
  title: string;             // Human-readable name
  type: string;              // "section", "example", "definition", etc.
  location: Location;        // Temporal/spatial bounds
  summary?: string;          // LLM-generated description
  children?: Node[];         // Nested nodes
}

interface Location {
  modality: string;          // "video", "document", "audio", "image", "text", "virtual"
  seconds?: [number, number];  // Video/Audio: [start_sec, end_sec]
  pages?: number[];            // Document: [start_page, end_page]
  lines?: [number, number];    // Text: [start_line, end_line]
  bbox?: [number, number, number, number];  // Image: [x, y, w, h]
}
```

---

## Performance Notes

- **Cache Hit**: ~1ms (instant return)
- **Typical Ingestion**: 5-30 seconds (depends on file size and mapper)
- **Large Files** (>1GB video): 1-5 minutes
- **Concurrency Impact**: Higher `--concurrency` speeds up batch operations but increases API load

---

## Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| Ingestion hangs | Mapper API timeout | Increase `--retries`, reduce `--concurrency` |
| "File not found" | Typo in path | Check path with `ls` or `dir` |
| Duplicate ingestion | No caching | Delete map from `.resource_maps/` and retry |
| Wrong structure | Mapper hallucination | Use `--mapper` with more reliable mapper |
| Out of memory | Large file + low RAM | Reduce `--concurrency`, use `--virtual` mode |

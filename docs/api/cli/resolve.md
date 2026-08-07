# `citekit resolve` — Complete API Reference

Converts a semantic node ID into a physical clip, slice, or virtual address.

## Usage

```bash
# Python
python -m citekit.cli resolve <node_id> [--resource <resource_id>] [--virtual]

# JavaScript
citekit resolve <node_id> [--resource <resource_id>] [--virtual]
```

### Node ID Formats

- **Dot notation**: `resource_id.node_id` (preferred)
- **Separate flags**: `--resource <resource_id>` with `node_id` as the argument

## Options

### `--resource` (`-res`)
Explicitly specify the resource ID (if not using dot notation).
*   **Format**: `resource_id`
*   **Example**: 
```bash
# Python
python -m citekit.cli resolve --resource lecture_01 chapter_1.intro

# JavaScript
citekit resolve --resource lecture_01 chapter_1.intro
```

### `--virtual`
Enable virtual resolution mode (metadata-only, no extraction).
*   **Behavior**: Skips file extraction and returns only the URI address and metadata.
*   **Use Case**: Faster for serverless apps or when the agent only needs the citation text, not the media.
*   **Example**: 
```bash
# Python
python -m citekit.cli resolve lecture_01.chapter_1 --virtual

# JavaScript
citekit resolve lecture_01.chapter_1 --virtual
```

---

## Resolution Workflow

### Physical Resolution (Default)

1.  **Map Lookup**: Loads the JSON map from `.resource_maps/<resource_id>.json`
2.  **Node Finder**: Recursively searches the hierarchical nodes for the target `node_id`
3.  **Location Extraction**: Gets the node's `location` field (pages, timestamps, bbox, etc.)
4.  **Resolver Selection**: Spawns the appropriate worker based on modality:
    - **Video**: FFmpeg time-slice extraction
    - **Audio**: FFmpeg segment extraction
    - **Document**: PyMuPDF page extraction
    - **Image**: PIL bbox crop
    - **Text**: Native line extraction
5.  **Surgical Extraction**: Slices only the exact segment (not the entire file)
6.  **Deduplication**: Checks if output file already exists (skips re-extraction if identical)
7.  **Evidence Return**: Returns absolute file path and the URI address

### Virtual Resolution

1.  **Map Lookup**: Loads the JSON map
2.  **Node Finder**: Searches for the target node
3.  **Address Building**: Constructs a URI (e.g., `video://lecture_01#t=145-285`)
4.  **Immediate Return**: Returns address + metadata without touching disk or external tools

## Examples

### Basic resolution (physical extraction):
```bash
# Python
python -m citekit.cli resolve lecture_01.intro

# JavaScript
citekit resolve lecture_01.intro
```

**Output:**
```
[RESOLVING] Node: intro
[SUCCESS] Output: .citekit_output/lecture_01_intro.mp4
   Modality: video
   Address: video://lecture_01#t=0-60
```

### Using separate resource flag:
```bash
# Python
python -m citekit.cli resolve chapter_1.definition --resource lecture_01

# JavaScript
citekit resolve chapter_1.definition --resource lecture_01
```

**Output:**
```
[RESOLVING] Node: chapter_1.definition
[SUCCESS] Output: .citekit_output/lecture_01_chapter_1_definition.pdf
   Modality: document
  Address: doc://lecture_01#pages=12-15
```

### Virtual resolution (no extraction):
```bash
# Python
python -m citekit.cli resolve lecture_01.intro --virtual

# JavaScript
citekit resolve lecture_01.intro --virtual
```

**Output:**
```
[RESOLVING] Node: intro
[SUCCESS] Virtual resolution successful.
   Modality: video
   Address: video://lecture_01#t=0-60
```

---

## Return Format

### Physical Resolution Success
```
[SUCCESS] Output: .citekit_output/lecture_01_intro.mp4
   Modality: video
   Address: video://lecture_01#t=145-285
```

### Virtual Resolution Success
```
[SUCCESS] Virtual resolution successful.
   Modality: video
   Address: video://lecture_01#t=145-285
```

---

## Error Codes & Handling

### Missing Resource ID (Exit Code 1)
```
[!] Resource ID missing. Use --resource or rid.nid format.
```

### Node Not Found (Exit Code 1)
```
[ERROR] Node 'nonexistent_node' not found in resource 'lecture_01'.
```

### Resolver/Extraction Failure (Exit Code 1)
```
[ERROR] {resolver error message}
```

---

## `citekit inspect`

View node metadata without resolving or extracting any files.

### Usage

```bash
python -m citekit.cli inspect <resource_id>.<node_id>
# or
python -m citekit.cli inspect <node_id> --resource <resource_id>
```

### Output Example

```
[INFO] Node: chapter_1.intro
   Resource: lecture_01 (video)
   Title: Introduction and Logistics
   Type: section
   Location: modality='video' start=145.5 end=285.0 pages=None lines=None bbox=None virtual_address=None
   Summary: Covers course overview, expectations, and key learning objectives
```

### Errors

**Missing Resource ID (Exit Code 1)**:
```
[!] Resource ID missing. Use --resource or rid.nid format.
```

**Node Not Found (Exit Code 1)**:
```
[ERROR] Node 'invalid' not found in resource 'lecture_01'.
```

**Resource Not Found (Exit Code 1)**:
```
[ERROR] No map found for resource 'missing_id'. Expected at: .resource_maps/missing_id.json
```

---

## Data Model (Location)

```typescript
// Video / Audio
location: {
  modality: "video" | "audio",
  start: number;        // seconds (float)
  end: number;          // seconds (float)
}

// Document (PDF, etc.)
location: {
  modality: "document",
  pages: number[];      // list of page numbers (1-indexed)
}

// Image
location: {
  modality: "image",
  bbox?: [number, number, number, number];  // [x1, y1, x2, y2] (0-1 normalized corners)
}

// Text
location: {
  modality: "text",
  lines: [number, number];  // [start_line, end_line] (1-indexed)
}

// Virtual
location: {
  modality: "virtual",
  virtual_address?: string;
}
```

# Data Models

The common data structures shared between Python, TypeScript, and the JSON storage.

## The Map Schema

The Resource Map is the source of truth.

### JSON Structure

```json
{
  "resource_id": "string (unique)",
  "title": "string (descriptive title)",
  "source_path": "string (absolute or relative path)",
  "type": "string (video|audio|document|image|text)",
  "nodes": [
    {
      "id": "string (unique within this map)",
      "title": "string",
      "summary": "string",
      "type": "string (section|topic|scene)",
      "location": {
        "start": 0.0,
        "end": 10.5
      }
    }
  ]
}
```

## Common Node Types

The `type` field is a free-form string. However, CiteKit's default prompts encourage the LLM to use these semantic categories:

*   **Video**: `scene`, `chapter`, `dialogue`
*   **Audio**: `segment`, `speech`, `music`
*   **Text**: `class`, `function`, `method`, `section`, `header`
*   **Document**: `chapter`, `section`, `table`, `image`
*   **Image**: `object`, `text_block`, `face`

## Location Objects

The `location` object is polymorphic.

**TimeRange (Video/Audio)**
```json
{
  "start": 120.5,
  "end": 180.0
}
```

**PageRange (PDF)**
```json
{
  "pages": [1, 2, 5, 6]
}
```
*Note: Page numbers are 1-indexed to match PDF viewers.*

**LineRange (Text)**
```json
{
  "lines": [10, 25]
}
```
*Format: [start_line, end_line] (1-indexed, inclusive)*

**LineRange (Text)**
```json
{
  "lines": [10, 25]
}
```
*Format: [start_line, end_line] (1-indexed, inclusive)*

**BoundingBox (Image)**
```json
{
  "bbox": [0.1, 0.1, 0.9, 0.9]
}
```
*Format: [x1, y1, x2, y2] (Normalized 0.0 - 1.0)*

## Resolved Evidence

The object returned by `client.resolve()`.

### JSON Structure
| Field | Type | Description |
| :--- | :--- | :--- |
| `output_path` | `string` | Absolute path to the extracted file (null in virtual mode). |
| `modality` | `string` | The resource type (video, doc, etc.). |
| `address` | `string` | The CiteKit URI (e.g., `doc://id#pages=1`). |
| `resource_id` | `string` | ID of the source resource. |
| `node` | `Node` | The full node object that was resolved. |

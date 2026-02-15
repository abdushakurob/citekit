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
  "type": "string (video|audio|document|image)",
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

## Node Types

Nodes can have different `type` values depending on the modality.

*   **Video**: `scene`, `chapter`, `dialogue`
*   **Audio**: `segment`, `speech`, `music`
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

**BoundingBox (Image)**
```json
{
  "bbox": [10, 10, 100, 100]
}
```
*Format: [x, y, width, height]*

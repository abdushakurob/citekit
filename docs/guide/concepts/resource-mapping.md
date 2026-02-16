# Resource Maps

The **Resource Map** is the core abstraction in CiteKit. It is a **Semantic Index** designed for **Hierarchical Retrieval**. Think of it as a **DOM (Document Object Model) for multimodal files**.

Just as the DOM allows JavaScript to query specific elements of a webpage (`document.getElementById`), the Resource Map allows an Agent to query specific segments of a video, PDF, or image (`map.nodes['chart_1']`).

## Schema Specification

A Resource Map is a strictly typed JSON object.

```typescript
interface ResourceMap {
  resource_id: string;      // Unique identifier (slugified filename)
  source_path: string;      // Absolute path to the original file
  type: 'video' | 'audio' | 'pdf' | 'image';
  metadata: {
    title?: string;
    duration?: number;      // Seconds (Video/Audio)
    page_count?: number;    // Pages (PDF)
    dimensions?: [number, number]; // [width, height] (Image)
  };
  nodes: ResourceNode[];    // Flat list or tree of semantic units
}

interface ResourceNode {
  id: string;               // Unique ID within this resource
  title: string;
  summary?: string;         // 1-2 sentence description
  type: 'chapter' | 'scene' | 'slide' | 'section' | 'topic';
  
  // Location is a Discriminated Union based on parent type
  location: 
    | { start: number; end: number }           // Video/Audio
    | { pages: number[] }                      // PDF
    | { bbox: [x, y, w, h] };                  // Image

  children?: ResourceNode[]; // Recursive structure
}
```

## JSON Example (Video)

```json
{
  "resource_id": "cs101_lecture",
  "type": "video",
  "nodes": [
    {
      "id": "intro",
      "title": "Introduction",
      "location": { "start": 0, "end": 120 }
    },
    {
      "id": "concept_recursion",
      "title": "Recursion Explained",
      "summary": "Visual demonstration of a recursive function stack.",
      "location": { "start": 300, "end": 450 },
      "children": [
        {
           "id": "base_case",
           "title": "The Base Case",
           "location": { "start": 300, "end": 345 }
        }
      ]
    }
  ]
}
```

## Design Philosophy

### 1. Structure over Content
The map does **not** contain the transcription or full text. It contains the *structure*. This keeps the map small (typically < 2KB), allowing it to fit into any Agent's context window with negligible cost.

### 2. Deterministic IDs
Node IDs are generated to be human-readable and deterministic where possible. This allows Agents to "hallucinate" the correct ID often, or at least reason about it easily (e.g., `chapter_1`, `chapter_2`).

### 3. Hierarchical
Content is rarely flat. A video has Chapters -> Scenes -> Shots. A book has Parts -> Chapters -> Sections. CiteKit preserves this hierarchy, allowing Agents to choose the right level of granularity (e.g., "Give me the whole chapter" vs "Give me just this paragraph").

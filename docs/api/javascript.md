# JavaScript/TypeScript SDK Reference

The `citekit` package exports a main client class `CiteKitClient`.

## Client

```typescript
import { CiteKitClient } from 'citekit';

const client = new CiteKitClient({
    apiKey?: string;        // Defaults to process.env.GEMINI_API_KEY
    model?: string;         // Defaults to 'gemini-2.0-flash'
    baseDir?: string;       // Defaults to '.', set to os.tmpdir() for serverless
    storageDir?: string;    // Defaults to '.resource_maps'
    outputDir?: string;     // Defaults to '.citekit_output'
    maxRetries?: number;    // Defaults to 3
});
```

---

## Methods

### `ingest`

Uploads file to LLM and generates a map.

```typescript
async ingest(
    sourcePath: string, 
    modality: 'video' | 'audio' | 'document' | 'image' | 'text'
): Promise<ResourceMap>
```

*   `sourcePath`: Path to local file.
*   `modality`: Type of media.
*   **Returns**: `Promise<ResourceMap>`.

### `getStructure`

Retrieves an existing map from local storage.

```typescript
getStructure(resourceId: string): ResourceMap
```

*   `resourceId`: The ID of the resource.
*   **Returns**: `ResourceMap` object.
*   **Throws**: Error if map doesn't exist.

### `resolve`

Extracts a specific node from the source file.

```typescript
async resolve(
    resourceId: string, 
    nodeId: string,
    options?: { virtual?: boolean }
): Promise<ResolvedEvidence>
```

*   `resource_id`: The ID of the resource.
*   `node_id`: The ID of the node to extract.
*   `options.virtual`: If `true`, returns metadata only (timestamps/pages) without physical file extraction. Required for environments without FFmpeg.
*   **Returns**: `Promise<ResolvedEvidence>`.

---

## Utilities

### `GeminiMapper`

```typescript
import { GeminiMapper } from 'citekit';

const mapper = new GeminiMapper(
    apiKey, 
    "gemini-2.0-flash", 
    3 // maxRetries
);
```

### `createAgentContext`

```typescript
import { createAgentContext } from 'citekit';

const context = createAgentContext(maps, 'markdown');
```

> [!IMPORTANT]
> Always pass an **array** of maps, even for a single resource: `createAgentContext([map])`.

---

## Data Models

### `ResourceMap`
```typescript
interface ResourceMap {
    resource_id: string;
    title: string;
    source_path: string;
    type: 'video' | 'audio' | 'document' | 'image' | 'text';
    nodes: Node[];
    metadata: Record<string, any>;
}
```

### `Node`
```typescript
interface Node {
    id: string;
    title: string;
    summary: string;
    type: string;
    location: Location;
    children?: Node[];
}
```

### `ResolvedEvidence`
```typescript
interface ResolvedEvidence {
    output_path?: string;   // Path to file. Undefined if virtual: true.
    modality: string;
    address: string;        // URI-style address, e.g. doc://book#pages=12-13
    node: Node;
    resource_id: string;
}
```

### `Location`
```typescript
interface Location {
    // For Text (1-indexed, inclusive)
    lines?: [number, number];
    start?: number;
    end?: number;
    
    // For Documents (1-indexed page numbers)
    pages?: number[];
    
    // For Images [x1, y1, x2, y2] (0.0 - 1.0)
    bbox?: [number, number, number, number];
}
```

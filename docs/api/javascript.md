# JavaScript/TypeScript SDK Reference

The `citekit` package exports a main client class `CiteKitClient`.

## Client

```typescript
import { CiteKitClient } from 'citekit';

const client = new CiteKitClient({
    apiKey?: string;        // Defaults to process.env.GEMINI_API_KEY
    modelName?: string;     // Defaults to 'gemini-1.5-flash'
    baseDir?: string;       // Defaults to process.cwd()
});
```

---

## Methods

### `ingest`

Uploads file to LLM and generates a map.

```typescript
async ingest(
    sourcePath: string, 
    modality: 'video' | 'audio' | 'document' | 'image'
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
    nodeId: string
): Promise<ResolvedEvidence>
```

*   `resourceId`: The ID of the resource.
*   `nodeId`: The ID of the node to extract.
*   **Returns**: `Promise<ResolvedEvidence>` containing `output_path`.

---

## interfaces

### `ResourceMap`
```typescript
interface ResourceMap {
    resource_id: string;
    title: string;
    source_path: string;
    type: 'video' | 'audio' | 'document' | 'image';
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

### `Location`
```typescript
interface Location {
    // For Video/Audio (seconds)
    start?: number;
    end?: number;
    
    // For Documents (1-indexed page numbers)
    pages?: number[];
    
    // For Images ([x, y, width, height])
    bbox?: number[];
}
```

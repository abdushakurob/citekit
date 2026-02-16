# JavaScript/TypeScript SDK Reference

The CiteKit JavaScript SDK is written in TypeScript and provides a modern, asynchronous API for managing multimodal resources.

```typescript
import { CiteKitClient } from 'citekit';
```

---

## `CiteKitClient`

The primary class for interacting with CiteKit in Node.js environments.

### Constructor Options

```typescript
interface CiteKitClientOptions {
    baseDir?: string;      // Base directory for all files (Default: ".")
    storageDir?: string;   // Map storage path (Default: ".resource_maps")
    outputDir?: string;    // Clippings output path (Default: ".citekit_output")
    apiKey?: string;       // Gemini API Key
    model?: string;        // Gemini Model (Default: "gemini-2.0-flash")
    maxRetries?: number;   // Mapping retries (Default: 3)
    mapper?: MapperProvider; // Custom mapper implementation
}

const client = new CiteKitClient(options);
```

---

### Ingestion

#### `async ingest(...)`
Analyzes a file and produces a `ResourceMap`.

```typescript
async ingest(
    resourcePath: string,
    resourceType: string,
    options?: { resourceId?: string }
): Promise<ResourceMap>
```

**Technical Features:**
*   **Hashing**: Uses `node:crypto` (SHA-256) to index content.
*   **Deduplication**: Automatically skip LLM calls if a map with the same hash exists in `storageDir`.
*   **Concurrency Locking**: Uses an internal `queue` and `activeRequests` counter (Semaphore pattern) to limit parallel API calls to **5** by default.

---

### Resolution

#### `async resolve(...)`
Converts a node ID into physical or virtual evidence.

```typescript
async resolve(
    resourceId: string, 
    nodeId: string, 
    options?: { virtual?: boolean }
): Promise<ResolvedEvidence>
```

**Technical Features:**
*   **Virtual Mode**: Returns a URI address immediately without touching FFmpeg or PDF tools.
*   **Physical Mode**: 
    -   **Documents**: Uses `pdf-lib` to slice PDF pages.
    -   **Video**: Uses `fluent-ffmpeg` to extract clips.
    -   **Text**: Uses native Node.js streams to slice line ranges.

---

### Map Management

#### `getMap(resourceId: string): ResourceMap`
Loads a map from disk. Synchonous.

#### `listMaps(): string[]`
Returns IDs of all locally stored maps.

#### `getStructure(resourceId: string): ResourceMap`
Alias for `getMap`, used for standardized terminology.

---

## Core Interfaces

### `ResourceMap`
```typescript
interface ResourceMap {
    resource_id: string;
    type: 'video' | 'audio' | 'document' | 'image' | 'text';
    title: string;
    source_path: string;
    nodes: Node[];
    metadata: Record<string, any>;
    created_at: string;
}
```

### `Node`
```typescript
interface Node {
    id: string;
    title?: string;
    type: string;
    location: Location;
    summary?: string;
    children?: Node[];
}
```

### `Location`
```typescript
interface Location {
    modality: string;
    pages?: number[];
    lines?: [number, number];
    start?: number;
    end?: number;
    bbox?: [number, number, number, number];
}
```

---

## Extension Protocols

### `MapperProvider`
Implement this to use your own LLM or service for mapping.

```typescript
interface MapperProvider {
    generateMap(
        resourcePath: string, 
        resourceType: string, 
        resourceId?: string
    ): Promise<ResourceMap>;
}
```

### `MapAdapter`
Implement this to convert external JSON/Objects into CiteKit format.

```typescript
interface MapAdapter {
    adapt(input: any, options?: any): Promise<ResourceMap>;
}
```

---

## Address Utilities

#### `parseAddress(address: string): { resourceId: string, location: Location }`
Parses strings like `video://lecture#t=10,20`.

#### `buildAddress(resourceId: string, location: Location): string`
Generates CiteKit URIs for easy grounding in LLM prompts.

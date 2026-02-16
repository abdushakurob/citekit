# JavaScript/TypeScript Client API Reference

The `CiteKitClient` is the primary interface for CiteKit in Node.js and TypeScript environments. It provides async/await-based ingestion, map management, and resolution.

## Constructor

```typescript
import { CiteKitClient } from 'citekit';
import { OllamaMapper } from './ollama-mapper';

// Using default Gemini mapper
const client = new CiteKitClient({
    apiKey: "YOUR_GEMINI_API_KEY"
});

// Using custom mapper
const client = new CiteKitClient({
    mapper: new OllamaMapper("llama3")
});

// Full options
const client = new CiteKitClient({
    apiKey?: "YOUR_GEMINI_API_KEY",
    baseDir?: ".",
    storageDir?: ".resource_maps",
    outputDir?: ".citekit_output",
    model?: "gemini-2.0-flash",
    maxRetries?: 3,
    concurrencyLimit?: 5,
    mapper?: undefined
});
```

### Constructor Options

```typescript
interface CiteKitClientOptions {
    /** Gemini API Key. Falls back to GEMINI_API_KEY environment variable. */
    apiKey?: string;

    /** Gemini Model ID (default: "gemini-2.0-flash") */
    model?: string;

    /** Max retries for Gemini API calls (default: 3) */
    maxRetries?: number;

    /** Base directory for all CiteKit operations. Useful for serverless (e.g., /tmp). */
    baseDir?: string;

    /** Directory where resource maps are stored (relative to baseDir). Default: ".resource_maps" */
    storageDir?: string;

    /** Directory for resolved output files (relative to baseDir). Default: ".citekit_output" */
    outputDir?: string;

    /** Max concurrent ingestion calls (default: 5). Prevents rate-limiting. */
    concurrencyLimit?: number;

    /** Custom mapper implementation. If provided, overrides Gemini mapper. */
    mapper?: MapperProvider;
}
```

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `apiKey` | `string \| undefined` | `GEMINI_API_KEY` env | Gemini API Key (only used if `mapper` is not provided). |
| `model` | `string` | `"gemini-2.0-flash"` | Gemini model ID (only used if `mapper` is not provided). |
| `maxRetries` | `number` | `3` | Retry attempts for failed mapper calls (only used if `mapper` is not provided). |
| `baseDir` | `string` | `"."` | Root directory for all operations (useful in serverless environments). |
| `storageDir` | `string` | `".resource_maps"` | Relative path where resource maps are persisted as JSON. |
| `outputDir` | `string` | `".citekit_output"` | Relative path where resolved clips/extracts are written. |
| `concurrencyLimit` | `number` | `5` | Maximum number of parallel mapper calls (ingestion). |
| `mapper` | `MapperProvider \| undefined` | `undefined` | Custom mapper instance. If provided, Gemini is not used. |

### Throws

- **`Error`**: If neither `mapper` nor `apiKey` (or `GEMINI_API_KEY` env) is provided when calling `ingest()`.

---

## Methods

### `async ingest(resourcePath, resourceType, options?)`

Analyzes a file using the configured mapper and generates a `ResourceMap`. This is the primary entry point for structuring your resources.

```typescript
async ingest(
    resourcePath: string,
    resourceType: 'video' | 'audio' | 'document' | 'image' | 'text',
    options?: { resourceId?: string }
): Promise<ResourceMap>
```

#### Parameters

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `resourcePath` | `string` | Absolute or relative path to the resource file. |
| `resourceType` | `'video' \| 'audio' \| 'document' \| 'image' \| 'text'` | The resource modality. |
| `options?.resourceId` | `string \| undefined` | Optional custom ID. Defaults to the filename stem. |

#### Returns

- **`Promise<ResourceMap>`**: The generated resource structure containing nodes, metadata, and location data.

#### Ingestion Workflow

The ingestion process is **atomic and idempotent**:

1. **Path Validation**: Checks that the file exists.
2. **SHA-256 Hashing**: Computes a content hash for deduplication.
3. **Cache Lookup**: Scans `storageDir` for an existing map with the same hash (skips LLM call if found).
4. **Concurrency Gate**: Waits for a semaphore slot (respects `concurrencyLimit`).
5. **Mapper Generation**: Calls the configured `MapperProvider.generateMap()`.
6. **JSON Extraction**: Automatically extracts JSON from the LLM response.
7. **Persistence**: Saves the map as `<resourceId>.json` in `storageDir`.
8. **Metadata Injection**: Adds `source_hash` and `source_size` to the map.

#### Examples

**Basic ingestion**:
```typescript
import { CiteKitClient } from 'citekit';

const client = new CiteKitClient({
    apiKey: process.env.GEMINI_API_KEY
});

const resourceMap = await client.ingest('lecture_01.mp4', 'video');
console.log(`Mapped '${resourceMap.resource_id}' with ${resourceMap.nodes.length} nodes`);
```

**Explicit type and custom ID**:
```typescript
const resourceMap = await client.ingest(
    'src/main.ts',
    'text',
    { resourceId: 'codebase_v2' }
);
console.log(resourceMap.resource_id);  // "codebase_v2"
```

**Using a custom mapper**:
```typescript
import { OllamaMapper } from './ollama-mapper';

const client = new CiteKitClient({
    mapper: new OllamaMapper('llama3')
});

// Ingest with local LLM (no API calls)
const resourceMap = await client.ingest('docs/README.md', 'text');
console.log(`Mapped locally with ${resourceMap.nodes.length} sections`);
```

**Concurrent ingestion**:
```typescript
// Multiple ingests run in parallel (respecting concurrencyLimit)
const maps = await Promise.all([
    client.ingest('video1.mp4', 'video'),
    client.ingest('document1.pdf', 'document'),
    client.ingest('code.ts', 'text')
]);

console.log(`Ingested ${maps.length} resources`);
```

#### Throws

- **`Error`**: If `resourcePath` does not exist.
- **`Error`**: If no mapper is configured.
- **`Error`**: If `resourceType` is not recognized.

---

### `async resolve(resourceId, nodeId, options?)`

Resolves a node to extracted evidence. Extracts the physical segment from the resource (video clip, PDF pages, image crop, etc.) or returns a metadata-only reference.

```typescript
async resolve(
    resourceId: string,
    nodeId: string,
    options?: { virtual?: boolean }
): Promise<ResolvedEvidence>
```

#### Parameters

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `resourceId` | `string` | The resource ID (from `ingest()` or `listMaps()`). |
| `nodeId` | `string` | The node ID to resolve (e.g., `"chapter_1.scene_2"`). |
| `options?.virtual` | `boolean \| undefined` | If `true`, returns metadata without extracting files (no FFmpeg/PDF library calls). Defaults to `false`. |

#### Returns

- **`Promise<ResolvedEvidence>`**: An object containing:
  - `output_path` (string or undefined): Path to the extracted file (undefined if `virtual=true`)
  - `address` (string): CiteKit URI address (e.g., `"video://lecture_01#t=10-20"`)
  - `modality` (string): The node's modality (e.g., "video", "document")
  - `node` (Node): The resolved node object
  - `resource_id` (string): The resource ID

#### Resolution Workflow

1. **Map Lookup**: Loads the resource map from `storageDir`.
2. **Node Search**: Recursively finds the node by ID in the hierarchical structure.
3. **Address Building**: Generates a CiteKit URI based on the node's location.
4. **Virtual Check**: If `virtual=true`, returns address without extraction.
5. **Modality Dispatch**: Selects the appropriate resolver (VideoResolver, DocumentResolver, etc.).
6. **Physical Extraction**: Resolver writes the extracted segment to `outputDir` (async I/O).

#### Examples

**Virtual resolution** (metadata only):
```typescript
const client = new CiteKitClient({
    apiKey: process.env.GEMINI_API_KEY
});

const evidence = await client.resolve(
    'lecture_01',
    'chapter_1.intro',
    { virtual: true }
);

console.log(evidence.address);     // e.g., "video://lecture_01#t=145-285"
console.log(evidence.output_path); // undefined
```

**Physical resolution** (extracts file):
```typescript
const evidence = await client.resolve('lecture_01', 'chapter_1.intro');

console.log(evidence.output_path);  // e.g., ".citekit_output/lecture_01_chapter_1_intro.mp4"
console.log(evidence.modality);     // "video"
```

**Document page extraction**:
```typescript
const evidence = await client.resolve('textbook', 'chapter_2.definition');
// Output: ".citekit_output/textbook_chapter_2_definition.pdf"
// Contains only pages 12-15 (as specified in the node's location)
```

**Resolve multiple nodes in parallel**:
```typescript
const nodeIds = ['chapter_1.intro', 'chapter_1.body', 'chapter_1.conclusion'];

const allEvidence = await Promise.all(
    nodeIds.map(id => client.resolve('lecture_01', id))
);

allEvidence.forEach(ev => {
    console.log(`${ev.node.title}: ${ev.output_path}`);
});
```

#### Throws

- **`Error`**: If the resource map doesn't exist.
- **`Error`**: If the node ID is not found.
- **`Error`**: If no resolver is available for the node's modality.

---

### `getMap(resourceId)`

Loads a previously ingested resource map from local storage.

```typescript
getMap(resourceId: string): ResourceMap
```

#### Parameters

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `resourceId` | `string` | The resource ID to retrieve. |

#### Returns

- **`ResourceMap`**: The deserialized resource structure.

#### Example

```typescript
const client = new CiteKitClient({
    apiKey: process.env.GEMINI_API_KEY
});

const resourceMap = client.getMap('lecture_01');
console.log(`Resource: ${resourceMap.title}`);
console.log(`Nodes: ${resourceMap.nodes.length}`);
```

#### Throws

- **`Error`**: If no map exists for the given `resourceId`.

---

### `listMaps()`

Returns all resource IDs (ingested maps) currently stored locally.

```typescript
listMaps(): string[]
```

#### Returns

- **`string[]`**: Array of resource IDs.

#### Example

```typescript
const client = new CiteKitClient({
    apiKey: process.env.GEMINI_API_KEY
});

const maps = client.listMaps();
console.log(`Available resources: ${maps.join(', ')}`);
// Output: Available resources: lecture_01, textbook, codebase_v2
```

---

### `getStructure(resourceId)`

Retrieves a resource map as a plain JavaScript object (JSON-serializable). Commonly used by MCP servers and integrations.

```typescript
getStructure(resourceId: string): ResourceMap
```

#### Parameters

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `resourceId` | `string` | The resource ID to retrieve. |

#### Returns

- **`ResourceMap`**: The resource map as a plain object (ready for JSON serialization).

#### Example

```typescript
const client = new CiteKitClient({
    apiKey: process.env.GEMINI_API_KEY
});

const structure = client.getStructure('lecture_01');
// Can be serialized directly to JSON
const jsonStr = JSON.stringify(structure);
console.log(jsonStr);
```

#### Throws

- **`Error`**: If no map exists for the given `resourceId`.

---

## Type Definitions

See [Core Data Models](/api/models.md) for unified definitions across all implementations.

**Quick Reference (TypeScript):**

```typescript
export interface ResourceMap {
    resource_id: string;    // Unique identifier
    type: "document" | "video" | "audio" | "image" | "text" | "virtual";
    title: string;          // Human-readable title
    source_path: string;    // Absolute path to the source file
    nodes: Node[];          // Hierarchical nodes
    metadata?: Record<string, string | number | null>;  // Custom metadata
    created_at: string;     // ISO 8601 timestamp
}

export interface Node {
    id: string;             // Unique within resource (e.g., "chapter_1.scene_2")
    title?: string;         // Display name
    type: string;           // "section", "scene", "chapter", "class", "function", etc.
    location: Location;     // Temporal/spatial bounds
    summary?: string;       // Brief description
    children?: Node[];      // Nested nodes (optional)
}

export interface Location {
    modality: "document" | "video" | "audio" | "image" | "text" | "virtual";
    start?: number;          // Video/Audio start (seconds)
    end?: number;            // Video/Audio end (seconds)
    pages?: number[];        // Document pages (1-indexed list)
    lines?: [number, number]; // Text lines (1-indexed)
    bbox?: [number, number, number, number];  // Image bbox [x1, y1, x2, y2] 0-1 normalized corners
    virtual_address?: string; // Virtual reference URI
}

export interface ResolvedEvidence {
    output_path?: string;   // Path to extracted file (undefined if virtual)
    modality: string;       // Node's modality
    address: string;        // CiteKit URI (e.g., "video://lecture_01#t=145.5-285.0")
    node: Node;             // The resolved node
    resource_id: string;    // The resource ID
}
```

All field names use snake_case (e.g., `resource_id`, not `resourceId`) for consistency with JSON serialization across all implementations (Python, JavaScript, MCP).

---

## Error Handling

### Common Errors

**Missing mapper or API key:**
```typescript
try {
    const client = new CiteKitClient();  // No mapper, no apiKey
    await client.ingest('file.mp4', 'video');
} catch (error) {
    console.error(error.message);  // "GEMINI_API_KEY or custom 'mapper' required..."
}
```

**Resource not found:**
```typescript
try {
    const map = client.getMap('nonexistent');
} catch (error) {
    console.error(error.message);  // "No map found for resource 'nonexistent'..."
}
```

**Node not found:**
```typescript
try {
    const evidence = await client.resolve('lecture_01', 'invalid.node.id');
} catch (error) {
    console.error(error.message);  // "Node 'invalid.node.id' not found..."
}
```

---

## Complete Example: Multi-Modal RAG Pipeline

```typescript
import { CiteKitClient } from 'citekit';

async function ragPipeline() {
    // Initialize client
    const client = new CiteKitClient({
        apiKey: process.env.GEMINI_API_KEY
    });

    // 1. Ingest resources
    console.log('Ingesting lecture...');
    const videoMap = await client.ingest('lecture.mp4', 'video', { resourceId: 'lecture_01' });

    console.log('Ingesting textbook...');
    const docMap = await client.ingest('textbook.pdf', 'document', { resourceId: 'textbook' });

    // 2. List all resources
    const allResources = client.listMaps();
    console.log(`Mapped resources: ${allResources.join(', ')}`);

    // 3. Resolve specific nodes
    const nodeIds = ['chapter_1.intro', 'chapter_1.definition'];
    
    for (const nodeId of nodeIds) {
        console.log(`\nResolving ${nodeId}...`);

        // Virtual resolution (metadata only)
        const virtualEvidence = await client.resolve('lecture_01', nodeId, { virtual: true });
        console.log(`  Address: ${virtualEvidence.address}`);

        // Physical extraction
        const physicalEvidence = await client.resolve('lecture_01', nodeId);
        console.log(`  Extracted to: ${physicalEvidence.output_path}`);
    }

    // 4. Export a resource structure (e.g., for MCP)
    const structure = client.getStructure('lecture_01');
    console.log(`\nStructure JSON: ${JSON.stringify(structure, null, 2)}`);
}

ragPipeline().catch(console.error);
```

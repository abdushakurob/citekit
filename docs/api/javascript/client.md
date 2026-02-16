# JavaScript Client

The `CiteKitClient` is the primary interface for CiteKit in Node.js/TypeScript.

## Constructor

```typescript
import { CiteKitClient } from 'citekit';

const client = new CiteKitClient({
    apiKey: "...",           // Required for Gemini
    baseDir: ".",            // Root directory
    storageDir: ".maps",     // Map cache path
    outputDir: ".output",    // Clipping output path
    maxRetries: 3            // API retry count
});
```

### Options

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `apiKey` | `string` | `undefined` | Gemini API Key. |
| `baseDir` | `string` | `"."` | Root path for operations. |
| `storageDir` | `string` | `".resource_maps"` | Where JSON maps are stored. |
| `outputDir` | `string` | `".citekit_output"` | Where resolved clips are saved. |
| `maxRetries` | `number` | `3` | Number of mapping retries. |
| `mapper` | `MapperProvider`| `undefined` | Custom mapper instance. |

---

## Methods

### `async ingest(...)`
Analyzes a file and generates a `ResourceMap`.

```typescript
async ingest(
    resourcePath: string,
    resourceType: 'video' | 'document' | 'text',
    options?: { resourceId?: string }
): Promise<ResourceMap>
```

#### The Ingestion Workflow

CiteKit for JavaScript is optimized for asynchronous, local-first workflows.

1.  **Identity Verification**: Computes a SHA-256 hash of the input file.
2.  **Deduplication**: If a resource map for this hash is found in `storageDir`, the SDK reuses it without calling the LLM.
3.  **Concurrency Locking**: 
    -   Requests are processed through an internal `async` queue.
    -   Parallelism is managed via an `activeRequests` counter.
4.  **Robust Mapping**: The `MapperProvider` generates the structure.
5.  **JSON Patching**: The SDK includes a "Repair Layer" that extracts JSON blocks from LLM markdown and fixes common syntax errors (e.g., trailing commas).
6.  **Storage**: The result is serialized and saved to the `resource_id`.json file.

---

### `async resolve(...)`
Converts a node ID into physical or virtual evidence.

```typescript
async resolve(
    resourceId: string,
    nodeId: string,
    options?: { virtual?: boolean }
): Promise<ResolvedEvidence>
```

**Internal Logic:**
-   **Address Determinism**: Addresses are built using CiteKit's standard URI protocol (e.g. `doc://book#pages=1-2`).
-   **Extraction**: Modality-specific resolvers (fluent-ffmpeg or pdf-lib) extract the segment only if the physical file does not already exist in `outputDir`.

### `getMap(resourceId: string)`
Returns a loaded map from disk.

### `listMaps()`
Lists all ingested resource IDs.

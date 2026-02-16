# JavaScript Mappers — Complete API Reference

Mappers analyze files and return the structured semantic map. Implement `MapperProvider` to use custom LLMs.

---

## `GeminiMapper`

The default mapper implementation using the Google Generative AI SDK.

### Constructor

```typescript
import { GeminiMapper } from 'citekit';

const mapper = new GeminiMapper(
    apiKey: string,
    model?: string,
    maxRetries?: number
);
```

### Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `apiKey` | `string` | (required) | Gemini API Key. Falls back to `GEMINI_API_KEY` environment variable. |
| `model` | `string` | `"gemini-2.0-flash"` | Gemini model to use: `gemini-2.0-flash`, `gemini-1.5-pro`, `gemini-1.5-flash`. |
| `maxRetries` | `number` | `3` | Number of retries for failed API calls (with exponential backoff). |

### Methods

#### `async generateMap(resourcePath, resourceType, resourceId?)`

Analyzes a file and generates a structured `ResourceMap`.

```typescript
async generateMap(
    resourcePath: string,
    resourceType: string,
    resourceId?: string
): Promise<ResourceMap>
```

**Parameters:**
- `resourcePath` (string): Path to the resource file
- `resourceType` (string): One of `document`, `video`, `audio`, `image`, `text`
- `resourceId` (string, optional): Custom ID; defaults to filename stem

**Returns:** `Promise<ResourceMap>`

**Example:**

```typescript
import { GeminiMapper } from 'citekit';

const mapper = new GeminiMapper(process.env.GEMINI_API_KEY);

// Map a PDF
const resourceMap = await mapper.generateMap(
    'paper.pdf',
    'document',
    'research_paper'
);

console.log(`Generated map with ${resourceMap.nodes.length} nodes`);
```

### Error Codes

**Success**:
```typescript
ResourceMap { resource_id: "...", nodes: [...] }
```

**Missing API Key**:
```
Error: GEMINI_API_KEY not set. Pass apiKey parameter or set environment variable.
```

**Solution**: Set `GEMINI_API_KEY` environment variable or pass to constructor

**Invalid API Key**:
```
Error: Invalid API key. Check GEMINI_API_KEY value.
Response code: 401 Unauthorized
```

**Solution**: Verify API key is correct

**Rate Limiting**:
```
Error: API rate limit exceeded after 3 retries
Recommendation: Increase maxRetries, reduce concurrency, or wait
```

**Solution**: Reduce concurrency, increase `maxRetries`, or wait

**Model Not Found**:
```
Error: Model 'gemini-xyz' not found
Available models: gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash
```

**Solution**: Use a valid model name

**Network Timeout**:
```
Error: Gemini API did not respond within 60 seconds
Increase timeout or retry
```

**Solution**: Check network, increase timeout, retry later

**Malformed Response**:
```
Error: Could not extract valid JSON from Gemini response
Retrying...
```

**Solution**: Increase `maxRetries`, try different model

---

## `MapperProvider` (Interface)

Implement this interface to create custom mappers.

### Interface Definition

```typescript
import type { ResourceMap } from 'citekit';

export interface MapperProvider {
    /**
     * Generate a ResourceMap from a resource file.
     *
     * @param resourcePath - Path to the resource (file or URL)
     * @param resourceType - Modality (document, video, audio, image, text)
     * @param resourceId - Optional custom ID
     * @returns ResourceMap with hierarchical nodes
     * @throws FileNotFoundError if resource_path doesn't exist
     * @throws ValueError if resource_type is invalid
     * @throws RuntimeError if generation fails
     */
    generateMap(
        resourcePath: string,
        resourceType: string,
        resourceId?: string
    ): Promise<ResourceMap>;
}
```

### Custom Mapper Example: Ollama Local LLM

```typescript
// ollama-mapper.ts
import type { MapperProvider, ResourceMap, Node } from 'citekit';
import { readFileSync } from 'node:fs';
import { basename, resolve } from 'node:path';

export class OllamaMapper implements MapperProvider {
    private model: string;
    private baseUrl: string;

    constructor(model: string = 'llama3', baseUrl: string = 'http://localhost:11434') {
        this.model = model;
        this.baseUrl = baseUrl;
    }

    async generateMap(
        resourcePath: string,
        resourceType: string,
        resourceId?: string
    ): Promise<ResourceMap> {
        // 1. Validate inputs
        if (!existsSync(resourcePath)) {
            throw new Error(`File not found: ${resourcePath}`);
        }

        if (!['document', 'video', 'audio', 'image', 'text'].includes(resourceType)) {
            throw new Error(`Invalid resource_type: ${resourceType}`);
        }

        const id = resourceId || basename(resourcePath, extname(resourcePath));

        // 2. For text/code only in this example
        if (resourceType !== 'text') {
            throw new Error(`Ollama mapper doesn't support ${resourceType}`);
        }

        const content = readFileSync(resourcePath, 'utf-8');

        const prompt = `
        Analyze this ${resourceType} and return ONLY a JSON object:
        {
            "title": "Short title",
            "nodes": [
                {"id": "section_1", "title": "Title", "type": "section", "summary": "...", "location": {"modality": "${resourceType}", "lines": [1, 10]}}
            ]
        }
        
        Content:
        ${content.slice(0, 4000)}
        `;

        // 3. Call Ollama API
        try {
            const response = await fetch(`${this.baseUrl}/api/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: this.model,
                    prompt,
                    stream: false
                }),
                signal: AbortSignal.timeout(120000)
            });

            if (!response.ok) {
                throw new Error(`Ollama API error: ${response.statusText}`);
            }

            const data = await response.json();
            const result = JSON.parse(data.response);

            // 4. Map to CiteKit nodes
            const nodes: Node[] = result.nodes.map((n: any) => ({
                id: n.id,
                title: n.title,
                type: n.type,
                summary: n.summary,
                location: {
                    modality: resourceType,
                    lines: n.location.lines as [number, number]
                }
            }));

            return {
                resource_id: id,
                type: resourceType,
                title: result.title || basename(resourcePath),
                source_path: resolve(resourcePath),
                nodes,
                created_at: new Date().toISOString()
            };
        } catch (error) {
            if (error instanceof TypeError) {
                throw new Error(`Cannot connect to Ollama at ${this.baseUrl}`);
            }
            throw error;
        }
    }
}
```

**Usage:**

```typescript
import { CiteKitClient } from 'citekit';
import { OllamaMapper } from './ollama-mapper';

const mapper = new OllamaMapper('llama3');
const client = new CiteKitClient({ mapper });

const map = await client.ingest('code.py', 'text');
console.log(`Generated ${map.nodes.length} nodes`);
```

---

## Error Handling Pattern

**Best Practice** for implementing custom mappers:

```typescript
class MyMapper implements MapperProvider {
    async generateMap(
        resourcePath: string,
        resourceType: string,
        resourceId?: string
    ): Promise<ResourceMap> {
        // 1. Validate inputs
        if (!existsSync(resourcePath)) {
            throw new Error(`File not found: ${resourcePath}`);
        }

        const validTypes = ['document', 'video', 'audio', 'image', 'text'];
        if (!validTypes.includes(resourceType)) {
            throw new Error(`Unsupported resource_type: ${resourceType}`);
        }

        // 2. Call API with timeout
        try {
            const result = await this.apiCallWithTimeout(resourcePath, 60000);
        } catch (error) {
            if (error instanceof TypeError) {
                throw new Error('Mapper API connection failed');
            }
            if (error.name === 'AbortError') {
                throw new Error('Mapper API timeout (>60s)');
            }
            throw error;
        }

        // 3. Parse and validate response
        try {
            const nodes = this.parseResponse(result);
        } catch (error) {
            throw new Error(`Invalid mapper response: ${error.message}`);
        }

        // 4. Return ResourceMap
        return {
            resource_id: resourceId || basename(resourcePath),
            type: resourceType,
            title: 'Analyzed Resource',
            source_path: resolve(resourcePath),
            nodes,
            created_at: new Date().toISOString()
        };
    }
}
```

---

## Performance & Cost

| Mapper | Speed | Cost | Best For |
| :--- | :--- | :--- | :--- |
| GeminiMapper | Fast (5-30s) | $$ per 1M tokens | Large files, multimodal, high quality |
| Local Ollama | Slow (30s-5min) | Free | Development, privacy-sensitive data |
| OpenAI (custom) | Medium (10-60s) | $ per token | Flexible, multiple models |
| Anthropic (custom) | Medium (10-60s) | $$ per token | Long context windows |

---

## TypeScript Type Definitions

```typescript
interface MapperProvider {
    generateMap(
        resourcePath: string,
        resourceType: string,
        resourceId?: string
    ): Promise<ResourceMap>;
}

interface ResourceMap {
    resource_id: string;
    type: string;  // 'document' | 'video' | 'audio' | 'image' | 'text' | 'virtual'
    title: string;
    source_path: string;
    nodes: Node[];
    metadata?: Record<string, any>;
    created_at: string;  // ISO 8601
}

interface Node {
    id: string;
    title: string;
    type: string;
    location: Location;
    summary?: string;
    children?: Node[];
}

interface Location {
    modality: string;
    seconds?: [number, number];
    pages?: [number, number];
    lines?: [number, number];
    bbox?: [number, number, number, number];
}
```

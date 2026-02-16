# JavaScript Mappers

Mappers analyze files and return the structured semantic map.

## `GeminiMapper`

The default mapper implementation using the Google Generative AI SDK.

```typescript
import { GeminiMapper } from 'citekit/mapper/gemini';

const mapper = new GeminiMapper({
    apiKey: "...",
    model: "gemini-2.0-flash",
    maxRetries: 3
});
```

---

## `MapperProvider` (Interface)

Implement this interface to use custom LLMs (OpenAI, Anthropic) or local models (Ollama).

```typescript
import { MapperProvider, ResourceMap } from 'citekit';

class MyMapper implements MapperProvider {
    async generateMap(
        resourcePath: string,
        resourceType: string,
        resourceId?: string
    ): Promise<ResourceMap> {
        // Implementation
    }
}
```

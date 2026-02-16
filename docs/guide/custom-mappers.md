# Custom Mappers (Local Models)

CiteKit is designed to be model-agnostic. While `GeminiMapper` is the default (best for multimodal understanding), you can implement your own `MapperProvider` to use **Local LLMs** (Ollama, Llama.cpp) or other APIs (OpenAI, Anthropic).

## The `MapperProvider` Interface

To create a custom mapper, sub-class `MapperProvider` and implement the `generate_map` method.

```python
from citekit.mapper.base import MapperProvider
from citekit.models import ResourceMap, Node, Location
from pathlib import Path

class MyLocalMapper(MapperProvider):
    async def generate_map(
        self,
        resource_path: str,
        resource_type: str,
        resource_id: str | None = None,
    ) -> ResourceMap:
        
        # 1. Read the file
        path = Path(resource_path)
        content = path.read_text(encoding="utf-8")
        
        # 2. Call your Local Model (pseudo-code)
        # response = await ollama.chat(model="llama3", prompt=f"Analyze structure: {content}")
        # nodes = parse_json(response)
        
        # 3. Return a ResourceMap
        return ResourceMap(
            resource_id=resource_id or path.stem,
            type=resource_type,
            title=path.stem,
            source_path=str(path.resolve()),
            nodes=nodes  # List[Node]
        )
```

## Example: Ollama Mapper (Text/Code)

Here is a fully functional example of using a local **Ollama** instance to map a Python file.

### 1. Implementation

```python
# my_mapper.py
import json
import asyncio
from pathlib import Path
from citekit.mapper.base import MapperProvider
from citekit.models import ResourceMap, Node, Location
import httpx

class OllamaMapper(MapperProvider):
    def __init__(self, model_name="llama3"):
        self.model = model_name
        self.api_url = "http://localhost:11434/api/generate"

    async def generate_map(self, resource_path: str, resource_type: str, resource_id: str | None = None) -> ResourceMap:
        path = Path(resource_path)
        
        if resource_type != "text":
            raise ValueError("OllamaMapper only supports text/code files.")

        content = path.read_text("utf-8")
        
        prompt = f"""
        Analyze this code and return a JSON array of structural nodes (classes, functions).
        Each node must have: id, title, type, location {{ lines: [start, end] }}, summary.
        Return ONLY JSON.
        
        Code:
        {content[:4000]} # Truncate for context window if needed
        """

        # Call Ollama API
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.api_url, json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            })
            result = resp.json()["response"]
            
        # Parse JSON
        raw_nodes = json.loads(result)
        nodes = []
        for n in raw_nodes:
            nodes.append(Node(
                id=n["id"],
                title=n["title"],
                type=n["type"],
                summary=n["summary"],
                location=Location(lines=tuple(n["location"]["lines"]))
            ))

        return ResourceMap(
            resource_id=resource_id or path.stem,
            type="text",
            source_path=str(path.resolve()),
            title=path.name,
            nodes=nodes
        )
```

### 2. Usage

Inject your custom mapper into the `CiteKitClient`.

```python
import asyncio
from citekit import CiteKitClient
from my_mapper import OllamaMapper

async def main():
    # Use Local Mapper instead of Gemini
    client = CiteKitClient(mapper=OllamaMapper(model_name="llama3"))
    
    map = await client.ingest("src/utils.py", "text")
    print(f"Mapped {map.resource_id} using Local Llama3!")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Example: JavaScript/TypeScript (Local LLM)

Here is the equivalent implementation if you are using Node.js/TypeScript.

### 1. Implementation

```typescript
// ollama-mapper.ts
import { MapperProvider, ResourceMap, Node } from 'citekit';
import { readFileSync } from 'node:fs';
import { basename, resolve } from 'node:path';

export class OllamaMapper implements MapperProvider {
    constructor(private model: string = "llama3") {}

    async generateMap(
        resourcePath: string,
        resourceType: string,
        resourceId?: string
    ): Promise<ResourceMap> {
        if (resourceType !== "text") {
            throw new Error("OllamaMapper sample only supports text.");
        }

        const content = readFileSync(resourcePath, "utf-8");
        const id = resourceId || basename(resourcePath, ".py");

        // Call Ollama local API
        const response = await fetch("http://localhost:11434/api/generate", {
            method: "POST",
            body: JSON.stringify({
                model: this.model,
                prompt: `Analyze this code and return a JSON array of nodes: ${content.slice(0, 4000)}`,
                stream: false,
                format: "json"
            })
        });

        const data = await response.json();
        const rawNodes = JSON.parse(data.response);

        const nodes: Node[] = rawNodes.map((n: any) => ({
            id: n.id,
            title: n.title,
            type: n.type,
            summary: n.summary,
            location: { modality: "text", lines: n.location.lines }
        }));

        return {
            resource_id: id,
            type: "text",
            source_path: resolve(resourcePath),
            title: id,
            nodes: nodes,
            created_at: new Date().toISOString()
        };
    }
}
```

### 2. Usage

```typescript
import { CiteKitClient } from 'citekit';
import { OllamaMapper } from './ollama-mapper';

const client = new CiteKitClient({
    mapper: new OllamaMapper("llama3")
});

const map = await client.ingest("src/index.ts", "text");
console.log(`Mapped ${map.resource_id} locally!`);
```

## Using OpenAI / Anthropic

You can follow the same pattern to use `OpenAI` or `Anthropic` SDKs. Just replace the `httpx` call with the respective library's completion call.

> [!TIP]
> **Why use Gemini?**
> By default, CiteKit uses Gemini 1.5 because of its **2M context window** and **native video/audio understanding**. Local models are great for text/code, but for long videos or 100+ page PDFs, a large-context multimodal model is highly recommended.

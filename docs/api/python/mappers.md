# Python Mappers — Complete API Reference

Mappers are responsible for analyzing source files and generating the initial `ResourceMap` structure. They are the "LLM interface" layer of CiteKit.

---

## `GeminiMapper`

The default mapper implementation powered by Google Gemini (multimodal understanding).

### Constructor

```python
from citekit.mapper.gemini import GeminiMapper

mapper = GeminiMapper(
    api_key: str | None = None,
    model: str = "gemini-2.0-flash",
    max_retries: int = 3
)
```

### Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `api_key` | `str \| None` | `None` | Gemini API Key. Falls back to `GEMINI_API_KEY` environment variable. |
| `model` | `str` | `"gemini-2.0-flash"` | Gemini model to use. Supports: `gemini-2.0-flash`, `gemini-1.5-pro`, `gemini-1.5-flash`. |
| `max_retries` | `int` | `3` | Number of retries for failed API calls (with exponential backoff). |

### Methods

#### `async generate_map(resource_path, resource_type, resource_id=None)`

Analyzes a file and generates a structured `ResourceMap`.

```python
async def generate_map(
    self,
    resource_path: str,
    resource_type: str,
    resource_id: str | None = None
) -> ResourceMap
```

**Parameters:**
- `resource_path` (str): Path to the resource file
- `resource_type` (str): One of `document`, `video`, `audio`, `image`, `text`
- `resource_id` (str | None): Optional custom ID; defaults to filename stem

**Returns:** `ResourceMap` object

**Example:**

```python
from citekit.mapper.gemini import GeminiMapper
import asyncio

async def main():
    mapper = GeminiMapper(api_key="YOUR_API_KEY")
    
    # Map a PDF
    resource_map = await mapper.generate_map(
        resource_path="paper.pdf",
        resource_type="document",
        resource_id="research_paper"
    )
    
    print(f"Generated map with {len(resource_map.nodes)} nodes")

asyncio.run(main())
```

### Error Codes

**Success (Mapper Returns)**:
```
ResourceMap(resource_id="...", nodes=[...])
```

**Error: Missing API Key**:
```python
# Raises at initialization or first call
RuntimeError: GEMINI_API_KEY not set. Pass api_key parameter or set environment variable.
```

**Solution**: Set `GEMINI_API_KEY` or pass `api_key` to constructor

**Error: Invalid API Key**:
```python
# Raises on first API call
ValueError: Invalid API key. Check GEMINI_API_KEY value.
  Response code: 401 Unauthorized
```

**Solution**: Verify API key is correct and has Gemini API enabled

**Error: Rate Limiting**:
```python
# Raises after retries exhausted
RateLimitError: API rate limit exceeded after 3 retries
  Recommendation: Increase max_retries, reduce concurrency, or wait before retrying
```

**Solution**: Reduce concurrency, increase `max_retries`, or wait

**Error: Model Not Found**:
```python
# Raises on API call
ValueError: Model 'gemini-xyz' not found
  Available models: gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash
```

**Solution**: Use a valid model name

**Error: Network Timeout**:
```python
# Raises if API doesn't respond
TimeoutError: Gemini API did not respond within 60 seconds
  Increase timeout or retry
```

**Solution**: Increase timeout, check network, retry later

**Error: Malformed Response**:
```python
# Raises if JSON extraction fails
ValueError: Could not extract valid JSON from Gemini response
  Response was not parseable. Retrying...
```

**Solution**: Increase `max_retries`, try different model

---

## `MapperProvider` (Protocol/Interface)

Implement this interface to create custom mappers (for local LLMs, OpenAI, Anthropic, etc.).

### Interface Definition

```python
from citekit.mapper.base import MapperProvider
from citekit.models import ResourceMap

class MapperProvider(Protocol):
    """Abstract protocol for all mappers."""
    
    async def generate_map(
        self,
        resource_path: str,
        resource_type: str,
        resource_id: str | None = None
    ) -> ResourceMap:
        """Generate a ResourceMap from a resource file.
        
        Args:
            resource_path: Path to the resource (file or URL)
            resource_type: Modality (document, video, audio, image, text)
            resource_id: Optional custom ID
            
        Returns:
            ResourceMap with hierarchical nodes
            
        Raises:
            FileNotFoundError: If resource_path doesn't exist
            ValueError: If resource_type is invalid
            RuntimeError: If generation fails
        """
        ...
```

### Custom Mapper Example: Ollama Local LLM

```python
# ollama_mapper.py
import json
import httpx
from pathlib import Path
from citekit.mapper.base import MapperProvider
from citekit.models import ResourceMap, Node, Location

class OllamaMapper(MapperProvider):
    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    async def generate_map(
        self,
        resource_path: str,
        resource_type: str,
        resource_id: str | None = None
    ) -> ResourceMap:
        path = Path(resource_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {resource_path}")
        
        if resource_type not in ["document", "video", "audio", "image", "text"]:
            raise ValueError(f"Invalid resource_type: {resource_type}")

        resource_id = resource_id or path.stem

        # For text/code
        if resource_type == "text":
            content = path.read_text("utf-8")
        else:
            raise NotImplementedError(f"Ollama mapper doesn't support {resource_type}")

        prompt = f"""
        Analyze this {resource_type} and return ONLY a JSON object with this structure:
        {{
            "title": "Short title",
            "nodes": [
                {{"id": "section_1", "title": "Title", "type": "section", "summary": "...", "location": {{"modality": "{resource_type}", "lines": [1, 10]}}}}
            ]
        }}
        
        Content:
        {content[:4000]}
        """

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.base_url}/api/generate",
                    json={"model": self.model, "prompt": prompt, "stream": False},
                    timeout=120.0
                )
                resp.raise_for_status()
        except httpx.TimeoutException:
            raise RuntimeError(f"Ollama API timeout after 120s. Is it running?")
        except httpx.ConnectError:
            raise RuntimeError(f"Cannot connect to Ollama at {self.base_url}")

        try:
            result = json.loads(resp.json()["response"])
        except (json.JSONDecodeError, KeyError):
            raise RuntimeError("Invalid response format from Ollama")

        nodes = []
        for n in result.get("nodes", []):
            nodes.append(Node(
                id=n["id"],
                title=n["title"],
                type=n["type"],
                summary=n.get("summary"),
                location=Location(
                    modality=resource_type,
                    lines=tuple(n["location"]["lines"])
                )
            ))

        return ResourceMap(
            resource_id=resource_id,
            type=resource_type,
            title=result.get("title", path.stem),
            source_path=str(path.resolve()),
            nodes=nodes
        )
```

**Usage:**

```python
from ollama_mapper import OllamaMapper
import asyncio

async def main():
    mapper = OllamaMapper(model="llama3")
    
    map = await mapper.generate_map("code.py", "text")
    print(f"Generated {len(map.nodes)} nodes")

asyncio.run(main())
```

### Error Codes for Custom Mappers

**File Not Found**:
```python
FileNotFoundError: File not found: /path/to/file
```

**Invalid Resource Type**:
```python
ValueError: Invalid resource_type: 'xyz'
  Valid: document, video, audio, image, text
```

**Generation Timeout**:
```python
RuntimeError: Mapper did not respond within timeout (120s)
```

**API Connection Error**:
```python
RuntimeError: Cannot connect to mapper service
  Check service is running and accessible
```

**Malformed Response**:
```python
RuntimeError: Mapper response is not valid JSON
```

---

## Error Handling Pattern

**Best Practice** for implementing custom mappers:

```python
class MyMapper(MapperProvider):
    async def generate_map(self, resource_path, resource_type, resource_id=None):
        # 1. Validate inputs
        if not Path(resource_path).exists():
            raise FileNotFoundError(f"File not found: {resource_path}")
        
        if resource_type not in ["document", "video", "audio", "image", "text"]:
            raise ValueError(f"Unsupported resource_type: {resource_type}")

        # 2. Call API with timeout
        try:
            result = await self.api_call_with_timeout(resource_path, timeout=60)
        except TimeoutError:
            raise RuntimeError("Mapper API timeout")
        except ConnectionError as e:
            raise RuntimeError(f"API connection failed: {e}")

        # 3. Parse and validate response
        try:
            nodes = self.parse_response(result)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise RuntimeError(f"Invalid mapper response: {e}")

        # 4. Return ResourceMap
        return ResourceMap(
            resource_id=resource_id or Path(resource_path).stem,
            type=resource_type,
            title="Analyzed Resource",
            source_path=str(Path(resource_path).resolve()),
            nodes=nodes
        )
```

---

## Performance & Cost

| Mapper | Speed | Cost | Best For |
| :--- | :--- | :--- | :--- |
| GeminiMapper | Fast (5-30s) | $$ per 1M tokens | Large files, multimodal, high quality |
| Local Ollama | Slow (30s-5min) | Free | Development, privacy-sensitive data |
| OpenAI (custom) | Medium (10-60s) | $ per token | Flexible, multiple models |
| Anthropic (custom) | Medium (10-60s) | $$ per token | Long context windows |

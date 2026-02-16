# Python Mappers

Mappers are responsible for analyzing source files and generating the initial `ResourceMap` structure.

## `GeminiMapper`

The default mapper powered by Google Gemini.

```python
from citekit.mapper.gemini import GeminiMapper

mapper = GeminiMapper(
    api_key="...",
    model="gemini-2.0-flash",
    max_retries=3
)
```

---

## `MapperProvider` (Protocol)

If you want to create a custom mapper (e.g., for Ollama or OpenAI), implement this protocol.

```python
from citekit.mapper.base import MapperProvider
from citekit.models import ResourceMap

class MyCustomMapper(MapperProvider):
    async def generate_map(
        self, 
        resource_path: str, 
        resource_type: str, 
        resource_id: str | None = None
    ) -> ResourceMap:
        # Your logic here
        ...
```

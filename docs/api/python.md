# Python SDK Reference

The CiteKit Python SDK is a local-first toolkit for multimodal agentic workflows. It is designed for high-performance ingestion and deterministic resolution.

## Quick Navigation

| Component | Responsibility | link |
| :--- | :--- | :--- |
| **CiteKitClient** | Main entry point, caching, and orchestration. | [Client API](/api/python/client) |
| **Mappers** | Analyzing and tree-generation (Gemini/Local). | [Mappers API](/api/python/mappers) |
| **Resolvers** | Physical clipping (FFmpeg/PyMuPDF). | [Resolvers API](/api/python/resolvers) |
| **Models** | Pydantic schemas for maps and nodes. | [Data Models](/api/models) |

## Philosophy

The Python SDK prioritizes **asynchronous performance** (via `asyncio`) and **strict schema validation** (via `Pydantic`). It is the core engine used by the CiteKit CLI and MCP server.

# JavaScript/TypeScript SDK Reference

The CiteKit JavaScript SDK brings multimodal mapping to the Node.js ecosystem. It is written in TypeScript for a fully typed, modern developer experience.

## Quick Navigation

| Component | Responsibility | link |
| :--- | :--- | :--- |
| **CiteKitClient** | Ingestion and resolution entry point. | [Client API](/api/javascript/client) |
| **Mappers** | File analysis and content extraction. | [Mappers API](/api/javascript/mappers) |
| **Resolvers** | Tooling (FFmpeg, pdf-lib) integration. | [Resolvers API](/api/javascript/resolvers) |
| **Interfaces** | TypeScript definitions for maps/nodes. | [Core Interfaces](/api/models) |
| **Utilities** | Aggregation helpers (create agent context). | [Utilities](#utilities) |

## Philosophy

The JavaScript SDK follows the **local-first** and **async-first** patterns of the modern web. It is designed to be easily integrated into Next.js applications, serverless functions, or custom agentic CLI tools.

## Utilities

### `createAgentContext(maps: ResourceMap[], format: "markdown" | "json" = "markdown") => string`

Aggregates multiple `ResourceMap` objects into a single context string for LLM use.

### `buildAddress(resourceId: string, location: Location) => string`

Builds a CiteKit URI address for a location.

### `parseAddress(address: string) => { resourceId: string; location: Location }`

Parses a CiteKit URI address into `{ resourceId, location }`.

## Adapters (JavaScript)

### `MapAdapter`

Interface for converting external data into a `ResourceMap`.

### `GenericAdapter`

Pass-through adapter that assumes the input matches the `ResourceMap` interface (no runtime validation).

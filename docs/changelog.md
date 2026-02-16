# Changelog

All notable changes to the CiteKit project will be documented in this file.

## [0.1.8] - Unreleased
### Planned
- **JavaScript CLI Parity**: Implement CLI commands in the JS package (ingest, resolve, list, structure, check-map, inspect, adapt).

## [0.1.7] - 2026-02-16
### Added
- **Text & Code Support**: First-class support for `.txt`, `.md`, and `.py` files. Includes sliding window analysis and line-range resolution.
- **Map Portability**:
    - **Adapters**: New `citekit adapt` command to ingest data from GraphRAG, LlamaIndex, or custom sources.
    - **Validator**: New `citekit check-map` command to verify map schema compliance.
    - **Standardized Schema**: Strict JSON schema alignment between Python and TypeScript SDKs.
- **Documentation**:
    - Added "Map Adapters" guide.
    - Clarified MCP tool error responses and CLI output formatting.
    - Updated client and model references to match actual SDK types and fields.
    - Expanded resolver and client references across Python/JS to reflect real schema shapes.
    - Published full API model and MCP tool docs alignment.
    - Added utilities sections for address parsing and agent-context helpers.
    - Added MCP integration details and CLI usage guides across Python/Node contexts.
    - Added requirements, troubleshooting, and deployment guidance for mapper-based ingestion.
    - Updated architecture/ingestion deep dives to reflect mapper abstraction.

### JavaScript SDK
- **Resolvers**: Added audio resolver and expanded modality-specific resolver docs.
- **Addressing**: Added `parseAddress`/`buildAddress` support for `text` and `virtual` schemes.
- **Client**: Added concurrency limiting, source-size metadata injection, and recursive node lookup.
- **Mappers**: Added audio/image prompts and improved MIME detection.
- **MCP**: Updated server metadata and tooling behavior to align with MCP docs.
- **Exports**: Added missing exports for text/audio resolvers and address utilities.

### Python SDK
- **CLI**: Added `--mapper` and `--mapper-config`, expanded text file type detection, and improved list output.
- **Adapters**: Added LlamaIndex adapter and normalized GraphRAG output to `virtual`.
- **Client**: Added `save_map()` convenience and virtual-modality short-circuiting.
- **Addressing**: Added virtual URI parsing/building and improved media MIME handling.
- **Mappers**: Async-safe Gemini calls and improved retry timing.

### Changed
- **CLI Scope**: CLI is Python-only; JavaScript package provides MCP server integration (CLI commands are not yet implemented in JS).
- **Client Type Snippets**: Quick references now mirror Pydantic and TypeScript interfaces exactly.
- **Docs Language**: Replaced Gemini-only language with mapper-agnostic phrasing across guides.
- **URI Format**: Standardized time ranges to `start-end` across docs and examples.

### Fixed
- **CLI Output**: Replaced emoji prefixes with professional text labels (`[INFO]`, `[SUCCESS]`).
- **Schema Parity**: Fixed model field mismatches (`start/end`, `pages` list, `bbox` corners, `virtual_address`) across docs.
- **Resolver Docs**: Aligned image bbox coordinates and document pages list with resolver behavior.
- **MCP Tools Docs**: Error handling now reflects plain-text `Error: ...` responses.
- **Client Docs**: Corrected ingest examples, node discovery guidance, and location schemas in Python/JS docs.
- **CLI Docs**: Updated resolve output formatting and removed unsupported/incorrect options.
- **Requirements**: Corrected dependency guidance (optional peer deps in Node, PyMuPDF in Python).

## [0.1.6] - 2026-02-16
### Added
- **Strategic Documentation Overhaul**: Completely refactored all guides to focus on **Modern AI Architectures** (Agentic RAG, LongRAG, GraphRAG, and Context Orchestration).
- **Context Economics**: Added transparency regarding the two-phase lifecycle (Cloud-mapped ingestion vs. Local-first resolution).
- **Dedicated API Docs**: Added separate technical specifications for [Virtual Resolution](/api/virtual) and [MCP Protocol](/api/mcp).
- **CLI Upgrades**: Support for `--virtual`, `--concurrency` (`-c`), and `--retries` (`-r`) flags in the Python CLI.
- **Virtual Pointer Protocol**: Official recommendation for the `virtual:` URI prefix in databases.

## [0.1.5] - 2026-02-16
### Added
- **Standardized Constructors**: Python `CiteKitClient` now supports `api_key`, `model`, and `max_retries` directly, matching the JS SDK.
- **Robustness**: Implemented exponential backoff and retry logic in `GeminiMapper` (429 handling).

### Fixed
- **TypeScript**: Fixed the `maxRetries` "Ghost Property" in `CiteKitClientOptions` interface.

## [0.1.4] - 2026-02-15
### Changed
- **Serverless First Refactor**: Optimized all SDKs for Vercel/AWS Lambda. This involved moving `sharp`, `fluent-ffmpeg`, and `pdf-lib` to optional peer dependencies.
- **Mapping Logic**: Removed local PDF parsing in favor of Google's Gemini File API for zero-binary environments.

### Added
- **`baseDir` support**: Added ability to redirect all storage/output to `/tmp` for read-only filesystems.

## [0.1.3] - 2026-02-15
### Added
- **Initial JavaScript Port**: Established the core JS logic to match the Python resolver patterns.

## [0.1.2] - 2026-02-15
### Added
- **Performance**: Added hashing, caching, and concurrency support for heavy mapping tasks.

## [0.1.0] - 2026-02-14
### Added
- **Initial Release**: Core multimodal resolution patterns for Video, Audio, and Images.
- **Gemini Integration**: Initial support for multimodal mapping via Gemini 1.5.

# Changelog

All notable changes to this project will be documented in this file.

## [0.1.7] - 2026-02-16

### Added
-   **Text/Code Modality Support**: First-class support for mapping and resolving text-based files (`.txt`, `.md`, `.py`, `.ts`, etc.).
    -   **Ingestion**: `TextMapper` uses sliding windows and LLM analysis to identify Classes, Functions, and Sections.
    -   **Resolution**: `TextResolver` supports exact line-range extraction (`lines=[10, 20]`).
    -   **Models**: Updated `Location` schema to support `lines` tuple.
    -   **CLI**: `citekit ingest file.py --type text` support.
-   **Map Portability**:
    -   **Standardized Schema**: Ensured Python Pydantic models and TypeScript Interfaces match 1:1.
    -   **Validator**: Added `citekit check-map <path.json>` command to validate maps against the strict schema.
-   **Map Adapters**:
    -   **New Protocol**: define `MapAdapter` to convert external data (GraphRAG, LlamaIndex, CSV) into CiteKit maps.
    -   **CLI**: Added `citekit adapt <input> --adapter <name>` command.
    -   **Built-in Support**: Added adapters for `graphrag` and `llamaindex`.
-   **Documentation**:
    -   Comprehensive audit to ensure "Text" modality is documented in all API references and guides.
    -   Added "Code Block" usage instructions to `getting-started.md`.

### Fixed
-   Fixed missing `lines` field in Python `Location` model.
-   Fixed missing `text` types in JavaScript `ResourceMap` and `Location` definitions.
-   Corrected numerous documentation omissions regarding text modality support.

## [0.1.6] - 2026-02-15

### Added
-   **CLI**: `citekit list` and `citekit inspect` commands.
-   **MCP**: Added `getNode` tool.

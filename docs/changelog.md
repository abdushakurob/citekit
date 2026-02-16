# Changelog

All notable changes to the CiteKit project will be documented in this file.

## [0.1.6] - 2026-02-16
### Added
- **CLI Upgrades**: Support for `--virtual`, `--concurrency` (`-c`), and `--retries` (`-r`) flags in the Python CLI.
- **Dedicated API Docs**: Added separate technical specifications for [Virtual Resolution](/api/virtual) and [MCP Protocol](/api/mcp).
- **Virtual Pointer Protocol**: Official recommendation for the `virtual:` URI prefix in databases.

### Fixed
- **Python SDK**: Added missing `os` import in `client.py` required for `/tmp` and environment variable support.
- **Documentation**: Fixed double-protocol typo (`virtual://video://`) in examples.

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

# CiteKit Examples

This directory contains **runnable real-world examples** demonstrating CiteKit's capabilities in production scenarios.

## Available Examples

### [Research App](./research-app/) (Node.js)
**Agentic Research Engine** for navigating technical papers and extracting evidence with perfect fidelity.

- **Tech**: Node.js, TypeScript
- **Use Case**: Research agents, document analysis
- **Demonstrates**: Hierarchical navigation, deterministic extraction, high-density grounding

### [Study Companion](./study-companion/) (MCP)
**Personal Study Agent** using Claude Desktop to navigate lecture videos with precise timestamp citations.

- **Tech**: Model Context Protocol (MCP), Claude Desktop
- **Use Case**: Education, video learning, lecture analysis
- **Demonstrates**: MCP integration, video temporal orchestration, concept-based search

### [Video Search CLI](./video-search-cli/) (Python)
**Temporal Content Orchestration** tool for concept-based navigation of video libraries.

- **Tech**: Python, Click CLI
- **Use Case**: Video archives, course libraries, conference recordings
- **Demonstrates**: Semantic timeline navigation, multi-step retrieval, local extraction

### [RAG Fusion](./rag-fusion/) (Python)
**Hybrid High-Fidelity Architecture** combining vector search with CiteKit's evidence extraction.

- **Tech**: Python, Vector DBs (ChromaDB, Pinecone compatible)
- **Use Case**: Production RAG systems, multimodal AI
- **Demonstrates**: Hybrid indexing, visual evidence orchestration, cost optimization

## Quick Start

Each example has its own directory with:
- Complete working code
- Setup instructions
- Prerequisites and dependencies
- Usage examples
- Production integration guidance

Navigate to any example directory and follow its README to get started!

## Choosing an Example

**New to CiteKit?** Start with [Research App](./research-app/) - simple Node.js demo

**Using Claude Desktop?** Try [Study Companion](./study-companion/) - MCP integration

**Working with videos?** Check out [Video Search CLI](./video-search-cli/) - Python CLI

**Building production RAG?** Explore [RAG Fusion](./rag-fusion/) - hybrid architecture

## Example Comparison

| Example | Language | Complexity | Use Case |
|---------|----------|------------|----------|
| Research App | JavaScript | Simple | Document analysis |
| Study Companion | Config | Simple | Video learning with Claude |
| Video Search CLI | Python | Medium | Video library search |
| RAG Fusion | Python | Advanced | Production RAG systems |

## Prerequisites

All examples require CiteKit to be installed:

**Python:**
```bash
pip install citekit
```

**Node.js:**
```bash
npm install -g citekit
```

Most examples also require a Gemini API key (free tier available):
- Get your key: https://aistudio.google.com/app/apikey

## Learn More

- [CiteKit Documentation](https://abdushakurob.github.io/citekit/)
- [Getting Started Guide](../docs/guide/getting-started.md)
- [Architecture Concepts](../docs/guide/concepts/architecture.md)
- [API Reference](../docs/api/)

## Contributing

Have an interesting use case? Submit an example via GitHub pull request!


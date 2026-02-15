# CiteKit

**Local-first AI resource mapping SDK for precise content extraction**

CiteKit enables AI agents to access specific parts of files—PDF pages, video clips, audio segments, image crops—without uploading entire documents to the cloud. It uses LLMs to generate structured "maps" of your content, then resolves exact references on demand.

[![PyPI](https://img.shields.io/pypi/v/citekit)](https://pypi.org/project/citekit/)
[![npm](https://img.shields.io/npm/v/citekit)](https://www.npmjs.com/package/citekit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Local-First**: All file processing happens on your machine. No cloud storage persistence.
- **Multi-Modal**: Supports PDF, Video (MP4/MOV), Audio (MP3/WAV), and Images (PNG/JPG).
- **Smart Ingestion**:
  - Uses **Gemini 1.5** via File API for handling large files (hours of video).
  - **SHA-256 Hashing & Caching**: Never re-process the same file twice.
  - **Concurrency Control**: Built-in queueing to manage API rate limits.
- **Precise Extraction**: Get exact PDF pages, video clips (stream-copied), or image crops.
- **MCP Compatible**: Works native with Claude Desktop and Cline.
- **Zero Config**: Smart defaults for immediate usage.

## Installation

### Python

```bash
pip install citekit
```

**Requirements:**
- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) (for video/audio support)

### JavaScript (Node.js)

```bash
npm install citekit
```

**Requirements:**
- Node.js 18+
- [ffmpeg](https://ffmpeg.org/) (for video/audio support)

## Quick Start

### 1. Set your API key

```bash
export GEMINI_API_KEY=your_gemini_api_key_here
```

Get a free API key at [Google AI Studio](https://makersuite.google.com/app/apikey).

### 2. Ingest a file

```bash
citekit ingest research.pdf
```

This generates a structured "map" of the document, identifying sections, pages, and concepts.

### 3. List your resources

```bash
citekit list
# Output:
# - research (document): Research Paper
```

### 4. Resolve specific content

```bash
citekit resolve research.methodology
# Output: .citekit_output/research_pages_5_8.pdf
```

## Usage

### Python SDK

```python
from citekit import CiteKitClient
import asyncio

async def main():
    client = CiteKitClient()
    
    # Ingest a document
    resource_map = await client.ingest("research.pdf", "document")
    
    # Print discovered nodes
    print(f"Title: {resource_map.title}")
    for node in resource_map.nodes:
        print(f"  [{node.type}] {node.id}: {node.title}")
    
    # Resolve a specific section
    evidence = await client.resolve("research", "methodology")
    print(f"Extracted to: {evidence.output_path}")

asyncio.run(main())
```

### JavaScript SDK

```javascript
import { CiteKitClient } from 'citekit';

const client = new CiteKitClient();

// Ingest a document
const map = await client.ingest('research.pdf', 'document');

// Print nodes
console.log(`Title: ${map.title}`);
map.nodes.forEach(node => {
    console.log(`  [${node.type}] ${node.id}: ${node.title}`);
});

// Resolve specific content
const evidence = await client.resolve('research', 'methodology');
console.log(`Extracted to: ${evidence.output_path}`);
```

### MCP Integration

Connect CiteKit to your AI agents (Claude Desktop, Cline) via the Model Context Protocol.

**Claude Desktop Configuration** (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "citekit": {
      "command": "citekit",
      "args": ["serve"],
      "env": {
        "GEMINI_API_KEY": "your_gemini_api_key_here"
      }
    }
  }
}
```

**Available MCP Tools:**
- `listResources` - List all ingested resources
- `getStructure` - Get the full map of a resource
- `resolve` - Extract specific content (mini-PDF, clip, crop)

## Documentation

- **[Full Documentation](docs/index.html)** - Comprehensive guide with examples
- **[API Reference](docs/api.html)** - Complete API documentation
- **[MCP Integration](docs/mcp.html)** - Set up with AI agents
- **[Examples](docs/examples.html)** - Real-world use cases

## Project Structure

```
citekit/
├── python/              # Python SDK
│   ├── citekit/
│   │   ├── client.py    # Main client
│   │   ├── mapper/      # LLM-based mapping
│   │   ├── resolvers/   # Content extractors
│   │   ├── models.py    # Data models
│   │   ├── mcp_server.py # MCP server
│   │   └── cli.py       # Command-line interface
│   └── pyproject.toml
├── javascript/          # JavaScript SDK
│   ├── src/
│   │   ├── client.ts
│   │   ├── mapper/
│   │   ├── resolvers/
│   │   └── models.ts
│   └── package.json
├── docs/                # Static documentation site
└── README.md
```

## How It Works

1. **Ingestion**: CiteKit sends your file to an LLM (Gemini) which analyzes it and returns a structured "map" in JSON format. This map contains:
   - Hierarchical nodes (sections, chapters, topics)
   - Physical locations (page ranges, timestamps, bounding boxes)
   - Summaries and metadata

2. **Storage**: Maps are stored locally in `.resource_maps/` as JSON files.

3. **Resolution**: When you request a specific node, CiteKit:
   - Looks up the node's location in the map
   - Extracts that exact content:
     - **PDFs**: Creates a mini-PDF with just those pages
     - **Videos**: Cuts a clip using ffmpeg (stream-copied, no re-encoding)
     - **Images**: Crops the specified region
   - Saves the result to `.citekit_output/`

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/abdushakurob/citekit.git
cd citekit

# Python development
cd python
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# JavaScript development
cd javascript
npm install
npm run build
```

### Running Tests

```bash
# Python
cd python
pytest

# JavaScript
cd javascript
npm test
```

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linters
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

- **Python**: Follow PEP 8, use Black for formatting
- **JavaScript**: Follow the existing style, use Prettier

## Publishing

See [PUBLISHING.md](PUBLISHING.md) for instructions on publishing to PyPI and npm.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

- [ ] Support for more LLM providers (OpenAI, Anthropic)
- [ ] Web-based UI for browsing resource maps
- [ ] Caching layer to avoid re-processing
- [ ] Support for more file formats (DOCX, PPTX, etc.)
- [ ] Collaborative map editing

## Support

- **Issues**: [GitHub Issues](https://github.com/abdushakurob/citekit/issues)
- **Discussions**: [GitHub Discussions](https://github.com/abdushakurob/citekit/discussions)
- **Documentation**: [docs/index.html](docs/index.html)

## Acknowledgments

Built with:
- [Gemini API](https://ai.google.dev/) for AI-powered mapping
- [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF processing
- [ffmpeg](https://ffmpeg.org/) for video/audio processing
- [Sharp](https://sharp.pixelplumbing.com/) for image processing

---

**Made for developers building AI agents**

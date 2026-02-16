# CiteKit Video Search CLI Example

A **Video Orchestration Tool** for concept-based navigation of video libraries. Goes beyond keyword search to extract complete logical temporal segments.

## What This Demonstrates

### The Strategy: Concept-Based Navigation

Standard video search relies on rough transcription chunks. This CLI shows a sophisticated workflow:

1. **Structural Mapping**: Ingest videos via mapper (Gemini by default) to discover semantic chapters/scenes
2. **Deterministic Retrieval**: After mapping, navigation and extraction is 100% local
3. **Zero-Latency Switching**: Use virtual resolution for cloud agents or physical extraction for local playback

### Why This is Modern

#### From Keywords to Concepts

Basic retrieval returns a fixed window around a keyword. **Temporal Orchestration** returns the **logical unit**. If a professor explains a proof over 5 minutes, CiteKit gives you all 5 minutes.

#### Multi-Step Agentic Retrieval

In an agentic loop (like ReAct), the agent can:
1. `list` - See the video library
2. View maps - "Read" video timelines in seconds
3. `seek` - Extract only the evidence needed to reason

#### Agentic Grounding

Retrieval is **deterministic** (based on maps), allowing agents to ground responses with stable CiteKit URIs (`video://lex#t=180-210`), compatible with **Context Caching** for ultra-low latency.

### CLI Alternative (JavaScript)

All commands used in this example are also available via JavaScript CLI:

```bash
# Install
npm install -g citekit

# Index videos
npx citekit ingest lectures/intro_to_ml.mp4 video

# List resources
npx citekit list

# View structure
npx citekit structure video_id

# Resolve a clip
npx citekit resolve video_id chapter_id
```

Choose Python or JavaScript based on your stack preferences.

## Prerequisites

- Python 3.9+ or Node.js 18+ (choose your preferred SDK)
- A Gemini API key (or configure a custom mapper)
- `ffmpeg` installed (for video extraction)
- A video player: `mpv` (recommended) or `vlc`

> **Note:** This example uses the Python SDK, but all CLI commands shown are also available in JavaScript (v0.1.8+). See [CLI Alternative](#cli-alternative-javascript) below.

### Installing ffmpeg

**Windows:**
```bash
winget install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg  # Debian/Ubuntu
sudo dnf install ffmpeg  # Fedora
```

### Installing a Video Player

**mpv (recommended):**
```bash
# Windows
winget install mpv

# macOS
brew install mpv

# Linux
sudo apt install mpv
```

**vlc:**
```bash
# Windows
winget install vlc

# macOS
brew install --cask vlc

# Linux
sudo apt install vlc
```

## Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Set your Gemini API key:

```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your_api_key_here"

# macOS/Linux
export GEMINI_API_KEY="your_api_key_here"
```

Or create a `.env` file:
```
GEMINI_API_KEY=your_api_key_here
```

Get a free Gemini API key from: https://aistudio.google.com/app/apikey

### 3. Add Video Files

Create a directory with your videos:

```bash
mkdir lectures
# Copy your video files to lectures/
```

Supported formats: mp4, mov, mkv, avi, webm

## Usage

### Index Your Video Library

First, generate structural maps for your videos:

```bash
python orchestrate_video.py index lectures/
```

This processes each video once, sending it to the mapper service to identify:
- Chapters and sections
- Topic boundaries
- Semantic segments

**Note**: This is the only time videos are sent to the cloud. All subsequent operations are 100% local.

### List Indexed Videos

See what's in your library:

```bash
python orchestrate_video.py list
```

Shows all indexed videos and their structural nodes (chapters/topics).

### Search and Play Concepts

Find and play specific concepts:

```bash
python orchestrate_video.py seek "gradient descent"
python orchestrate_video.py seek "introduction"
python orchestrate_video.py seek "methodology"
```

This will:
1. Search all indexed videos for the concept
2. Find the matching semantic segment (not just a keyword)
3. Extract that segment as a high-fidelity clip
4. Open it in your video player

### Using a Different Player

By default, clips open in `mpv`. To use a different player:

```bash
python orchestrate_video.py seek "neural networks" --player vlc
```

## Example Workflow

```bash
# 1. Index your course videos
python orchestrate_video.py index ./courses/ml_fundamentals/

# 2. See what's available
python orchestrate_video.py list

# 3. Find specific concepts
python orchestrate_video.py seek "backpropagation"
python orchestrate_video.py seek "loss function"
python orchestrate_video.py seek "regularization"
```

## Output

Extracted clips are saved in the CiteKit output directory (default: `~/.citekit/output/`) and automatically opened in your video player.

Each clip preserves:
- Original video quality
- Audio synchronization
- Exact temporal boundaries
- Metadata about the source

## Advanced Usage

### Custom Mapper

To use a custom mapper instead of Gemini:

```bash
export CITEKIT_MAPPER_PROVIDER=custom
export CITEKIT_MAPPER_ENDPOINT=http://localhost:8000/map
```

### Batch Processing

Index multiple directories:

```bash
python orchestrate_video.py index ./lectures/
python orchestrate_video.py index ./conferences/
python orchestrate_video.py index ./tutorials/
```

All videos become searchable through a single interface.

### Integration with Agents

This CLI is a demonstration. In production, you'd integrate CiteKit's Python SDK directly into your agent:

```python
from citekit import CiteKitClient

client = CiteKitClient()

# Agent discovers available videos
maps = client.list_maps()

# Agent reads structural understanding
resource_map = client.get_map(maps[0])

# Agent makes retrieval decision
evidence = await client.resolve(maps[0], "chapter_3")
```

## Troubleshooting

### "ffmpeg not found"

Install ffmpeg using instructions above, then restart your terminal.

### "mpv not found"

Either install mpv or specify a different player:
```bash
python orchestrate_video.py seek "concept" --player vlc
```

### "No videos indexed yet"

Run the index command first:
```bash
python orchestrate_video.py index <directory>
```

### Videos fail to process

- Ensure videos are in supported formats (mp4, mov, mkv, avi, webm)
- Check that GEMINI_API_KEY is set correctly
- Verify internet connection for initial mapping

## Learn More

- [CiteKit Documentation](https://abdushakurob.github.io/citekit/)
- [Video Search Guide](https://abdushakurob.github.io/citekit/guide/examples/video-search-cli)
- [Python SDK Reference](https://abdushakurob.github.io/citekit/api/python)

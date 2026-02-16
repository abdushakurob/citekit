# CiteKit Study Companion Example

Build a **Personal Study Agent** using Claude Desktop and CiteKit to navigate lecture videos with precise timestamp citations.

## What This Demonstrates

Ask Claude:
> "Can you find where the professor explains 'Gradient Descent' and show me that clip?"

Claude will:
1. Understand the lecture's structural map
2. Locate the exact timestamp
3. **Send you a video clip** you can watch immediately

## Why CiteKit vs. Traditional Video RAG

### The Snippet Problem in Vector RAG

Traditional vector databases for video transcripts:
- Find keyword "Gradient Descent"
- Return surrounding 30 seconds of text
- **Result**: Random sentence like *"So that is gradient descent. Now let's move on..."*

### CiteKit Structural Advantage

CiteKit maps videos into logical **Episodes/Chapters**:
- **Map**: `ID: gradient_descent_explanation, Start: 10:00, End: 15:00`
- **Result**: You get the **full 5-minute explanation**
- **Accuracy**: Agent cites the *concept*, not just keyword matches

### Privacy & Locality

- Your 2GB video file stays on your hard drive
- Extraction (cutting clips) happens via local `ffmpeg`
- Perfect for sensitive data (private meetings, proprietary research)

## Prerequisites

- Claude Desktop (latest version)
- Python 3.9+ or Node.js 18+ (for CiteKit installation)
- A Gemini API key (for the default mapper)

## Get the Example (Git)

```bash
git clone https://github.com/abdushakurob/citekit.git
cd citekit/examples/study-companion
```

## Setup

### 1. Install CiteKit

Choose your preferred environment (both have full CLI support):

**Python:**
```bash
pip install citekit

# Verify installation
python -m citekit --version
```

**Node.js:**
```bash
npm install -g citekit

# Verify installation
npx citekit --version
```

Since v0.1.8, both CLIs support all 8 commands identically.

### 2. Configure Claude Desktop

Open your Claude Desktop configuration file:

**macOS:** 
```bash
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:** 
```bash
code %APPDATA%\Claude\claude_desktop_config.json
```

Add the CiteKit MCP server:

```json
{
  "mcpServers": {
    "citekit": {
      "command": "citekit",
      "args": ["serve"],
      "env": {
        "GEMINI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

Get a free Gemini API key from: https://aistudio.google.com/app/apikey

### 3. Restart Claude Desktop

After saving the configuration, fully quit and restart Claude Desktop.

## Usage Workflow

### Step 1: Ingest Your Lecture

Before you can ask Claude about a video, you need to map its structure:

**Python CLI:**
```bash
python -m citekit ingest lectures/intro_to_ml.mp4 video
```

**JavaScript CLI:**
```bash
npx citekit ingest lectures/intro_to_ml.mp4 video
```

Both commands create an identical structural map of your video (chapters, topics, timestamps).

### Step 2: Chat with Claude

Open Claude Desktop and try:

> "I want to study 'intro_to_ml'. Show me the section on 'Gradient Descent'."

Claude can now:
- List all available videos you've ingested
- Show you the structural map (chapters/topics)
- Resolve specific sections to video clips
- Extract timestamps for any concept

### Example Queries

**List available content:**
> "What lectures do I have mapped in CiteKit?"

**Explore structure:**
> "Show me the table of contents for intro_to_ml"

**Get specific content:**
> "Extract the 'neural networks' section from intro_to_ml as a video clip"

**Multi-step research:**
> "Find all sections across my lectures that mention 'backpropagation', then extract those clips"

## Adding More Lectures

Simply ingest additional videos:

```bash
citekit ingest lectures/advanced_ml.mp4 video
citekit ingest lectures/deep_learning.mp4 video
```

All videos will be available to Claude through the MCP interface.

## Customization

### Using a Custom Mapper

If you don't want to use Gemini, you can configure a custom mapper in your `.env` or Claude config:

```json
{
  "mcpServers": {
    "citekit": {
      "command": "citekit",
      "args": ["serve"],
      "env": {
        "CITEKIT_MAPPER_PROVIDER": "custom",
        "CITEKIT_MAPPER_ENDPOINT": "http://localhost:8000/map"
      }
    }
  }
}
```

## MCP Tools Available

When CiteKit is configured, Claude has access to these tools:

- `ingest_resource`: Map a new video/document
- `list_resources`: See all mapped content
- `get_resource_map`: Get structural map (TOC)
- `resolve_node`: Extract a specific section
- `search_nodes`: Find nodes by query

## Troubleshooting

### Claude doesn't see CiteKit tools

1. Check configuration file is valid JSON
2. Ensure CiteKit is installed globally (`citekit serve` works in terminal)
3. Restart Claude Desktop completely (quit, not just close)
4. Check Claude's MCP panel (hammer icon) shows CiteKit connected

### Video extraction fails

1. Ensure `ffmpeg` is installed and in PATH
2. Check video file format is supported (mp4, mov, mkv)
3. Verify the video path is absolute or relative to where you ran ingest

## Learn More

- [CiteKit Documentation](https://abdushakurob.github.io/citekit/)
- [MCP Integration Guide](https://abdushakurob.github.io/citekit/guide/mcp)
- [Study Companion Guide](https://abdushakurob.github.io/citekit/guide/examples/study-companion)
- [Model Context Protocol](https://modelcontextprotocol.io/)

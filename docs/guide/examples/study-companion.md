# Build a Study Companion (MCP Agent)

In this guide, we will configure a powerful **Personal Study Agent** that can "watch" lectures with you and cite specific timestamps, using Claude Desktop and CiteKit.

## Run the Complete Example

A fully configured version of this example is available in the repository:

**Location:** `examples/study-companion/`

**Quick Start:**
```bash
# Install CiteKit
pip install citekit
# or
npm install -g citekit

# Follow the configuration guide in examples/study-companion/README.md
```

See the [README](https://github.com/abdushakurob/citekit/tree/main/examples/study-companion) for full Claude Desktop setup instructions.

## Get the Example (Git)

```bash
git clone https://github.com/abdushakurob/citekit.git
cd citekit/examples/study-companion
```

## The Goal
We want to ask Claude:
> "Can you find the part of the lecture where the professor explains 'Gradient Descent' and show me that clip?"

And have Claude:
1.  Understand the lecture structure.
2.  Locate the exact timestamp.
3.  **Send us a video clip** we can watch immediately.

## 1. Installation

CiteKit comes with a built-in MCP server. Choose your preferred SDK:

**Python:**
```bash
pip install citekit
python -m citekit --version  # Verify
```

**JavaScript:**
```bash
npm install -g citekit
npx citekit --version  # Verify
```

Both provide identical MCP server and CLI functionality (v0.1.8+).

## 2. Configuration

Open your Claude Desktop configuration file:
-   **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
-   **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add the `citekit` server:

```json
{
  "mcpServers": {
    "citekit": {
      "command": "citekit",
      "args": ["serve"],
      "env": {
        "GEMINI_API_KEY": "AIzaSy..."  // Only needed for the default Gemini mapper
      }
    }
  }
}
```

## 3. Workflow

### Step 1: Ingest your material

**Python CLI:**
```bash
python -m citekit ingest lectures/intro_to_ml.mp4 video
```

**JavaScript CLI:**
```bash
npx citekit ingest lectures/intro_to_ml.mp4 video
```

Both produce the same structural map.

### Step 2: Ask Claude
> "I want to study 'intro_to_ml'. Show me the section on 'Gradient Descent'."

## Why is this better than Video RAG?

### The "Snippet Problem" in RAG
If you use a Vector Database to search for "Gradient Descent" in a video transcript:
*   It finds the word "Gradient".
*   It returns the surrounding 30 seconds of text.
*   **Result**: You get a random sentence. *"So that is gradient descent. Now let's move on..."*

### The CiteKit Structural Advantage
CiteKit maps the video into logical **Episodes/Chapters**:
*   **Map**: `ID: gradient_descent_explanation, Start: 10:00, End: 15:00`.
*   **Result**: When you ask for "Gradient Descent", you get the **full 5-minute explanation**.
*   **Accuracy**: The agent cites the *concept*, not just a keyword match.

### Privacy & Locality
*   Your 2GB video file stays on your hard drive.
*   The extraction (cutting the clip) happens via local `ffmpeg`.
*   Use this for sensitive data (private meetings, proprietary research) where uploading full files to a cloud vector store is risky.

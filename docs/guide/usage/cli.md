# Command Line Interface (CLI)

The CLI is the primary tool for managing your local CiteKit library. It provides a robust interface for ingesting files, inspecting their generated structure, and resolving content for downstream use.

## Installation

The CLI is automatically installed when you install the python package:

```bash
pip install citekit
```

## 1. Ingest (Map)

The `ingest` command serves as the bridge between your raw files and CiteKit's structured format. It performs two key actions:
1.  **Hashes the file** to check if a map already exists (skipping redundant API calls).
2.  **Uploads to Gemini** (if new) to analyze structure using multimodal understanding.
3.  **Saves JSON** to your local `.resource_maps` directory.

### Usage

```bash
python -m citekit.cli ingest [PATH] [OPTIONS]
```

### Examples

**Standard Ingestion**
Detects type from extension.
```bash
python -m citekit.cli ingest lecture.mp4
```

**Forcing a Modality**
Useful for non-standard extensions or specific parsing needs.
```bash
# Treat a .md file as a documentation source
python -m citekit.cli ingest README.md --type document
```

### Options

| Option | Shorthand | Description | Default |
| :--- | :--- | :--- | :--- |
| `--type` | `-t` | Force resource type (`video`, `audio`, `document`, `image`). | Auto-detect |
| `--concurrency` | `-c` | Max parallel chunks to process. Higher = faster, but may hit rate limits. | `5` |
| `--retries` | `-r` | Number of times to retry failed API calls. | `3` |

## 2. Inspect (Plan)

Before you extract content, you often need to know *what* to extract. The `list` and `inspect` commands allow you to explore the "Map" created during ingestion.

### List Resources

View all files currently managed by CiteKit in your local project.

```bash
python -m citekit.cli list
```

**Output:**
```text
found 3 resources:
 - lecture_01 (video): Introduction to Algorithms
 - research_paper_v2 (document): Attention Is All You Need
 - app_codebase (document): Main Application Logic
```

### List Nodes

View the hierarchical structure of a specific resource. This helps you find the `node_id` you need for resolution.

```bash
python -m citekit.cli list lecture_01
```

**Output:**
```text
Nodes in 'lecture_01':
 - intro (section): Introduction and Logistics
 - chapter_1 (section): Big O Notation
   └─ chapter_1.example_1 (example): O(n) loop example
 - summary (section): Conclusion
```

### Inspect Node Details

Drill down into a specific node to see exactly what it covers (timestamps, page numbers, summary). This is useful for debugging or verification.

```bash
python -m citekit.cli inspect lecture_01.chapter_1
```

**Output:**
```text
Node: chapter_1
   Resource: lecture_01 (video)
   Title: Big O Notation
   Location: 10:45 - 22:30
   Summary: Explains the concept of asymptotic runtime...
```

## 3. Resolve (Extract)

Resolution is the final step where CiteKit produces a tangible file for you or your agent. It reads the Map and uses local tools (FFmpeg, etc.) to extract the exact segment.

### Usage

```bash
python -m citekit.cli resolve [RESOURCE_ID] [NODE_ID]
```

### Physical Resolution (Default)

Produces a new file containing *only* the requested content.

```bash
python -m citekit.cli resolve lecture_01 chapter_1
```

**What happens:**
- CiteKit looks up `chapter_1` in `lecture_01.json`.
- It finds the timestamp `645s - 1350s`.
- It invokes `ffmpeg` to stream-copy that segment.
- It saves to `.citekit_output/lecture_01_chapter_1.mp4`.

### Virtual Resolution (Metadata)

Fetches the coordinates/metadata *without* creating a file. Ideal for passing timestamps to a frontend player or calculating duration.

```bash
python -m citekit.cli resolve lecture_01 chapter_1 --virtual
```

**Output:**
```text
Virtual resolution successful.
   Modality: video
   Address: video://lecture_01#t=645-1350
   Location: lines=None, pages=None, start=645, end=1350
```

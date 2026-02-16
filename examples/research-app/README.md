# CiteKit Research App Example

An **Agentic Research Engine** that uses CiteKit to navigate technical papers and extract specific sections with perfect fidelity.

## What This Demonstrates

Unlike traditional systems that rely on keyword search or random text chunks, this example shows:
1. **Structural Understanding**: The agent sees the document's table of contents first
2. **Hierarchical Navigation**: Decides which sections are relevant based on summaries
3. **Deterministic Extraction**: Pulls exact pages, preserving diagrams, formulas, and formatting

## Prerequisites

- Node.js 18+
- A Gemini API key (or configure a custom mapper)

## Get the Example (Git)

```bash
git clone https://github.com/abdushakurob/citekit.git
cd citekit/examples/research-app
```

## Setup

### 1. Install Dependencies

```bash
npm install
```

> **Note**: This example requires `pdf-lib` for document resolution. It's included in package.json dependencies.

### 2. Configure API Key

Copy the example environment file and add your Gemini API key:

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

Get a free Gemini API key from: https://aistudio.google.com/app/apikey

### 3. Add Sample Paper

Create a `papers/` directory and add your PDF:

```bash
mkdir papers
# Copy your PDF paper to papers/sample_paper.pdf
```

You can use any technical paper or document. The example will:
- Map its structure using CiteKit
- Search for methodology/experiment sections
- Extract those sections as separate PDF files

## Running the Example

```bash
npm start
```

The agent will:
1. Ingest your paper and generate a structural map
2. Analyze the map to find methodology sections
3. Extract relevant sections to `research_evidence/` folder

## Output

Extracted evidence will be saved in `research_evidence/` with high-fidelity preservation of:
- Original formatting
- Mathematical equations
- Diagrams and figures
- Page references

## Modern Capabilities

### 1. Hierarchical Navigation
By using the CiteKit Map, your agent sees a recursive structure (Parts → Chapters → Sections) allowing for **zoomable context**.

### 2. High-Density Grounding
When the agent cites a formula or diagram from page 14, it provides the **visual evidence** (PDF slice) to the reasoning model, ensuring accurate grounding.

## CLI Usage (Both SDKs Supported)

While this example uses the Node.js programmatic API, you can also use CiteKit CLI commands for quick operations:

**JavaScript CLI:**
```bash
npx citekit ingest papers/sample.pdf document
npx citekit list
npx citekit resolve paper_id section_id
```

**Python CLI:**
```bash
python -m citekit ingest papers/sample.pdf document
python -m citekit list
python -m citekit resolve paper_id section_id
```

Both CLIs support all 8 commands: `ingest`, `resolve`, `list`, `structure`, `check-map`, `inspect`, `adapt`, and `serve`.

## Customization

To search for different concepts, modify the filter in `research_agent.js`:

```javascript
const methodologyNodes = map.nodes.filter(node => 
    node.id.includes('your_concept') || 
    (node.summary && node.summary.toLowerCase().includes('your_concept'))
);
```

## Learn More

- [CiteKit Documentation](https://abdushakurob.github.io/citekit/)
- [Research App Guide](https://abdushakurob.github.io/citekit/guide/examples/research-app)

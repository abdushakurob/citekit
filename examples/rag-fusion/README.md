# CiteKit RAG Fusion Example

A **Hybrid High-Fidelity Architecture** combining traditional vector search with CiteKit's deterministic evidence extraction.

## What This Demonstrates

### Beyond "Dumb" Retrieval

In modern AI systems, retrieving a text chunk is often insufficient:

1. **Semantic Orphanage**: Retrieved text says *"As shown in Figure 4..."*, but without the actual figure, models hallucinate
2. **Context Overload**: Sending entire documents just to see one chart increases cost and reduces focus

### The Orchestration Workflow

This example implements a four-phase approach:

1. **Hybrid Indexing**
   - Text Part: Embed document text into Vector Database
   - Structure Part: Ingest into CiteKit (mapper processes file once)

2. **Multimodal Retrieval**
   - Vector search finds relevant text passages

3. **Context Orchestration** (CiteKit)
   - Detect when text references visual evidence
   - Resolve specific sections/nodes as images or PDF slices

4. **High-Fidelity Reasoning**
   - Send focused evidence packages (Text + High-Res Visual) to multimodal LLM
   - Achieve accurate grounding without context overload

## Prerequisites

- Python 3.9+
- A Gemini API key (or configure a custom mapper)

## Get the Example (Git)

```bash
git clone https://github.com/abdushakurob/citekit.git
cd citekit/examples/rag-fusion
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note**: Python users get all resolution dependencies automatically. If using JavaScript, install `npm install pdf-lib` for document resolution.

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

### 3. Add Sample Document

Place a PDF document in this directory and name it `sample_document.pdf`.

**Ideal document characteristics:**
- Technical content (specifications, research papers, manuals)
- Contains diagrams, figures, or charts
- Multiple sections with cross-references

## Running the Example

```bash
python hybrid_rag.py
```

The demo will:
1. **Index** the document in both vector DB and CiteKit
2. **Query** with example questions
3. **Show** how visual references are detected
4. **Extract** high-fidelity evidence using CiteKit
5. **Present** hybrid responses with verified evidence

## How It Works

### Phase 1: Hybrid Ingestion

```python
# Vector indexing (text chunks)
vector_db.add_document(text_chunk, metadata)

# CiteKit structural mapping (sent to mapper once)
resource_map = await citekit.ingest(file_path, "document")
```

### Phase 2: Intelligent Retrieval

## CLI Usage (Both SDKs Supported)

While this example uses Python's programmatic API, you can also use CLI commands for quick exploration:

**Python CLI:**
```bash
python -m citekit ingest sample_document.pdf document
python -m citekit list
python -m citekit structure doc_id
python -m citekit resolve doc_id figure_4
```

**JavaScript CLI:**
```bash
npx citekit ingest sample_document.pdf document
npx citekit list
npx citekit structure doc_id
npx citekit resolve doc_id figure_4
```

Both CLIs provide identical functionality (v0.1.8+), so choose based on your stack.

### Phase 2: Intelligent Retrieval (continued)

```python
# Discovery via vector search
results = vector_db.search(query)

# Detect if visual evidence is needed
if "Figure" in results[0].content:
    # Orchestrate high-fidelity extraction
    evidence = await citekit.resolve(resource_id, node_id)
```

## Performance & Reliability

| Strategy | Speed | Cost | Reliability |
| :--- | :--- | :--- | :--- |
| **Discovery-Only (Text)** | Very Fast | Low | Poor (Visual hallucinations) |
| **Full Vision RAG** | Slow | Extreme | High (Expensive tokens) |
| **CiteKit Hybrid** | **Fast** | **Low** | **Highest (Verified evidence)** |

## Architecture Benefits

### 1. Cost Efficiency

- Only send relevant visual evidence to multimodal models
- Avoid processing entire documents for single figures
- Cache structural maps for repeated queries

### 2. Accuracy Improvement

- No orphaned references (text without visuals)
- Deterministic extraction (no random chunks)
- Preserve diagrams, formulas, charts at original quality

### 3. Scalability

- Vector DB handles broad discovery across large corpora
- CiteKit provides surgical extraction on-demand
- Decouple indexing from retrieval for better performance

## Production Integration

### With Real Vector Databases

Replace the `SimpleVectorDB` with production systems:

```python
# ChromaDB
import chromadb
client = chromadb.Client()
collection = client.create_collection("docs")

# Pinecone
import pinecone
pinecone.init(api_key="...")
index = pinecone.Index("docs")

# Weaviate
import weaviate
client = weaviate.Client("http://localhost:8080")
```

### With Multimodal Models

Send extracted evidence to vision-capable models:

```python
# GPT-4V
response = openai.ChatCompletion.create(
    model="gpt-4-vision-preview",
    messages=[
        {"role": "user", "content": [
            {"type": "text", "text": query},
            {"type": "image_url", "image_url": evidence_url}
        ]}
    ]
)

# Gemini 1.5 Pro
model = genai.GenerativeModel('gemini-1.5-pro')
response = model.generate_content([query, image_data])

# Claude 3
response = anthropic.messages.create(
    model="claude-3-opus-20240229",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": query},
            {"type": "image", "source": {"type": "base64", "data": image_b64}}
        ]
    }]
)
```

## Advanced Patterns

### 1. Multi-Step Reasoning

```python
# Step 1: Broad discovery
text_results = vector_db.search("system design")

# Step 2: Extract related diagrams
for result in text_results:
    if has_visual_reference(result):
        evidence = await citekit.resolve(...)
        diagrams.append(evidence)

# Step 3: Comprehensive reasoning
response = multimodal_model.generate(
    context=text_results,
    visuals=diagrams
)
```

### 2. Agentic Workflows

```python
# Agent decides what evidence to gather
agent_plan = [
    "Find text about authentication",
    "Extract Figure 7 (auth flow)",
    "Get security checklist from Appendix A"
]

# Execute plan with hybrid retrieval
for step in agent_plan:
    if is_text_query(step):
        result = vector_db.search(step)
    else:
        result = await citekit.resolve(...)
```

### 3. Context Caching

```python
# CiteKit URIs enable stable references
uri = "document://spec#section_7_architecture"

# Cache multimodal responses
if uri in cache:
    return cache[uri]

# First time: full orchestration
evidence = await citekit.resolve_uri(uri)
response = multimodal_model.generate(query, evidence)
cache[uri] = response
```

## Why This is the Future

By treating CiteKit as a **Context Orchestrator** for your Vector Database, you enable **High-Density Agents**:

- Don't just "guess" from text chunks
- **Verify** by extracting exact source evidence
- Work like human engineers: read text, open diagrams, verify details
- Achieve GPT-4V-level understanding at 10x lower cost

## Learn More

- [CiteKit Documentation](https://abdushakurob.github.io/citekit/)
- [RAG Fusion Guide](https://abdushakurob.github.io/citekit/guide/examples/rag-fusion)
- [Architecture Concepts](https://abdushakurob.github.io/citekit/guide/concepts/architecture)
- [Python SDK Reference](https://abdushakurob.github.io/citekit/api/python)

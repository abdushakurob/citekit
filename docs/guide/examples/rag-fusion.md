# Example: Hybrid High-Fidelity Architectures

In this guide, we'll build a **Hybrid Context System**. We will use a traditional Vector Database (Embeddings) for broad discovery, and CiteKit as the **High-Fidelity Orchestrator** to provide the exact visual or temporal evidence (diagrams, charts, or video segments) required for a reliable response.

## Beyond "Dumb" Retrieval
In modern AI systems, retrieving a text chunk is often insufficient for reasoning:
1.  **Semantic Orphanage**: A retrieved text chunk might say *"As shown in Figure 4..."*, but without the actual figure, the model is left to hallucinate details.
2.  **Context Overload**: Sending the entire document just to see one chart increases cost and reduces model focus (attention loss).

## The Orchestration Workflow

1.  **Hybrid Indexing**:
    -   **Text Part**: Embed the document text into a Vector Database.
    -   **Structure Part**: Ingest the document into **CiteKit**. This sends the file to the configured mapper (Gemini by default) *one time* to generate a structural map.
2.  **Multimodal Retrieval**:
    -   A user query triggers a standard Vector Search to find the relevant text.
3.  **Context Orchestration (CiteKit)**:
    -   The agent detects that the text reference requires visual evidence.
    -   CiteKit **Resolves** the specific section/node as an image or mini-PDF instantly.
4.  **High-Fidelity Reasoning**:
    -   The agent sends the highly-focused "evidence package" (Text + High-Res Image) to a Multimodal LLM (e.g., Gemini 1.5 or GPT-4o).

## Implementation (Python)

```python
import asyncio
from citekit import CiteKitClient

# CiteKit acts as our high-fidelity orchestrator
citekit = CiteKitClient()

async def modern_hybrid_query(query: str, vector_db):
    # Discovery Phase: Find relevant text via semantic similarity
    results = vector_db.search(query, k=1)
    if not results: return "No text found."
    
    text_chunk = results[0].content
    
    # Orchestration Phase: CiteKit provides the "Evidence"
    # Imagine the text mentions: "Figure 7: System Topology"
    if "Figure 7" in text_chunk:
        print("Detected visual reference. Orchestrating evidence...")
        
        # Deterministic resolution of Section 7 (Diagram)
        evidence = await citekit.resolve(
            resource_id="internal_spec", 
            node_id="fig_7_topology"
        )
        
        return await call_multimodal_model(
            prompt=f"Based on the spec: {text_chunk}",
            image_path=evidence.output_path
        )

    return text_chunk
```

## Performance & Reliability

| Strategy | Speed | Cost | Reliability |
| :--- | :--- | :--- | :--- |
| **Discovery-Only (Text)** | Very Fast | Low | Poor (Visual hallucinations) |
| **Full Vision RAG** | Slow | Extreme | High (Expensive tokens) |
| **CiteKit Hybrid** | **Fast** | **Low** | **Highest (Verified evidence)** |

## Why this is the Future
By treating CiteKit as a **Context Orchestrator** for your Vector Database, you enable **High-Density Agents**. These agents don't just "guess" based on text chunks; they "verify" by opening the exact part of the source file they need—exactly like a human engineer would.

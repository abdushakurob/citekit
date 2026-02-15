# Example: Hybrid RAG (Diagram-Aware AI)

In this guide, we'll build a **Hybrid Retrieval** system. We will use a traditional Vector Database (RAG) to find text answers, and CiteKit to provide the **Visual Evidence** (diagrams, charts, or maps) related to those answers.

## The Problem with Pure RAG
Standard RAG is great for text, but it fails on multimodal documents:
1.  **Missing Visuals**: When RAG retrieves a text chunk that says *"As shown in Figure 4..."*, the LLM doesn't actually see Figure 4.
2.  **Broken Context**: Text-only embedding models ignore the charts and diagrams that are often the most important part of technical documentation.

## The Hybrid Solution: RAG + CiteKit

1.  **Indexing**:
    -   Chunk the document text into a **Vector Database** (e.g., Pinecone, Chroma).
    -   Ingest the document into **CiteKit** to create a structural map of all diagrams.
2.  **Retrieval**:
    -   User asks a question.
    -   Vector Search find the relevant **text chunk**.
3.  **Enhancement (CiteKit)**:
    -   If the text chunk mentions a diagram or figure, use CiteKit to **Resolve** that region as an image.
4.  **Reasoning**:
    -   Send both the **Text Chunk** and the **Resolved Image** to a multimodal LLM.

## Implementation (Python)

```python
import asyncio
from citekit import CiteKitClient

# 1. Setup CiteKit
citekit = CiteKitClient()

async def hybrid_query(query: str, vector_db):
    # STEP A: Standard Vector Search (Mocked for this example)
    # This returns the best-matching text chunk from a technical manual.
    text_chunk = vector_db.search(query, k=1)[0]
    
    print(f"RAG retrieved text: \"{text_chunk.text}\"")
    
    # STEP B: Detect Citations
    # Let's say the chunk says: "See the wiring diagram in Section 4.2"
    if "Section 4.2" in text_chunk.text:
        print("Detected visual reference! Extracting diagram via CiteKit...")
        
        # Resolve the specific section from the local file
        # CiteKit knows EXACTLY where Section 4.2 is as an image crop
        evidence = await citekit.resolve(
            resource_id="technical_manual", 
            node_id="section_4_2_diagram"
        )
        
        print(f"Diagram extracted to: {evidence.output_path}")
        
        # STEP C: Multimodal Reasoning
        # Use a model like Gemini 1.5 Pro to explain the diagram in context of the text
        response = await call_llm(
            prompt=f"Explain this based on the text: {text_chunk.text}",
            image_path=evidence.output_path
        )
        return response

    return text_chunk.text
```

## Comparison: Accuracy vs. Efficiency

| Strategy | Search Speed | Result Quality | Reliability |
| :--- | :--- | :--- | :--- |
| **Pure RAG** | Very Fast | Low (Hallucinates on "Figure 4") | Text-only |
| **Full Vision RAG** | Very Slow | High | Expensive (needs vision tokens for every chunk) |
| **Hybrid (CiteKit)** | **Fast** | **Highest** | **High (Verified visual evidence)** |

## Why use this for Images/Diagrams?
By using CiteKit as a "Visual Evidence Engine" for RAG, you get the best of both worlds:
-   **Text-based scale**: Search across millions of pages using vectors.
-   **Pixel-perfect precision**: Only pay for multimodal inference on the specific regions (Diagrams/Charts) that are actually relevant to the user's query.

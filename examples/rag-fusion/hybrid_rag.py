import asyncio
import os
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

from citekit import CiteKitClient

# Simulated Vector Database (replace with real ChromaDB, Pinecone, etc.)
@dataclass
class VectorResult:
    content: str
    metadata: dict
    score: float

class SimpleVectorDB:
    """Simulated vector database for demonstration.
    
    In production, replace with:
    - ChromaDB
    - Pinecone
    - Weaviate
    - Qdrant
    """
    
    def __init__(self):
        self.documents = []
    
    def add_document(self, content: str, metadata: dict):
        """Add a document chunk to the vector store."""
        self.documents.append({
            "content": content,
            "metadata": metadata
        })
    
    def search(self, query: str, k: int = 3) -> List[VectorResult]:
        """Simple keyword search (in production, use embeddings)."""
        results = []
        query_lower = query.lower()
        
        for doc in self.documents:
            # Simple scoring based on keyword matches
            content_lower = doc["content"].lower()
            score = sum(1 for word in query_lower.split() if word in content_lower)
            
            if score > 0:
                results.append(VectorResult(
                    content=doc["content"],
                    metadata=doc["metadata"],
                    score=score
                ))
        
        # Sort by score descending
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:k]

# Initialize CiteKit as the high-fidelity orchestrator
citekit = CiteKitClient(output_dir="evidence")

# Initialize vector database
vector_db = SimpleVectorDB()

async def ingest_hybrid(file_path: str):
    """Hybrid ingestion: Both vector embeddings and CiteKit mapping.
    
    This demonstrates the two-phase approach:
    1. Text extraction for vector search (broad discovery)
    2. CiteKit mapping for high-fidelity extraction
    """
    print(f"\n[PHASE 1] Vector Indexing: {Path(file_path).name}")
    
    # In production, use proper text extraction and embeddings
    # For this demo, we'll create simple chunks
    sample_chunks = [
        {
            "content": "The system architecture follows a microservices pattern as shown in Figure 7. Each service communicates via REST APIs.",
            "metadata": {"source": file_path, "page": 7, "section": "Architecture", "has_diagram": True, "diagram_ref": "fig_7_topology"}
        },
        {
            "content": "Performance benchmarks indicate 99.9% uptime. See Table 3 for detailed metrics across all services.",
            "metadata": {"source": file_path, "page": 12, "section": "Performance", "has_table": True}
        },
        {
            "content": "The authentication flow uses JWT tokens with RSA-256 signing. Security considerations are detailed in Appendix A.",
            "metadata": {"source": file_path, "page": 15, "section": "Security"}
        }
    ]
    
    for chunk in sample_chunks:
        vector_db.add_document(chunk["content"], chunk["metadata"])
    
    print(f"  ✓ Indexed {len(sample_chunks)} text chunks")
    
    print(f"\n[PHASE 2] CiteKit Structural Mapping: {Path(file_path).name}")
    
    # CiteKit ingestion (sends file to mapper ONCE)
    resource_map = await citekit.ingest(file_path, "document")
    
    print(f"  ✓ Mapped {len(resource_map.nodes)} structural nodes")
    print(f"  ✓ Resource ID: {resource_map.resource_id}")
    
    return resource_map.resource_id

def hybrid_query(query: str, resource_id: str):
    """Modern hybrid query: Vector search + CiteKit orchestration.
    
    This implements the pattern described in the documentation:
    1. Discovery: Vector search finds relevant text
    2. Analysis: Detect if visual evidence is needed
    3. Orchestration: CiteKit extracts high-fidelity evidence
    4. Reasoning: Combine text + visuals for final response
    """
    
    print(f"\n{'='*60}")
    print(f"QUERY: {query}")
    print(f"{'='*60}")
    
    # STEP 1: Discovery Phase - Vector Search
    print("\n[DISCOVERY] Searching vector database...")
    results = vector_db.search(query, k=1)
    
    if not results:
        return "No relevant text found in vector database."
    
    best_result = results[0]
    print(f"  ✓ Found relevant text (score: {best_result.score})")
    print(f"  Section: {best_result.metadata.get('section', 'Unknown')}")
    print(f"  Content: {best_result.content[:100]}...")
    
    # STEP 2: Analysis - Detect Visual References
    needs_visual = (
        "figure" in best_result.content.lower() or
        "diagram" in best_result.content.lower() or
        "chart" in best_result.content.lower() or
        best_result.metadata.get("has_diagram", False) or
        best_result.metadata.get("has_table", False)
    )
    
    if not needs_visual:
        print("\n[RESPONSE] Text-only response (no visual evidence needed)")
        return f"**Answer:** {best_result.content}"
    
    # STEP 3: Context Orchestration - CiteKit High-Fidelity Extraction
    print("\n[ORCHESTRATION] Visual reference detected. Extracting evidence...")
    
    # Get the CiteKit map to find the relevant node
    resource_map = citekit.get_map(resource_id)
    
    # Find node matching the section (in production, LLM would choose)
    target_node = None
    section = best_result.metadata.get("section", "").lower()
    diagram_ref = best_result.metadata.get("diagram_ref")
    
    for node in resource_map.nodes:
        node_id_lower = node.id.lower()
        if diagram_ref and diagram_ref in node_id_lower:
            target_node = node
            break
        elif section and section in node_id_lower:
            target_node = node
            break
    
    if not target_node:
        # Fallback: use first node
        print("  ⚠ No exact match, using first available node")
        target_node = resource_map.nodes[0] if resource_map.nodes else None
    
    if not target_node:
        return f"**Answer:** {best_result.content}\n\n*Note: Visual evidence requested but no structural nodes available.*"
    
    print(f"  ✓ Resolving node: {target_node.id}")
    
    # Deterministic extraction of the visual evidence
    evidence = client.resolve(resource_id, target_node.id)
    
    print(f"  ✓ Evidence extracted: {evidence.output_path}")
    
    # STEP 4: High-Fidelity Response
    print("\n[RESPONSE] Hybrid response with verified evidence")
    
    response = f"""**Answer:** {best_result.content}

**High-Fidelity Evidence:**
- Type: {evidence.content_type}
- Location: {evidence.output_path}
- Node: {target_node.title or target_node.id}

In a production system, this evidence would be:
1. Sent to a multimodal model (GPT-4V, Gemini 1.5 Pro, Claude 3)
2. Used for visual reasoning (analyzing diagrams, charts, formulas)
3. Grounded with the original text for highest accuracy
"""
    
    return response

async def main():
    """Demonstration of hybrid high-fidelity architecture."""
    
    print("="*60)
    print("CiteKit Hybrid RAG Fusion Demo")
    print("="*60)
    print("\nThis demonstrates combining:")
    print("  • Vector Database (broad discovery)")
    print("  • CiteKit (high-fidelity evidence extraction)")
    print("\nFor production-grade multimodal AI systems.")
    
    # Check for sample document
    sample_doc = Path("sample_document.pdf")
    
    if not sample_doc.exists():
        print("\n" + "="*60)
        print("SETUP REQUIRED")
        print("="*60)
        print("\nTo run this demo, add a PDF document:")
        print("  1. Place a PDF file in this directory")
        print("  2. Name it 'sample_document.pdf'")
        print("  3. Run this script again")
        print("\nThe document should ideally contain:")
        print("  • Technical content")
        print("  • Diagrams or figures")
        print("  • Multiple sections")
        print("\nExiting demo...")
        return
    
    # Ingest the document (hybrid indexing)
    resource_id = await ingest_hybrid(str(sample_doc))
    
    # Example queries demonstrating the hybrid approach
    queries = [
        "What is the system architecture?",
        "Show me the performance metrics",
        "How does authentication work?"
    ]
    
    for query in queries:
        response = hybrid_query(query, resource_id)
        print(response)
        print()

if __name__ == "__main__":
    asyncio.run(main())

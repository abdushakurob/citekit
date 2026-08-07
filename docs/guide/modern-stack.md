# The Modern AI Stack

CiteKit is designed to work alongside modern retrieval and agentic techniques, providing the high-fidelity "bridge" between discovery and reasoning.

## Enhancing Modern AI Architectures

Modern AI workflows (Agentic RAG, Long-Context, etc.) often require more precision than arbitrary text chunking can provide. CiteKit introduces **Semantic Structure**, which acts as a high-fidelity bridge for the following techniques.

---

## 1. Retrieval Techniques

CiteKit complements the latest in retrieval science:

*   **Hybrid & Dense Retrieval**: While Vector Search (Dense) and Keyword Search (BM25) find *where* information might be, CiteKit provides the *exact file boundaries* (page ranges, timestamps) to ensure the model sees the full context of a citation.
*   **Reranking**: Use Rerankers to score nodes in a CiteKit map. This combines CiteKit's structural precision with a second model's accuracy.
*   **Hierarchical Retrieval**: This is where CiteKit shines. CiteKit allows you to retrieve at the **Document → Section → Paragraph** level natively, preserving the relationship between parent and child nodes.
*   **GraphRAG**: CiteKit maps can be used as the structural foundation for Knowledge Graphs, mapping entities directly to their visual or temporal locations in multimodal files.

## 2. Long-Context Handling

Modern models (Gemini 1.5, GPT-4o) have massive context windows, but they are not "infinite attention" machines.

*   **Complementing Long-Context**: Even with a 1M+ context window, models suffer from the "Lost in the Middle" effect. CiteKit lets you send **High-Density blocks** (LongRAG style)—sending only the relevant 50 pages of a 500-page book keeps the attention focused and the cost low.
*   **Contextual Retrieval**: By mapping files first, CiteKit ensuring that every retrieved "chunk" is actually a coherent semantic unit (like a full scene or a whole chart).

## 3. Context Efficiency

CiteKit is a performance multiplier for context optimization:

*   **Context Caching**: CiteKit's stable URI pointers (e.g., `doc://resource#pages=12-15`) are perfect keys for **Context Caching**. You can resolve the same semantic slice across different agent runs without re-processing.
*   **Semantic Caching**: If a similar query is retrieved, CiteKit can immediately resolve the associated media node from its local storage.

## 4. Agentic Workflows

CiteKit is built for **Autonomous Agents**:

*   **Agentic RAG**: In this paradigm, the LLM is a planner. It uses CiteKit as a **Tool** to "open" specific parts of a file, just like a human collaborator would.
*   **Tool-Using Agents (ReAct)**: CiteKit provides the `ingest`, `list`, and `resolve` tools that allow an agent to reason about a file's structure and then act to retrieve specific evidence.
*   **Context Orchestration**: CiteKit serves as the orchestrator, allowing multi-agent systems to pass high-fidelity "evidence" (mini-PDFs, clips) between specialized agents (e.g., a "Researcher" agent passing a clip to a "Critic" agent).

## Context Window Economics

One of the greatest challenges in modern AI is **Context Exhaustion**. Even with 1M+ token windows, sending large media files repeatedly is slow and expensive.

CiteKit solves this through **Deterministic Pre-Mapping**:
-   **The Mapping Tax**: You spend ~50k–150k tokens (multimodal) to `ingest` a file once.
-   **The Metadata Dividend**: The resulting JSON map (~2KB) fits into *any* context window. Your agent can now "know" about every scene in a feature-length film for less than 500 tokens of prompt space.
-   **Surgical Resolution**: When the agent needs to "see" a scene, it resolves only the relevant 3-minute clip. This keeps the attention mechanism focused and the per-query token cost near zero.

---

## Summary: Where CiteKit Fits

| Technique | CiteKit's Role |
| :--- | :--- |
| **Vector Search** | The "High-Fidelity" fallback. Vectors find the text; CiteKit provides the visual evidence. |
| **Agentic RAG** | The primary tool for navigating multimodal file structures. |
| **Context Caching** | The stable URI provider for cache-keying specific semantic slices. |
| **Long-Context** | The "Attention Filter" that keeps models focused on relevant data blocks. |

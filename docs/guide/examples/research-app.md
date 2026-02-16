# Example: Agentic Research Engine (Node.js)

In this tutorial, we'll build an **Agentic Research** tool. It uses CiteKit to navigate a library of technical papers, performing **Contextual Retrieval** to extract specific sections (like "Methodology") with perfect fidelity.

This demonstrates the core power of CiteKit: Providing **Deterministic Evidence** for high-density research agents.

## Why this is a "Modern" Approach

Unlike traditional systems that rely on keyword search or random text chunks, an **Agentic Research** workflow uses CiteKit to:
1.  **Understand Structure**: The agent sees the "TOC" of the document first.
2.  **Navigate Hierarchically**: It decides which section is relevant based on summaries.
3.  **Extract Deterministically**: It pulls the exact pages, preserving all diagrams, formulas, and formatting.

## Prerequisites

-   Node.js 18+
-   A Gemini API Key.

## 1. Project Setup

```bash
mkdir citekit-research-agent
cd citekit-research-agent
npm init -y
npm install citekit dotenv
```

## 2. The Implementation

```javascript
/* research_agent.js */
import 'dotenv/config';
import fs from 'node:fs';
import path from 'node:path';
import { CiteKitClient } from 'citekit';

// CiteKit acts as the "Optical" layer for our researcher
const client = new CiteKitClient({
    outputDir: 'research_evidence'
});

async function runResearchTask() {
    const paperPath = './papers/deep_research_v4.pdf';
    
    console.log(`🔍 Inspecting Paper: ${path.basename(paperPath)}`);

    // STEP 1: Discovery (Ingestion)
    // The file is sent to the Gemini File API ONCE to generate the map.
    // This is the only time the file leaves your local machine.
    const map = await client.ingest(paperPath, 'document');
    
    // STEP 2: Intent Analysis
    // We want to find where the experimental methodology is.
    // In a real agent, the LLM would pick these node IDs.
    const methodologyNodes = map.nodes.filter(node => 
        node.id.includes('method') || node.summary?.includes('experimental')
    );

    // STEP 3: Contextual Retrieval & Evidence Extraction
    for (const node of methodologyNodes) {
        console.log(`🎯 Orchestrating Context: "${node.title}"`);
        
        // This extracts the specific pages as a high-fidelity PDF slice
        const evidence = await client.resolve(map.resource_id, node.id);
        
        console.log(`✅ Evidence extracted to: ${evidence.output_path}`);
    }
}

runResearchTask().catch(console.error);
```

## Modern Capabilities

### 1. Hierarchical Navigation
By using the CiteKit Map, your agent doesn't have to "guess" where information is. It sees a recursive structure of Parts → Chapters → Sections, allowing for **Zoomable Context**.

### 2. High-Density Grounding
When the agent cites a formula or a diagram from page 14, it doesn't just quote text. It provides the **Visual Evidence** (the PDF slice) to the reasoning model, ensuring the most accurate grounding possible.

### 3. Context Orchestration
This pattern is ideal for **Multi-Agent Systems**. One agent (the "Map Reader") identifies the relevant nodes, and another agent (the "Verifier") receives the sliced PDF to perform deep analysis.

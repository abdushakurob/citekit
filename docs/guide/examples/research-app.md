# Build a Research Assistant (Node.js)

In this tutorial, we will build a complete command-line tool that scans a folder of PDF research papers, finds their "Methodology" sections, and extracts them as standalone PDFs.

This demonstrates the core power of CiteKit: **Structured Extraction** without needing a vector database.

## Prerequisites

-   Node.js 18+
-   A folder containing some PDF research papers.
-   A Gemini API Key.

## 1. Project Setup

Create a new directory and initialize your project:

```bash
mkdir research-extractor
cd research-extractor
npm init -y
npm install citekit dotenv
```

Create a `.env` file with your API key:

```env
GEMINI_API_KEY=AIzaSy...
```

## 2. The Implementation

Create `extract.js`:

```javascript
/* extract.js */
import 'dotenv/config';
import fs from 'node:fs';
import path from 'node:path';
import { CiteKitClient } from 'citekit';

// Initialize CiteKit (Local-First by default)
const client = new CiteKitClient({
    storageDir: '.resource_maps',
    outputDir: 'extracted_methods'
});

async function main() {
    const inputDir = './papers';
    
    // 1. Get all PDF files
    if (!fs.existsSync(inputDir)) {
        console.error(`Error: Directory '${inputDir}' not found.`);
        return;
    }
    
    const papers = fs.readdirSync(inputDir).filter(file => file.endsWith('.pdf'));
    console.log(`Found ${papers.length} papers to process...`);

    for (const file of papers) {
        const filePath = path.join(inputDir, file);
        console.log(`\n📄 Processing: ${file}`);

        // 2. Ingest: Generate the Map (Cached automatically)
        const resourceMap = await client.ingest(filePath, 'document');
        
        // 3. Search: Find the relevant nodes in the map
        const methodologyNodes = resourceMap.nodes.filter(node => {
            const id = node.id.toLowerCase();
            const summary = (node.summary || "").toLowerCase();
            
            return id.includes('method') || 
                   id.includes('experiment') || 
                   summary.includes('how we tested');
        });

        if (methodologyNodes.length === 0) {
            console.log("   ⚠️ No methodology section found.");
            continue;
        }

        // 4. Resolve: Extract semantic sections
        for (const node of methodologyNodes) {
            console.log(`   🎯 Found: "${node.id}" (Pages ${node.location.start}-${node.location.end})`);
            
            // This pulls ONLY these pages into a new PDF
            const evidence = await client.resolve(resourceMap.resource_id, node.id);
            console.log(`      ✅ Extracted: ${evidence.output_path}`);
        }
    }
}

main().catch(console.error);
```

## 3. Comparision: Why Use This Approach?

### vs. Context Stuffing
**Context Stuffing**: You allow the LLM to read all 20 PDFs (File Upload).
*   **Cost**: Huge. You pay for 100% of tokens for every query.
*   **Performance**: "Lost in the Middle" phenomenon. Finding a specific methodology detail in 500 pages of text often fails.
*   **Latency**: Waiting for 500 pages to be processed takes ~30-60s.

**CiteKit**:
*   **Cost**: You pay for mapping *once*. Queries run on local JSON (free).
*   **Performance**: You extract only the 3 pages that matter. The LLM sees *exactly* what it needs to see.

### vs. Traditional RAG (Vector DB)
**RAG**: You chunk the PDF into 500-word segments and embed them.
*   **Loss of Layout**: Equations, tables, and diagrams in methodology sections are often mangled by text extractors.
*   **Fragmentation**: A "Methodology" section is a logical unit. RAG returns random paragraphs *from* the section, possibly missing the critical context or the diagram on the next page.

**CiteKit**:
*   **Semantic Integrity**: The map identifies the "Methodology" as a start/end page range.
*   **Visual Fidelity**: By extracting a *PDF subset* (pages 3-5), you preserve the layout, fonts, and diagrams perfectly for a multimodal Model.

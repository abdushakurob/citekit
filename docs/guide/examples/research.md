# Example: AI Research Dashboard

In this example, we show how to build an AI-powered research assistant that can pinpoint methodology and results across a library of PDFs without ever uploading the full papers to the cloud.

## The Workflow

1.  **Batch Ingestion**: Ingest a folder of scientific papers. CiteKit generates maps for each.
2.  **Breadth-First Query**: The agent searches the **Resource Maps** for "Methodology" sections.
3.  **Local Resolution**: CiteKit extracts only those sections as mini-PDFs.
4.  **Synthesis**: The agent reads the extracted sections and provides a master synthesis.

## Implementation (JavaScript)

```javascript
import { CiteKitClient } from 'citekit';
import path from 'node:path';
import fs from 'node:fs';

const client = new CiteKitClient();

async function analyzePapers(paperFolder) {
    const files = fs.readdirSync(paperFolder).filter(f => f.endsWith('.pdf'));
    
    // 1. Ingest all papers (Cached automatically)
    for (const file of files) {
        await client.ingest(path.join(paperFolder, file), 'document');
    }

    // 2. Search for "Methodology" across all maps
    const allResources = client.listMaps();
    for (const resId of allResources) {
        const map = client.getStructure(resId);
        
        // Find nodes related to methodology
        const methodologyNodes = map.nodes.filter(n => 
            n.id.toLowerCase().includes('method') || 
            n.summary?.toLowerCase().includes('how')
        );

        // 3. Resolve and synthesize
        for (const node of methodologyNodes) {
            const evidence = await client.resolve(resId, node.id);
            console.log(`Extracted methodology for ${resId}: ${evidence.output_path}`);
            
            // Now you can send 'evidence.output_path' to your LLM
            // The LLM gets a 2-page PDF instead of a 40-page one!
        }
    }
}
```

## Why this is better than search
-   **Context**: The LLM gets the actual PDF pages of the methodology, including the tables and equations that raw text-PDF-parsing often fails on.
-   **Cost**: You send ~50kb of PDF data to your synthesis LLM instead of ~5MB.
-   **Speed**: No vector database required. Finding sections in the locally-stored JSON map is microsecond-fast.

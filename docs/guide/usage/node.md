# Node.js SDK Guide

The Node.js SDK provides a fully typed TypeScript interface for CiteKit, making it ideal for web applications (Next.js, Express) and serverless functions.

## Initialization

The `CiteKitClient` class accepts a configuration object to customize paths and API behavior.

```typescript
import { CiteKitClient } from 'citekit';

// Default Initialization
const client = new CiteKitClient();

// Custom Configuration
const client = new CiteKitClient({
    storageDir: "./.maps",       // Custom map storage location
    outputDir: "./public/media", // Output resolvable files to public folder
    apiKey: process.env.GEMINI_KEY, // Explicit API key
    concurrencyLimit: 5          // Control parallel ingestion
});
```

## 1. Ingestion (Mapping)

Ingestion is asynchronous. It returns a `ResourceMap` object containing the file's structure.

```typescript
async function mapContent() {
    try {
        const videoMap = await client.ingest(
            "./uploads/lecture.mp4", 
            "video" // 'video' | 'audio' | 'document' | 'image' | 'text'
        );
        
        console.log(`Map ID: ${videoMap.resource_id}`);
        console.log(`Detected Title: ${videoMap.title}`);
    } catch (error) {
        console.error("Ingestion failed:", error);
    }
}
```

## 2. Inspection (Planning)

You can retrieve resource maps synchronously or asynchronously depending on your needs. The structure is fully typed.

```typescript
// Get the map structure
const map = client.getStructure("lecture_01");

// Navigate the tree
map.nodes.forEach(node => {
    console.log(`Section: ${node.title} (${node.id})`);
    
    // Check location type
    if (node.location.start !== undefined) {
        console.log(`Review from ${node.location.start}s to ${node.location.end}s`);
    }
});
```

## 3. Resolution (Extraction)

Extraction supports both physical file creation and virtual metadata resolution.

### Physical Resolution
Useful for creating clips or slices to serve to a user.

```typescript
const result = await client.resolve(
    "lecture_01",    // resource_id
    "chapter_2_demo" // node_id
);

// Points to the generated file on disk
// e.g., /app/public/media/lecture_01_chapter_2_demo.mp4
console.log(result.output_path);
```

### Virtual Resolution (Serverless/Edge)
If you are running in a restricted environment (like Vercel Edge or AWS Lambda) where specialized tools like FFmpeg aren't available, or you just want to control a frontend player, use virtual resolution.

```typescript
const result = await client.resolve(
    "lecture_01", 
    "chapter_2_demo", 
    { virtual: true }
);

// No file created
console.log(result.output_path); // null

// Use metadata to drive logic
const { start, end } = result.node.location;
// return res.json({ jumpTo: start, duration: end - start });
```

## Configuration

```typescript
const client = new CiteKitClient({
    baseDir: '/tmp',        // For serverless (Vercel/AWS)
    concurrencyLimit: 5,
    apiKey: process.env.GEMINI_API_KEY
});
```

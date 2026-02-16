# JavaScript/TypeScript Resolvers — Complete API Reference

Resolvers handle physical extraction of content from resources. They extract video clips, PDF pages, image crops, audio segments, or text lines.

---

## Resolvers Overview

All resolvers implement a common interface and are automatically instantiated by `CiteKitClient`. You can access them directly if needed.

### Base Interface: `Resolver`

```typescript
export interface Resolver {
    /**
     * Extract evidence for a node from the source file.
     *
     * @param resourceId - The resource ID
     * @param nodeId - The node ID to resolve
     * @param sourcePath - Path to the source file
     * @param location - Node location information
     * @param outputDir - Directory for output files
     * @param options - Optional resolution parameters
     * @returns ResolvedEvidence or URL
     * @throws Error if extraction fails
     */
    resolve(
        resourceId: string,
        nodeId: string,
        sourcePath: string,
        location: Location,
        outputDir: string,
        options?: any
    ): Promise<any>;
}
```

---

## `DocumentResolver` (PDF/eBook)

Extracts pages from PDF and eBook files.

### Dependencies

- **NPM**: `pdf-lib` for PDF manipulation
- **Install**: `npm install pdf-lib`

### Usage

```typescript
import { DocumentResolver } from 'citekit';

const resolver = new DocumentResolver();

const evidence = await resolver.resolve(
    'textbook',
    'chapter_2',
    '/path/to/textbook.pdf',
    { modality: 'document', pages: [12, 15] },
    '.citekit_output'
);

console.log(evidence);
// { output_path: '.citekit_output/textbook_chapter_2.pdf', ... }
```

### Location Schema

```typescript
// location must have:
{
    modality: 'document',
    pages: [12, 15]  // 1-indexed: pages 12 through 15
}
```

### Example

```typescript
import { CiteKitClient } from 'citekit';

const client = new CiteKitClient({ apiKey: process.env.GEMINI_API_KEY });

// Ingest a PDF
const map = await client.ingest('textbook.pdf', 'document');

// Resolve pages 5-10
const evidence = await client.resolve('textbook', 'chapter_1', { virtual: false });
// Output: .citekit_output/textbook_chapter_1.pdf (pages 5-10)
```

### Error Codes

**Success**:
```typescript
{ output_path: '.citekit_output/textbook_chapter_1.pdf', ... }
```

**File Not Found**:
```
Error: Source file not found: /path/to/document.pdf
```

**Invalid Pages**:
```
Error: Invalid page range [5, 100] for document with 50 pages
```

**Corrupted PDF**:
```
Error: PDF parsing failed
Could not read PDF file. File may be encrypted or corrupted.
```

**Unsupported Format**:
```
Error: File format not supported
Only PDF files are supported
```

---

## `VideoResolver` (MP4, WebM, MOV)

Extracts video segments/clips using FFmpeg.

### Dependencies

- **External**: `ffmpeg` binary must be installed
- **NPM**: `fluent-ffmpeg` for Node.js integration
- **Install**:
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt-get install ffmpeg`
  - Windows: Download from https://ffmpeg.org

### Usage

```typescript
import { VideoResolver } from 'citekit';

const resolver = new VideoResolver();

const evidence = await resolver.resolve(
    'lecture_01',
    'chapter_1.intro',
    '/path/to/lecture.mp4',
    { modality: 'video', start: 145.0, end: 285.0 },
    '.citekit_output'
);

console.log(evidence);
// { output_path: '.citekit_output/lecture_01_chapter_1_intro.mp4', ... }
```

### Location Schema

```typescript
// location must have:
{
    modality: 'video',
    start: 145.0,      // seconds (float)
    end: 285.0         // seconds (float)
}
```

### Example

```typescript
import { CiteKitClient } from 'citekit';

const client = new CiteKitClient({ apiKey: process.env.GEMINI_API_KEY });

// Ingest a video
const map = await client.ingest('lecture.mp4', 'video');

// Extract clip from 2:25 to 4:45
const evidence = await client.resolve('lecture', 'intro');
// Output: .citekit_output/lecture_intro.mp4 (140s clip)
```

### Error Codes

**Success**:
```typescript
{ output_path: '.citekit_output/lecture_intro.mp4', ... }
```

**FFmpeg Not Found**:
```
Error: ffmpeg binary not found
Install: brew install ffmpeg (macOS) or apt-get install ffmpeg (Linux)
```

**Invalid Timestamps**:
```
Error: Invalid time range [500.0, 400.0] (start > end)
```

**Corrupted Video**:
```
Error: FFmpeg failed to process video
Video file is corrupted or unsupported format
```

**Codec Not Supported**:
```
Error: Video codec not supported
FFmpeg may not support this video format
```

---

## `AudioResolver` (MP3, WAV, M4A)

Extracts audio segments using FFmpeg.

### Dependencies

- **External**: `ffmpeg` binary (same as VideoResolver)
- **NPM**: `fluent-ffmpeg`

### Usage

```typescript
import { AudioResolver } from 'citekit';

const resolver = new AudioResolver();

const evidence = await resolver.resolve(
    'podcast_01',
    'episode_1.intro',
    '/path/to/podcast.mp3',
    { modality: 'audio', start: 0.0, end: 60.0 },
    '.citekit_output'
);

console.log(evidence);
// { output_path: '.citekit_output/podcast_01_episode_1_intro.mp3', ... }
```

### Location Schema

```typescript
// location must have:
{
    modality: 'audio',
    start: 30.5,       // seconds (float)
    end: 150.0         // seconds (float)
}
```

### Example

```typescript
const evidence = await client.resolve('podcast_01', 'episode_1.intro');
// Output: .citekit_output/podcast_01_episode_1_intro.mp3 (60s segment)
```

---

## `ImageResolver` (JPG, PNG, WebP)

Crops image regions based on bounding box.

### Dependencies

- **NPM**: `sharp` for fast image processing
- **Install**: `npm install sharp`

### Usage

```typescript
import { ImageResolver } from 'citekit';

const resolver = new ImageResolver();

const evidence = await resolver.resolve(
    'photo_album',
    'photo_1.person',
    '/path/to/photo.jpg',
    { modality: 'image', bbox: [0.6, 0.2, 0.9, 0.8] },
    '.citekit_output'
);

console.log(evidence);
// { output_path: '.citekit_output/photo_album_photo_1_person.jpg', ... }
```

    bbox: [x1, y1, x2, y2]  // Normalized 0-1 corners (top-left to bottom-right)

```typescript
// location must have:
- `x1`: Left edge (0 = leftmost, 1 = rightmost)
- `y1`: Top edge (0 = topmost, 1 = bottommost)
- `x2`: Right edge (0 = leftmost, 1 = rightmost)
- `y2`: Bottom edge (0 = topmost, 1 = bottommost)
```

**Coordinates** (all 0-1 normalized):
- `x`: Left edge (0 = leftmost, 1 = rightmost)
- `y`: Top edge (0 = topmost, 1 = bottommost)
- `width`: Crop width (0.5 = half image width)
- `height`: Crop height (0.5 = half image height)

### Example

```typescript
// Crop bottom-right corner (person's face)
const evidence = await client.resolve('photo_album', 'photo_1.person');
// bbox [0.6, 0.2, 0.9, 0.8] → crops from 60%→90% width and 20%→80% height
// Output: .citekit_output/photo_album_photo_1_person.jpg (cropped)
```

### Error Codes

**Invalid Bbox**:
```
Error: Invalid bbox [1.5, 0.5, 0.3, 0.3] (values must be 0-1)
```

**Unsupported Format**:
```
Error: Image format not supported
Supported: JPG, PNG, WebP, BMP
```

---

## `TextResolver` (TXT, MD, PY, JS)

Extracts lines from text files (source code, markdown, etc.).

### Dependencies

- **None** - uses native Node.js file reading

### Usage

```typescript
import { TextResolver } from 'citekit';

const resolver = new TextResolver();

const evidence = await resolver.resolve(
    'main_code',
    'function_process',
    '/path/to/code.py',
    { modality: 'text', lines: [5, 15] },
    '.citekit_output'
);

console.log(evidence);
// { output_path: '.citekit_output/main_code_function_process.py', ... }
```

### Location Schema

```typescript
// location must have:
{
    modality: 'text',
    lines: [5, 15]     // 1-indexed: lines 5 through 15
}
```

### Example

```typescript
// Extract function definition
const evidence = await client.resolve('main_code', 'function_process');
// Extracts lines 5-15 from code.py
// Output: .citekit_output/main_code_function_process.py
```

### Error Codes

**Invalid Line Range**:
```
Error: Invalid line range [5, 100] for file with 50 lines
```

**File Not Found**:
```
Error: Source file not found: /path/to/code.py
```

---

## Virtual Resolution

For all resolvers, if a node has `modality: 'virtual'`, no extraction occurs:

```typescript
const evidence = await client.resolve('resource_id', 'node_id', { virtual: true });

console.log(evidence);
// { 
//   output_path: undefined,  // No file
//   address: 'virtual://resource_id#node_123',
//   modality: 'virtual'
// }
```

---

## Resolver Interface (Advanced)

If you need to implement a custom resolver:

```typescript
import type { Location } from 'citekit';

export class CustomResolver {
    async resolve(
        resourceId: string,
        nodeId: string,
        sourcePath: string,
        location: Location,
        outputDir: string,
        options?: any
    ): Promise<any> {
        // 1. Validate inputs
        if (!existsSync(sourcePath)) {
            throw new Error(`File not found: ${sourcePath}`);
        }

        // 2. Extract based on location
        const outputPath = await this.extract(sourcePath, location, outputDir);

        // 3. Return evidence
        return {
            output_path: outputPath,
            modality: location.modality
        };
    }

    private async extract(sourcePath: string, location: Location, outputDir: string): Promise<string> {
        // Your extraction logic
        return outputPath;
    }
}
```

---

## Performance Benchmarks

| Resolver | Input Size | Time | Output Size |
| :--- | :--- | :--- | :--- |
| DocumentResolver (10 pages) | 5MB | 0.5-1s | 500KB |
| VideoResolver (5s clip, H.264) | 500MB | 2-3s | 10-15MB |
| AudioResolver (1min, MP3) | 1MB | 1-2s | 500KB |
| ImageResolver (bbox crop) | 5MB | 0.2-0.5s | 1-2MB |
| TextResolver (100 lines) | 10KB | 10ms | 5KB |

---

## Error Handling Pattern

```typescript
async function resolveWithErrorHandling(
    client: CiteKitClient,
    resourceId: string,
    nodeId: string
): Promise<string | null> {
    try {
        const evidence = await client.resolve(resourceId, nodeId);
        return evidence.output_path;
    } catch (error) {
        if (error instanceof Error) {
            if (error.message.includes('not found')) {
                console.error('Resource or node not found');
            } else if (error.message.includes('extraction failed')) {
                console.error('Extraction failed - try virtual mode');
            } else {
                console.error(`Unexpected error: ${error.message}`);
            }
        }
        return null;
    }
}
```

---

## Type Definitions

```typescript
interface Location {
    modality: 'video' | 'audio' | 'document' | 'image' | 'text' | 'virtual';
    
    // Video/Audio
    start?: number;
    end?: number;
    
    // Document
    pages?: number[];
    
    // Image
    bbox?: [number, number, number, number]; // [x1, y1, x2, y2]
    
    // Text
    lines?: [number, number];
    
    // Virtual
    virtual_address?: string;
}

interface ResolvedEvidence {
    output_path?: string;      // Path to extracted file (undefined if virtual)
    modality: string;
    address: string;           // URI address
    node: Node;
    resource_id: string;
}
```

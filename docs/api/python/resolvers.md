# Python Resolvers & Adapters — Complete API Reference

Resolvers handle physical extraction of content from resources. Adapters convert external data formats into CiteKit `ResourceMap` objects.

---

    "bbox": [x1, y1, x2, y2]  # Normalized 0-1 corners

Resolvers take a `Node` with location data and extract the physical segment from the source file.

- `x1`: Left edge (0 = leftmost, 1 = rightmost)
- `y1`: Top edge (0 = topmost, 1 = bottommost)
- `x2`: Right edge (0 = leftmost, 1 = rightmost)
- `y2`: Bottom edge (0 = topmost, 1 = bottommost)
from citekit.models import Node

class Resolver(ABC):
    """Base class for all resolvers."""
    
    def __init__(self, output_dir: str = ".citekit_output"):
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def resolve(self, node: Node, source_path: str) -> str:
        """Extract evidence for a node from the source file.
        
        Args:
            node: The node to resolve, containing location info
            source_path: Path to the original resource file
            
        Returns:
            Path to the generated output file
            
        Raises:
            FileNotFoundError: If source file doesn't exist
            ValueError: If node location is invalid
            RuntimeError: If extraction fails
        """
        ...
```

---

## `DocumentResolver` (PDF/eBook)

Extracts pages from PDF and eBook files.

### Dependencies

- **Python**: `pymupdf` (PyMuPDF)
- **Install**: `pip install pymupdf`

### Signature

```python
from citekit.resolvers.document import DocumentResolver

resolver = DocumentResolver(output_dir=".citekit_output")
output_path = resolver.resolve(node, "/path/to/document.pdf")
```

### Location Schema

```python
# node.location must have:
{
    "modality": "document",
    "pages": [1, 2, 3]  # 1-indexed list of page numbers
}
```

### Example

```python
from citekit.models import Node, Location

# Resolve pages 5-10 from a PDF
node = Node(
    id="chapter_2",
    title="Chapter 2",
    type="section",
    location=Location(modality="document", pages=[5, 6, 7, 8, 9, 10])
)

resolver = DocumentResolver()
output_path = resolver.resolve(node, "textbook.pdf")
# Output: .citekit_output/textbook_chapter_2.pdf (pages 5-10 only)
```

### Error Codes

**Success**:
```
.citekit_output/textbook_chapter_2.pdf
```

**File Not Found**:
```
FileNotFoundError: Source file not found: /path/to/document.pdf
```

**Invalid Pages**:
```
ValueError: Invalid page range [5, 100] for document with 50 pages
```

**Corrupted PDF**:
```
RuntimeError: PyMuPDF failed to read PDF
  Error: File is encrypted or corrupted
```

**No Permissions**:
```
PermissionError: Cannot write to output directory: .citekit_output
```

---

## `VideoResolver` (MP4, WebM, MOV)

Extracts video segments/clips.

### Dependencies

- **External**: `ffmpeg` binary
- **Python**: `ffmpeg-python` (optional, but recommended)
- **Install**: 
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt-get install ffmpeg`
  - Windows: Download from https://ffmpeg.org

### Signature

```python
from citekit.resolvers.video import VideoResolver

resolver = VideoResolver(output_dir=".citekit_output")
output_path = resolver.resolve(node, "/path/to/lecture.mp4")
```

### Location Schema

```python
# node.location must have:
{
    "modality": "video",
    "start": 145.5,    # seconds (float)
    "end": 285.0       # seconds (float)
}
```

### Example

```python
from citekit.models import Node, Location

# Extract video clip from 2:25 to 4:45
node = Node(
    id="chapter_1.intro",
    title="Introduction",
    type="section",
    location=Location(modality="video", start=145.0, end=285.0)
)

resolver = VideoResolver()
output_path = resolver.resolve(node, "lecture.mp4")
# Output: .citekit_output/lecture_chapter_1_intro.mp4 (140s duration)
```

### Error Codes

**Success**:
```
.citekit_output/lecture_chapter_1_intro.mp4
```

**FFmpeg Not Found**:
```
RuntimeError: ffmpeg binary not found
  Install: brew install ffmpeg (macOS) or apt-get install ffmpeg (Linux)
```

**Invalid Timestamps**:
```
ValueError: Invalid time range [500.0, 400.0] (start > end)
```

**Corrupted Video**:
```
RuntimeError: FFmpeg failed to read video
  Error: Video file is corrupted or unsupported format
```

**Codec Not Supported**:
```
RuntimeError: Video codec not supported by ffmpeg
```

---

## `AudioResolver` (MP3, WAV, M4A)

Extracts audio segments.

### Dependencies

- **External**: `ffmpeg` binary
- **Install**: Same as VideoResolver

### Signature

```python
from citekit.resolvers.audio import AudioResolver

resolver = AudioResolver(output_dir=".citekit_output")
output_path = resolver.resolve(node, "/path/to/podcast.mp3")
```

### Location Schema

```python
# node.location must have:
{
    "modality": "audio",
    "start": 30.5,     # seconds (float)
    "end": 150.0       # seconds (float)
}
```

### Example

```python
# Extract audio segment
node = Node(
    id="episode_1.intro",
    title="Intro Segment",
    type="section",
    location=Location(modality="audio", start=0.0, end=60.0)
)

resolver = AudioResolver()
output_path = resolver.resolve(node, "podcast.mp3")
# Output: .citekit_output/podcast_episode_1_intro.mp3
```

---

## `ImageResolver` (JPG, PNG, WebP)

Crops image regions based on bounding box.

### Dependencies

- **Python**: `pillow` (PIL)
- **Install**: `pip install pillow`

### Signature

```python
from citekit.resolvers.image import ImageResolver

resolver = ImageResolver(output_dir=".citekit_output")
output_path = resolver.resolve(node, "/path/to/photo.jpg")
```

### Location Schema

```python
# node.location must have:
{
    "modality": "image",
    "bbox": [x1, y1, x2, y2]  # Normalized 0-1 corners
}
```

**Coordinates**: Normalized to 0-1 range (relative to image dimensions)
- `x1`: Left edge (0 = leftmost, 1 = rightmost)
- `y1`: Top edge (0 = topmost, 1 = bottommost)
- `x2`: Right edge (0 = leftmost, 1 = rightmost)
- `y2`: Bottom edge (0 = topmost, 1 = bottommost)

### Example

```python
# Crop bottom-right corner (person's face)
node = Node(
    id="photo.person",
    title="Person",
    type="object",
    location=Location(modality="image", bbox=[0.6, 0.2, 0.9, 0.8])
    # x1=0.6 (60% from left), y1=0.2 (20% from top)
    # x2=0.9 (90% from left), y2=0.8 (80% from top)
)

resolver = ImageResolver()
output_path = resolver.resolve(node, "photo.jpg")
# Output: .citekit_output/photo_person.jpg (cropped)
```

### Error Codes

**Success**:
```
.citekit_output/photo_person.jpg
```

**Invalid Bbox**:
```
ValueError: Invalid bbox [1.5, 0.5, 0.3, 0.3] (values must be 0-1)
```

**Unsupported Format**:
```
RuntimeError: Image format not supported
  Supported: JPG, PNG, WebP, BMP
```

---

## `TextResolver` (TXT, MD, PY)

Extracts lines from text files.

### Dependencies

- **None** - uses native Python

### Signature

```python
from citekit.resolvers.text import TextResolver

resolver = TextResolver(output_dir=".citekit_output")
output_path = resolver.resolve(node, "/path/to/code.py")
```

### Location Schema

```python
# node.location must have:
{
    "modality": "text",
    "lines": [start_line, end_line]  # 1-indexed integers
}
```

### Example

```python
# Extract function definition (lines 5-15)
node = Node(
    id="code.function_process",
    title="process() function",
    type="function",
    location=Location(modality="text", lines=[5, 15])
)

resolver = TextResolver()
output_path = resolver.resolve(node, "main.py")
# Output: .citekit_output/main_code_function_process.py (lines 5-15)
```

### Error Codes

**Success**:
```
.citekit_output/main_code_function_process.py
```

**Invalid Line Range**:
```
ValueError: Invalid line range [5, 100] for file with 50 lines
```

---

## Adapters

Adapters convert external data formats into CiteKit `ResourceMap` objects.

### `GraphRAGAdapter`

Converts GraphRAG entity/community outputs to CiteKit maps.

```python
from citekit.adapters import GraphRAGAdapter

adapter = GraphRAGAdapter()
resource_map = adapter.adapt("graphrag_output.parquet", resource_id="knowledge_graph")
```

**Input Format**: GraphRAG parquet or JSON output (entities, communities, relationships)

**Behavior**:
- Creates nodes from entities/communities
- Sets `modality: "virtual"` (no file extraction)
- Preserves entity relationships as node hierarchy

**CLI Usage**:
```bash
python -m citekit.cli adapt graph_entities.parquet --adapter graphrag
```

### `LlamaIndexAdapter`

Converts LlamaIndex nodes/documents to CiteKit maps.

```python
from citekit.adapters import LlamaIndexAdapter

adapter = LlamaIndexAdapter()
resource_map = adapter.adapt("llamaindex_nodes.json", resource_id="rag_index")
```

**Input Format**: LlamaIndex JSON exports or node arrays

**Behavior**:
- Maps LlamaIndex nodes to CiteKit nodes
- Attempts to infer locations from metadata if available
- Falls back to `virtual` modality for abstract nodes

**CLI Usage**:
```bash
python -m citekit.cli adapt index_nodes.json --adapter llamaindex
```

### `GenericAdapter`

Fallback adapter for custom JSON structures.

```python
from citekit.adapters import GenericAdapter

adapter = GenericAdapter()
resource_map = adapter.adapt("custom_data.json", resource_id="my_resource")
```

**Expected JSON Format**:
```json
{
  "title": "My Resource",
  "nodes": [
    {
      "id": "section_1",
      "title": "Section 1",
      "type": "section",
      "summary": "Description"
    }
  ]
}
```

**CLI Usage**:
```bash
python -m citekit.cli adapt custom_data.json --adapter generic
```

### Custom Adapters (Python)

Write your own adapter in Python:

```python
# my_adapter.py
from citekit.models import ResourceMap, Node, Location

def adapt(input_path: str, resource_id: str = None) -> ResourceMap:
    """Convert your custom format to ResourceMap."""
    
    # 1. Read your format
    data = load_custom_format(input_path)
    
    # 2. Map to CiteKit nodes
    nodes = []
    for item in data:
        nodes.append(Node(
            id=item["id"],
            title=item["name"],
            type="section",
            location=Location(modality="virtual"),
            summary=item.get("description")
        ))
    
    # 3. Return ResourceMap
    return ResourceMap(
        resource_id=resource_id or "adapted_resource",
        type="virtual",
        title="Adapted Data",
        source_path=input_path,
        nodes=nodes
    )
```

**Usage**:
```bash
python -m citekit.cli adapt mydata.csv --adapter ./my_adapter.py
```

### Error Codes

**Success (All Adapters)**:
```
ResourceMap(resource_id="...", nodes=[...])
```

**File Not Found**:
```
FileNotFoundError: Cannot read input file: mydata.json
```

**Invalid Format**:
```
ValueError: Input file format not recognized
  Expected: JSON, Parquet, or CSV
```

**Missing Required Fields**:
```
ValueError: Adapter requires 'id' and 'title' fields
```

---

## Performance Benchmarks

| Resolver | File Size | Time | Output Size |
| :--- | :--- | :--- | :--- |
| DocumentResolver (10 pages PDF) | 5MB | 0.5-1s | 500KB |
| VideoResolver (5s clip, H.264) | 500MB | 2-3s | 10-15MB |
| AudioResolver (1min, MP3) | 1MB | 1-2s | 500KB |
| ImageResolver (bbox crop) | 5MB | 0.2-0.5s | 1-2MB |
| TextResolver (100 lines) | 10KB | 10ms | 5KB |

---

## Error Handling Pattern

```python
from citekit.models import Node
from pathlib import Path

def safe_resolve(resolver, node: Node, source_path: str) -> str | None:
    """Resolve with comprehensive error handling."""
    
    try:
        # 1. Validate inputs
        if not Path(source_path).exists():
            raise FileNotFoundError(f"Source not found: {source_path}")
        
        # 2. Attempt extraction
        output_path = resolver.resolve(node, source_path)
        return output_path
        
    except FileNotFoundError as e:
        print(f"Source file error: {e}")
        return None
    except ValueError as e:
        print(f"Invalid node location: {e}")
        return None
    except RuntimeError as e:
        print(f"Extraction failed: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

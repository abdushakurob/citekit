# Data Models

CiteKit uses a strict, cross-language schema to ensure that a `ResourceMap` generated in Python can be resolved by a Node.js client (and vice-versa).

## The ResourceMap Schema

The `ResourceMap` represents an entire indexed file. It is the primary unit of storage and portability.

### Specification

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `resource_id` | `string` | Yes | Unique slug (Regex: `^[a-z0-9_-]+$`). |
| `title` | `string` | Yes | Human-readable name. |
| `type` | `Enum` | Yes | `video`, `audio`, `document`, `image`, `text`. |
| `source_path` | `string` | Yes | Absolute path or URI to the source media. |
| `nodes` | `Array<Node>` | Yes | Flat or nested list of semantic segments. |
| `metadata` | `Object` | No | Extensible store for hashes, timestamps, etc. |
| `created_at` | `ISO8601` | Yes | Generation timestamp in UTC. |

---

## Coordinate Systems & Units

This is the most critical part of the CiteKit protocol. All locations must follow these absolute rules:

### 📄 Document (PDF)
- **Attribute**: `pages`
- **Unit**: Integers
- **Index**: **1-indexed** (to match standard PDF viewers like Acrobat or Chrome).
- **Format**: An array of page numbers (e.g., `[1, 2, 5]`).

### 🎬 Video / Audio
- **Attributes**: `start`, `end`
- **Unit**: **Seconds** (Floating point)
- **Index**: **0-indexed** (relative to the start of the file stream).
- **Precision**: We recommend 2 decimal places (e.g., `12.45`).
- **Range**: `end` must be strictly greater than `start`.

### 📝 Text
- **Attribute**: `lines`
- **Unit**: Integers
- **Index**: **1-indexed inclusive** (to match IDE line numbers).
- **Format**: A tuple or array `[start_line, end_line]`.
- **Note**: A single line citation should use `[10, 10]`.

### 🖼️ Image
- **Attribute**: `bbox`
- **Unit**: **Normalized Percentage** (`0.0` to `1.0`)
- **Index**: **Top-Left coordinate system**.
- **Format**: `[x1, y1, x2, y2]`
- **Calculation**: Multiply by image width/height to get pixel values for extraction.

---

## The Node Schema

A `Node` represents a semantic unit (a chapter, a scene, an object).

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `string` | Semantic key (e.g., `intro`). Dot-notation is recommended for hierarchy. |
| `title` | `string` | (Optional) Short title. |
| `type` | `string` | Contextual type (e.g., `section`, `dialogue`, `button`). |
| `location` | `Location` | The physical coordinates (see above). |
| `summary` | `string` | (Optional) LLM-generated description for agent context. |
| `children`| `Array<Node>`| (Optional) Nested nodes for hierarchical maps. |

---

## Resolved Evidence

This is the object returned after successful resolution.

| Field | Type | Description |
| :--- | :--- | :--- |
| `output_path` | `string`| Path to the extracted file slice. |
| `modality` | `string`| Mirror of the source type. |
| `address` | `string`| The standardized URI address (deterministic). |
| `resource_id` | `string`| The parent resource identifier. |
| `node` | `Node` | The original node definition. |

# JavaScript Resolvers

Resolvers perform the physical surgery on multimodal files to extract specific segments (e.g., 20 seconds of video or 3 pages of PDF).

## Built-in Resolvers

CiteKit for JavaScript includes the following:

-   **Video**: Uses `fluent-ffmpeg`.
-   **Document**: Uses `pdf-lib`.
-   **Text**: Native file system line-slicing.
-   **Image**: (Coming soon) Uses `sharp`.

---

## Resolver Lifecycle

1.  **Selection**: The `CiteKitClient` chooses a resolver based on the node's `modality`.
2.  **Path Calculation**: Generates a deterministic filename for the output clip (caching).
3.  **Extraction**: Executes the underlying tool (FFmpeg, etc.).
4.  **Verification**: Confirms the output file exists and returns the path.

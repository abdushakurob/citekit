# Example: Interactive Study Companion (MCP)

CiteKit is uniquely powerful when used as an MCP server for agents like Claude Desktop or Cline. It allows the agent to "browse" your local files and "cite" exact timestamps or page ranges.

## Scenario: Studying a Lecture Video

Imagine you have a 1-hour lecture on "Quantum Physics" (`lecture_01.mp4`).

### 1. The Human starts the session
You tell Claude: *"Hey, I added my lecture to CiteKit. Can you explain the part where the professor talks about the Double Slit experiment?"*

### 2. The Agent explores (getStructure)
Claude calls `getStructure(resourceId: "lecture_01")`. CiteKit returns:

```json
[
  { "id": "intro", "location": { "start": 0, "end": 300 }, "summary": "Intro" },
  { "id": "double_slit", "location": { "start": 305, "end": 600 }, "summary": "Double Slit Experiment explanation with diagrams." },
  ...
]
```

### 3. The Agent resolves (resolve)
Claude sees the node `double_slit`. It calls `resolve("lecture_01", "double_slit")`.
CiteKit uses FFmpeg to instantly cut a clip from `05:05` to `10:00`.

### 4. The Agent "Sees" the clip
CiteKit returns the path to the clip. If you are using a multimodal-capable UI (like Claude Desktop with local access), the agent can now "watch" those specific 5 minutes and explain them to you with 100% accuracy.

## Benefits for Students

-   **Pinpoint Citations**: The agent can say: "The professor explains this at timestamp 05:20 (see clip)."
-   **Reduced Hallucination**: Because the agent is looking at the actual source material extracted for it, it doesn't have to guess or rely on potentially incorrect transcripts.
-   **Multimodal Learning**: Works for "the diagram on page 12 of the textbook" just as easily as video.

## Try it yourself
```bash
# Ingest your file
citekit ingest my_lecture.mp4 video

# Open Claude Desktop and ask about it!
```

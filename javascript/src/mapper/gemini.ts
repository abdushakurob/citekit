import { GoogleGenerativeAI } from "@google/generative-ai";
import { GoogleAIFileManager } from "@google/generative-ai/server";
import { readFileSync, existsSync } from "node:fs";
import { basename, extname } from "node:path";

import { MapperProvider } from "./base.js";
import type { ResourceMap, Node, Location } from "../models.js";

// ── Prompt Templates ────────────────────────────────────────────────────────

const DOCUMENT_PROMPT = `\
You are a structure analyzer. Analyze the attached document to produce a JSON map \
that identifies the key concepts, sections, definitions, examples, and diagrams.

Each node must have:
- "id": a dot-separated identifier (e.g. "chapter1.derivatives.definition")
- "title": a short human-readable title
- "type": one of "section", "definition", "example", "explanation", "diagram", "theorem", "exercise", "summary"
- "location": { "modality": "document", "pages": [list of 1-indexed page numbers] }
- "summary": a 1-2 sentence summary of what this section covers

Rules:
- Be thorough — capture ALL distinct concepts, not just top-level sections.
- Page numbers are 1-indexed.
- Keep summaries concise but informative.
- IDs should be hierarchical and descriptive.

Return ONLY a JSON array of nodes. No markdown, no explanation.

Document title: {title}
`;

const VIDEO_PROMPT = `\
You are a video structure analyzer. Given metadata about a video, identify key segments.

Video duration: {duration} seconds
Filename: {filename}

Each node must have:
- "id": a descriptive dot-separated identifier
- "title": a short human-readable title
- "type": one of "introduction", "explanation", "example", "demonstration", "summary", "transition"
- "location": { "modality": "video", "start": <seconds>, "end": <seconds> }
- "summary": brief description of what this segment covers

Rules:
- Segments should be meaningful chunks, not arbitrary splits.
- start/end are in seconds.
- Cover the entire video duration.

Return ONLY a JSON array of nodes. No markdown, no explanation.
`;

export class GeminiMapper implements MapperProvider {
    private genAI: GoogleGenerativeAI;
    private model: any;

    constructor(apiKey: string, modelName: string = "gemini-2.0-flash") {
        this.genAI = new GoogleGenerativeAI(apiKey);
        this.model = this.genAI.getGenerativeModel({ model: modelName });
    }

    async generateMap(
        resourcePath: string,
        resourceType: string,
        resourceId?: string
    ): Promise<ResourceMap> {
        if (!existsSync(resourcePath)) {
            throw new Error(`Resource not found: ${resourcePath}`);
        }

        const id = resourceId || basename(resourcePath, extname(resourcePath));
        let nodes: Node[] = [];

        if (resourceType === "document") {
            nodes = await this.mapDocument(resourcePath);
        } else if (resourceType === "video") {
            nodes = await this.mapVideo(resourcePath);
        } else {
            // Fallback or TODO for image/audio
            throw new Error(`Resource type '${resourceType}' not fully implemented in JS port yet.`);
        }

        return {
            resource_id: id,
            type: resourceType,
            title: id.replace(/[_-]/g, " ").replace(/\b\w/g, c => c.toUpperCase()),
            source_path: resourcePath,
            nodes: nodes,
            created_at: new Date().toISOString()
        };
    }

    private async mapDocument(path: string): Promise<Node[]> {
        const prompt = DOCUMENT_PROMPT
            .replace("{title}", basename(path));

        return this.callGeminiWithFile(path, prompt, "application/pdf");
    }

    private async mapVideo(path: string): Promise<Node[]> {
        // We need duration for the prompt, though we could also just upload it.
        // Let's get duration to be safe and consistent with prompt structure.
        const { ffprobe } = await import("fluent-ffmpeg");

        const duration = await new Promise<number>((resolve, reject) => {
            ffprobe(path, (err, metadata) => {
                // If ffprobe fails, we might still proceed with upload, but let's try to get it.
                if (err) resolve(0);
                else resolve(metadata.format.duration || 0);
            });
        });

        const prompt = VIDEO_PROMPT
            .replace("{duration}", duration.toString())
            .replace("{filename}", basename(path));

        return this.callGeminiWithFile(path, prompt, "video/mp4");
    }

    private async callGeminiWithFile(path: string, prompt: string, mimeType: string): Promise<Node[]> {
        const fileManager = new GoogleAIFileManager(this.genAI.apiKey);

        console.log(`DEBUG: Uploading ${basename(path)} to Gemini File API...`);

        let uploadResult;
        try {
            uploadResult = await fileManager.uploadFile(path, {
                mimeType: mimeType,
                displayName: basename(path),
            });
            console.log(`DEBUG: Uploaded as ${uploadResult.file.name}`);

            // Wait for processing if video
            if (mimeType.startsWith("video")) {
                let file = await fileManager.getFile(uploadResult.file.name);
                while (file.state === "PROCESSING") {
                    console.log("DEBUG: Waiting for video processing...");
                    await new Promise(r => setTimeout(r, 2000));
                    file = await fileManager.getFile(uploadResult.file.name);
                }

                if (file.state === "FAILED") {
                    throw new Error("Video processing failed.");
                }
            }

            // Generate content
            const result = await this.model.generateContent([
                prompt,
                {
                    fileData: {
                        fileUri: uploadResult.file.uri,
                        mimeType: uploadResult.file.mimeType,
                    },
                },
            ]);

            const response = await result.response;
            const text = response.text();
            return this.parseNodesResponse(text);

        } finally {
            // Cleanup
            if (uploadResult && uploadResult.file) {
                console.log(`DEBUG: Deleting remote file ${uploadResult.file.name}`);
                try {
                    await fileManager.deleteFile(uploadResult.file.name);
                } catch (e) {
                    console.warn(`WARNING: Failed to delete remote file: ${e}`);
                }
            }
        }
    }

    private async callGemini(prompt: string): Promise<Node[]> {
        const result = await this.model.generateContent(prompt);
        const response = await result.response;
        const text = response.text();
        return this.parseNodesResponse(text);
    }

    private parseNodesResponse(text: string): Node[] {
        let cleaned = text.trim();

        // Regex to extract JSON array [ ... ]
        const match = cleaned.match(/\[.*\]/s);
        if (match) {
            cleaned = match[0];
        }

        // Remove markdown fences
        if (cleaned.startsWith("```")) {
            cleaned = cleaned.replace(/^```[a-z]*\n/, "").replace(/\n```$/, "");
        }

        // Fix trailing commas: remove comma before ] or }
        cleaned = cleaned.replace(/,\s*([\]}])/g, "$1");

        // Fix object comma separation: } { -> }, {
        cleaned = cleaned.replace(/}\s*{/g, "}, {");

        // Attempt verify/repair brackets
        const openBrackets = (cleaned.match(/\[/g) || []).length - (cleaned.match(/\]/g) || []).length;
        const openBraces = (cleaned.match(/{/g) || []).length - (cleaned.match(/}/g) || []).length;

        if (openBraces > 0) {
            cleaned = cleaned.replace(/,+$/, "");
            cleaned += "}".repeat(openBraces);
        }
        if (openBrackets > 0) {
            cleaned = cleaned.replace(/,+$/, "");
            cleaned += "]".repeat(openBrackets);
        }

        try {
            const rawNodes = JSON.parse(cleaned);
            return rawNodes.map((raw: any) => ({
                id: raw.id,
                title: raw.title,
                type: raw.type || "section",
                location: raw.location,
                summary: raw.summary
            }));
        } catch (e) {
            console.error("DEBUG: Failed JSON parse. Raw:", cleaned);
            throw new Error(`Failed to parse Gemini JSON: ${e}`);
        }
    }
}

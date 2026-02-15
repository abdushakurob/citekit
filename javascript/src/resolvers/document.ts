import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { Resolver } from "./base.js";
import type { ResolvedEvidence } from "../models.js";

export class DocumentResolver implements Resolver {
    async resolve(
        resourceId: string,
        nodeId: string,
        sourcePath: string,
        location: any,
        outputDir: string,
        options?: { virtual?: boolean }
    ): Promise<ResolvedEvidence> {
        // Virtual Resolution: Return page metadata without PDF manipulation
        if (options?.virtual) {
            return {
                modality: "document",
                address: `doc://${resourceId}#pages=${location.pages.join(",")}`,
                node: { id: nodeId, location: location } as any,
                resource_id: resourceId
            };
        }

        let PDFDocument;
        try {
            const mod = await import("pdf-lib");
            PDFDocument = mod.PDFDocument;
        } catch (e) {
            throw new Error(
                "The 'pdf-lib' package is required for document resolution. " +
                "Please install it with: npm install pdf-lib"
            );
        }

        if (!location.pages || location.pages.length === 0) {
            throw new Error(`Node ${nodeId} has no pages specified.`);
        }

        const pdfBytes = readFileSync(sourcePath);
        const srcDoc = await PDFDocument.load(pdfBytes);
        const newDoc = await PDFDocument.create();

        // Pages are 1-indexed in our map, but 0-indexed in pdf-lib
        const pagesToCopy = location.pages.map((p: number) => p - 1);

        // Copy pages
        const copiedPages = await newDoc.copyPages(srcDoc, pagesToCopy);
        copiedPages.forEach((page) => newDoc.addPage(page));

        const outputBytes = await newDoc.save();

        // Generate filename similar to Python SDK: {resource}_{pages}_{p1}_{p2}.pdf
        const pageStr = location.pages.join("_");
        const filename = `${resourceId}_pages_${pageStr}.pdf`;
        const outputPath = join(outputDir, filename);

        // Caching
        if (require("node:fs").existsSync(outputPath)) {
            return {
                output_path: outputPath,
                modality: "document",
                address: `doc://${resourceId}#pages=${location.pages[0]}-${location.pages[location.pages.length - 1]}`,
                node: { id: nodeId, location: location } as any,
                resource_id: resourceId
            };
        }

        writeFileSync(outputPath, outputBytes);

        return {
            output_path: outputPath,
            modality: "document",
            address: `doc://${resourceId}#pages=${location.pages[0]}-${location.pages[location.pages.length - 1]}`,
            node: { id: nodeId, location: location } as any, // Only minimal node needed? Or fetch full?
            resource_id: resourceId
        };
    }
}

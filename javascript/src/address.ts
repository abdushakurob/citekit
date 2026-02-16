/**
 * CiteKit Address Parser — parse and build URI-style addresses.
 *
 * Formats:
 *   doc://resource_id#pages=3-5
 *   video://resource_id#t=192-230
 *   audio://resource_id#t=60-120
 *   image://resource_id#bbox=0.2,0.3,0.8,0.7
 */

import type { Location } from "./models.js";

const SCHEME_TO_MODALITY: Record<string, Location["modality"]> = {
    doc: "document",
    video: "video",
    audio: "audio",
    image: "image",
    text: "text",
    virtual: "virtual",
};

const MODALITY_TO_SCHEME: Record<string, string> = {
    document: "doc",
    video: "video",
    audio: "audio",
    image: "image",
    text: "text",
    virtual: "virtual",
};

/**
 * Parse a CiteKit address into a resource ID and location.
 *
 * @example
 * parseAddress("doc://calculus_book#pages=12-13")
 * // → { resourceId: "calculus_book", location: { modality: "document", pages: [12, 13] } }
 */
export function parseAddress(address: string): {
    resourceId: string;
    location: Location;
} {
    const match = address.match(/^(\w+):\/\/([^#]+)(?:#(.+))?$/);
    if (!match) {
        throw new Error(`Invalid CiteKit address: ${address}`);
    }

    const [, scheme, resourceId, fragment] = match;

    const modality = SCHEME_TO_MODALITY[scheme];
    if (!modality) {
        throw new Error(
            `Unknown scheme '${scheme}'. Expected: ${Object.keys(SCHEME_TO_MODALITY).join(", ")}`
        );
    }

    const location: Location = { modality };

    if (scheme === "virtual") {
        location.virtual_address = address;
        return { resourceId, location };
    }

    if (fragment) {
        const params = Object.fromEntries(
            fragment.split("&").map((part) => {
                const [key, value] = part.split("=", 2);
                return [key, value];
            })
        );

        if (params.pages) {
            if (params.pages.includes("-")) {
                const [start, end] = params.pages.split("-").map(Number);
                location.pages = Array.from(
                    { length: end - start + 1 },
                    (_, i) => start + i
                );
            } else {
                location.pages = params.pages.split(",").map(Number);
            }
        }

        if (params.t) {
            const [start, end] = params.t.split("-").map(parseTime);
            location.start = start;
            location.end = end;
        }

        if (params.bbox) {
            const parts = params.bbox.split(",").map(Number);
            if (parts.length !== 4) {
                throw new Error(`bbox must have 4 values, got ${parts.length}`);
            }
            location.bbox = parts as [number, number, number, number];
        }

        if (params.lines) {
            const [start, end] = params.lines.split("-").map(Number);
            if (Number.isNaN(start) || Number.isNaN(end)) {
                throw new Error(`lines must be numeric, got '${params.lines}'`);
            }
            location.lines = [start, end];
        }
    }

    return { resourceId, location };
}

/**
 * Build a CiteKit address from a resource ID and location.
 *
 * @example
 * buildAddress("book", { modality: "document", pages: [3, 4, 5] })
 * // → "doc://book#pages=3-5"
 */
export function buildAddress(resourceId: string, location: Location): string {
    const scheme = MODALITY_TO_SCHEME[location.modality];
    if (!scheme) {
        throw new Error(`Unknown modality: ${location.modality}`);
    }

    if (location.modality === "virtual") {
        return location.virtual_address ?? `virtual://${resourceId}`;
    }

    const fragments: string[] = [];

    if (location.pages && location.pages.length > 0) {
        const sorted = [...location.pages].sort((a, b) => a - b);
        const isConsecutive =
            sorted.length === sorted[sorted.length - 1] - sorted[0] + 1;

        if (isConsecutive) {
            fragments.push(`pages=${sorted[0]}-${sorted[sorted.length - 1]}`);
        } else {
            fragments.push(`pages=${sorted.join(",")}`);
        }
    }

    if (location.start !== undefined && location.end !== undefined) {
        fragments.push(`t=${formatTime(location.start)}-${formatTime(location.end)}`);
    }

    if (location.bbox) {
        fragments.push(`bbox=${location.bbox.join(",")}`);
    }

    if (location.lines) {
        fragments.push(`lines=${location.lines[0]}-${location.lines[1]}`);
    }

    const fragment = fragments.join("&");
    return fragment ? `${scheme}://${resourceId}#${fragment}` : `${scheme}://${resourceId}`;
}

// ── Helpers ────────────────────────────────────────────────────────────────

function parseTime(timeStr: string): number {
    const trimmed = timeStr.trim();
    if (trimmed.includes(":")) {
        const parts = trimmed.split(":").map(Number);
        if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
        if (parts.length === 2) return parts[0] * 60 + parts[1];
    }
    return Number(trimmed);
}

function formatTime(seconds: number): string {
    if (Number.isInteger(seconds)) {
        if (seconds >= 3600) {
            const h = Math.floor(seconds / 3600);
            const m = Math.floor((seconds % 3600) / 60);
            const s = seconds % 60;
            return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
        }
        if (seconds >= 60) {
            const m = Math.floor(seconds / 60);
            const s = seconds % 60;
            return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
        }
    }
    return String(seconds);
}

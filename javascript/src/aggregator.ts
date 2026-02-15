import type { ResourceMap } from "./models.js";

/**
 * Aggregates multiple ResourceMaps into a single string for LLM context.
 */
export function createAgentContext(maps: ResourceMap[], format: 'markdown' | 'json' = 'markdown'): string {
    if (format === 'json') {
        const summary = maps.map(rmap => ({
            id: rmap.resource_id,
            title: rmap.title,
            type: rmap.type,
            nodes: rmap.nodes.map(node => ({
                id: node.id,
                title: node.title,
                summary: node.summary
            }))
        }));
        return JSON.stringify(summary, null, 2);
    }

    // Default: Markdown
    let output = "# Available Resources Index\n\n";
    for (const rmap of maps) {
        output += `## ${rmap.title} (ID: ${rmap.resource_id}, Type: ${rmap.type})\n`;
        for (const node of rmap.nodes) {
            output += `- **${node.id}**: ${node.title} - ${node.summary || ''}\n`;
        }
        output += "\n";
    }

    return output.trim();
}

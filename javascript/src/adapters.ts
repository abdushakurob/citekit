import { ResourceMap } from "./models.js";

/**
 * Interface for converting external data into a CiteKit ResourceMap.
 */
export interface MapAdapter {
    /**
     * Adapt arbitrary input into a ResourceMap.
     * @param input - The raw input data (object, string, etc.)
     * @param options - Additional options for the adapter
     */
    adapt(input: any, options?: any): Promise<ResourceMap>;
}

/**
 * A generic adapter that passes through a valid JSON object.
 */
export class GenericAdapter implements MapAdapter {
    async adapt(input: any, options?: any): Promise<ResourceMap> {
        // In a real implementation we would validate against schema using Zod
        // For now, we assume input matches ResourceMap interface
        return input as ResourceMap;
    }
}

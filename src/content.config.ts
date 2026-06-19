import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const logos = defineCollection({
    loader: glob({ pattern: "**/index.md", base: "./src/content/logos" }),
    schema: z
        .object({
            colors: z.array(z.string()).optional(),
            images: z.array(z.string()).optional(),
            font: z.any().optional(),
            guide: z.string().optional(),
            h1: z.string().optional(),
            logohandle: z.string().optional(),
            no_h1: z.boolean().optional(),
            noindex: z.boolean().optional(),
            notes: z.string().optional(),
            resource: z.string().optional(),
            sort: z.string().optional(),
            subtitle: z.string().optional(),
            timestamp: z.string().optional(),
            tags: z.array(z.string()).optional(),
            title: z.string().optional(),
            type: z.string().optional(),
            website: z.string().optional(),
            redirect_from: z
                .union([z.string(), z.array(z.string())])
                .optional(),
        })
        .passthrough(),
});

export const collections = {
  logos
};

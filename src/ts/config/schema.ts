// src/ts/config/schema.ts
import { z } from 'zod';

export const AstockConfigSchema = z.object({
  llm: z.object({
    provider: z.enum(['openai', 'kimi', 'glm']).default('kimi'),
    model: z.string().optional(),
    temperature: z.number().min(0).max(2).default(0.7),
    maxTokens: z.number().min(1).max(32000).default(4096),
    mode: z.enum(['single', 'multi']).default('single'),
  }).optional(),

  apiKeys: z.object({
    openai: z.string().optional(),
    kimi: z.string().optional(),
    glm: z.string().optional(),
  }).optional(),

  agent: z.object({
    verbose: z.boolean().default(false),
    maxIterations: z.number().default(10),
    timeoutMs: z.number().default(60000),
  }).optional(),

  memory: z.object({
    maxHistoryLength: z.number().default(50),
    enableLongTermMemory: z.boolean().default(true),
  }).optional(),
});

export type AstockConfig = z.infer<typeof AstockConfigSchema>;

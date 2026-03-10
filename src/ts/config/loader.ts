// src/ts/config/loader.ts
import fs from 'fs';
import path from 'path';
import { AstockConfigSchema, type AstockConfig } from './schema.js';

export const CONFIG_PATHS = [
  path.join(process.env.HOME || '', '.astock', 'config.json'),
  path.join(process.cwd(), '.astockrc'),
  path.join(process.cwd(), 'astock.config.json'),
];

// Default config values
const DEFAULT_CONFIG: Partial<AstockConfig> = {
  llm: {
    provider: 'kimi',
    temperature: 0.7,
    maxTokens: 4096,
    mode: 'single',
  },
  agent: {
    verbose: false,
    maxIterations: 10,
    timeoutMs: 60000,
  },
  memory: {
    maxHistoryLength: 50,
    enableLongTermMemory: true,
  },
};

export async function loadConfig() {
  let fileConfig: Partial<AstockConfig> = {};

  for (const configPath of CONFIG_PATHS) {
    if (fs.existsSync(configPath)) {
      try {
        const content = fs.readFileSync(configPath, 'utf-8');
        fileConfig = JSON.parse(resolveEnvVars(content)) as Partial<AstockConfig>;
        break;
      } catch (error) {
        console.warn(`Failed to load config from ${configPath}:`, error);
      }
    }
  }

  const envConfig: Partial<AstockConfig> = {
    apiKeys: {
      openai: process.env.OPENAI_API_KEY || fileConfig.apiKeys?.openai,
      kimi: process.env.KIMI_API_KEY || process.env.MOONSHOT_API_KEY || fileConfig.apiKeys?.kimi,
      glm: process.env.GLM_API_KEY || process.env.ZHIPU_API_KEY || fileConfig.apiKeys?.glm,
    },
  };

  const merged = deepMerge(deepMerge(DEFAULT_CONFIG, fileConfig), envConfig);
  return AstockConfigSchema.parse(merged);
}

function resolveEnvVars(content: string): string {
  return content.replace(/\$\{(\w+)\}/g, (_, name) => process.env[name] || '');
}

function deepMerge<T extends Record<string, unknown>>(base: T, override: Partial<T>): T {
  const result = { ...base } as T;
  for (const key in override) {
    if (override[key] !== undefined) {
      if (
        typeof override[key] === 'object' &&
        override[key] !== null &&
        !Array.isArray(override[key]) &&
        typeof base[key] === 'object' &&
        base[key] !== null
      ) {
        result[key] = deepMerge(
          base[key] as Record<string, unknown>,
          override[key] as Record<string, unknown>
        ) as T[Extract<keyof T, string>];
      } else {
        result[key] = override[key] as T[Extract<keyof T, string>];
      }
    }
  }
  return result;
}

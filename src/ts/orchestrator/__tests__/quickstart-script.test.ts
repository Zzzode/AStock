import { describe, it, expect } from 'vitest';
import { readFile } from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '../../../../');

describe('quickstart scripts', () => {
  it('exposes dev:team script', async () => {
    const packageJsonPath = path.join(ROOT, 'package.json');
    const raw = await readFile(packageJsonPath, 'utf-8');
    const pkg = JSON.parse(raw) as { scripts?: Record<string, string> };
    expect(pkg.scripts?.['dev:team']).toBeDefined();
  });

  it('documents dev:team usage in readme', async () => {
    const readmePath = path.join(ROOT, 'README.md');
    const content = await readFile(readmePath, 'utf-8');
    expect(content).toContain('pnpm run dev:team -- 000001 "现在是否适合介入？"');
  });
});

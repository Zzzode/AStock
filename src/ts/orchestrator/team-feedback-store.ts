import { mkdir, readFile, writeFile } from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

export interface TeamFeedbackRecord {
  code: string;
  action: 'watch_buy' | 'wait' | 'hold_or_reduce';
  outcome: 'good' | 'bad';
  strategy?: string;
  note?: string;
  created_at: string;
}

export interface TeamFeedbackProfile {
  sample_count: number;
  aggressiveness: number;
  caution: number;
}

export interface GlobalFeedbackProfile {
  sample_count: number;
  risk_appetite: number;
  strategy_weights: Record<string, number>;
}

interface FeedbackStoreShape {
  records: TeamFeedbackRecord[];
}

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_FEEDBACK_FILE = path.resolve(__dirname, '../../../data/team-feedback.json');

function getFeedbackFilePath(): string {
  const custom = process.env.ASTOCK_TEAM_FEEDBACK_FILE;
  if (custom && custom.trim().length > 0) {
    return custom;
  }
  return DEFAULT_FEEDBACK_FILE;
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

async function readStore(): Promise<FeedbackStoreShape> {
  try {
    const raw = await readFile(getFeedbackFilePath(), 'utf-8');
    const parsed = JSON.parse(raw) as FeedbackStoreShape;
    if (!Array.isArray(parsed.records)) {
      return { records: [] };
    }
    return parsed;
  } catch {
    return { records: [] };
  }
}

async function writeStore(data: FeedbackStoreShape): Promise<void> {
  const filePath = getFeedbackFilePath();
  await mkdir(path.dirname(filePath), { recursive: true });
  await writeFile(filePath, JSON.stringify(data, null, 2), 'utf-8');
}

export async function appendTeamFeedback(
  input: Omit<TeamFeedbackRecord, 'created_at'>
): Promise<TeamFeedbackRecord> {
  const store = await readStore();
  const record: TeamFeedbackRecord = {
    ...input,
    created_at: new Date().toISOString(),
  };
  store.records.push(record);
  await writeStore(store);
  return record;
}

export async function loadTeamFeedbackProfile(code: string): Promise<TeamFeedbackProfile> {
  const store = await readStore();
  const records = store.records.filter((record) => record.code === code);

  if (records.length === 0) {
    return {
      sample_count: 0,
      aggressiveness: 0,
      caution: 0,
    };
  }

  const positiveBuy = records.filter(
    (record) => record.action === 'watch_buy' && record.outcome === 'good'
  ).length;
  const negativeBuy = records.filter(
    (record) => record.action === 'watch_buy' && record.outcome === 'bad'
  ).length;
  const positiveReduce = records.filter(
    (record) => record.action === 'hold_or_reduce' && record.outcome === 'good'
  ).length;
  const negativeReduce = records.filter(
    (record) => record.action === 'hold_or_reduce' && record.outcome === 'bad'
  ).length;

  const buySignal = records.length > 0 ? (positiveBuy - negativeBuy) / records.length : 0;
  const reduceSignal = records.length > 0 ? (positiveReduce - negativeReduce) / records.length : 0;

  return {
    sample_count: records.length,
    aggressiveness: clamp(buySignal, -1, 1),
    caution: clamp(reduceSignal, -1, 1),
  };
}

export async function loadGlobalFeedbackProfile(): Promise<GlobalFeedbackProfile> {
  const store = await readStore();
  const records = store.records;

  if (records.length === 0) {
    return {
      sample_count: 0,
      risk_appetite: 0,
      strategy_weights: {},
    };
  }

  let riskSignal = 0;
  const strategyScore: Record<string, number> = {};
  const strategyCount: Record<string, number> = {};

  for (const record of records) {
    if (record.action === 'watch_buy') {
      riskSignal += record.outcome === 'good' ? 1 : -1;
    } else if (record.action === 'hold_or_reduce') {
      riskSignal += record.outcome === 'good' ? -1 : 1;
    }

    if (record.strategy && record.strategy.trim().length > 0) {
      strategyScore[record.strategy] = (strategyScore[record.strategy] ?? 0)
        + (record.outcome === 'good' ? 1 : -1);
      strategyCount[record.strategy] = (strategyCount[record.strategy] ?? 0) + 1;
    }
  }

  const strategyWeights: Record<string, number> = {};
  for (const [strategy, score] of Object.entries(strategyScore)) {
    const count = strategyCount[strategy] ?? 1;
    strategyWeights[strategy] = clamp(score / count, -1, 1);
  }

  return {
    sample_count: records.length,
    risk_appetite: clamp(riskSignal / records.length, -1, 1),
    strategy_weights: strategyWeights,
  };
}

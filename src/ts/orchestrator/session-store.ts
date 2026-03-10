import { mkdir, readdir, readFile, stat, writeFile } from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { AgentTeamOutputData } from './agent-team-handler.js';
import { ArbitrationResult, ConflictInfo } from './conflict-arbiter.js';

/**
 * 任务节点 - 表示 Agent Team 分析过程中的任务分解
 */
export interface TaskNode {
  id: string;
  agent: string;
  task: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: string;
  children?: TaskNode[];
}

/**
 * 证据 - 记录分析过程中的关键数据点
 */
export interface Evidence {
  id: string;
  source: string;
  type: 'market' | 'analysis' | 'strategy' | 'risk' | 'style';
  content: string;
  confidence?: number;
  timestamp: string;
}

/**
 * 结论 - 最终决策输出
 */
export interface Conclusion {
  action: 'watch_buy' | 'wait' | 'hold_or_reduce';
  confidence: number;
  rationale: string[];
  counterpoints: string[];
  influence: {
    base_score: number;
    risk_penalty: number;
    style_bias: number;
    risk_appetite: number;
    strategy_weight: number;
    final_score: number;
  };
}

/**
 * 会话 - 完整的 Agent Team 分析会话
 */
export interface Session {
  id: string;
  stockCode: string;
  query: string;
  createdAt: string;
  taskTree: TaskNode[];
  evidence: Evidence[];
  conclusion: Conclusion;
  finalAction: string;
  experts?: AgentTeamOutputData['experts'];
  arbitration?: ArbitrationResult;
}

/**
 * 会话列表项 - 用于展示摘要信息
 */
export interface SessionListItem {
  id: string;
  stockCode: string;
  query: string;
  createdAt: string;
  finalAction: string;
  confidence: number;
}

/**
 * 会话统计
 */
export interface SessionStats {
  total: number;
  byAction: Record<string, number>;
  byDate: Record<string, number>;
}

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_SESSIONS_DIR = path.resolve(__dirname, '../../data/sessions');

function getSessionsDir(): string {
  const custom = process.env.ASTOCK_SESSIONS_DIR;
  if (custom && custom.trim().length > 0) {
    return custom;
  }
  return DEFAULT_SESSIONS_DIR;
}

/**
 * 获取当前日期字符串 (YYYY-MM-DD)
 */
function getDateString(date: Date = new Date()): string {
  return date.toISOString().split('T')[0];
}

/**
 * 生成 UUID
 */
function generateId(): string {
  return crypto.randomUUID();
}

/**
 * 确保日期目录存在并返回路径
 */
async function ensureDateDir(date: Date = new Date()): Promise<string> {
  const sessionsDir = getSessionsDir();
  const dateDir = path.join(sessionsDir, getDateString(date));
  await mkdir(dateDir, { recursive: true });
  return dateDir;
}

/**
 * 创建新会话
 */
export function createSession(stockCode: string, query: string): Session {
  const now = new Date();
  return {
    id: generateId(),
    stockCode,
    query,
    createdAt: now.toISOString(),
    taskTree: [],
    evidence: [],
    conclusion: {
      action: 'wait',
      confidence: 0.5,
      rationale: [],
      counterpoints: [],
      influence: {
        base_score: 0,
        risk_penalty: 0,
        style_bias: 0,
        risk_appetite: 0,
        strategy_weight: 0,
        final_score: 0,
      },
    },
    finalAction: 'wait',
  };
}

/**
 * 添加任务节点到会话
 */
export function addTaskNode(
  session: Session,
  task: string,
  agent: string,
  parentId?: string
): TaskNode {
  const node: TaskNode = {
    id: generateId(),
    agent,
    task,
    status: 'pending',
  };

  if (!parentId) {
    session.taskTree.push(node);
  } else {
    const parent = findTaskNode(session.taskTree, parentId);
    if (parent) {
      parent.children = parent.children || [];
      parent.children.push(node);
    } else {
      session.taskTree.push(node);
    }
  }

  return node;
}

/**
 * 查找任务节点
 */
function findTaskNode(nodes: TaskNode[], id: string): TaskNode | null {
  for (const node of nodes) {
    if (node.id === id) {
      return node;
    }
    if (node.children) {
      const found = findTaskNode(node.children, id);
      if (found) {
        return found;
      }
    }
  }
  return null;
}

/**
 * 更新任务节点状态
 */
export function updateTaskNode(
  session: Session,
  nodeId: string,
  status: TaskNode['status'],
  result?: string
): void {
  const node = findTaskNode(session.taskTree, nodeId);
  if (node) {
    node.status = status;
    if (result !== undefined) {
      node.result = result;
    }
  }
}

/**
 * 添加证据到会话
 */
export function addEvidence(
  session: Session,
  source: string,
  type: Evidence['type'],
  content: string,
  confidence?: number
): Evidence {
  const evidence: Evidence = {
    id: generateId(),
    source,
    type,
    content,
    confidence,
    timestamp: new Date().toISOString(),
  };
  session.evidence.push(evidence);
  return evidence;
}

/**
 * 设置会话结论
 */
export function setConclusion(session: Session, data: AgentTeamOutputData): void {
  session.conclusion = {
    action: data.decision.action,
    confidence: data.decision.confidence,
    rationale: data.decision.rationale,
    counterpoints: data.decision.counterpoints,
    influence: data.decision.influence,
  };
  session.finalAction = data.decision.action;
  session.experts = data.experts;
}

/**
 * 设置仲裁结果
 */
export function setArbitration(session: Session, arbitration: ArbitrationResult): void {
  session.arbitration = arbitration;
}

/**
 * 保存会话到文件
 */
export async function saveSession(session: Session): Promise<string> {
  const date = new Date(session.createdAt);
  const dateDir = await ensureDateDir(date);
  const filePath = path.join(dateDir, `${session.id}.json`);
  await writeFile(filePath, JSON.stringify(session, null, 2), 'utf-8');
  return filePath;
}

/**
 * 加载会话
 */
export async function loadSession(sessionId: string, date?: string): Promise<Session | null> {
  const sessionsDir = getSessionsDir();

  if (date) {
    const filePath = path.join(sessionsDir, date, `${sessionId}.json`);
    try {
      const raw = await readFile(filePath, 'utf-8');
      return JSON.parse(raw) as Session;
    } catch {
      return null;
    }
  }

  // 如果没有提供日期，搜索所有日期目录
  try {
    const dateDirs = await readdir(sessionsDir);
    for (const dateDir of dateDirs) {
      const filePath = path.join(sessionsDir, dateDir, `${sessionId}.json`);
      try {
        const raw = await readFile(filePath, 'utf-8');
        return JSON.parse(raw) as Session;
      } catch {
        continue;
      }
    }
  } catch {
    return null;
  }

  return null;
}

/**
 * 列出指定日期的会话
 */
export async function listSessionsByDate(date: string): Promise<SessionListItem[]> {
  const sessionsDir = getSessionsDir();
  const dateDir = path.join(sessionsDir, date);

  try {
    const files = await readdir(dateDir);
    const sessions: SessionListItem[] = [];

    for (const file of files) {
      if (!file.endsWith('.json')) {
        continue;
      }
      try {
        const raw = await readFile(path.join(dateDir, file), 'utf-8');
        const session = JSON.parse(raw) as Session;
        sessions.push({
          id: session.id,
          stockCode: session.stockCode,
          query: session.query,
          createdAt: session.createdAt,
          finalAction: session.finalAction,
          confidence: session.conclusion.confidence,
        });
      } catch {
        continue;
      }
    }

    return sessions.sort((a, b) => b.createdAt.localeCompare(a.createdAt));
  } catch {
    return [];
  }
}

/**
 * 列出最近 N 天的会话
 */
export async function listRecentSessions(days: number = 7): Promise<SessionListItem[]> {
  const sessionsDir = getSessionsDir();
  const sessions: SessionListItem[] = [];

  try {
    const dateDirs = await readdir(sessionsDir);
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);

    for (const dateDir of dateDirs) {
      const dirDate = new Date(dateDir);
      if (dirDate < cutoffDate) {
        continue;
      }

      const dateSessions = await listSessionsByDate(dateDir);
      sessions.push(...dateSessions);
    }

    return sessions.sort((a, b) => b.createdAt.localeCompare(a.createdAt));
  } catch {
    return [];
  }
}

/**
 * 获取会话统计
 */
export async function getSessionStats(days: number = 30): Promise<SessionStats> {
  const sessions = await listRecentSessions(days);

  const stats: SessionStats = {
    total: sessions.length,
    byAction: {},
    byDate: {},
  };

  for (const session of sessions) {
    stats.byAction[session.finalAction] = (stats.byAction[session.finalAction] || 0) + 1;
    const date = session.createdAt.split('T')[0];
    stats.byDate[date] = (stats.byDate[date] || 0) + 1;
  }

  return stats;
}

/**
 * 格式化会话输出
 */
export function formatSessionOutput(session: Session): string {
  const lines: string[] = [
    '┌──────────────────────────────────────────────────────────────┐',
    '│ Agent Team 会话记录                                           │',
    '├──────────────────────────────────────────────────────────────┤',
    `│ 会话ID: ${session.id.slice(0, 36).padEnd(52)} │`,
    `│ 标的: ${session.stockCode.padEnd(54)} │`,
    `│ 问题: ${session.query.slice(0, 50).padEnd(50)} │`,
    `│ 创建时间: ${session.createdAt.slice(0, 19).padEnd(49)} │`,
    `│ 最终建议: ${session.finalAction.padEnd(50)} │`,
    `│ 置信度: ${(session.conclusion.confidence * 100).toFixed(0).padStart(3)}%                                               │`,
    '├──────────────────────────────────────────────────────────────┤',
    '│ 任务树:                                                       │',
  ];

  for (const task of session.taskTree) {
    lines.push(`│   [${task.status.padEnd(8)}] ${task.agent}: ${task.task.slice(0, 36).padEnd(36)} │`);
  }

  lines.push('├──────────────────────────────────────────────────────────────┤');
  lines.push('│ 证据:                                                         │');

  for (const evidence of session.evidence.slice(0, 5)) {
    lines.push(`│   [${evidence.type.padEnd(8)}] ${evidence.content.slice(0, 44).padEnd(44)} │`);
  }

  if (session.evidence.length > 5) {
    lines.push(`│   ... 还有 ${session.evidence.length - 5} 条证据${' '.repeat(43)} │`);
  }

  lines.push('├──────────────────────────────────────────────────────────────┤');
  lines.push('│ 结论:                                                         │');

  for (const r of session.conclusion.rationale.slice(0, 3)) {
    lines.push(`│   - ${r.slice(0, 54).padEnd(54)} │`);
  }

  lines.push('└──────────────────────────────────────────────────────────────┘');

  return lines.join('\n');
}

/**
 * 格式化会话列表输出
 */
export function formatSessionListOutput(sessions: SessionListItem[]): string {
  if (sessions.length === 0) {
    return '暂无会话记录';
  }

  const lines: string[] = [
    '┌──────────────────────────────────────────────────────────────┐',
    '│ Agent Team 会话列表                                           │',
    '├──────────────────────────────────────────────────────────────┤',
  ];

  for (const session of sessions.slice(0, 20)) {
    const time = session.createdAt.slice(11, 19);
    lines.push(`│ ${time} ${session.stockCode} ${session.finalAction.padEnd(15)} ${(session.confidence * 100).toFixed(0).padStart(3)}%  ${session.query.slice(0, 24).padEnd(24)} │`);
  }

  if (sessions.length > 20) {
    lines.push(`│ ... 还有 ${sessions.length - 20} 条记录${' '.repeat(43)} │`);
  }

  lines.push('└──────────────────────────────────────────────────────────────┘');

  return lines.join('\n');
}

/**
 * 格式化统计输出
 */
export function formatStatsOutput(stats: SessionStats): string {
  const lines: string[] = [
    '┌──────────────────────────────────────────────────────────────┐',
    '│ Agent Team 会话统计                                           │',
    '├──────────────────────────────────────────────────────────────┤',
    `│ 总会话数: ${String(stats.total).padEnd(51)} │`,
    '├──────────────────────────────────────────────────────────────┤',
    '│ 按动作分类:                                                   │',
  ];

  for (const [action, count] of Object.entries(stats.byAction)) {
    lines.push(`│   ${action.padEnd(15)} ${String(count).padEnd(43)} │`);
  }

  lines.push('├──────────────────────────────────────────────────────────────┤');
  lines.push('│ 按日期分布:                                                   │');

  const sortedDates = Object.entries(stats.byDate).sort((a, b) => b[0].localeCompare(a[0]));
  for (const [date, count] of sortedDates.slice(0, 7)) {
    lines.push(`│   ${date} ${String(count).padEnd(51)} │`);
  }

  lines.push('└──────────────────────────────────────────────────────────────┘');

  return lines.join('\n');
}

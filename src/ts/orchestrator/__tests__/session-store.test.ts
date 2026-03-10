import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { mkdir, rm, readFile, readdir } from 'fs/promises';
import path from 'path';
import {
  createSession,
  addTaskNode,
  updateTaskNode,
  addEvidence,
  setConclusion,
  saveSession,
  loadSession,
  listSessionsByDate,
  listRecentSessions,
  getSessionStats,
  Session,
} from '../session-store.js';

const TEST_SESSIONS_DIR = path.resolve(__dirname, '../../../../test-sessions');

describe('session-store', () => {
  const originalEnv = process.env.ASTOCK_SESSIONS_DIR;

  beforeEach(async () => {
    process.env.ASTOCK_SESSIONS_DIR = TEST_SESSIONS_DIR;
    await mkdir(TEST_SESSIONS_DIR, { recursive: true });
  });

  afterEach(async () => {
    process.env.ASTOCK_SESSIONS_DIR = originalEnv;
    await rm(TEST_SESSIONS_DIR, { recursive: true, force: true });
  });

  describe('createSession', () => {
    it('creates a session with generated UUID', () => {
      const session = createSession('000001', '测试问题');
      expect(session.id).toMatch(/^[0-9a-f-]{36}$/);
      expect(session.stockCode).toBe('000001');
      expect(session.query).toBe('测试问题');
      expect(session.taskTree).toEqual([]);
      expect(session.evidence).toEqual([]);
      expect(session.finalAction).toBe('wait');
    });

    it('creates session with valid createdAt timestamp', () => {
      const before = new Date();
      const session = createSession('000001', 'test');
      const after = new Date();
      const createdAt = new Date(session.createdAt);
      expect(createdAt >= before).toBe(true);
      expect(createdAt <= after).toBe(true);
    });
  });

  describe('addTaskNode', () => {
    it('adds task node to root level', () => {
      const session = createSession('000001', 'test');
      const node = addTaskNode(session, '获取行情', 'Market Agent');
      expect(session.taskTree).toHaveLength(1);
      expect(session.taskTree[0]).toEqual(node);
      expect(node.task).toBe('获取行情');
      expect(node.agent).toBe('Market Agent');
      expect(node.status).toBe('pending');
    });

    it('adds task node as child', () => {
      const session = createSession('000001', 'test');
      const parent = addTaskNode(session, '父任务', 'Parent Agent');
      const child = addTaskNode(session, '子任务', 'Child Agent', parent.id);
      expect(parent.children).toHaveLength(1);
      expect(parent.children![0]).toEqual(child);
    });
  });

  describe('updateTaskNode', () => {
    it('updates task node status and result', () => {
      const session = createSession('000001', 'test');
      const node = addTaskNode(session, '获取行情', 'Market Agent');
      updateTaskNode(session, node.id, 'completed', '涨跌幅 1.2%');
      expect(node.status).toBe('completed');
      expect(node.result).toBe('涨跌幅 1.2%');
    });

    it('does nothing for non-existent node', () => {
      const session = createSession('000001', 'test');
      updateTaskNode(session, 'non-existent-id', 'completed');
      expect(session.taskTree).toHaveLength(0);
    });
  });

  describe('addEvidence', () => {
    it('adds evidence to session', () => {
      const session = createSession('000001', 'test');
      const evidence = addEvidence(session, 'quote', 'market', '价格: 10.5', 0.8);
      expect(session.evidence).toHaveLength(1);
      expect(session.evidence[0]).toEqual(evidence);
      expect(evidence.source).toBe('quote');
      expect(evidence.type).toBe('market');
      expect(evidence.content).toBe('价格: 10.5');
      expect(evidence.confidence).toBe(0.8);
    });

    it('generates timestamp for evidence', () => {
      const session = createSession('000001', 'test');
      const evidence = addEvidence(session, 'test', 'analysis', 'test content');
      expect(evidence.timestamp).toBeDefined();
      const timestamp = new Date(evidence.timestamp);
      expect(timestamp.getTime()).not.toBeNaN();
    });
  });

  describe('setConclusion', () => {
    it('sets conclusion from AgentTeamOutputData', () => {
      const session = createSession('000001', 'test');
      const data = {
        code: '000001',
        question: 'test',
        summary: '测试结论',
        experts: {
          market: { stance: 'bullish' as const, confidence: 0.7, summary: 'test', evidence: [] },
          analysis: { stance: 'neutral' as const, confidence: 0.5, summary: 'test', evidence: [] },
          strategy: { stance: 'neutral' as const, confidence: 0.5, summary: 'test', evidence: [] },
          risk: { level: 'medium' as const, stance: 'neutral' as const, confidence: 0.5, summary: 'test', evidence: [] },
          style: { stance: 'neutral' as const, confidence: 0.5, summary: 'test', evidence: [] },
        },
        decision: {
          action: 'watch_buy' as const,
          confidence: 0.75,
          rationale: ['理由1'],
          counterpoints: ['反例1'],
          influence: {
            base_score: 0.5,
            risk_penalty: 0.1,
            style_bias: 0,
            risk_appetite: 0,
            strategy_weight: 0,
            final_score: 0.4,
          },
        },
      };
      setConclusion(session, data);
      expect(session.finalAction).toBe('watch_buy');
      expect(session.conclusion.action).toBe('watch_buy');
      expect(session.conclusion.confidence).toBe(0.75);
      expect(session.conclusion.rationale).toEqual(['理由1']);
      expect(session.experts).toBeDefined();
    });
  });

  describe('saveSession and loadSession', () => {
    it('saves session to file and loads it back', async () => {
      const session = createSession('000001', '测试会话');
      addTaskNode(session, '任务1', 'Agent1');
      addEvidence(session, 'source1', 'market', '证据内容');

      await saveSession(session);

      const loaded = await loadSession(session.id);
      expect(loaded).not.toBeNull();
      expect(loaded!.id).toBe(session.id);
      expect(loaded!.stockCode).toBe('000001');
      expect(loaded!.query).toBe('测试会话');
      expect(loaded!.taskTree).toHaveLength(1);
      expect(loaded!.evidence).toHaveLength(1);
    });

    it('returns null for non-existent session', async () => {
      const loaded = await loadSession('non-existent-id');
      expect(loaded).toBeNull();
    });

    it('saves to date-based directory', async () => {
      const session = createSession('000001', 'test');
      const filePath = await saveSession(session);

      // Verify path includes date
      const date = new Date(session.createdAt).toISOString().split('T')[0];
      expect(filePath).toContain(date);
    });
  });

  describe('listSessionsByDate', () => {
    it('lists sessions for a specific date', async () => {
      const session1 = createSession('000001', '问题1');
      const session2 = createSession('000002', '问题2');

      // Set conclusion so we have confidence
      session1.conclusion.confidence = 0.7;
      session1.finalAction = 'watch_buy';
      session2.conclusion.confidence = 0.5;
      session2.finalAction = 'wait';

      await saveSession(session1);
      await saveSession(session2);

      const date = new Date(session1.createdAt).toISOString().split('T')[0];
      const list = await listSessionsByDate(date);

      expect(list.length).toBeGreaterThanOrEqual(2);
      const ids = list.map((s) => s.id);
      expect(ids).toContain(session1.id);
      expect(ids).toContain(session2.id);
    });

    it('returns empty array for non-existent date', async () => {
      const list = await listSessionsByDate('2020-01-01');
      expect(list).toEqual([]);
    });
  });

  describe('listRecentSessions', () => {
    it('lists sessions from recent days', async () => {
      const session = createSession('000001', 'test');
      session.conclusion.confidence = 0.7;
      session.finalAction = 'watch_buy';
      await saveSession(session);

      const list = await listRecentSessions(7);
      expect(list.length).toBeGreaterThanOrEqual(1);
      expect(list.some((s) => s.id === session.id)).toBe(true);
    });
  });

  describe('getSessionStats', () => {
    it('calculates session statistics', async () => {
      const session1 = createSession('000001', 'test');
      session1.conclusion.confidence = 0.7;
      session1.finalAction = 'watch_buy';
      await saveSession(session1);

      const session2 = createSession('000002', 'test');
      session2.conclusion.confidence = 0.5;
      session2.finalAction = 'wait';
      await saveSession(session2);

      const stats = await getSessionStats(7);

      expect(stats.total).toBeGreaterThanOrEqual(2);
      expect(stats.byAction['watch_buy']).toBeGreaterThanOrEqual(1);
      expect(stats.byAction['wait']).toBeGreaterThanOrEqual(1);
      expect(Object.keys(stats.byDate).length).toBeGreaterThanOrEqual(1);
    });
  });
});

import { analyzeStock, getQuote, screenStocks } from '../utils/python-bridge.js';
import {
  loadGlobalFeedbackProfile,
  loadTeamFeedbackProfile,
} from './team-feedback-store.js';
import {
  addEvidence,
  addTaskNode,
  createSession,
  saveSession,
  Session,
  setConclusion,
  setArbitration,
  updateTaskNode,
} from './session-store.js';
import {
  arbitrate,
  ConflictArbiter,
  ExpertOpinions,
  formatArbitrationResult,
} from './conflict-arbiter.js';

type Stance = 'bullish' | 'bearish' | 'neutral';
type RiskLevel = 'low' | 'medium' | 'high';
type DecisionAction = 'watch_buy' | 'wait' | 'hold_or_reduce';

interface ExpertOpinion {
  stance: Stance;
  confidence: number;
  summary: string;
  evidence: string[];
}

interface RiskOpinion extends ExpertOpinion {
  level: RiskLevel;
}

interface FeedbackProfile {
  sample_count: number;
  aggressiveness: number;
  caution: number;
}

interface GlobalFeedbackProfile {
  sample_count: number;
  risk_appetite: number;
  strategy_weights: Record<string, number>;
}

const STRATEGY_SCREEN_TIMEOUT_MS = 25000;

export interface AgentTeamInput {
  code: string;
  question?: string;
  days?: number;
}

export interface AgentTeamOutputData {
  code: string;
  question: string;
  summary: string;
  experts: {
    market: ExpertOpinion;
    analysis: ExpertOpinion;
    strategy: ExpertOpinion;
    risk: RiskOpinion;
    style: ExpertOpinion;
  };
  decision: {
    action: DecisionAction;
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
  };
}

export interface AgentTeamOutput {
  success: boolean;
  data?: AgentTeamOutputData;
  error?: string;
  sessionId?: string;
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function confidenceFromSignals(total: number): number {
  return clamp(0.45 + total * 0.1, 0.4, 0.9);
}

function getMarketOpinion(changePercent: number): ExpertOpinion {
  if (changePercent >= 1) {
    return {
      stance: 'bullish',
      confidence: confidenceFromSignals(Math.abs(changePercent)),
      summary: `市场动能偏强，涨跌幅 ${changePercent.toFixed(2)}%`,
      evidence: ['短期动量为正', '资金关注度提升可能性更高'],
    };
  }

  if (changePercent <= -1) {
    return {
      stance: 'bearish',
      confidence: confidenceFromSignals(Math.abs(changePercent)),
      summary: `市场动能转弱，涨跌幅 ${changePercent.toFixed(2)}%`,
      evidence: ['短期动量为负', '价格压力增加'],
    };
  }

  return {
    stance: 'neutral',
    confidence: 0.5,
    summary: `市场动能中性，涨跌幅 ${changePercent.toFixed(2)}%`,
    evidence: ['短期波动有限'],
  };
}

function getAnalysisOpinion(signals: Array<{ bias: 'bullish' | 'bearish' }>): ExpertOpinion {
  const bullish = signals.filter((s) => s.bias === 'bullish').length;
  const bearish = signals.filter((s) => s.bias === 'bearish').length;

  if (bullish > bearish) {
    return {
      stance: 'bullish',
      confidence: clamp(0.55 + bullish * 0.1, 0.55, 0.9),
      summary: `技术信号偏多（多头 ${bullish}，空头 ${bearish}）`,
      evidence: ['均线与动量指标整体偏多'],
    };
  }

  if (bearish > bullish) {
    return {
      stance: 'bearish',
      confidence: clamp(0.55 + bearish * 0.1, 0.55, 0.9),
      summary: `技术信号偏空（多头 ${bullish}，空头 ${bearish}）`,
      evidence: ['趋势和动量指标出现走弱迹象'],
    };
  }

  return {
    stance: 'neutral',
    confidence: 0.5,
    summary: '技术信号分歧或不足，短期方向不明',
    evidence: ['多空信号接近平衡'],
  };
}

function getStrategyOpinion(inScreen: boolean, score?: number): ExpertOpinion {
  if (inScreen && typeof score === 'number' && score >= 70) {
    return {
      stance: 'bullish',
      confidence: clamp(0.55 + (score - 70) / 100, 0.55, 0.85),
      summary: `策略筛选通过，综合得分 ${score.toFixed(1)}`,
      evidence: ['符合当前因子过滤条件'],
    };
  }

  if (inScreen && typeof score === 'number') {
    return {
      stance: 'neutral',
      confidence: 0.5,
      summary: `进入候选池但得分一般（${score.toFixed(1)}）`,
      evidence: ['部分因子匹配，优势不明显'],
    };
  }

  return {
    stance: 'bearish',
    confidence: 0.55,
    summary: '未进入当前策略候选池',
    evidence: ['策略侧缺乏正向筛选证据'],
  };
}

function getRiskOpinion(rsi6: number, kdjJ: number, changePercent: number): RiskOpinion {
  let level: RiskLevel = 'medium';
  if (rsi6 >= 70 || kdjJ >= 90 || Math.abs(changePercent) >= 3) {
    level = 'high';
  } else if (rsi6 <= 30 && kdjJ <= 20 && Math.abs(changePercent) < 2) {
    level = 'low';
  }

  if (level === 'high') {
    return {
      level,
      stance: 'bearish',
      confidence: 0.8,
      summary: `风险偏高（RSI6 ${rsi6.toFixed(1)}，KDJ-J ${kdjJ.toFixed(1)}）`,
      evidence: ['波动与超买/超卖指标提示回撤风险'],
    };
  }

  if (level === 'low') {
    return {
      level,
      stance: 'bullish',
      confidence: 0.65,
      summary: `风险偏低（RSI6 ${rsi6.toFixed(1)}，KDJ-J ${kdjJ.toFixed(1)}）`,
      evidence: ['短期风险暴露可控'],
    };
  }

  return {
    level,
    stance: 'neutral',
    confidence: 0.55,
    summary: `风险中性（RSI6 ${rsi6.toFixed(1)}，KDJ-J ${kdjJ.toFixed(1)}）`,
    evidence: ['当前处于常规波动区间'],
  };
}

function getStyleOpinion(profile: FeedbackProfile): ExpertOpinion {
  const { sample_count, aggressiveness, caution } = profile;
  if (sample_count <= 0) {
    return {
      stance: 'neutral',
      confidence: 0.5,
      summary: '风格学习模块暂以稳健偏好为默认假设',
      evidence: ['待接入用户反馈闭环后可动态更新'],
    };
  }

  if (aggressiveness - caution >= 0.15) {
    return {
      stance: 'bullish',
      confidence: clamp(0.55 + aggressiveness * 0.2, 0.55, 0.8),
      summary: `历史反馈偏积极（样本 ${sample_count}，进攻偏好 ${(aggressiveness * 100).toFixed(0)}%）`,
      evidence: ['用户过往对买入建议反馈更正向'],
    };
  }

  if (caution - aggressiveness >= 0.15) {
    return {
      stance: 'bearish',
      confidence: clamp(0.55 + caution * 0.2, 0.55, 0.8),
      summary: `历史反馈偏谨慎（样本 ${sample_count}，防御偏好 ${(caution * 100).toFixed(0)}%）`,
      evidence: ['用户过往对风险控制建议反馈更正向'],
    };
  }

  return {
    stance: 'neutral',
    confidence: 0.5,
    summary: `历史反馈中性（样本 ${sample_count}）`,
    evidence: ['当前无明显进攻或防御偏好'],
  };
}

function scoreStance(stance: Stance): number {
  if (stance === 'bullish') {
    return 1;
  }
  if (stance === 'bearish') {
    return -1;
  }
  return 0;
}

function getStrategyWeight(
  globalProfile: GlobalFeedbackProfile,
  matchedFactors: string[]
): number {
  if (matchedFactors.length === 0) {
    return 0;
  }
  const scores = matchedFactors
    .map((factor) => globalProfile.strategy_weights[factor] ?? 0)
    .filter((value) => Number.isFinite(value));
  if (scores.length === 0) {
    return 0;
  }
  return scores.reduce((sum, value) => sum + value, 0) / scores.length;
}

function aggregateDecision(
  experts: AgentTeamOutputData['experts'],
  globalProfile: GlobalFeedbackProfile,
  matchedFactors: string[]
): { decision: AgentTeamOutputData['decision']; arbitration: ReturnType<typeof arbitrate> } {
  // 使用仲裁器进行冲突仲裁
  const expertOpinions: ExpertOpinions = {
    market: experts.market,
    analysis: experts.analysis,
    strategy: experts.strategy,
    risk: experts.risk,
    style: experts.style,
  };

  const arbitration = arbitrate(expertOpinions, globalProfile);

  // 构建决策说明
  const rationale: string[] = [
    experts.market.summary,
    experts.analysis.summary,
    experts.strategy.summary,
    experts.risk.summary,
  ];

  // 如果有冲突，添加冲突信息到推理
  if (arbitration.conflictInfo) {
    rationale.push(`[仲裁] ${arbitration.conflictInfo.description}`);
  }

  const counterpoints = [
    experts.risk.level === 'high' ? '短期波动风险较高，追涨需谨慎' : '风险未显著放大',
    experts.style.summary,
  ];

  // 计算影响因素
  const opinions: ExpertOpinion[] = [
    experts.market,
    experts.analysis,
    experts.strategy,
    experts.style,
  ];

  const weighted = opinions.reduce((acc, item) => {
    return acc + scoreStance(item.stance) * item.confidence;
  }, 0);
  const totalConfidence = opinions.reduce((acc, item) => acc + item.confidence, 0);
  const baseScore = totalConfidence > 0 ? weighted / totalConfidence : 0;
  const riskPenalty = experts.risk.level === 'high' ? 0.5 : experts.risk.level === 'medium' ? 0.2 : 0;
  const styleBias = scoreStance(experts.style.stance) * experts.style.confidence * 0.25;
  const riskAppetiteBoost = clamp(globalProfile.risk_appetite, -1, 1) * 0.15;
  const strategyWeight = getStrategyWeight(globalProfile, matchedFactors) * 0.2;
  const score = baseScore + styleBias + riskAppetiteBoost + strategyWeight - riskPenalty;

  const decision: AgentTeamOutputData['decision'] = {
    action: arbitration.finalDecision,
    confidence: arbitration.confidence,
    rationale,
    counterpoints,
    influence: {
      base_score: baseScore,
      risk_penalty: riskPenalty,
      style_bias: styleBias,
      risk_appetite: riskAppetiteBoost,
      strategy_weight: strategyWeight,
      final_score: score,
    },
  };

  return { decision, arbitration };
}

function formatAction(action: DecisionAction): string {
  if (action === 'watch_buy') {
    return '建议关注并分批试探';
  }
  if (action === 'hold_or_reduce') {
    return '建议观望或减仓控制风险';
  }
  return '建议等待更清晰信号';
}

function formatTeamOutput(data: AgentTeamOutputData, arbitration?: ReturnType<typeof arbitrate>): string {
  const influence = data.decision.influence;
  const formatSigned = (value: number): string => (value >= 0 ? `+${value.toFixed(3)}` : value.toFixed(3));
  const trace1 = (data.decision.rationale[0] || '').slice(0, 50).padEnd(50);
  const trace2 = (data.decision.rationale[1] || '').slice(0, 50).padEnd(50);
  const trace3 = (data.decision.rationale[2] || '').slice(0, 50).padEnd(50);

  let output = `
┌──────────────────────────────────────────────────────────────┐
│ Agent Team 综合结论                                           │
├──────────────────────────────────────────────────────────────┤
│ 标的: ${data.code.padEnd(8)} 问题: ${data.question.slice(0, 34).padEnd(34)} │
│ 结论: ${formatAction(data.decision.action).padEnd(52)} │
│ 置信度: ${(data.decision.confidence * 100).toFixed(0).padStart(3)}%                                               │
├──────────────────────────────────────────────────────────────┤
│ Market:   ${data.experts.market.summary.slice(0, 50).padEnd(50)} │
│ Analysis: ${data.experts.analysis.summary.slice(0, 50).padEnd(50)} │
│ Strategy: ${data.experts.strategy.summary.slice(0, 50).padEnd(50)} │
│ Risk:     ${data.experts.risk.summary.slice(0, 50).padEnd(50)} │
├──────────────────────────────────────────────────────────────┤
│ 影响权重:                                                     │
│ 基础分: ${formatSigned(influence.base_score).padEnd(52)} │
│ 风险扣分: ${formatSigned(-influence.risk_penalty).padEnd(50)} │
│ 风格偏置: ${formatSigned(influence.style_bias).padEnd(50)} │
│ 风险偏好: ${formatSigned(influence.risk_appetite).padEnd(50)} │
│ 策略权重: ${formatSigned(influence.strategy_weight).padEnd(50)} │
│ 最终分: ${formatSigned(influence.final_score).padEnd(52)} │
├──────────────────────────────────────────────────────────────┤
│ 推理轨迹:                                                     │
│ 1) ${trace1} │
│ 2) ${trace2} │
│ 3) ${trace3} │`;

  // 添加冲突仲裁信息
  if (arbitration?.conflictInfo) {
    output += `
├──────────────────────────────────────────────────────────────┤
│ 冲突仲裁:                                                     │
│ 类型: ${arbitration.conflictInfo.type.padEnd(52)} │
│ 严重程度: ${arbitration.conflictInfo.severity.padEnd(47)} │
│ 描述: ${arbitration.conflictInfo.description.slice(0, 52).padEnd(52)} │`;
  }

  output += `
└──────────────────────────────────────────────────────────────┘
`;

  return output;
}

export async function handleAgentTeam(input: AgentTeamInput): Promise<AgentTeamOutput> {
  // 创建会话
  const question = input.question || '当前是否适合介入？';
  const session: Session = createSession(input.code, question);

  try {
    if (!/^\d{6}$/.test(input.code)) {
      return {
        success: false,
        error: `无效的股票代码格式: ${input.code}，应为6位数字`,
      };
    }

    const days = input.days ?? 100;

    // 任务: 获取行情数据
    const quoteTask = addTaskNode(session, '获取实时行情数据', 'Market Agent');
    updateTaskNode(session, quoteTask.id, 'running');
    console.log('正在获取行情数据...');
    const quote = await getQuote(input.code);
    updateTaskNode(session, quoteTask.id, 'completed', `涨跌幅 ${quote.change_percent.toFixed(2)}%`);

    // 添加行情证据
    addEvidence(
      session,
      'quote',
      'market',
      `价格: ${quote.price}, 涨跌幅: ${quote.change_percent.toFixed(2)}%`,
      Math.abs(quote.change_percent) / 5
    );

    // 任务: 技术分析
    const analysisTask = addTaskNode(session, '技术指标分析', 'Analysis Agent');
    updateTaskNode(session, analysisTask.id, 'running');
    console.log('正在进行技术分析...');
    const analysis = await analyzeStock(input.code, days);
    updateTaskNode(session, analysisTask.id, 'completed', `识别 ${analysis.signals.length} 个信号`);

    // 添加分析证据
    addEvidence(
      session,
      'analysis',
      'analysis',
      `RSI6: ${analysis.latest.rsi6.toFixed(1)}, KDJ-J: ${analysis.latest.kdj_j.toFixed(1)}`,
      0.7
    );

    // 任务: 策略筛选
    const strategyTask = addTaskNode(session, '策略筛选评估', 'Strategy Agent');
    updateTaskNode(session, strategyTask.id, 'running');
    console.log('正在进行策略筛选...');
    let strategyTimedOut = false;
    const screenPromise = screenStocks(undefined, 1, [input.code]);
    const timeoutPromise = new Promise<never>((_, reject) => {
      setTimeout(() => reject(new Error('STRATEGY_SCREEN_TIMEOUT')), STRATEGY_SCREEN_TIMEOUT_MS);
    });
    const screen = await Promise.race([screenPromise, timeoutPromise]).catch((error) => {
      if (error instanceof Error && error.message === 'STRATEGY_SCREEN_TIMEOUT') {
        strategyTimedOut = true;
        console.log('策略筛选超时，使用降级策略继续汇总...');
        return { total: 0, results: [] };
      }
      throw error;
    });
    updateTaskNode(session, strategyTask.id, 'completed', strategyTimedOut ? '超时降级' : `筛选 ${screen.total} 只`);

    // 任务: 加载反馈画像
    const styleTask = addTaskNode(session, '加载用户反馈画像', 'Style Agent');
    updateTaskNode(session, styleTask.id, 'running');
    console.log('正在加载用户反馈画像...');
    const feedbackProfile = await loadTeamFeedbackProfile(input.code);
    const globalProfile = await loadGlobalFeedbackProfile();
    updateTaskNode(session, styleTask.id, 'completed', `样本 ${feedbackProfile.sample_count}`);

    // 添加风格证据
    addEvidence(
      session,
      'feedback',
      'style',
      `风险偏好: ${globalProfile.risk_appetite.toFixed(2)}`,
      Math.abs(globalProfile.risk_appetite)
    );

    const screenMatched = screen.results.find((item) => item.code === input.code);

    const strategyOpinion = strategyTimedOut
      ? {
          stance: 'neutral' as const,
          confidence: 0.45,
          summary: '策略筛选超时，暂按中性处理',
          evidence: ['策略侧未返回可用结果，未纳入正负加权'],
        }
      : getStrategyOpinion(Boolean(screenMatched), screenMatched?.score);

    // 任务: 风险评估
    const riskTask = addTaskNode(session, '风险评估', 'Risk Agent');
    const experts: AgentTeamOutputData['experts'] = {
      market: getMarketOpinion(quote.change_percent),
      analysis: getAnalysisOpinion(analysis.signals),
      strategy: strategyOpinion,
      risk: getRiskOpinion(analysis.latest.rsi6, analysis.latest.kdj_j, quote.change_percent),
      style: getStyleOpinion(feedbackProfile),
    };
    updateTaskNode(session, riskTask.id, 'completed', `风险等级: ${experts.risk.level}`);

    // 添加风险证据
    addEvidence(
      session,
      'risk',
      'risk',
      `风险等级: ${experts.risk.level}, RSI6: ${analysis.latest.rsi6.toFixed(1)}`,
      experts.risk.level === 'high' ? 0.8 : experts.risk.level === 'low' ? 0.4 : 0.6
    );

    // 任务: 汇总决策
    const decisionTask = addTaskNode(session, '汇总多专家结论', 'Orchestrator');
    updateTaskNode(session, decisionTask.id, 'running');
    console.log('正在汇总多专家结论...');
    const matchedFactors = screenMatched?.matched_factors ?? [];
    const { decision, arbitration } = aggregateDecision(experts, globalProfile, matchedFactors);
    const summary = `${formatAction(decision.action)}（置信度 ${(decision.confidence * 100).toFixed(0)}%）`;
    updateTaskNode(session, decisionTask.id, 'completed', summary);

    // 任务: 冲突仲裁
    if (arbitration.conflictInfo) {
      const arbitrationTask = addTaskNode(session, '冲突仲裁', 'Conflict Arbiter');
      updateTaskNode(session, arbitrationTask.id, 'completed', arbitration.conflictInfo.description);
      console.log(formatArbitrationResult(arbitration));
    }

    const data: AgentTeamOutputData = {
      code: input.code,
      question,
      summary,
      experts,
      decision,
    };

    // 设置会话结论
    setConclusion(session, data);

    // 设置仲裁结果
    setArbitration(session, arbitration);

    // 保存会话
    const sessionPath = await saveSession(session);
    console.log(`会话已保存: ${sessionPath}`);

    console.log(formatTeamOutput(data, arbitration));

    return {
      success: true,
      data,
      sessionId: session.id,
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    // 即使失败也保存会话记录
    setConclusion(session, {
      code: input.code,
      question,
      summary: '分析失败',
      experts: {
        market: { stance: 'neutral', confidence: 0.5, summary: '获取失败', evidence: [] },
        analysis: { stance: 'neutral', confidence: 0.5, summary: '获取失败', evidence: [] },
        strategy: { stance: 'neutral', confidence: 0.5, summary: '获取失败', evidence: [] },
        risk: { level: 'medium', stance: 'neutral', confidence: 0.5, summary: '获取失败', evidence: [] },
        style: { stance: 'neutral', confidence: 0.5, summary: '获取失败', evidence: [] },
      },
      decision: {
        action: 'wait',
        confidence: 0,
        rationale: [message],
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
    });
    await saveSession(session).catch(() => {});

    return {
      success: false,
      error: `Agent Team 分析失败: ${message}`,
      sessionId: session.id,
    };
  }
}

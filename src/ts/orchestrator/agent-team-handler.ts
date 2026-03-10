import { analyzeStock, getQuote, screenStocks } from '../utils/python-bridge.js';
import {
  loadGlobalFeedbackProfile,
  loadTeamFeedbackProfile,
} from './team-feedback-store.js';

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
): AgentTeamOutputData['decision'] {
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

  let action: DecisionAction = 'wait';
  if (score >= 0.5 && experts.risk.level !== 'high') {
    action = 'watch_buy';
  } else if (score <= -0.2 || experts.risk.level === 'high') {
    action = 'hold_or_reduce';
  }

  const rationale: string[] = [
    experts.market.summary,
    experts.analysis.summary,
    experts.strategy.summary,
    experts.risk.summary,
  ];

  const counterpoints = [
    experts.risk.level === 'high' ? '短期波动风险较高，追涨需谨慎' : '风险未显著放大',
    experts.style.summary,
  ];

  return {
    action,
    confidence: clamp(0.45 + Math.abs(score) * 0.45, 0.45, 0.95),
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

function formatTeamOutput(data: AgentTeamOutputData): string {
  const influence = data.decision.influence;
  const formatSigned = (value: number): string => (value >= 0 ? `+${value.toFixed(3)}` : value.toFixed(3));
  const trace1 = (data.decision.rationale[0] || '').slice(0, 50).padEnd(50);
  const trace2 = (data.decision.rationale[1] || '').slice(0, 50).padEnd(50);
  const trace3 = (data.decision.rationale[2] || '').slice(0, 50).padEnd(50);
  return `
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
│ 3) ${trace3} │
└──────────────────────────────────────────────────────────────┘
`;
}

export async function handleAgentTeam(input: AgentTeamInput): Promise<AgentTeamOutput> {
  try {
    if (!/^\d{6}$/.test(input.code)) {
      return {
        success: false,
        error: `无效的股票代码格式: ${input.code}，应为6位数字`,
      };
    }

    const question = input.question || '当前是否适合介入？';
    const days = input.days ?? 100;

    console.log('正在获取行情数据...');
    const quote = await getQuote(input.code);

    console.log('正在进行技术分析...');
    const analysis = await analyzeStock(input.code, days);

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

    console.log('正在加载用户反馈画像...');
    const feedbackProfile = await loadTeamFeedbackProfile(input.code);
    const globalProfile = await loadGlobalFeedbackProfile();

    const screenMatched = screen.results.find((item) => item.code === input.code);

    const strategyOpinion = strategyTimedOut
      ? {
          stance: 'neutral' as const,
          confidence: 0.45,
          summary: '策略筛选超时，暂按中性处理',
          evidence: ['策略侧未返回可用结果，未纳入正负加权'],
        }
      : getStrategyOpinion(Boolean(screenMatched), screenMatched?.score);

    const experts: AgentTeamOutputData['experts'] = {
      market: getMarketOpinion(quote.change_percent),
      analysis: getAnalysisOpinion(analysis.signals),
      strategy: strategyOpinion,
      risk: getRiskOpinion(analysis.latest.rsi6, analysis.latest.kdj_j, quote.change_percent),
      style: getStyleOpinion(feedbackProfile),
    };

    console.log('正在汇总多专家结论...');
    const matchedFactors = screenMatched?.matched_factors ?? [];
    const decision = aggregateDecision(experts, globalProfile, matchedFactors);
    const summary = `${formatAction(decision.action)}（置信度 ${(decision.confidence * 100).toFixed(0)}%）`;

    const data: AgentTeamOutputData = {
      code: input.code,
      question,
      summary,
      experts,
      decision,
    };

    console.log(formatTeamOutput(data));

    return {
      success: true,
      data,
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      success: false,
      error: `Agent Team 分析失败: ${message}`,
    };
  }
}

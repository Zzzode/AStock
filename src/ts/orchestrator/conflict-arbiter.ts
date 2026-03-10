/**
 * 专家冲突仲裁器
 * 当多个专家意见分歧时进行仲裁
 */

import { GlobalFeedbackProfile } from './team-feedback-store.js';

type Stance = 'bullish' | 'bearish' | 'neutral';
type RiskLevel = 'low' | 'medium' | 'high';
type DecisionAction = 'watch_buy' | 'wait' | 'hold_or_reduce';

/**
 * 专家意见接口
 */
export interface ExpertOpinion {
  stance: Stance;
  confidence: number;
  summary: string;
  evidence: string[];
}

/**
 * 风险专家意见接口
 */
export interface RiskOpinion extends ExpertOpinion {
  level: RiskLevel;
}

/**
 * 冲突信息
 */
export interface ConflictInfo {
  type: 'stance' | 'confidence' | 'action';
  severity: 'low' | 'medium' | 'high';
  involvedAgents: string[];
  description: string;
}

/**
 * 仲裁结果
 */
export interface ArbitrationResult {
  finalDecision: DecisionAction;
  confidence: number;
  reasoning: string[];
  conflictInfo?: ConflictInfo;
  weights: Record<string, number>;
}

/**
 * 专家意见集合
 */
export interface ExpertOpinions {
  market: ExpertOpinion;
  analysis: ExpertOpinion;
  strategy: ExpertOpinion;
  risk: RiskOpinion;
  style: ExpertOpinion;
}

/**
 * 仲裁器配置
 */
export interface ArbiterConfig {
  /** 立场冲突阈值（0-2） */
  stanceConflictThreshold: number;
  /** 置信度差异阈值（0-1） */
  confidenceConflictThreshold: number;
  /** 风险专家一票否决权 */
  riskVetoEnabled: boolean;
  /** 高风险惩罚系数 */
  highRiskPenalty: number;
  /** 中风险惩罚系数 */
  mediumRiskPenalty: number;
  /** 最小置信度 */
  minConfidence: number;
  /** 最大置信度 */
  maxConfidence: number;
}

/**
 * 专家权重配置
 */
export interface ExpertWeights {
  market: number;
  analysis: number;
  strategy: number;
  risk: number;
  style: number;
}

const DEFAULT_CONFIG: ArbiterConfig = {
  stanceConflictThreshold: 1.0,
  confidenceConflictThreshold: 0.3,
  riskVetoEnabled: true,
  highRiskPenalty: 0.5,
  mediumRiskPenalty: 0.2,
  minConfidence: 0.45,
  maxConfidence: 0.95,
};

const DEFAULT_WEIGHTS: ExpertWeights = {
  market: 1.0,
  analysis: 1.2,
  strategy: 0.8,
  risk: 1.5,
  style: 0.6,
};

/**
 * 将立场转换为数值分数
 */
function stanceToScore(stance: Stance): number {
  switch (stance) {
    case 'bullish':
      return 1;
    case 'bearish':
      return -1;
    case 'neutral':
    default:
      return 0;
  }
}

/**
 * 将动作转换为数值分数
 */
function actionToScore(action: DecisionAction): number {
  switch (action) {
    case 'watch_buy':
      return 1;
    case 'hold_or_reduce':
      return -1;
    case 'wait':
    default:
      return 0;
  }
}

/**
 * 计算专家的有效权重（基于历史反馈学习）
 */
function calculateEffectiveWeights(
  baseWeights: ExpertWeights,
  globalProfile: GlobalFeedbackProfile
): Record<string, number> {
  const weights: Record<string, number> = { ...baseWeights };

  // 根据风险偏好调整风险专家权重
  const riskAppetite = globalProfile.risk_appetite;
  if (riskAppetite > 0.3) {
    // 激进用户，降低风险专家权重
    weights.risk = baseWeights.risk * (1 - riskAppetite * 0.3);
  } else if (riskAppetite < -0.3) {
    // 保守用户，提高风险专家权重
    weights.risk = baseWeights.risk * (1 - riskAppetite * 0.3);
  }

  // 根据样本数量调整风格专家权重
  if (globalProfile.sample_count < 5) {
    weights.style = baseWeights.style * 0.5;
  } else if (globalProfile.sample_count > 20) {
    weights.style = baseWeights.style * 1.2;
  }

  return weights;
}

/**
 * 检测立场冲突
 */
function detectStanceConflict(
  opinions: ExpertOpinions,
  threshold: number
): ConflictInfo | null {
  const agents = Object.keys(opinions) as (keyof ExpertOpinions)[];
  const scores: { agent: string; score: number; confidence: number }[] = agents.map(
    (agent) => ({
      agent,
      score: stanceToScore(opinions[agent].stance),
      confidence: opinions[agent].confidence,
    })
  );

  // 找出最大分歧
  let maxDiff = 0;
  let conflictAgents: string[] = [];

  for (let i = 0; i < scores.length; i++) {
    for (let j = i + 1; j < scores.length; j++) {
      const diff = Math.abs(scores[i].score - scores[j].score);
      if (diff > maxDiff) {
        maxDiff = diff;
        conflictAgents = [scores[i].agent, scores[j].agent];
      }
    }
  }

  if (maxDiff >= threshold) {
    const bullishAgents = scores.filter((s) => s.score > 0).map((s) => s.agent);
    const bearishAgents = scores.filter((s) => s.score < 0).map((s) => s.agent);

    let description = '';
    if (bullishAgents.length > 0 && bearishAgents.length > 0) {
      description = `立场分歧：${bullishAgents.join(', ')} 偏多 vs ${bearishAgents.join(', ')} 偏空`;
    } else {
      description = `立场存在较大分歧，最大差异值 ${maxDiff.toFixed(2)}`;
    }

    const severity = maxDiff >= 1.5 ? 'high' : maxDiff >= 1.0 ? 'medium' : 'low';

    return {
      type: 'stance',
      severity,
      involvedAgents: conflictAgents,
      description,
    };
  }

  return null;
}

/**
 * 检测置信度冲突
 */
function detectConfidenceConflict(
  opinions: ExpertOpinions,
  threshold: number
): ConflictInfo | null {
  const agents = Object.keys(opinions) as (keyof ExpertOpinions)[];
  const confidences = agents.map((agent) => ({
    agent,
    confidence: opinions[agent].confidence,
  }));

  const maxConf = Math.max(...confidences.map((c) => c.confidence));
  const minConf = Math.min(...confidences.map((c) => c.confidence));
  const diff = maxConf - minConf;

  if (diff >= threshold) {
    const highConfAgents = confidences.filter((c) => c.confidence === maxConf).map((c) => c.agent);
    const lowConfAgents = confidences.filter((c) => c.confidence === minConf).map((c) => c.agent);

    return {
      type: 'confidence',
      severity: diff >= 0.5 ? 'high' : diff >= 0.3 ? 'medium' : 'low',
      involvedAgents: [...highConfAgents, ...lowConfAgents],
      description: `置信度差异显著：${highConfAgents.join(', ')} (${(maxConf * 100).toFixed(0)}%) vs ${lowConfAgents.join(', ')} (${(minConf * 100).toFixed(0)}%)`,
    };
  }

  return null;
}

/**
 * 检测动作冲突（根据立场推导推荐动作）
 */
function detectActionConflict(opinions: ExpertOpinions): ConflictInfo | null {
  const agents = Object.keys(opinions) as (keyof ExpertOpinions)[];
  const actionPreferences: Record<DecisionAction, string[]> = {
    watch_buy: [],
    wait: [],
    hold_or_reduce: [],
  };

  for (const agent of agents) {
    const opinion = opinions[agent];
    if (opinion.stance === 'bullish') {
      actionPreferences.watch_buy.push(agent);
    } else if (opinion.stance === 'bearish') {
      actionPreferences.hold_or_reduce.push(agent);
    } else {
      actionPreferences.wait.push(agent);
    }
  }

  const hasBuy = actionPreferences.watch_buy.length > 0;
  const hasReduce = actionPreferences.hold_or_reduce.length > 0;

  if (hasBuy && hasReduce) {
    return {
      type: 'action',
      severity: 'high',
      involvedAgents: [
        ...actionPreferences.watch_buy,
        ...actionPreferences.hold_or_reduce,
      ],
      description: `动作建议冲突：${actionPreferences.watch_buy.join(', ')} 建议关注买入 vs ${actionPreferences.hold_or_reduce.join(', ')} 建议减仓观望`,
    };
  }

  return null;
}

/**
 * 检测所有冲突
 */
function detectConflicts(
  opinions: ExpertOpinions,
  config: ArbiterConfig
): ConflictInfo[] {
  const conflicts: ConflictInfo[] = [];

  const stanceConflict = detectStanceConflict(opinions, config.stanceConflictThreshold);
  if (stanceConflict) {
    conflicts.push(stanceConflict);
  }

  const confidenceConflict = detectConfidenceConflict(opinions, config.confidenceConflictThreshold);
  if (confidenceConflict) {
    conflicts.push(confidenceConflict);
  }

  const actionConflict = detectActionConflict(opinions);
  if (actionConflict) {
    conflicts.push(actionConflict);
  }

  return conflicts;
}

/**
 * 获取最严重的冲突
 */
function getMostSevereConflict(conflicts: ConflictInfo[]): ConflictInfo | undefined {
  const severityOrder = { high: 3, medium: 2, low: 1 };
  return conflicts.sort((a, b) => severityOrder[b.severity] - severityOrder[a.severity])[0];
}

/**
 * 加权投票仲裁
 */
function weightedVoting(
  opinions: ExpertOpinions,
  weights: Record<string, number>,
  config: ArbiterConfig
): { score: number; reasoning: string[] } {
  const reasoning: string[] = [];
  let weightedSum = 0;
  let totalWeight = 0;

  const agentNames: (keyof ExpertOpinions)[] = ['market', 'analysis', 'strategy', 'risk', 'style'];

  for (const agent of agentNames) {
    const opinion = opinions[agent];
    const weight = weights[agent] ?? 1;
    const score = stanceToScore(opinion.stance);
    const contribution = score * opinion.confidence * weight;

    weightedSum += contribution;
    totalWeight += opinion.confidence * weight;

    reasoning.push(
      `[${agent}] 立场: ${opinion.stance}, 置信度: ${(opinion.confidence * 100).toFixed(0)}%, 权重: ${weight.toFixed(2)}, 贡献: ${contribution.toFixed(3)}`
    );
  }

  const score = totalWeight > 0 ? weightedSum / totalWeight : 0;
  reasoning.push(`加权投票结果: ${score.toFixed(3)}`);

  return { score, reasoning };
}

/**
 * 应用风险专家一票否决权
 */
function applyRiskVeto(
  riskOpinion: RiskOpinion,
  score: number,
  config: ArbiterConfig
): { score: number; action: DecisionAction; reasoning: string } {
  if (!config.riskVetoEnabled) {
    return { score, action: 'wait', reasoning: '风险否决权未启用' };
  }

  if (riskOpinion.level === 'high') {
    // 高风险一票否决买入建议
    return {
      score: Math.min(score, -0.2),
      action: 'hold_or_reduce',
      reasoning: `风险专家行使否决权：风险等级为 high，建议改为观望或减仓`,
    };
  }

  return { score, action: 'wait', reasoning: '风险等级未触发否决' };
}

/**
 * 根据分数确定最终动作
 */
function determineAction(
  score: number,
  riskLevel: RiskLevel,
  config: ArbiterConfig
): DecisionAction {
  if (score >= 0.5 && riskLevel !== 'high') {
    return 'watch_buy';
  }
  if (score <= -0.2 || riskLevel === 'high') {
    return 'hold_or_reduce';
  }
  return 'wait';
}

/**
 * 计算最终置信度
 */
function calculateFinalConfidence(
  score: number,
  opinions: ExpertOpinions,
  config: ArbiterConfig
): number {
  // 基础置信度基于分数绝对值
  const baseConfidence = config.minConfidence + Math.abs(score) * 0.45;

  // 考虑专家意见的一致性
  const agentNames: (keyof ExpertOpinions)[] = ['market', 'analysis', 'strategy', 'risk', 'style'];
  const scores = agentNames.map((agent) => stanceToScore(opinions[agent].stance));
  const avgScore = scores.reduce((sum, s) => sum + s, 0) / scores.length;
  const variance = scores.reduce((sum, s) => sum + (s - avgScore) ** 2, 0) / scores.length;

  // 一致性越高，置信度越高
  const consistencyBonus = Math.max(0, 0.1 - variance * 0.05);

  return Math.min(config.maxConfidence, Math.max(config.minConfidence, baseConfidence + consistencyBonus));
}

/**
 * 冲突仲裁器主函数
 */
export function arbitrate(
  opinions: ExpertOpinions,
  globalProfile: GlobalFeedbackProfile,
  customConfig?: Partial<ArbiterConfig>,
  customWeights?: Partial<ExpertWeights>
): ArbitrationResult {
  // 合并配置
  const config: ArbiterConfig = { ...DEFAULT_CONFIG, ...customConfig };
  const baseWeights: ExpertWeights = { ...DEFAULT_WEIGHTS, ...customWeights };

  // 计算有效权重（基于历史反馈学习）
  const weights = calculateEffectiveWeights(baseWeights, globalProfile);

  // 检测冲突
  const conflicts = detectConflicts(opinions, config);
  const mostSevereConflict = getMostSevereConflict(conflicts);

  // 加权投票
  const votingResult = weightedVoting(opinions, weights, config);
  let score = votingResult.score;
  const reasoning = [...votingResult.reasoning];

  // 应用风险否决权
  if (config.riskVetoEnabled && opinions.risk.level === 'high') {
    const vetoResult = applyRiskVeto(opinions.risk, score, config);
    score = vetoResult.score;
    reasoning.push(vetoResult.reasoning);
  }

  // 计算风险惩罚
  let riskPenalty = 0;
  if (opinions.risk.level === 'high') {
    riskPenalty = config.highRiskPenalty;
  } else if (opinions.risk.level === 'medium') {
    riskPenalty = config.mediumRiskPenalty;
  }
  score -= riskPenalty;

  // 确定最终动作
  const action = determineAction(score, opinions.risk.level, config);

  // 计算最终置信度
  const confidence = calculateFinalConfidence(score, opinions, config);

  // 添加冲突信息到推理
  if (mostSevereConflict) {
    reasoning.push(`检测到冲突 [${mostSevereConflict.severity}]: ${mostSevereConflict.description}`);
    reasoning.push(`仲裁策略: 加权投票 + 风险优先`);
  }

  return {
    finalDecision: action,
    confidence,
    reasoning,
    conflictInfo: mostSevereConflict,
    weights,
  };
}

/**
 * 仲裁器配置管理
 */
export class ConflictArbiter {
  private config: ArbiterConfig;
  private weights: ExpertWeights;

  constructor(
    customConfig?: Partial<ArbiterConfig>,
    customWeights?: Partial<ExpertWeights>
  ) {
    this.config = { ...DEFAULT_CONFIG, ...customConfig };
    this.weights = { ...DEFAULT_WEIGHTS, ...customWeights };
  }

  /**
   * 执行仲裁
   */
  arbitrate(
    opinions: ExpertOpinions,
    globalProfile: GlobalFeedbackProfile
  ): ArbitrationResult {
    return arbitrate(opinions, globalProfile, this.config, this.weights);
  }

  /**
   * 更新配置
   */
  updateConfig(newConfig: Partial<ArbiterConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  /**
   * 更新权重
   */
  updateWeights(newWeights: Partial<ExpertWeights>): void {
    this.weights = { ...this.weights, ...newWeights };
  }

  /**
   * 获取当前配置
   */
  getConfig(): ArbiterConfig {
    return { ...this.config };
  }

  /**
   * 获取当前权重
   */
  getWeights(): ExpertWeights {
    return { ...this.weights };
  }

  /**
   * 根据历史反馈学习更新权重
   */
  learnFromFeedback(
    globalProfile: GlobalFeedbackProfile,
    strategySuccessRate?: number
  ): void {
    // 根据风险偏好调整风险权重
    if (globalProfile.risk_appetite > 0.3) {
      this.weights.risk = DEFAULT_WEIGHTS.risk * (1 - globalProfile.risk_appetite * 0.3);
    } else if (globalProfile.risk_appetite < -0.3) {
      this.weights.risk = DEFAULT_WEIGHTS.risk * (1 - globalProfile.risk_appetite * 0.3);
    }

    // 根据策略成功率调整策略权重
    if (strategySuccessRate !== undefined) {
      this.weights.strategy = DEFAULT_WEIGHTS.strategy * (0.5 + strategySuccessRate);
    }

    // 根据样本数量调整风格权重
    if (globalProfile.sample_count >= 20) {
      this.weights.style = DEFAULT_WEIGHTS.style * 1.2;
    } else if (globalProfile.sample_count < 5) {
      this.weights.style = DEFAULT_WEIGHTS.style * 0.5;
    }
  }
}

/**
 * 格式化仲裁结果输出
 */
export function formatArbitrationResult(result: ArbitrationResult): string {
  const lines: string[] = [
    '┌──────────────────────────────────────────────────────────────┐',
    '│ 冲突仲裁结果                                                  │',
    '├──────────────────────────────────────────────────────────────┤',
    `│ 最终决策: ${result.finalDecision.padEnd(50)} │`,
    `│ 置信度: ${(result.confidence * 100).toFixed(0).padStart(3)}%                                               │`,
  ];

  if (result.conflictInfo) {
    lines.push('├──────────────────────────────────────────────────────────────┤');
    lines.push('│ 冲突信息:                                                     │');
    lines.push(`│   类型: ${result.conflictInfo.type.padEnd(52)} │`);
    lines.push(`│   严重程度: ${result.conflictInfo.severity.padEnd(47)} │`);
    lines.push(`│   涉及专家: ${result.conflictInfo.involvedAgents.join(', ').slice(0, 48).padEnd(48)} │`);
    lines.push(`│   描述: ${result.conflictInfo.description.slice(0, 52).padEnd(52)} │`);
  }

  lines.push('├──────────────────────────────────────────────────────────────┤');
  lines.push('│ 专家权重:                                                     │');
  for (const [agent, weight] of Object.entries(result.weights)) {
    lines.push(`│   ${agent.padEnd(10)} ${weight.toFixed(2).padEnd(46)} │`);
  }

  lines.push('├──────────────────────────────────────────────────────────────┤');
  lines.push('│ 仲裁推理:                                                     │');
  for (const r of result.reasoning.slice(0, 8)) {
    lines.push(`│   ${r.slice(0, 58).padEnd(58)} │`);
  }
  if (result.reasoning.length > 8) {
    lines.push(`│   ... 还有 ${result.reasoning.length - 8} 条推理${' '.repeat(43)} │`);
  }

  lines.push('└──────────────────────────────────────────────────────────────┘');

  return lines.join('\n');
}

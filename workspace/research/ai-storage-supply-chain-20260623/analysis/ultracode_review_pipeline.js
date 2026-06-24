export const meta = {
  name: 'ai-storage-ultracode-review',
  description: '顶尖投行视角多 reviewer 审查 AI 存储产业链研报 + 文档专家改进',
  phases: [
    { title: '审查（并行 · 6 视角）', detail: '投资总监/估值/卖方研究/风险/合规/逆向 6 位 reviewer 独立找问题' },
    { title: '对抗校验（并行 · 2 视角）', detail: '对立视角 refute 审查结论 + 交叉优先级合成' },
    { title: '文档专家改进（2 路径）', detail: 'LaTeX 改进（可落地修改建议）+ 叙事结构重写建议' },
  ],
}

const CASE = '/Users/bytedance/Develop/AStock/workspace/research/ai-storage-supply-chain-20260623'

const CH_TARGETS = [
  'sections/ch01_ic_summary.tex',
  'sections/ch02_executive_summary.tex',
  'sections/ch03_supply_chain_map.tex',
  'sections/ch04_ai_demand.tex',
  'sections/ch05_supply_price_cycle.tex',
  'sections/ch06_competition_substitution.tex',
  'sections/ch07_ashare_targets.tex',
  'sections/ch08_valuation.tex',
  'sections/ch09_consensus_divergence.tex',
  'sections/ch10_risk_stress.tex',
  'sections/ch11_investment_reco.tex',
  'sections/app_sources_audit.tex',
  'data/source_registry.md',
  'data/claim_audit.md',
  'analysis/industry_landscape.md',
  'review_log.md',
]

const COMMON_HINT = `工作区根目录：${CASE}。请深度阅读以下关键文件并据此审查：
章节 LaTeX：${CH_TARGETS.join('、')}
治理文件：data/source_registry.md / data/claim_audit.md / data/source_registry.json
参考锚：workspace/research/power-semiconductor-20260621/data/source_registry.md 与 claim_audit.md（如果存在）
verifier 输出为 PASS=124 FAIL=0 ADVISORY=2，gate=PUBLISH。
要求：按 S（阻断发布）/A（必须修复）/B（建议改进）三级严重性输出，每条问题必须给出 文件:行号（若可读）、问题描述、证据等级、投行惯例违反点、修复建议。严禁泛泛而谈。`

const FINDINGS_SCHEMA = {
  type: 'object',
  required: ['reviewer', 'summary', 'overall_grade', 'total_issues', 's_level', 'a_level', 'b_level', 'findings', 'top5_priority'],
  properties: {
    reviewer: { type: 'string' },
    summary: { type: 'string' },
    overall_grade: { enum: ['PUBLISH','PUBLISH_WITH_A_FIXES','CONDITIONAL_PASS','REJECT_NEEDS_REWRITE'] },
    total_issues: { type: 'integer' },
    s_level: { type: 'integer' },
    a_level: { type: 'integer' },
    b_level: { type: 'integer' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id','severity','title','file','line','evidence','broker_standard','recommendation'],
        properties: {
          id: { type: 'string' },
          severity: { enum: ['S','A','B'] },
          title: { type: 'string' },
          file: { type: 'string' },
          line: { type: ['integer','null'] },
          evidence: { type: 'string' },
          broker_standard: { type: 'string' },
          recommendation: { type: 'string' },
        },
        additionalProperties: false,
      },
    },
    top5_priority: { type: 'array', items: { type: 'string' } },
  },
  additionalProperties: false,
}

phase('审查（并行 · 6 视角）')

const reviewerPrompts = [
  { label: '投资总监-IC', prompt: `你是 Goldman Sachs 亚太科技研究部投资委员会主席（Managing Director）。以投委会一票否决权视角审查这份 AI 存储产业链深度研报。你只关心：(1) IC Summary (ch01) 是否在前 2 页回答了「买什么、多少、何时、为什么」四问；(2) 推荐组合的赔率（upside/downside ratio）是否量化，有没有「没有下行情景分析」的严重问题；(3) 核心论点有没有被自己的风险章节（ch10）证伪；(4) 首章数字有没有与 ch08/ch11 自洽（例如目标价区间、EPS、上行空间数字三章一致）。S 级问题只留给「数据矛盾导致推荐不可信」。${COMMON_HINT}` },
  { label: '估值专家', prompt: `你是 Morgan Stanley 亚洲半导体资深估值分析师（Executive Director）。深度审查 ch08_valuation.tex 与 app_sources_audit.tex 的估值审计。重点：(1) 国际可比估值表（表 8-1）A 股溢价 2x 的「合理性」论证，引用 GS 三因子模型但表 8-3 三因子数字是否相加即等于各行溢价（例如北华 38+35+32=105，应等于+105%，检查每一行）；(2) 表 8-2 三表预测：PE × EPS 是否严格等于 Price（例如澜起 45x×2.70=121.5，验算全部 9 只），以及 EV/EBITDA、PS 法分母与表 8-1 的营收/EBITDA 数字是否前后一致；(3) 江波龙 BLOCK 区间 [17.1,31.7] EPS 的 Q25/Q75 分位数来源披露是否充分（爱建/国信/中邮三家分位数区间是否在来源注册表中有 S-ID 映射）；(4) 权重纪律（中微 9% = 北华 15%×60%，拓荆 6% ≤ 北华×60%）是否在 ch11 与 ch08 双向说明；(5) 是否存在「目标价 = 整数」这种非科学拍脑袋。将每个算术/会计问题标为 S 或 A。${COMMON_HINT}` },
  { label: '卖方研究-MD', prompt: `你是 JPMorgan 大中华区半导体研究主管（MD）。站在卖方首席视角，审查这份研报的「投行可读性」。重点：(1) 叙事节奏——每章开头是否有 "Investment Question" 式开头段，而不是一上来就堆表；(2) 每一张核心表格后面有没有「投资含义」段落（Investment Implication），把数据翻译成行动；(3) ch04 AI 需求 / ch05 供需周期 / ch07 标的深度 / ch09 共识分歧，这四章是否互相引用而不是孤岛；(4) 核心结论的「三支柱」是否在 ch01/ch02/ch11 三处严格重复对齐（GS/MS 的 3×3 叙述纪律）；(5) 有没有「表比字多」的图表书风格章节（单表占 >2 页且前后解释 <0.5 页 = FAIL）；(6) 英文术语首现是否定义（CXL/TSV/HBM/CoWoS/BIS 等）；(7) 图表编号是否全连续无跳号、exhibitbox 标题是否中英对照一致。${COMMON_HINT}` },
  { label: '风险-压力测试', prompt: `你是 BlackRock 亚太科技投资组合风险经理。审查 ch10_risk_stress.tex 与 ch11 的概率权重。重点：(1) 基准 65% + 乐观 15% + 下行 20% = 100% 是否恒等，有没有第三种中间情景缺失导致只有三档；(2) 下行情景的「最大回撤 -25%」是拍脑袋还是来自历史 2018/2022 两轮回撤统计；(3) 出口管制（BIS HBM 单独管制）风险是否建模了概率×冲击，而不是定性描述；(4) 风险因子之间的相关性（AI 需求下修 + BIS 升级 + 原厂 capex 收缩同时发生）是否给出了联合概率（>=3 因子联合概率必须 <5%）；(5) 组合的 60%/30%/10% 三层的集中度风险（前 3 只标的是否 >50%）、流动性风险（日均成交额 > 仓位 10x）有没有量化说明；(6) ch11 表 11-1 触发条件有没有 KRI（关键风险指标）对应阈值，否则只是口号。${COMMON_HINT}` },
  { label: '合规-来源治理', prompt: `你是 SEC/FCA 合规官 + 中金研究合规主管联合审查。重点：(1) claim_audit.md 中 C 级（自媒体）和 D 级（不可信）主张是否真的没出现在正文估值里（扫描 ch08/ch11 中所有量化数字，追溯到 source_registry 或 claim_audit，若命中 C/D 且未声明 BLOCK = S 级）；(2) app_sources_audit 附录 A 的 20 条来源，是否每条都有明确的 S-ID 回链到正文（正文首次引用时必须标注 S-XX）；(3) ch03/ch04 中大量 HBM 容量/ASP 数字，是否都有 S-ID 标注（若仅写「行业调研综合」= C 级 = BLOCK）；(4) ch01/ch11 目标回报「+25-40%」是否符合「合理价值区间而非目标价」的 BLOCK 治理声明（ch08 第 145 行要求）；(5) 分析师独立性声明、利益冲突披露、数据质量警示三段（app D）是否遗漏「香港《操守准则》第 16 条要求的发布人身份/资格声明」；(6) 研报日期 2026-06-23 与所有数据截止日期是否在脚注/首页统一披露。${COMMON_HINT}` },
  { label: '逆向-看空', prompt: `你是 S3 Partners 空头分析师 + 逆向投资组合经理。你的任务是找到报告所有「多头一厢情愿」：(1) DDR5 涨价 8-10 季持续性（历史平均 4-6 季），为什么本轮不同？给出的 3 条理由是否能在来源注册表中找到 L1/L2 支持；(2) 长存 290L / 长鑫 15nm 的良率突破是否只来自 L4 产业媒体，有没有 L1/L2 交叉验证；(3) 先进封装「>5 亿 AI 收入」买入触发是否有任意一家封测厂 L1 披露分拆；(4) 「CXL 二阶 Alpha」澜起 18% 核心权重，CXL 2027 20 亿收入是否是 L1 管理层指引还是 Wind 一致预期中值，偏离度多少；(5) 2026E 全链净利增速 42%，是否在历史可比 2017-2018 周期峰值（48%）附近，但本轮 capex 增速低于 2018，论证 42% 可持续的证据链是否完整；(6) 给出「如果全部乐观假设失败，报告核心结论剩什么」的 stripped-down 版本（只保留 L1/L2 支持的结论）。${COMMON_HINT}` },
]

const findings = await parallel(
  reviewerPrompts.map(function(r) {
    return function() {
      return agent(r.prompt, {
        label: '审查-' + r.label,
        phase: '审查（并行 · 6 视角）',
        schema: FINDINGS_SCHEMA,
        effort: 'max',
        model: 'opus',
      })
    }
  })
)

const FILTERED = findings.filter(Boolean)

phase('对抗校验（并行 · 2 视角）')

const allIssuesFlat = FILTERED.reduce(function(acc, r) {
  return acc.concat(r.findings.map(function(f) {
    var o = {}
    Object.keys(f).forEach(function(k) { o[k] = f[k] })
    o._reviewer = r.reviewer
    o._grade = r.overall_grade
    return o
  }))
}, [])

const adversarial_schema = {
  type: 'object',
  required: ['adversarial_checked','unique_s_count','unique_a_count','dismissed_count','merged_groups'],
  properties: {
    adversarial_checked: { type: 'array', items: { type: 'object', required: ['canonical_id','original_ids','file','severity','confirmed','severity_correction','root_cause','merge_note'], properties: { canonical_id:{type:'string'}, original_ids:{type:'array'}, file:{type:'string'}, severity:{enum:['S','A','B']}, confirmed:{type:'boolean'}, severity_correction:{type:'string'}, root_cause:{type:'string'}, merge_note:{type:'string'} }, additionalProperties: false } } },
    unique_s_count: { type: 'integer' },
    unique_a_count: { type: 'integer' },
    dismissed_count: { type: 'integer' },
    merged_groups: { type: 'array' },
  },
  additionalProperties: false,
}

const synthesis_schema = {
  type: 'object',
  required: ['global_recommendation','one_line_executive_summary','reviewer_votes','must_fix','should_fix','nice_to_have','total_estimated_work_hours','estimated_pdf_pages_touched'],
  properties: {
    global_recommendation: { enum: ['PUBLISH','PUBLISH_WITH_A_FIXES','CONDITIONAL_PASS','REJECT_NEEDS_REWRITE'] },
    one_line_executive_summary: { type: 'string' },
    reviewer_votes: { type: 'array' },
    must_fix: { type: 'array' },
    should_fix: { type: 'array' },
    nice_to_have: { type: 'array' },
    total_estimated_work_hours: { type: 'number' },
    estimated_pdf_pages_touched: { type: 'integer' },
  },
  additionalProperties: false,
}

var adversarialRefute =
  `你是对抗性评审员。以下是 6 位顶尖投行 reviewer 对 AI 存储产业链研报给出的共 ` + allIssuesFlat.length + ` 个问题：\n` +
  JSON.stringify(allIssuesFlat.slice(0, 80), null, 2) + `\n\n` +
  `对每个 S/A 级问题，你要做三件事：\n(1) 确认问题属实（True=确实存在问题）或 误判（False=reviewer 未读全文/误解证据/verifier 已门控）；\n(2) 属实的问题，评级是否过高或过低（应降级/升级的给理由）；\n(3) 合并重复问题（多位 reviewer 指出同一根因），给合并后的 canonical id。\n只对 S/A 级做判断，B 级自动保留无需 refute。\n按 schema 输出 JSON。`

var synthesisPrompt =
  `你是研究总监管控优先级。综合 6 位 reviewer 结果：\n` +
  JSON.stringify(FILTERED.map(function(r) {
    return {
      reviewer: r.reviewer,
      grade: r.overall_grade,
      S: r.s_level,
      A: r.a_level,
      B: r.b_level,
      top5: r.top5_priority,
      findings_summary: r.findings.filter(function(f){return f.severity!=='B'}).map(function(f){return f.id+':'+f.title})
    }
  }), null, 2) + `\n\n` +
  `输出一份综合优先级排序：全局评级 + MUST-FIX Top 10 + SHOULD-FIX Top 15 + NICE-TO-HAVE。每项给 estimated_fix_minutes, dependencies, affected_pages_in_pdf。按 schema 输出 JSON。`

var adversarial = await agent(adversarialRefute, {
  label: '对抗校验-去重',
  phase: '对抗校验（并行 · 2 视角）',
  model: 'opus',
  effort: 'xhigh',
  schema: adversarial_schema,
})

var priorities = await agent(synthesisPrompt, {
  label: '优先级合成',
  phase: '对抗校验（并行 · 2 视角）',
  model: 'opus',
  effort: 'xhigh',
  schema: synthesis_schema,
})

phase('文档专家改进（2 路径）')

var allIssuesJson = JSON.stringify(allIssuesFlat, null, 2)
var prioritiesJson = JSON.stringify(priorities, null, 2)
var adversarialJson = JSON.stringify(adversarial, null, 2)
if (allIssuesJson.length > 40000) allIssuesJson = allIssuesJson.slice(0, 40000)
if (prioritiesJson.length > 15000) prioritiesJson = prioritiesJson.slice(0, 15000)
if (adversarialJson.length > 15000) adversarialJson = adversarialJson.slice(0, 15000)

const latex_schema = {
  type: 'object',
  required: ['edits','batch_order','post_fix_actions','new_exhibits_needed','total_edits','files_touched','compile_check_required'],
  properties: {
    edits: { type: 'array', items: { type: 'object', required: ['id','file','line_hint','old_string','new_string','addresses_issue_ids','rationale','risk_level'], properties: { id:{type:'string'}, file:{type:'string'}, line_hint:{type:['integer','string']}, old_string:{type:'string'}, new_string:{type:'string'}, addresses_issue_ids:{type:'array'}, rationale:{type:'string'}, risk_level:{enum:['safe','low','medium','high']} }, additionalProperties: false } } },
    batch_order: { type: 'array' },
    post_fix_actions: { type: 'array' },
    new_exhibits_needed: { type: 'array' },
    total_edits: { type: 'integer' },
    files_touched: { type: 'integer' },
    compile_check_required: { type: 'boolean' },
  },
  additionalProperties: false,
}

const narrative_schema = {
  type: 'object',
  required: ['three_pillars_proposal','per_chapter_rewrite','pre_post_templates','glossary_required','ch01_ic_gs_template','total_words_to_rewrite_estimate'],
  properties: {
    three_pillars_proposal: { type: 'object' },
    per_chapter_rewrite: { type: 'array' },
    pre_post_templates: { type: 'object' },
    glossary_required: { type: 'array' },
    ch01_ic_gs_template: { type: 'object' },
    total_words_to_rewrite_estimate: { type: 'integer' },
  },
  additionalProperties: false,
}

var latexPrompt =
  `你是 IB 级别的 LaTeX 文档工程师（Goldman Sachs Research 文档团队 Lead）。针对以下 must_fix / should_fix 列表以及 6 位 reviewer 所有 findings，输出一份可直接落地的 LaTeX 修改建议清单（old_string / new_string 对，可被 Edit 工具直接消费）。\n\n原始 findings：\n` + allIssuesJson + `\n\n合成优先级：\n` + prioritiesJson + `\n\n对抗校验：\n` + adversarialJson + `\n\n` +
  `要求：(1) 针对每个 confirmed=true 的 S/A 级问题，给出 file + line_hint + old_string + new_string + rationale + risk_level；(2) 针对章节风格修复，给出模板 + 应用章节；(3) 结尾给 batch_order 建议 + post_fix_actions（重新运行 verifier、refresh checksums 等）。按 schema 输出 JSON。`

var narrativePrompt =
  `你是 Morgan Stanley 研究叙事架构师。请基于这份 AI 存储产业链研报的 reviewer findings 与优先级合成结果，提出「不改数字、只改结构和文字组织」的叙事重写建议。\n\nreviewer 结果摘要：\n` +
  JSON.stringify(FILTERED.map(function(r){return {reviewer:r.reviewer,findings:r.findings.map(function(f){return f.id+'/'+f.severity+': '+f.title+' @'+f.file+(f.line?':'+f.line:'')})}}), null, 2).slice(0, 30000) +
  `\n\n优先级合成：\n` + prioritiesJson + `\n\n` +
  `要求：(1) 每章给 3 个叙事弱点 + Goldman Sachs BLUF/3 pillars/supporting decks/counterview/investment implication 五段式蓝图；(2) 跨章节核心三支柱 proposal + ch01/ch02/ch11 三处对齐时间表；(3) 表前引导段 + 表后投资含义段模板（带字数）；(4) 英文术语首次出现的双语定义清单；(5) ch01 IC Summary 的 Goldman Sachs 标准 IC 一页模板（中文 LaTeX 内容）。按 schema 输出 JSON。`

const [latexPatches, narrativeRewrite] = await parallel([
  function() { return agent(latexPrompt, { label:'LaTeX-编辑建议', phase:'文档专家改进（2 路径）', model:'opus', effort:'max', schema:latex_schema }) },
  function() { return agent(narrativePrompt, { label:'叙事架构改进', phase:'文档专家改进（2 路径）', model:'opus', effort:'max', schema:narrative_schema }) },
])

log('Ultracode review pipeline complete: ' + FILTERED.length + ' reviewers → 原始 S=' +
  FILTERED.reduce(function(a,r){return a+r.s_level},0) +
  ' A=' + FILTERED.reduce(function(a,r){return a+r.a_level},0) +
  ' B=' + FILTERED.reduce(function(a,r){return a+r.b_level},0) +
  ' → 对抗后 unique S=' + (adversarial && adversarial.unique_s_count) +
  ' A=' + (adversarial && adversarial.unique_a_count) +
  ' → 最终建议 = ' + (priorities && priorities.global_recommendation))

return {
  raw_reviews: FILTERED,
  adversarial: adversarial,
  priorities: priorities,
  latex_patches: latexPatches,
  narrative_rewrite: narrativeRewrite,
}

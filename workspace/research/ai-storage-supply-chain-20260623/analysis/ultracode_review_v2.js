// ULTRACODE REVIEW PIPELINE (PLAIN JS ONLY, NO TS TOKENS)
// Phase 1: 6 reviewers in parallel
// Phase 2: adversarial check + priority synthesis
// Phase 3: LaTeX patch engineer + narrative architect
export const meta = {
  name: 'ai-storage-ultracode-review-v2',
  description: 'Top-tier IB multi-reviewer audit + document improvement',
  phases: [
    { title: '审查并行（6视角）' },
    { title: '对抗校验与优先级' },
    { title: '文档专家改进' },
  ],
}

var CASE = '/Users/bytedance/Develop/AStock/workspace/research/ai-storage-supply-chain-20260623'
var CHS = [
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
var HINT = '工作区根：' + CASE + '。深度阅读以下关键文件并审查：' + CHS.join('、') +
  '。治理：data/source_registry.md / data/claim_audit.md / source_registry.json。' +
  'verifier=PASS=124 FAIL=0 ADVISORY=2 gate=PUBLISH。' +
  '输出结构化 JSON，字段=reviewer(身份) summary(一句话总评) overall_grade(PUBLISH|PUBLISH_WITH_A_FIXES|CONDITIONAL_PASS|REJECT_NEEDS_REWRITE) total_issues s_level a_level b_level findings(array,每条含 id severity(S|A|B) title file line evidence broker_standard recommendation) top5_priority(array of id)。' +
  '每条问题必须精准指向文件:行号并引述原文。严禁泛泛而谈。'

var ROLES = [
  ['投资总监-IC', '你是 Goldman Sachs 亚太科技 MD/投委会主席。一票否决视角。只关心 4 件事：(1) ch01 IC Summary 是否在前 2 页回答买什么/多少/何时/为什么；(2) 组合赔率(upside/downside)是否量化、下行情景是否存在；(3) 核心论点是否被 ch10 风险章节自证伪；(4) ch01 数字与 ch08/ch11 是否三章一致（目标价/EPS/上行空间）。S 级只留给数据冲突导致推荐不可信。' + HINT],
  ['估值专家', '你是 Morgan Stanley 亚洲半导体估值 ED。深度审 ch08 与附录。重点：(1) 表 8-1 A股溢价 2x 合理性；(2) 表 8-3 三因子相加是否等于每行溢价（逐行验算 38+35+32=105 这类）；(3) 表 8-2 PE*EPS=Price 全 9 只验算，EV/EBITDA/PS 分母与表 8-1 营收一致；(4) 江波龙 EPS [17.1,31.7] Q25/Q75 来源是否可映射至来源注册表 S-ID；(5) 权重纪律中微9%=北华15%*60%、拓荆6%<=9% 是否双向说明；(6) 是否存在整数目标价拍脑袋。算术不通过直接标S/A。' + HINT],
  ['卖方MD-叙事', '你是 JPM 大中华区半导体 MD。投行可读性视角。(1) 每章开头是否有 investment question 段而非直接堆表；(2) 核心表格后是否有投资含义段；(3) ch04/05/07/09 是否互相引用非孤岛；(4) 核心三支柱是否在 ch01/ch02/ch11 三处精确重复对齐（GS/MS 3x3 纪律）；(5) 是否存在「表比字多」图表书章节（单表>2页且解释<0.5页=FAIL）；(6) 英文术语首现是否 CXL/TSV/HBM/CoWoS/BIS 全定义；(7) 图表编号连续无跳号、exhibitbox 中英一致。' + HINT],
  ['风险压力测试', '你是 BlackRock 亚太科技组合风险经理。审 ch10 + ch11。(1) 基准65%+乐观15%+下行20%是否=100%，是否缺情景（如仅三档）；(2) 最大回撤 -25% 是否来自 2018/2022 两轮回撤统计；(3) BIS 管制风险是否建模 概率×冲击；(4) 3因子同时发生的联合概率是否<5%；(5) 前3大标的集中度是否>50%、日均成交额是否>仓位10x；(6) 表11-1触发条件是否有KRI阈值。' + HINT],
  ['合规来源治理', '你是 SEC/FCA+中金合规联合审查。(1) claim_audit 的 C/D 级主张是否未出现在 ch08/ch11 估值或核心数字中（命中且无 BLOCK=S）；(2) 附录A 20条来源 S-ID 是否在正文首次引用处标注；(3) ch03/04 HBM 容量/ASP 是否都有 S-ID（仅写行业调研综合=C级=BLOCK）；(4) ch01/11 「目标回报+25-40%」是否符合 BLOCK 区间化声明（ch08 145行）；(5) 附录D是否遗漏香港《操守准则》第16条的发布人身份声明；(6) 2026-06-23 研报日期与数据截止日是否在首页/脚注统一披露。' + HINT],
  ['逆向看空', '你是 S3 Partners 空头分析师。找所有多头一厢情愿。(1) DDR5 涨价 8-10 季（历史平均4-6季）3条理由是否有 L1/L2 支持；(2) 长存290L/长鑫15nm 是否仅 L4 无 L1/L2 交叉；(3) >5亿 AI 先进封装收入是否有任意 L1 分拆披露；(4) 澜起18%核心权重 CXL 2027 20亿收入是否 L1 指引或 Wind 中值；(5) 2026E 全链净利 42% 增速的 capex 增速差证据是否完整；(6) 全部乐观假设失败的 stripped-down 结论（仅保留L1/L2支持）。' + HINT],
]

phase('审查并行（6视角）')

// Call 6 reviewers in parallel. Don't pass complex schema objects to avoid TS parser confusion.
var raw = await parallel(ROLES.map(function (r) {
  return function () {
    return agent(r[1], {
      label: '审查-' + r[0],
      phase: '审查并行（6视角）',
      model: 'opus',
      effort: 'max',
    })
  }
}))

var R = raw.filter(Boolean)
log('Phase1 done: ' + R.length + ' reviewers returned')

phase('对抗校验与优先级')

var flat = []
R.forEach(function (r) {
  // r is returned text; agent() without schema returns string. Try JSON.parse.
  var obj = r
  if (typeof r === 'string') {
    try { obj = JSON.parse(r.replace(/```json/g,'').replace(/```/g,'').trim()) } catch (e) { obj = { reviewer: 'parse-fail', findings: [] } }
  }
  (obj.findings || []).forEach(function (f) {
    f._reviewer = obj.reviewer
    f._grade = obj.overall_grade
    flat.push(f)
  })
})

var REVIEWER_STATS = R.map(function (r) {
  var obj = r
  if (typeof r === 'string') { try { obj = JSON.parse(r.replace(/```json/g,'').replace(/```/g,'').trim()) } catch (e) { obj = {} } }
  return {
    reviewer: obj.reviewer || 'unknown',
    grade: obj.overall_grade || 'N/A',
    S: obj.s_level || 0,
    A: obj.a_level || 0,
    B: obj.b_level || 0,
    top5: obj.top5_priority || [],
  }
})

var ADVERSARIAL_PROMPT =
  '你是对抗性评审员。以下是 6 位投行 reviewer 的全部 findings（共 ' + flat.length + ' 条）：\n' +
  JSON.stringify(flat.slice(0, 90), null, 2) + '\n\n' +
  '任务：(1) 对每条 S/A 级问题，判定属实 confirmed=true 或 误判=false（reviewer 未读全文/误解/verifier已门控）；(2) 属实的评级修正建议；(3) 合并重复问题给 canonical id；(4) B 级自动保留不refute。\n' +
  '输出 JSON：字段 adversarial_checked(数组) 每元素= canonical_id, original_ids(数组), file, severity, confirmed(boolean), severity_correction(string), root_cause, merge_note。再加 unique_s_count, unique_a_count, dismissed_count, merged_groups(数组)。'

var SYNTHESIS_PROMPT =
  '你是研究总监。6位 reviewer 投票汇总：\n' + JSON.stringify(REVIEWER_STATS, null, 2) + '\n' +
  '全部问题（可能重复）：\n' + JSON.stringify(flat.slice(0, 90).map(function (f) { return { severity:f.severity, title:f.title, file:f.file, reviewer:f._reviewer, rec:f.recommendation } }), null, 2) + '\n\n' +
  '输出 JSON：字段 global_recommendation(PUBLISH|PUBLISH_WITH_A_FIXES|CONDITIONAL_PASS|REJECT_NEEDS_REWRITE), one_line_executive_summary, reviewer_votes(透传数组), must_fix(Top 10, 每项 id/severity/title/file/estimated_fix_minutes/dependencies(数组)/affected_pages), should_fix(Top 15, 同结构), nice_to_have(数组, 同结构), total_estimated_work_hours(number), estimated_pdf_pages_touched。'

var adversarial = await agent(ADVERSARIAL_PROMPT, {
  label: '对抗校验-去重评级',
  phase: '对抗校验与优先级',
  model: 'opus',
  effort: 'xhigh',
})
var priorities = await agent(SYNTHESIS_PROMPT, {
  label: '优先级合成-MUST/SHOULD/NICE',
  phase: '对抗校验与优先级',
  model: 'opus',
  effort: 'xhigh',
})

phase('文档专家改进')

var FLAT_JS = JSON.stringify(flat.slice(0, 80), null, 2)
var PRIO_JS = typeof priorities === 'string' ? priorities : JSON.stringify(priorities, null, 2)
var ADVE_JS = typeof adversarial === 'string' ? adversarial : JSON.stringify(adversarial, null, 2)

var LATEX_PROMPT =
  '你是 Goldman Sachs Research 文档团队 Lead LaTeX 工程师。根据投行 reviewer 的问题与优先级，输出可直接 Edit 工具消费的修改建议。\n\n' +
  '所有 findings:\n' + FLAT_JS + '\n\n' +
  '优先级合成:\n' + PRIO_JS + '\n\n' +
  '对抗校验:\n' + ADVE_JS + '\n\n' +
  '输出 JSON：\n' +
  '- edits (数组) 每项: id, file, line_hint, old_string, new_string, addresses_issue_ids(数组), rationale, risk_level(safe|low|medium|high)\n' +
  '- batch_order (id数组，推荐修改顺序)\n' +
  '- post_fix_actions (数组：重跑 verifier/refresh checksums 等动作及触发条件)\n' +
  '- new_exhibits_needed (数组：需新增的图表清单，给出文件名+标题+数据来源+类型)\n' +
  '- total_edits, files_touched, compile_check_required(boolean)\n' +
  'old_string 必须逐字可被 Edit 工具匹配（含空格、换行符）。不要虚构不存在的行号。无法精确定位的给出前后上下文作为锚点。'

var NARRATIVE_PROMPT =
  '你是 Morgan Stanley 研究叙事架构师。不改数字，仅改结构和文字组织建议。\n\n' +
  'Reviewer 摘要：\n' + JSON.stringify(REVIEWER_STATS, null, 2) + '\n' +
  '问题列表（精简）：\n' + JSON.stringify(flat.slice(0, 80).map(function (f) { return f._reviewer + '/' + f.severity + ': ' + f.title + ' @ ' + f.file + (f.line?':'+f.line:'') + ' — ' + (f.evidence||'').slice(0, 80) }), null, 2) + '\n\n' +
  '优先级：\n' + PRIO_JS + '\n\n' +
  '输出 JSON：\n' +
  '- three_pillars_proposal：pillar_1/2/3（每条含文字+ch01首次亮相方式+ch02展开方式+ch11量化落地方式）、evidence_map（支柱→支撑章节）、alignment_schedule（ch01/ch02/ch11三处精确重复的措辞）\n' +
  '- per_chapter_rewrite（数组，每章: chapter, weaknesses(数组3条), gs_5_stage_blueprint(BLUF/3pillars/supporting/counterview/implication 五段式建议), reorder_map（哪几段移到哪））\n' +
  '- pre_post_templates：table_preamble(模板80-120字字数要求) / table_implication(150-220字) / chapter_opening(投资问题段模板120-180字)\n' +
  '- glossary_required（数组，每项 term/zh/en/first_occurrence(chapter, approx location)）\n' +
  '- ch01_ic_gs_template：title + bullet_sections（对象含 current_positioning / target_return / upside_drivers_3 / downside_risks_2 / core_trades_3 / catalyst_calendar_summary，每段给出可直接粘贴进 LaTeX 的中文内容，不含公式）\n' +
  '- total_words_to_rewrite_estimate（整数，中文汉字估计）'

var latexP = agent(LATEX_PROMPT, {
  label: 'LaTeX可落地修改建议',
  phase: '文档专家改进',
  model: 'opus',
  effort: 'max',
})
var narrP = agent(NARRATIVE_PROMPT, {
  label: '叙事结构改进方案',
  phase: '文档专家改进',
  model: 'opus',
  effort: 'max',
})

var LP = await latexP
var NP = await narrP

// Roll up
var TOT_S = REVIEWER_STATS.reduce(function (a, x) { return a + x.S }, 0)
var TOT_A = REVIEWER_STATS.reduce(function (a, x) { return a + x.A }, 0)
var TOT_B = REVIEWER_STATS.reduce(function (a, x) { return a + x.B }, 0)
var GRADES = REVIEWER_STATS.map(function (x) { return x.reviewer + '=' + x.grade }).join('; ')
log('汇总: 原始问题 S=' + TOT_S + ' A=' + TOT_A + ' B=' + TOT_B + ' | ' + GRADES)

return {
  reviewers: REVIEWER_STATS,
  all_findings_flat: flat,
  adversarial: adversarial,
  priorities: priorities,
  latex_patches: LP,
  narrative_rewrite: NP,
}

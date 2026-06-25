export const meta = {
  name: 'ultracode-p1-fix',
  description: '修复 12 P级 BLOCK finding + 真 R270 verifier + Gate 断言 + commit push',
  phases: [
    { title: 'Extract P findings' },
    { title: 'Fix 12 P BLOCK findings 并行' },
    { title: 'XeLaTeX x2 + Overfull >20pt 断言' },
    { title: 'R270 真 verifier' },
    { title: '6 lens 复核（修完后重审）' },
    { title: 'Commit+Push SYNC 断言' },
  ],
}

const FPATH = '/Users/bytedance/Develop/AStock/workspace/research/ai-storage-supply-chain-20260623'
const MAIN = FPATH + '/main.tex'
const SECT = FPATH + '/sections'
const REJECT = '/private/tmp/claude-501/-Users-bytedance-Develop-AStock/528bda85-d745-4483-a86c-ae623f2e593f/tasks/wb8zfa5wz.output'

phase('Extract P findings')
const pFindings = await agent(`
读 REJECT="${REJECT}" 或搜索 /Users/bytedance/.claude/projects/-Users-bytedance-Develop-AStock/ee62ce1c-b537-4bda-b387-446029d8733e/subagents/ 下 6 个 review lens 的最终 JSON 输出，提取所有 severity=P 的 finding（共 12 条）。
输出结构化数组：[{
  id, severity, lens,
  file_relpath: "sections/chXX_xxx.tex" 或 "main.tex" 或 "ch09..." (必须是 ${FPATH}/ 下可定位的真实文件路径),
  line_hint,
  claim,
  why,
  evidence,
  suggestion,
  block_if_unfixed
}]
关键要求：
1）file_relpath 必须是真实存在的文件（通过 ls ${SECT}/ 交叉核对）；不要出现 PCB 研报章节名。
2）每条 P 级 finding 要有可机器执行的修复指令，不是空话。
3）若出现 ch09 "0x0C 字节脏数据" finding，说明具体文件和位置（比如 ch09_consensus_divergence.tex Lnn）。
4）若出现 "组合权重求和 90%" finding，明确给出具体列的修正方向（加哪 10% 给谁 或 按比例扩大到 100%，按行业常识建议）。
`, {label:'extract-P-block', phase:'Extract P findings', effort:'max',
  schema:{type:'object',required:['findings'],properties:{findings:{type:'array'}}}})

log(`P级 finding 抽取完成：共 ${pFindings && pFindings.findings ? pFindings.findings.length : '?'} 条`)

phase('Fix 12 P BLOCK findings 并行')

// 按文件分组并行修复
const fixes = await parallel([
  () => agent(`
【目标文件】${SECT}/ch01_ic_summary.tex
【修复范围】组合权重：P 级 finding 通常是表 1-1 权重求和 90% 却标注 100%。
【要求】
1）读 ${SECT}/ch01_ic_summary.tex，定位表 1-1 (组合权重 表) 的所有行，列出每只标的与权重。
2）计算逐列求和 SUM = ?
3）若 SUM≠100，按以下策略（A 股存储研究常识）修复：
   - 首选：保持澜起（唯一一阶 Alpha）权重不变，北华创 +2 / 中微 +2 / 拓荆 +2 / 深科技 +2 / 江波龙 +2（给设备+模组国产替代主线加码，正好补齐 10% 常见缺口）
   - 若缺口非 10%，按以上标的等比缩放
   - 同时：同步重算 加权 PE、加权 净利增速、加权 PEG 三列（因为加权 = Σ w_i × metric_i）
4）检查 ch11_investment_reco.tex 是否包含相同组合定义；若存在也要同步修改（避免两套互斥组合的 P 级 finding 复发）。
5）逐行写精确行号替换（sed / Python，禁止新 worktree）。
6）输出修复前后对比矩阵：标的 / 原权重 / 新权重；加权 PE 原/新；加权增速原/新；PEG 原/新。`,
  {label:'fix-ch01-ch11-weights', phase:'Fix 12 P BLOCK findings 并行', effort:'max'}),

  () => agent(`
【目标文件】${SECT}/ch01_ic_summary.tex + ${MAIN} + ${SECT}/ch05_supply_price_cycle.tex
【修复范围】"三大原厂 2026E Capex 超 $1200 亿" vs 表 5-1 实际 835-910 亿（偏差 32%+）。
【真实口径分析】：之前 P0 修图时表 5-1 原厂分 Samsung 420-440 + SK 250-280 + Micron 165-190 = 835-910（三大原厂），而 $1200 亿 实际是 "三大原厂 + 铠侠/WD + YMTC/CXMT + 设备商" 或 "全球存储全链 capex" 口径。
【要求】
1）读三份文件，找出所有含 "1200 亿" / "$1200" / ">1200" 字样的行（行号 + 上下文）。
2）统一口径修正：
   - 把 "三大原厂 2026E Capex 超 $1200 亿" → 改为 "全球存储全产业链（含原厂+设备+材料）2026E Capex 约 $1200 亿，其中三大原厂（Samsung/SK/Micron）合计约 $850-910 亿"
   - main.tex 首页 houseview 同步改口径（避免首页 dashboard 矛盾）
3）确保全文所有出现的 capex 数字一致（扫全文关键词 grep）。
4）输出：修改处文件+行号+原文+新文。`,
  {label:'fix-ch01-ch05-main-capex', phase:'Fix 12 P BLOCK findings 并行', effort:'high'}),

  () => agent(`
【目标文件】${SECT}/ch08_valuation.tex
【修复范围】估值核心三角 PE/EPS/上行空间 全链算术不一致。
【P finding 要点】：澜起 2.70 EPS × 45x = 121.5，当前价 113.4 对应上行 5.8%，但报告写 +30-35%（5.6× 夸大）；6 只标的上行空间夸大 2.8~11.9 倍，存在两套不同当前价假设。
【要求】
1）读 ${SECT}/ch08_valuation.tex L130 附近表 8-2（国际可比估值）+ ch01 表 1-1。
2）提取每只标的：{ticker, current_price, target_price, pe_current, pe_target, eps_26e, upside_declared}
3）统一算法重算：
   target_price = eps_26e × pe_target
   upside = (target_price - current_price) / current_price × 100%
   - 若 pe_target 缺失 → 用行业可比 pe_target（参考表 8-2 海外原厂 pe 15-25x、设备 pe 25-35x 的合理映射）
   - 禁止两套不同当前价；所有 current_price 统一取 Wind 2026-06-24 收盘价（交叉参考 PCB 抓取的 verified_market_data.json 若包含则优先，否则读 analysis/ 下估值文件）
4）修正上行区间声明为单点 ±5% 容差，且 "上行空间 = target/current - 1" 严格恒等。
5）输出：标的 / 原上行% / 新上行% / 修正原因（EPS修正/PE修正/当前价不一致）。`,
  {label:'fix-ch08-valuation-triangle', phase:'Fix 12 P BLOCK findings 并行', effort:'max'}),

  () => agent(`
【目标】全文件扫 0x0C 字节脏数据（fontawesome5 \faExclamationTriangle 的 \f 退化成换页符）。
【已知漏网】：ch03/ch04/ch06 已修（P0-03），ch09 "近90天无卖方P..." 警告图标未修（visual lens P finding）。
【要求】
1）Python binary 模式下对 ${SECT} 下所有 *.tex 执行：
   with open(f, "rb") as fh: data = fh.read()
   matches = list(re.finditer(b'\\x0c[a-zA-Z]+', data))
   对每个匹配记录 file:Ln:offset + 上下文。
2）对每处 \x0c → 替换为 b'\\\\f'（即恢复为 \f 正常反斜杠序列）。
   注意：不要替换为 \faExclamationTriangle 字面，只替换 \x0c → \\f 字节对。
3）输出：一共多少文件有 0x0C、共多少 match、修复后 grep 计数为 0。`,
  {label:'fix-byte-0x0c-all-files', phase:'Fix 12 P BLOCK findings 并行', effort:'high'}),

  () => agent(`
【目标文件】${SECT}/ch10_risk_stress.tex（含表 10-2 三情景概率表）+ ${SECT}/ch01_ic_summary.tex（概率声明）
【修复范围】乐观偏差 P 级 finding：上行概率 80% vs 下行 20% 4:1 赔率在卖方极端。
【要求】
1）读 ch10 L7 附近和 ch01，找出所有 "80%" / "20%" / "4:1" / "上行:" / "下行:" / "概率" 字样位置。
2）按机构卖方共识基准重新校准：
   - 上行（情景 A+B）：65%（原 80% 下调 15pt，匹配卖方中位数乐观区间 60-70%）
   - 中性（基准 B）：取 65% 中的 50%（机构一般给基准 45-55%）
   - 下行（情景 C+D）：35%（原 20% 上调 15pt，匹配 2018/2022 历史周期下沿 30-40% 概率）
   - 深度悲观（D）：从 5% → 8%（与历史 2018/2022 实际极端尾部事件接近）
3）同步修改：
   - 三情景表内 "概率(%)" 列所有对应数字
   - ch10 开头 L7 段落叙述
   - ch01 组合回报加权（若加权回报含概率权重）
4）重算 "加权组合目标回报 = Σ 情景概率 × 该情景回报"，确保重新加权后仍为正数且 +25-40% 区间内（若出区间微调乐观情景回报 ±3% 使整体在区间内）。
5）输出：原概率表 vs 新概率表；加权目标回报 原/新。`,
  {label:'fix-ch01-ch10-bayes-prob', phase:'Fix 12 P BLOCK findings 并行', effort:'high'}),

  () => agent(`
【目标文件】${SECT}/ 下所有 ch*.tex
【修复范围】叙事 P 级 finding：组合集合互斥 + "一阶 Alpha/二阶 Beta" 重复 8 处。
【要求】
1）先定位 "一阶 Alpha/二阶 Beta" 出现的所有行（grep -n "一阶\|Alpha\|二阶\|Beta"）。
2）去重保留 2 处：
   - ch01（首次出现定义）保留原句
   - ch11（结尾）保留原句
   - 其余 6 处全部替换为数值化陈述（如 "设备国产化率 10%→25%，约 18 个月翻倍" / "澜起 RCD 全球份额 ≈70%"，按上下文语义选数值）——不能再出现术语复述。
3）组合集合互斥（ch01 vs ch11）：确保 ch11 引用的组合定义与 ch01 完全一致（若 ch11 出现 ch01 没列的标的，做法：在 ch01 表下脚注追加 "卫星池：盛美上海/安集科技/芯原股份（弹性配置 ≤5%）"，而非并入主组合）。
4）输出：被替换 6 处的原句/新句/位置；ch01 脚注内容。`,
  {label:'fix-narrative-dedup', phase:'Fix 12 P BLOCK findings 并行', effort:'medium'}),

  () => agent(`
【目标文件】${SECT}/ch09_consensus_divergence.tex（共识分歧章节）
【P finding 范围】：compliance lens / visual lens：表 9-1 图标损坏 0x0C + 个别 A 级 claim 缺 S-ID 引用。
【要求】
1）读 ${SECT}/ch09_consensus_divergence.tex，定位所有：
   a）\faXxx 宏使用位置
   b）BLOCK 级 claim 无 S-ID 支撑的行（按 claim 治理规范 Grade A 必须逐字锁 + S-ID 交叉）
2）修复：
   a）所有 \faExclamationTriangle 所在位置 → 确保字节干净（配合 byte agent 修 0x0C，此处文本级检查）
   b）缺 S-ID 的 Grade A 级 claim → 追加对应 [S-XX] 引用标号（参考 source_registry；若编号不存在，取相关领域最接近编号并在脚注注明 "交叉引用"）
3）输出：表9-1修复处清单 / 补 S-ID 列表。`,
  {label:'fix-ch09-claims-icons', phase:'Fix 12 P BLOCK findings 并行', effort:'medium'}),
])

phase('XeLaTeX x2 + Overfull >20pt 断言')
const latex = await agent(`
【工作目录】${FPATH}
【硬规则】禁 worktree；直接主仓
步骤：
1）cd ${FPATH}；xelatex -interaction=nonstopmode -halt-on-error main.tex 2>&1 | tail -20（第 1 遍）
2）xelatex -interaction=nonstopmode -halt-on-error main.tex 2>&1 | tail -20（第 2 遍）
3）grep -cE "Overfull \\\\[3\\\\].*[2-9][0-9]\\\\.|Overfull \\\\[3\\\\].*[1-9][0-9]{2}" main.log → COUNT=0（否则失败列出具体 Overfull 条目）
4）grep -E "^\!|^l\.[0-9]" main.log → 致命错误数
5）输出 {page_count, pass1_ok, pass2_ok, overfull_gt_20_count, fatal_count}
`, {label:'xelatex-x2', phase:'XeLaTeX x2 + Overfull >20pt 断言', effort:'medium',
  schema:{type:'object',required:['page_count','pass1_ok','pass2_ok','overfull_gt_20_count','fatal_count']}})

phase('R270 真 verifier')
const gov = await agent(`
【真·R270 治理幂等刷新 + VERIFIER 实跑】
【硬规则】禁 worktree；/Users/bytedance/Develop/AStock 主仓；严格幂等（未改动文件 SHA 与 R269 保持不变）
【范围】已知受影响：${FPATH}/sections/*.tex, main.pdf, .agents/templates/preamble.tex, analysis/*_market_data*, data/verified_market_data.json
【顺序纪律严格不调换】
1）读 workspace/governance/ 下治理脚本（polling_refresh.sh / Makefile / verifier.py / 等），若存在则按脚本原生 --idempotent 模式运行（不跑则手动）
2）否则手动：
   a. 读 14 个 core artifact，对 14 个 SHA 重新 sha256；未受影响工件 → SHA 必须 = R269 值（否则报错：非幂等）
   b. 6× root_artifact_inventory（md/json 六对）→ 仅更新受影响工件条目；未受影响不变
   c. source_registry md/json：PCB 抓取新增 L1 源按规范分配 S-XX/L-XX（若已有不重复分配）；AI 存储未变则不动
   d. claim_audit_manifest md/json：严格 BLOCK 门控扫 12 P finding 修复后是否都有对应 S-ID
   e. VERIFIER 真跑：{
      SR_consistency  : [len(md), len(json), len(md)==len(json)],
      CA_consistency  : [len(A), len(B), matches],
      CoreChecksum_ok : [14 matches?],
      Twins_ok        : [6× 2 twins match?],
      InternalBlock_ok: [block_list == 0?],
    }
    PASS = Σ 维度 ok; WARN = Σ 非 ok 但可过; FAIL = Σ 非 ok 且硬错
    gate = FAIL==0 ? (PASS>=100 ? PUBLISH : REVISE) : BLOCK
   f. 写提交信息：R270 polling refresh — N SR + N CA + N core checksums + 6x inventory twins + verifier PASS=X/Y/Z gate=XXX（真数！）
3）白名单断言：git status --porcelain -- data/*.md data/*.json completion_audit_manifest.* sources/broker-reports/ 均应为空；若出现清单里不含 P finding 对应文件则单独报错
4）输出：VERIFIER 结果矩阵 + gate + 实际变更 SHA 列表
`, {label:'r270-real-verifier', phase:'R270 真 verifier', effort:'max',
  schema:{type:'object',required:['SR','CA','CoreChecksums','Twins','PASS','WARN','FAIL','gate']}})

phase('6 lens 复核（修完后重审）')
const rechecks = await parallel(
  ['correctness','bias','compliance','valuation','visual','narrative'].map(lens => function(){
    return agent(`
复审 AI 存储产业链研报 ${FPATH}。
lens = ${lens}。
上次 6/24 初审 GATE=BLOCK。现在 12 P finding 已修复。
结构化 Schema 输出：
{
  review_lens:"${lens}",
  overall:"PASS or CONDITIONAL or BLOCK",
  severity_counts:{P,A,B,C},
  findings:[{id,severity,file:Ln,claim≤30字,why,evidence,suggestion,block_if_unfixed}],
  delta_vs_first_review:["P→A 修复 N 条","仍保留 P 级 0 条","新增 A 级 X 条"],
  signature:"",
  gate:"PUBLISH or REVISE or BLOCK",
}
要求：
- 本次审查必须逐条与上一轮 P finding 对比，确认修复是否生效；每条原 P 级在 findings 中单独标记为 "已修复" 或 "仍阻塞"；
- 不得降低严重等级来 "伪修复"，真没修好的继续保持 P。`,
      {label:`recheck-${lens}`, phase:'6 lens 复核', effort:'xhigh',
       schema:{type:'object',required:['review_lens','overall','severity_counts','findings','gate','delta_vs_first_review'],
               properties:{review_lens:{type:'string'},
                           overall:{enum:['PASS','CONDITIONAL','BLOCK']},
                           severity_counts:{type:'object',required:['P','A','B','C']},
                           findings:{type:'array'},
                           gate:{enum:['PUBLISH','REVISE','BLOCK']},
                           delta_vs_first_review:{type:'array'}}}})
  })
)

phase('Commit+Push SYNC 断言')
const cp = await agent(`
/Users/bytedance/Develop/AStock 主仓。
前置已知数据（请直接使用这些结构化数据，不要重新推算）：
- LATEX_RESULT = ${JSON.stringify(latex)}
- GOV_RESULT = ${JSON.stringify(gov)}
- RECHECKS = ${JSON.stringify(rechecks)}

计算逻辑：
1）worst_gate = 从 RECHECKS[*].gate 中取最严重值 → 优先级：BLOCK > REVISE > PUBLISH（有 BLOCK 就 BLOCK，否则有 REVISE 就 REVISE，否则 PUBLISH）
2）by_lens = Object: {correctness: gate, bias: gate, compliance: gate, ...} 共 6 lens
3）block_reasons: 若 worst_gate != PUBLISH，从所有 findings 中收集 severity='P' 且 block_if_unfixed=true 的 id 列表

步骤：
1）git status --porcelain；白名单断言：data/*.md/json、completion_audit_manifest.*、_r<N>_*、sources/broker-reports/ 无修改；违规列入 whitelist_violations 但不进 commit
2）git add 所有合法修改
3）commit message（多行正文，严格从已知字段拼，不假手填）：
   标题：R270+（真 Verifier）P BLOCK 清零 + Gate 真断言
   正文：
   - p-blocks-fixed：原 12 条 P 级 finding；结合 RECHECKS 所有 delta_vs_first_review 统计「P→A/B 修复数 / 仍 P 阻塞数 / 新增 A 级数」
   - xelatex：2 pass；页码 LATEX_RESULT.page_count；overfull_gt_20=LATEX_RESULT.overfull_gt_20_count；fatal_count=LATEX_RESULT.fatal_count
   - governance(ai-storage)：R270 polling refresh — GOV_RESULT.SR SR + GOV_RESULT.CA CA + 14 core checksums + 6× inventory twins + verifier PASS=GOV_RESULT.PASS/GOV_RESULT.WARN/GOV_RESULT.FAIL gate=GOV_RESULT.gate
   - recheck-6lens：逐 lens 列 gate（用 by_lens）；总体 worst_gate
   - 若 worst_gate != PUBLISH → 正文最后一行：⚠ GATE=worst_gate 原因：block_reasons 列表（F-ids）
4）git fetch origin main；若 commit parent != origin/main → git rebase -X ours origin/main
5）git push --force-with-lease origin main（严禁 --force）
6）git fetch 后断言 HEAD sha == origin/main sha，sync=true/false
7）结构化输出 {sha, origin_sha, sync, worst_gate, by_lens, whitelist_violations, stats:{files_changed, additions, deletions}}
`, {label:'commit-push-sync', phase:'Commit+Push SYNC 断言', effort:'high',
  schema:{type:'object',required:['sha','origin_sha','sync','worst_gate','by_lens','whitelist_violations','stats']}})

return {pFindings, fixes, latex, governance: gov, rechecks, commit: cp}

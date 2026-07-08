#!/usr/bin/env python3
"""
AIDC 产业链研究 — 季度证据刷新脚本

用途:
    自动检测字段证据矩阵的变化，支持季度财报后和事件驱动的证据刷新流程。
    对比新旧矩阵，识别代理字段升级机会，评估观察名单公司升级条件。

用法:
    python3 refresh_evidence_quarterly.py \
        --case-dir /path/to/aidc-supply-chain-20260630 \
        --refresh-type quarterly \
        --new-sources /path/to/new_sources_manifest.json \
        --output-dir /path/to/output

输入:
    - 当前字段证据矩阵 (field_evidence_completion_*.json)
    - 残余代理字段审计 (residual_proxy_field_audit_*.json)
    - 观察名单触发器 (watchlist_valuation_triggers.json)
    - 新来源清单 (new_sources_manifest.json, 可选)

输出:
    - 更新后的字段证据矩阵
    - 证据变化日志 (evidence_refresh_delta_*.json)
    - 代理字段升级建议 (proxy_upgrade_candidates_*.json)
    - 观察名单升级评估 (watchlist_upgrade_assessment_*.json)
    - 刷新执行摘要 (refresh_summary_*.md)
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict


# ============================================================================
# 数据结构定义
# ============================================================================

@dataclass
class FieldEvidence:
    """单个字段的证据状态"""
    status: str  # direct, proxy, broker_indirect, demand_anchor, etc.
    evidence: str
    raw_snippet: str
    source: str
    score: int
    materiality: str
    valuation_consequence: str


@dataclass
class CompanyRow:
    """单家公司的字段证据行"""
    ticker: str
    company: str
    model_family: str
    publication_status: str
    target_model: bool
    watchlist_blocked: bool
    chain_blocks: List[str]
    source_file_count: int
    fields: Dict[str, FieldEvidence]


@dataclass
class FieldChange:
    """单个字段的变化记录"""
    ticker: str
    company: str
    field_name: str
    field_label: str
    old_status: str
    new_status: str
    old_source: str
    new_source: str
    change_type: str  # status_upgrade, evidence_update, new_evidence, source_exhausted
    confidence: float  # 0.0 - 1.0
    reason: str


@dataclass
class ProxyUpgradeCandidate:
    """代理字段升级候选"""
    ticker: str
    company: str
    field_name: str
    field_label: str
    current_status: str
    upgrade_evidence_found: bool
    new_evidence_source: str
    new_evidence_snippet: str
    confidence_score: float
    recommended_action: str  # upgrade_to_direct, keep_proxy, more_research_needed
    reason: str


@dataclass
class WatchlistUpgradeAssessment:
    """观察名单升级评估"""
    ticker: str
    company: str
    triggers_checked: Dict[str, bool]  # trigger_id -> satisfied
    triggers_satisfied_count: int
    triggers_total: int
    comprehensive_gap_score_before: float
    comprehensive_gap_score_after: float
    minimum_upgrade_combination_satisfied: bool
    recommendation: str  # upgrade, maintain, downgrade
    reason: str
    requires_R1_review: bool


@dataclass
class RefreshResult:
    """刷新结果汇总"""
    refresh_id: str
    refresh_type: str  # quarterly, event_driven, manual
    refresh_date: str
    case_id: str
    baseline_date: str
    total_companies: int
    total_fields: int
    changes: List[FieldChange] = field(default_factory=list)
    proxy_upgrade_candidates: List[ProxyUpgradeCandidate] = field(default_factory=list)
    watchlist_assessments: List[WatchlistUpgradeAssessment] = field(default_factory=list)
    new_sources_archived: int = 0
    requires_R0_review: bool = False
    requires_R1_review: bool = False
    R0_review_reason: str = ""
    R1_review_reason: str = ""
    summary_notes: List[str] = field(default_factory=list)


# ============================================================================
# 核心刷新引擎
# ============================================================================

class EvidenceRefreshEngine:
    """字段证据刷新引擎"""

    # 字段名称映射 (英文 key → 中文标签)
    FIELD_LABELS = {
        "revenue_exposure": "AIDC收入/产品暴露",
        "customer_or_platform": "客户/平台",
        "order_or_backlog": "订单/在手/出货",
        "capacity_or_certification": "产能/认证",
        "asp_or_price_proxy": "ASP/价格代理",
        "utilization_or_yield": "利用率/良率/爬坡",
        "margin_impact": "毛利率/盈利影响",
    }

    # 代理字段升级关键词 (在新来源中搜索这些模式)
    UPGRADE_KEYWORDS = {
        "capacity_or_certification": [
            r"产能.*?(\d+\s*(?:万|亿|MW|GW|万只|万条))",
            r"利用率.*?(\d+\s*%)",
            r"稼动率.*?(\d+\s*%)",
            r"良率.*?(\d+\s*%)",
            r"认证.*?(?:通过|获得|取得)",
            r"投产.*?(?:项目|产线|产能)",
            r"产能.*?(?:扩张|扩建|新增|释放)",
            r"上架率.*?(\d+\s*%)",
            r"机柜.*?(\d+\s*(?:个|万))",
        ],
        "utilization_or_yield": [
            r"利用率.*?(\d+\s*%)",
            r"稼动率.*?(\d+\s*%)",
            r"良率.*?(\d+\s*%)",
            r"产能.*?爬坡",
            r"产能.*?释放",
            r"满产",
            r"开工率.*?(\d+\s*%)",
            r"PUE.*?(\d+\.?\d*)",
        ],
        "revenue_exposure": [
            r"(?:AI|人工智能|算力|数据中心).*?收入.*?(\d+\s*(?:万|亿))",
            r"(?:光模块|液冷|UPS|电源).*?营收.*?(\d+\s*(?:万|亿))",
        ],
        "order_or_backlog": [
            r"在手订单.*?(\d+\s*(?:万|亿))",
            r"中标.*?(\d+\s*(?:万|亿))",
            r"合同.*?(\d+\s*(?:万|亿))",
            r"订单.*?(\d+\s*(?:万|亿))",
        ],
        "asp_or_price_proxy": [
            r"(?:ASP|单价|价格).*?(?:上涨|下降|提升|降低|同比)",
            r"毛利率.*?(\d+\s*%)",
        ],
        "margin_impact": [
            r"毛利率.*?(\d+\s*%)",
            r"净利率.*?(\d+\s*%)",
            r"盈利.*?(?:改善|恶化|提升|下降)",
        ],
        "customer_or_platform": [
            r"(?:客户|认证).*?(?:字节|腾讯|阿里|百度|京东|美团|移动|电信|联通|华为|浪潮|中科曙光)",
            r"(?:通过|获得).*?认证",
        ],
    }

    def __init__(self, case_dir: Path, output_dir: Optional[Path] = None):
        self.case_dir = Path(case_dir)
        self.output_dir = Path(output_dir) if output_dir else self.case_dir / "improvements"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 数据目录
        self.data_dir = self.case_dir / "data"
        self.analysis_dir = self.case_dir / "analysis"
        self.sources_dir = self.case_dir / "sources"

        # 刷新状态
        self.current_matrix: Optional[Dict] = None
        self.residual_proxy_audit: Optional[Dict] = None
        self.watchlist_triggers: Optional[Dict] = None
        self.refresh_result: Optional[RefreshResult] = None

    def load_current_state(self) -> None:
        """加载当前字段证据状态"""

        # 加载最新的字段证据矩阵
        matrix_files = sorted(self.data_dir.glob("field_evidence_completion_*.json"))
        if not matrix_files:
            raise FileNotFoundError("未找到字段证据完成矩阵文件")
        latest_matrix = matrix_files[-1]

        print(f"[INFO] 加载字段证据矩阵: {latest_matrix.name}")
        with open(latest_matrix, "r", encoding="utf-8") as f:
            self.current_matrix = json.load(f)

        # 加载残余代理字段审计
        proxy_files = sorted(self.data_dir.glob("residual_proxy_field_audit_*.json"))
        if proxy_files:
            with open(proxy_files[-1], "r", encoding="utf-8") as f:
                self.residual_proxy_audit = json.load(f)
            print(f"[INFO] 加载残余代理字段审计: {proxy_files[-1].name}")
        else:
            print("[WARN] 未找到残余代理字段审计文件")

        # 加载观察名单触发器
        watchlist_file = self.case_dir / "improvements" / "watchlist_valuation_triggers.json"
        if watchlist_file.exists():
            with open(watchlist_file, "r", encoding="utf-8") as f:
                self.watchlist_triggers = json.load(f)
            print(f"[INFO] 加载观察名单触发器: {watchlist_file.name}")
        else:
            print("[WARN] 未找到观察名单触发器文件")

        # 打印当前状态摘要
        if self.current_matrix:
            meta = self.current_matrix.get("metadata", {})
            status_counts = meta.get("status_counts", {})
            print(f"[INFO] 当前基线: {meta.get('candidate_rows', '?')} 家公司, "
                  f"{meta.get('total_field_cells', '?')} 个字段")
            print(f"[INFO] 状态分布: {json.dumps(status_counts, ensure_ascii=False)}")

    def detect_field_changes(self, new_evidence: Dict[str, Dict]) -> List[FieldChange]:
        """
        检测字段证据变化

        参数:
            new_evidence: 新证据字典 {ticker: {field_name: FieldEvidence}}

        返回:
            变化列表
        """
        changes = []

        if not self.current_matrix:
            return changes

        for row in self.current_matrix.get("rows", []):
            ticker = row.get("ticker")
            company = row.get("company")

            if ticker not in new_evidence:
                continue

            for field_name, current_field in row.get("fields", {}).items():
                if field_name not in new_evidence.get(ticker, {}):
                    continue

                new_field = new_evidence[ticker][field_name]
                current_status = current_field.get("status", "")
                new_status = new_field.status

                # 检测状态变化
                if current_status != new_status:
                    change = FieldChange(
                        ticker=ticker,
                        company=company,
                        field_name=field_name,
                        field_label=self.FIELD_LABELS.get(field_name, field_name),
                        old_status=current_status,
                        new_status=new_status,
                        old_source=current_field.get("source", ""),
                        new_source=new_field.source,
                        change_type=self._classify_change(current_status, new_status),
                        confidence=self._calculate_confidence(current_field, new_field),
                        reason=f"状态从 {current_status} 变为 {new_status}"
                    )
                    changes.append(change)

                # 检测证据更新 (即使状态不变)
                elif (current_field.get("source", "") != new_field.source or
                      current_field.get("raw_snippet", "") != new_field.raw_snippet):
                    change = FieldChange(
                        ticker=ticker,
                        company=company,
                        field_name=field_name,
                        field_label=self.FIELD_LABELS.get(field_name, field_name),
                        old_status=current_status,
                        new_status=new_status,
                        old_source=current_field.get("source", ""),
                        new_source=new_field.source,
                        change_type="evidence_update",
                        confidence=0.9,
                        reason="证据来源或片段更新"
                    )
                    changes.append(change)

        return changes

    def check_proxy_upgrade_opportunities(self, new_sources_text: Dict[str, List[str]]) -> List[ProxyUpgradeCandidate]:
        """
        检查代理字段升级机会

        参数:
            new_sources_text: 新来源文本 {ticker: [source_text_1, source_text_2, ...]}

        返回:
            升级候选列表
        """
        candidates = []

        if not self.residual_proxy_audit:
            return candidates

        for proxy_row in self.residual_proxy_audit.get("rows", []):
            ticker = proxy_row.get("ticker")
            company = proxy_row.get("company")
            field_name = proxy_row.get("field")
            field_label = proxy_row.get("field_label", field_name)
            current_status = proxy_row.get("status", "proxy")

            # 搜索该公司的新来源文本
            company_texts = new_sources_text.get(ticker, [])
            if not company_texts:
                candidates.append(ProxyUpgradeCandidate(
                    ticker=ticker,
                    company=company,
                    field_name=field_name,
                    field_label=field_label,
                    current_status=current_status,
                    upgrade_evidence_found=False,
                    new_evidence_source="",
                    new_evidence_snippet="",
                    confidence_score=0.0,
                    recommended_action="keep_proxy",
                    reason="无新来源可供检查"
                ))
                continue

            # 在新来源中搜索升级关键词
            best_match = None
            best_confidence = 0.0
            best_source = ""

            keywords = self.UPGRADE_KEYWORDS.get(field_name, [])
            for text in company_texts:
                for pattern in keywords:
                    matches = re.findall(pattern, text)
                    if matches:
                        # 计算置信度: 基于匹配数量和具体性
                        match_confidence = min(0.5 + len(matches) * 0.15, 0.95)
                        if match_confidence > best_confidence:
                            best_confidence = match_confidence
                            # 提取匹配上下文
                            for match in re.finditer(pattern, text):
                                start = max(0, match.start() - 50)
                                end = min(len(text), match.end() + 50)
                                best_match = text[start:end].strip()
                                break

            # 评估升级建议
            if best_confidence >= 0.7:
                action = "upgrade_to_direct"
                reason = f"在新来源中发现直接证据 (置信度: {best_confidence:.0%})"
            elif best_confidence >= 0.4:
                action = "more_research_needed"
                reason = f"发现部分证据但不足以直接升级 (置信度: {best_confidence:.0%})"
            else:
                action = "keep_proxy"
                reason = f"新来源中未发现足够的直接证据 (置信度: {best_confidence:.0%})"

            candidates.append(ProxyUpgradeCandidate(
                ticker=ticker,
                company=company,
                field_name=field_name,
                field_label=field_label,
                current_status=current_status,
                upgrade_evidence_found=best_confidence >= 0.4,
                new_evidence_source=best_source,
                new_evidence_snippet=best_match or "",
                confidence_score=best_confidence,
                recommended_action=action,
                reason=reason
            ))

        return candidates

    def assess_watchlist_upgrades(self, new_data: Dict[str, Dict]) -> List[WatchlistUpgradeAssessment]:
        """
        评估观察名单公司升级条件

        参数:
            new_data: 新数据 {ticker: {trigger指标数据}}

        返回:
            升级评估列表
        """
        assessments = []

        if not self.watchlist_triggers:
            return assessments

        for company_data in self.watchlist_triggers.get("companies", []):
            ticker = company_data.get("ticker")
            company = company_data.get("company")
            triggers = company_data.get("upgrade_triggers", [])
            min_upgrade = company_data.get("minimum_upgrade_combination", "")
            current_gap_score = company_data.get("comprehensive_gap_score", 0)

            # 检查每个触发器
            triggers_checked = {}
            satisfied_count = 0
            company_new_data = new_data.get(ticker, {})

            for trigger in triggers:
                trigger_id = trigger.get("id")
                condition = trigger.get("condition", "")
                threshold = trigger.get("quantitative_threshold", "")

                # 检查新数据是否满足触发器
                satisfied = self._check_trigger_satisfied(trigger, company_new_data)
                triggers_checked[trigger_id] = satisfied
                if satisfied:
                    satisfied_count += 1

            # 检查最小升级组合是否满足
            min_combo_satisfied = self._check_minimum_upgrade_combination(
                min_upgrade, triggers_checked, company_new_data
            )

            # 计算新的差距评分 (满足的触发器越多，差距越小)
            total_triggers = len(triggers)
            gap_reduction = satisfied_count * 0.8 if total_triggers > 0 else 0
            new_gap_score = max(0, current_gap_score - gap_reduction)

            # 生成建议
            if min_combo_satisfied or any(triggers_checked.get(f"U{i}", False) for i in [3]):
                recommendation = "upgrade"
                requires_R1 = True
                reason = f"满足升级条件: {min_upgrade if min_combo_satisfied else 'U3单笔大额订单触发'}"
            elif satisfied_count >= 2:
                recommendation = "maintain_monitor"
                requires_R1 = False
                reason = f"已满足 {satisfied_count}/{total_triggers} 个触发器，继续观察"
            elif satisfied_count == 0 and company_new_data.get("deteriorating", False):
                recommendation = "downgrade"
                requires_R1 = True
                reason = "经营指标恶化，建议降级评估"
            else:
                recommendation = "maintain"
                requires_R1 = False
                reason = f"仅满足 {satisfied_count}/{total_triggers} 个触发器，维持观察名单"

            assessments.append(WatchlistUpgradeAssessment(
                ticker=ticker,
                company=company,
                triggers_checked=triggers_checked,
                triggers_satisfied_count=satisfied_count,
                triggers_total=total_triggers,
                comprehensive_gap_score_before=current_gap_score,
                comprehensive_gap_score_after=new_gap_score,
                minimum_upgrade_combination_satisfied=min_combo_satisfied,
                recommendation=recommendation,
                reason=reason,
                requires_R1_review=requires_R1
            ))

        return assessments

    def run_refresh(self, refresh_type: str = "quarterly",
                    new_sources_manifest: Optional[Dict] = None,
                    new_evidence: Optional[Dict] = None,
                    new_watchlist_data: Optional[Dict] = None) -> RefreshResult:
        """
        执行完整刷新流程

        参数:
            refresh_type: 刷新类型 (quarterly, event_driven, manual)
            new_sources_manifest: 新来源清单
            new_evidence: 新证据 (手动提供或从新来源提取)
            new_watchlist_data: 观察名单公司新数据

        返回:
            刷新结果
        """
        refresh_id = f"REFRESH-{refresh_type}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        today = date.today().isoformat()

        print(f"\n{'='*60}")
        print(f"[REFRESH] 启动证据刷新")
        print(f"[REFRESH] ID: {refresh_id}")
        print(f"[REFRESH] 类型: {refresh_type}")
        print(f"[REFRESH] 日期: {today}")
        print(f"{'='*60}\n")

        # 步骤 1: 加载当前状态
        self.load_current_state()

        # 步骤 2: 准备新来源文本
        new_sources_text = self._prepare_new_sources_text(new_sources_manifest)

        # 步骤 3: 检测字段变化
        print("[STEP 1] 检测字段证据变化...")
        changes = self.detect_field_changes(new_evidence or {})
        print(f"  发现 {len(changes)} 个字段变化")

        # 步骤 4: 检查代理字段升级
        print("[STEP 2] 检查代理字段升级机会...")
        proxy_candidates = self.check_proxy_upgrade_opportunities(new_sources_text)
        upgrades = [c for c in proxy_candidates if c.recommended_action == "upgrade_to_direct"]
        print(f"  代理字段升级候选: {len(upgrades)}/{len(proxy_candidates)}")

        # 步骤 5: 评估观察名单升级
        print("[STEP 3] 评估观察名单公司升级条件...")
        watchlist_assessments = self.assess_watchlist_upgrades(new_watchlist_data or {})
        upgrade_recs = [a for a in watchlist_assessments if a.recommendation == "upgrade"]
        print(f"  观察名单升级建议: {len(upgrade_recs)}/{len(watchlist_assessments)}")

        # 步骤 6: 汇总结果
        total_changes = len(changes) + len(upgrades)
        requires_R0 = total_changes > 5
        requires_R1 = any(a.requires_R1_review for a in watchlist_assessments)

        result = RefreshResult(
            refresh_id=refresh_id,
            refresh_type=refresh_type,
            refresh_date=today,
            case_id=self.current_matrix.get("metadata", {}).get("case_id", "unknown") if self.current_matrix else "unknown",
            baseline_date=self.current_matrix.get("metadata", {}).get("run_date", "unknown") if self.current_matrix else "unknown",
            total_companies=self.current_matrix.get("metadata", {}).get("candidate_rows", 0) if self.current_matrix else 0,
            total_fields=self.current_matrix.get("metadata", {}).get("total_field_cells", 0) if self.current_matrix else 0,
            changes=changes,
            proxy_upgrade_candidates=proxy_candidates,
            watchlist_assessments=watchlist_assessments,
            new_sources_archived=len(new_sources_text) if new_sources_text else 0,
            requires_R0_review=requires_R0,
            requires_R1_review=requires_R1,
            R0_review_reason=f"字段变化总数 ({total_changes}) 超过阈值 (5)" if requires_R0 else "",
            R1_review_reason="观察名单公司满足升级条件" if requires_R1 else "",
        )

        # 步骤 7: 生成摘要
        self.refresh_result = result
        self._print_refresh_summary(result)

        # 步骤 8: 输出结果
        self._write_refresh_outputs(result)

        return result

    # ========================================================================
    # 内部辅助方法
    # ========================================================================

    def _classify_change(self, old_status: str, new_status: str) -> str:
        """分类变化类型"""
        upgrade_path = {
            ("proxy", "direct"): "proxy_to_direct_upgrade",
            ("broker_indirect", "direct"): "broker_indirect_to_direct_upgrade",
            ("proxy", "broker_indirect"): "proxy_to_broker_indirect",
            ("direct", "proxy"): "direct_to_proxy_downgrade",
            ("direct", "broker_indirect"): "direct_to_broker_indirect_downgrade",
            ("direct", "source_exhausted"): "source_exhausted",
        }
        return upgrade_path.get((old_status, new_status), "status_change")

    def _calculate_confidence(self, old_field: Dict, new_field: FieldEvidence) -> float:
        """计算变化置信度"""
        # 基于来源类型和证据质量
        source_quality = {
            "annual_report": 0.95,
            "semi_annual_report": 0.90,
            "quarterly_report": 0.85,
            "ir_activity_record": 0.80,
            "official_announcement": 0.90,
            "broker_report": 0.70,
            "news": 0.50,
        }

        # 检查新来源是否为更高质量来源
        new_source = new_field.source.lower()
        for src_type, quality in source_quality.items():
            if src_type in new_source:
                return quality

        return 0.6  # 默认置信度

    def _prepare_new_sources_text(self, manifest: Optional[Dict]) -> Dict[str, List[str]]:
        """准备新来源文本"""
        if not manifest:
            return {}

        result = {}
        sources_list = manifest.get("new_sources", [])

        for source_entry in sources_list:
            ticker = source_entry.get("ticker")
            file_path = source_entry.get("file_path", "")
            source_type = source_entry.get("source_type", "")

            full_path = self.case_dir / file_path
            if not full_path.exists():
                print(f"  [WARN] 来源文件不存在: {full_path}")
                continue

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    text = f.read()

                if ticker not in result:
                    result[ticker] = []
                result[ticker].append(text)
            except Exception as e:
                print(f"  [ERROR] 读取来源文件失败 {full_path}: {e}")

        return result

    def _check_trigger_satisfied(self, trigger: Dict, company_data: Dict) -> bool:
        """检查单个触发器是否满足"""
        trigger_id = trigger.get("id")

        # 从新数据中查找对应指标
        if trigger_id == "U1":
            gm = company_data.get("gross_margin_qoq")
            return gm is not None and gm > 2  # 毛利率环比改善 >2pct
        elif trigger_id == "U2":
            growth = company_data.get("aidc_revenue_yoy")
            return growth is not None and growth > 50  # AIDC收入同比 >50%
        elif trigger_id == "U3":
            order = company_data.get("major_order_amount_cny")
            cert = company_data.get("major_certification")
            return (order is not None and order > 1e8) or cert is True
        elif trigger_id == "U4":
            utilization = company_data.get("utilization_rate")
            yield_rate = company_data.get("yield_rate")
            return (utilization is not None and utilization > 70) or (yield_rate is not None and yield_rate > 90)
        elif trigger_id == "U5":
            return company_data.get("broker_coverage_with_target", False)

        return False

    def _check_minimum_upgrade_combination(self, min_combo: str,
                                           triggers: Dict[str, bool],
                                           company_data: Dict) -> bool:
        """检查最小升级组合是否满足"""
        # 解析最小升级组合
        if "U1+U4" in min_combo:
            return triggers.get("U1", False) and triggers.get("U4", False)
        elif "U1+U2" in min_combo:
            return triggers.get("U1", False) and triggers.get("U2", False)
        elif "U3" in min_combo and "单独" in min_combo:
            return triggers.get("U3", False)

        # 默认: 至少2个触发器满足
        return sum(1 for v in triggers.values() if v) >= 2

    def _print_refresh_summary(self, result: RefreshResult) -> None:
        """打印刷新结果摘要"""
        print(f"\n{'='*60}")
        print(f"[REFRESH] 刷新完成")
        print(f"{'='*60}")
        print(f"  刷新ID: {result.refresh_id}")
        print(f"  字段变化数: {len(result.changes)}")
        print(f"  代理字段升级候选: {len(result.proxy_upgrade_candidates)}")
        print(f"    - 建议直接升级: {sum(1 for c in result.proxy_upgrade_candidates if c.recommended_action == 'upgrade_to_direct')}")
        print(f"    - 建议进一步研究: {sum(1 for c in result.proxy_upgrade_candidates if c.recommended_action == 'more_research_needed')}")
        print(f"  观察名单评估: {len(result.watchlist_assessments)}")
        print(f"    - 建议升级: {sum(1 for a in result.watchlist_assessments if a.recommendation == 'upgrade')}")
        print(f"    - 建议维持: {sum(1 for a in result.watchlist_assessments if a.recommendation == 'maintain')}")
        print(f"  新来源归档: {result.new_sources_archived}")
        print(f"  R0审查: {'需要' if result.requires_R0_review else '不需要'}")
        print(f"  R1审查: {'需要' if result.requires_R1_review else '不需要'}")
        print(f"{'='*60}\n")

    def _write_refresh_outputs(self, result: RefreshResult) -> None:
        """写出刷新结果文件"""
        date_str = result.refresh_date.replace("-", "")

        # 1. 证据变化日志
        delta_file = self.output_dir / f"evidence_refresh_delta_{date_str}.json"
        delta_data = {
            "metadata": {
                "refresh_id": result.refresh_id,
                "refresh_type": result.refresh_type,
                "refresh_date": result.refresh_date,
                "case_id": result.case_id,
                "baseline_date": result.baseline_date,
            },
            "summary": {
                "total_changes": len(result.changes),
                "proxy_upgrade_candidates": len(result.proxy_upgrade_candidates),
                "watchlist_upgrade_recommendations": sum(
                    1 for a in result.watchlist_assessments if a.recommendation == "upgrade"
                ),
                "requires_R0_review": result.requires_R0_review,
                "requires_R1_review": result.requires_R1_review,
            },
            "field_changes": [asdict(c) for c in result.changes],
            "proxy_upgrade_candidates": [asdict(c) for c in result.proxy_upgrade_candidates],
            "watchlist_assessments": [asdict(a) for a in result.watchlist_assessments],
        }
        with open(delta_file, "w", encoding="utf-8") as f:
            json.dump(delta_data, f, ensure_ascii=False, indent=2)
        print(f"[OUTPUT] 证据变化日志: {delta_file}")

        # 2. 代理字段升级建议
        proxy_file = self.output_dir / f"proxy_upgrade_candidates_{date_str}.json"
        proxy_data = {
            "metadata": {
                "refresh_id": result.refresh_id,
                "refresh_date": result.refresh_date,
            },
            "candidates": [asdict(c) for c in result.proxy_upgrade_candidates],
        }
        with open(proxy_file, "w", encoding="utf-8") as f:
            json.dump(proxy_data, f, ensure_ascii=False, indent=2)
        print(f"[OUTPUT] 代理字段升级建议: {proxy_file}")

        # 3. 观察名单升级评估
        watchlist_file = self.output_dir / f"watchlist_upgrade_assessment_{date_str}.json"
        watchlist_data = {
            "metadata": {
                "refresh_id": result.refresh_id,
                "refresh_date": result.refresh_date,
            },
            "assessments": [asdict(a) for a in result.watchlist_assessments],
        }
        with open(watchlist_file, "w", encoding="utf-8") as f:
            json.dump(watchlist_data, f, ensure_ascii=False, indent=2)
        print(f"[OUTPUT] 观察名单升级评估: {watchlist_file}")

        # 4. 刷新执行摘要 (Markdown)
        summary_file = self.output_dir / f"refresh_summary_{date_str}.md"
        summary_md = self._generate_summary_markdown(result)
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary_md)
        print(f"[OUTPUT] 刷新执行摘要: {summary_file}")

    def _generate_summary_markdown(self, result: RefreshResult) -> str:
        """生成Markdown格式的刷新摘要"""
        lines = []
        lines.append(f"# 证据刷新执行摘要")
        lines.append("")
        lines.append(f"- **刷新ID**: {result.refresh_id}")
        lines.append(f"- **刷新类型**: {result.refresh_type}")
        lines.append(f"- **刷新日期**: {result.refresh_date}")
        lines.append(f"- **案例ID**: {result.case_id}")
        lines.append(f"- **基线日期**: {result.baseline_date}")
        lines.append(f"- **公司总数**: {result.total_companies}")
        lines.append(f"- **字段总数**: {result.total_fields}")
        lines.append("")

        # 变化摘要
        lines.append("## 变化摘要")
        lines.append("")
        lines.append(f"| 指标 | 数量 |")
        lines.append(f"|------|------|")
        lines.append(f"| 字段变化 | {len(result.changes)} |")
        lines.append(f"| 代理字段升级候选 | {len(result.proxy_upgrade_candidates)} |")
        lines.append(f"| 观察名单升级建议 | {sum(1 for a in result.watchlist_assessments if a.recommendation == 'upgrade')} |")
        lines.append(f"| 新来源归档 | {result.new_sources_archived} |")
        lines.append("")

        # 字段变化详情
        if result.changes:
            lines.append("## 字段变化详情")
            lines.append("")
            lines.append("| 公司 | 字段 | 变化类型 | 旧状态 | 新状态 | 置信度 |")
            lines.append("|------|------|---------|--------|--------|--------|")
            for c in result.changes:
                lines.append(
                    f"| {c.company} ({c.ticker}) | {c.field_label} | "
                    f"{c.change_type} | {c.old_status} | {c.new_status} | "
                    f"{c.confidence:.0%} |"
                )
            lines.append("")

        # 代理字段升级
        if result.proxy_upgrade_candidates:
            lines.append("## 代理字段升级候选")
            lines.append("")
            lines.append("| 公司 | 字段 | 当前状态 | 建议 | 置信度 | 原因 |")
            lines.append("|------|------|---------|------|--------|------|")
            for c in result.proxy_upgrade_candidates:
                lines.append(
                    f"| {c.company} ({c.ticker}) | {c.field_label} | "
                    f"{c.current_status} | {c.recommended_action} | "
                    f"{c.confidence_score:.0%} | {c.reason} |"
                )
            lines.append("")

        # 观察名单评估
        if result.watchlist_assessments:
            lines.append("## 观察名单升级评估")
            lines.append("")
            lines.append("| 公司 | 满足触发器 | 总触发器 | 差距评分(前) | 差距评分(后) | 建议 | R1审查 |")
            lines.append("|------|-----------|---------|-------------|-------------|------|--------|")
            for a in result.watchlist_assessments:
                lines.append(
                    f"| {a.company} ({a.ticker}) | "
                    f"{a.triggers_satisfied_count} | {a.triggers_total} | "
                    f"{a.comprehensive_gap_score_before:.1f} | "
                    f"{a.comprehensive_gap_score_after:.1f} | "
                    f"{a.recommendation} | {'是' if a.requires_R1_review else '否'} |"
                )
            lines.append("")

        # 治理审查
        lines.append("## 治理审查")
        lines.append("")
        if result.requires_R0_review:
            lines.append(f"- **R0 审查**: 需要 ({result.R0_review_reason})")
        else:
            lines.append(f"- **R0 审查**: 不需要")

        if result.requires_R1_review:
            lines.append(f"- **R1 审查**: 需要 ({result.R1_review_reason})")
        else:
            lines.append(f"- **R1 审查**: 不需要")
        lines.append("")

        # 后续步骤
        lines.append("## 后续步骤")
        lines.append("")
        lines.append("1. 审核字段变化的证据来源和分类准确性")
        lines.append("2. 评估代理字段升级建议")
        lines.append("3. 对观察名单升级建议进行 R1 审查 (如需)")
        lines.append("4. 更新字段证据完成矩阵")
        lines.append("5. 更新 field_evidence_completion_audit.md")
        lines.append("6. 更新 source_exhaustion_log.md (如有新来源)")
        lines.append("7. 运行验证器 (39 PASS / 0 FAIL)")
        lines.append("8. 运行工作流门控 (RESULT PASS)")
        lines.append("")

        return "\n".join(lines)


# ============================================================================
# CLI 入口
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="AIDC 产业链研究 — 季度证据刷新脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 季度刷新 (使用默认路径)
  python3 refresh_evidence_quarterly.py --case-dir /path/to/case

  # 事件驱动刷新 (指定新来源)
  python3 refresh_evidence_quarterly.py \\
      --case-dir /path/to/case \\
      --refresh-type event_driven \\
      --new-sources-manifest new_sources.json

  # 仅生成刷新框架 (不执行实际刷新)
  python3 refresh_evidence_quarterly.py --case-dir /path/to/case --dry-run
        """
    )

    parser.add_argument(
        "--case-dir",
        required=True,
        help="研究案例目录 (包含 data/, analysis/, sources/ 子目录)"
    )
    parser.add_argument(
        "--refresh-type",
        choices=["quarterly", "event_driven", "manual"],
        default="quarterly",
        help="刷新类型 (默认: quarterly)"
    )
    parser.add_argument(
        "--new-sources-manifest",
        help="新来源清单 JSON 文件路径"
    )
    parser.add_argument(
        "--output-dir",
        help="输出目录 (默认: case-dir/improvements)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅加载当前状态并打印摘要，不执行刷新"
    )

    args = parser.parse_args()

    # 初始化引擎
    engine = EvidenceRefreshEngine(
        case_dir=Path(args.case_dir),
        output_dir=Path(args.output_dir) if args.output_dir else None
    )

    if args.dry_run:
        print("[DRY-RUN] 加载当前状态...")
        engine.load_current_state()
        print("[DRY-RUN] 完成。未执行刷新。")
        return

    # 加载新来源清单 (可选)
    new_sources = None
    if args.new_sources_manifest:
        manifest_path = Path(args.new_sources_manifest)
        if manifest_path.exists():
            with open(manifest_path, "r", encoding="utf-8") as f:
                new_sources = json.load(f)
            print(f"[INFO] 加载新来源清单: {manifest_path}")
        else:
            print(f"[WARN] 新来源清单文件不存在: {manifest_path}")

    # 执行刷新
    result = engine.run_refresh(
        refresh_type=args.refresh_type,
        new_sources_manifest=new_sources,
    )

    # 打印退出码提示
    if result.requires_R0_review or result.requires_R1_review:
        print("\n[NOTE] 本次刷新需要治理审查，请按流程提交 R0/R1 审查。")
    else:
        print("\n[NOTE] 本次刷新无需额外治理审查。")

    print(f"[DONE] 刷新完成。输出文件位于: {engine.output_dir}")


if __name__ == "__main__":
    main()

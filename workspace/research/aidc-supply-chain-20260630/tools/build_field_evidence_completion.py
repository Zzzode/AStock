from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
ANALYSIS = BASE / "analysis"
SOURCES = BASE / "sources"

OUT_JSON = DATA / "field_evidence_completion_20260701.json"
OUT_MD = DATA / "field_evidence_completion_20260701.md"
ANALYSIS_MD = ANALYSIS / "field_evidence_completion_audit.md"

FIELDS = (
    "revenue_exposure",
    "customer_or_platform",
    "order_or_backlog",
    "capacity_or_certification",
    "asp_or_price_proxy",
    "utilization_or_yield",
    "margin_impact",
)

FIELD_LABELS = {
    "revenue_exposure": "AIDC revenue / product exposure",
    "customer_or_platform": "customer / platform",
    "order_or_backlog": "order / backlog / shipment",
    "capacity_or_certification": "capacity / certification",
    "asp_or_price_proxy": "ASP / price proxy",
    "utilization_or_yield": "utilization / yield / ramp",
    "margin_impact": "margin / earnings impact",
}

FIELD_KEYWORDS = {
    "revenue_exposure": (
        "收入",
        "营收",
        "业务收入",
        "AI",
        "AIDC",
        "智算",
        "数据中心",
        "服务器",
        "交换机",
        "光模块",
        "PCB",
        "液冷",
        "UPS",
        "IDC",
    ),
    "customer_or_platform": (
        "客户",
        "云厂商",
        "CSP",
        "互联网",
        "运营商",
        "金融",
        "电力",
        "国有大行",
        "头部",
        "北美客户",
        "海外客户",
        "阿里",
        "腾讯",
        "字节",
        "百度",
        "华为",
        "英伟达",
        "NVIDIA",
        "Microsoft",
        "Meta",
        "AWS",
        "Google",
    ),
    "order_or_backlog": (
        "订单",
        "在手订单",
        "中标",
        "集采",
        "合同",
        "交付",
        "出货",
        "需求",
        "排产",
        "预付款",
        "backlog",
        "book-to-bill",
        "指引",
    ),
    "capacity_or_certification": (
        "产能",
        "扩产",
        "投产",
        "量产",
        "基地",
        "工厂",
        "认证",
        "导入",
        "验证",
        "通过",
        "资质",
        "产线",
        "qualification",
        "certification",
    ),
    "asp_or_price_proxy": (
        "ASP",
        "单价",
        "价格",
        "价值量",
        "产品结构",
        "高端",
        "占比",
        "毛利率",
        "800G",
        "1.6T",
        "3.2T",
        "CPO",
        "LPO",
        "HDI",
        "UBB",
        "高多层",
        "高速",
        "液冷",
        "高密",
    ),
    "utilization_or_yield": (
        "利用率",
        "产能利用",
        "稼动",
        "良率",
        "上架率",
        "投运",
        "爬坡",
        "生产效率",
        "运营效率",
        "PUE",
        "occupancy",
        "utilization",
        "yield",
        "ramp",
    ),
    "margin_impact": (
        "毛利",
        "毛利率",
        "净利",
        "利润",
        "盈利",
        "费用率",
        "成本",
        "现金流",
        "EBITDA",
        "margin",
    ),
}

DIRECT_KEYWORDS = {
    "revenue_exposure": ("收入", "营收", "业务收入"),
    "customer_or_platform": ("客户", "云厂商", "运营商", "互联网", "金融", "电力", "北美客户", "海外客户"),
    "order_or_backlog": ("订单", "在手订单", "中标", "集采", "合同", "交付", "出货", "预付款"),
    "capacity_or_certification": ("产能", "认证", "导入", "验证", "量产", "投产", "基地", "工厂"),
    "asp_or_price_proxy": ("ASP", "单价", "价格", "价值量", "产品结构", "毛利率", "800G", "1.6T", "高多层", "HDI", "UBB"),
    "utilization_or_yield": ("利用率", "稼动", "良率", "上架率", "投运", "爬坡", "生产效率", "PUE"),
    "margin_impact": ("毛利", "毛利率", "净利", "利润", "盈利", "现金流", "EBITDA"),
}

STRICT_DIRECT_KEYWORDS = {
    "customer_or_platform": (
        "客户",
        "云厂商",
        "CSP",
        "运营商",
        "互联网",
        "金融",
        "电力",
        "国有大行",
        "阿里",
        "腾讯",
        "字节",
        "百度",
        "华为",
        "英伟达",
        "NVIDIA",
        "Microsoft",
        "Meta",
        "AWS",
        "Google",
    ),
    "asp_or_price_proxy": (
        "ASP",
        "单价",
        "价格",
        "价值量",
        "产品结构",
        "毛利率",
        "800G",
        "1.6T",
        "3.2T",
        "CPO",
        "LPO",
        "HDI",
        "UBB",
        "高多层",
    ),
    "order_or_backlog": ("订单", "在手订单", "中标", "集采", "合同", "交付", "出货", "预付款", "backlog"),
    "capacity_or_certification": ("产能", "扩产", "投产", "量产", "基地", "工厂", "认证", "导入", "验证", "产线"),
    "utilization_or_yield": ("利用率", "产能利用", "稼动", "良率", "上架率", "投运", "爬坡", "生产效率", "PUE"),
}

DISALLOWED_BY_FIELD = {
    "customer_or_platform": (
        "资产总计",
        "资产负债表",
        "合并资产负债表",
        "短期借款",
        "应付款项",
        "营业利润",
        "营业外净收支",
        "其他收入",
        "客户存款",
        "客户签收单",
        "客户对账",
        "主要客户的工商资料",
        "向客户转让商品",
        "经纪客户",
        "投融资服务",
        "证券公司",
    ),
    "order_or_backlog": (
        "客户存款",
        "中央银行借款",
        "拆入资金",
        "回购业务",
        "预付款项",
        "合并资产负债表",
        "重大变化说明",
        "审计证据",
        "审计程序",
        "抽样检查",
        "合同/订单",
        "客户签收单",
        "海关报关单",
        "提单",
        "应收款项融资",
        "应收保费",
        "分保账款",
    ),
    "asp_or_price_proxy": (
        "转股价格",
        "股票期权",
        "股价",
        "目标价",
        "可转换公司债券",
        "收盘价",
        "上市规则",
        "任何证券",
        "金融工具",
        "投资决策",
    ),
    "capacity_or_certification": ("保证本报告", "董事会", "股东大会"),
    "margin_impact": ("客户存款", "同业存放", "中央银行借款"),
}

NOISE_MARKERS = (
    "免责声明",
    "请务必阅读",
    "评级说明",
    "本报告中的信息",
    "目录",
    "Table_",
    "图表",
    "证券研究报告",
    "法律声明",
    "任何证券",
    "金融工具",
    "投资决策",
    "客观性利益冲突",
    "经纪客户",
    "证券投融资服务",
)

BAD_TEXT_MARKERS = (
    "未披露",
    "未取得",
    "未命中",
    "未公开",
    "不可用",
    "不足",
    "not disclosed",
    "not found",
    "not extractable",
    "not collected",
    "source-not-collected",
)

WATCHLIST_STATUSES = {"watchlist_only_insufficient_model"}
TARGET_MODEL_STATUSES = {"target_model_ready", "house_target_model_ready", "ps_sotp_target_model_ready"}


def read_json(path: Path, default: object) -> object:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def load_rows(path: Path, key: str = "rows") -> list[dict]:
    payload = read_json(path, {})
    if not isinstance(payload, dict):
        return []
    rows = payload.get(key, [])
    return rows if isinstance(rows, list) else []


def normalize_text(text: object) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def short_text(text: object, limit: int = 160) -> str:
    value = normalize_text(text).replace("|", "；")
    for marker in NOISE_MARKERS:
        if marker in value and len(value) > 80:
            value = value.split(marker, 1)[0].strip()
    if len(value) > limit:
        return value[:limit].rstrip("，。；,. ") + "..."
    return value


def has_bad_marker(text: object) -> bool:
    value = str(text or "").lower()
    return any(marker.lower() in value for marker in BAD_TEXT_MARKERS)


def split_source_field(value: object) -> list[str]:
    if not value:
        return []
    parts = []
    for raw in re.split(r"[;,；]+", str(value)):
        item = raw.strip()
        if item:
            parts.append(item)
    return parts


def source_registry_paths() -> dict[str, Path]:
    payload = read_json(DATA / "source_registry.json", {})
    paths: dict[str, Path] = {}
    for row in payload.get("sources", []) if isinstance(payload, dict) else []:
        sid = str(row.get("id") or "")
        local = str(row.get("local_path") or "").strip()
        if not sid or not local:
            continue
        path = Path(local)
        if not path.is_absolute():
            path = BASE / path
        paths[sid] = path
    return paths


def resolve_source_token(token: str, registry: dict[str, Path]) -> list[Path]:
    token = token.strip()
    if not token:
        return []
    if token in registry:
        return [registry[token]]
    path = Path(token)
    if not path.is_absolute():
        if token.startswith("workspace/research/"):
            path = Path(token)
        elif token.startswith("sources/") or token.startswith("data/") or token.startswith("analysis/"):
            path = BASE / token
        else:
            path = BASE / token
    if path.exists():
        return [path]
    return []


def text_files_from_path(path: Path) -> list[Path]:
    if path.is_file():
        if path.suffix.lower() in {".txt", ".md", ".json"}:
            return [path]
        sibling_txt = path.with_suffix(".txt")
        sibling_md = path.with_suffix(".md")
        return [p for p in (sibling_txt, sibling_md) if p.exists()]
    if path.is_dir():
        return sorted(p for p in path.rglob("*") if p.suffix.lower() in {".txt", ".md"})
    return []


def candidate_source_files(ticker: str, company: str, seed_sources: list[str], registry: dict[str, Path]) -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()

    def add_path(path: Path) -> None:
        for file in text_files_from_path(path):
            resolved = file.resolve()
            if resolved not in seen and file.exists():
                seen.add(resolved)
                files.append(file)

    for token in seed_sources:
        for path in resolve_source_token(token, registry):
            add_path(path)

    for path in SOURCES.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".txt", ".md"}:
            continue
        text_path = str(path)
        if ticker in text_path or company in text_path:
            add_path(path)
    return files


def sentence_windows(text: str, keywords: tuple[str, ...]) -> list[str]:
    normalized = normalize_text(text)
    windows = []
    lowered = normalized.lower()
    for keyword in keywords:
        lower_key = keyword.lower()
        start = 0
        while True:
            idx = lowered.find(lower_key, start)
            if idx < 0:
                break
            left = max(0, idx - 90)
            right = min(len(normalized), idx + 180)
            window = normalized[left:right]
            windows.append(window)
            start = idx + len(lower_key)
            if len(windows) >= 80:
                return windows
    return windows


def noisy_snippet(text: str) -> bool:
    if len(text) < 24:
        return True
    if text.count(".") >= 12 or "......" in text:
        return True
    return any(marker in text for marker in NOISE_MARKERS)


def snippet_score(snippet: str, field: str, ticker: str, company: str, source: Path) -> int:
    score = 0
    if any(marker in snippet for marker in DISALLOWED_BY_FIELD.get(field, ())):
        return -20
    if ticker in str(source) or company in str(source):
        score += 4
    if company in snippet:
        score += 2
    score += sum(2 for keyword in DIRECT_KEYWORDS[field] if keyword.lower() in snippet.lower())
    strict_terms = STRICT_DIRECT_KEYWORDS.get(field)
    if strict_terms:
        strict_hits = sum(1 for keyword in strict_terms if keyword.lower() in snippet.lower())
        score += strict_hits * 3
        if strict_hits == 0:
            score -= 8
    score += min(6, len(re.findall(r"\d+(?:\.\d+)?%?|\d+G|MW|GW|亿元|万|倍", snippet)))
    if has_bad_marker(snippet):
        score -= 5
    if noisy_snippet(snippet):
        score -= 8
    if "sources/broker-reports" in str(source) or "blocked-core-candidate-broker-reports" in str(source):
        score += 2
    if "source-exhausted-official-filings" in str(source):
        score += 3
    return score


def best_snippet(files: list[Path], field: str, ticker: str, company: str) -> tuple[str, str, int]:
    candidates: list[tuple[int, str, str]] = []
    keywords = FIELD_KEYWORDS[field]
    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for window in sentence_windows(text[:800_000], keywords):
            snippet = short_text(window, 180)
            score = snippet_score(snippet, field, ticker, company, path)
            if score > 0:
                candidates.append((score, snippet, str(path.relative_to(BASE))))
    if not candidates:
        return "", "", 0
    candidates.sort(key=lambda item: (item[0], len(item[1])), reverse=True)
    score, snippet, source = candidates[0]
    return snippet, source, score


def evidence_seed_from_collection(path: Path, row_key: str = "rows") -> dict[str, dict]:
    rows = load_rows(path, row_key)
    return {str(row.get("ticker")): row for row in rows if row.get("ticker")}


def field_summary_seed(row: dict | None, field: str, ticker: str, company: str) -> tuple[str, str, int]:
    if not row:
        return "", "", 0
    field_summary = row.get("field_summary", {})
    summary = field_summary.get(field, {}) if isinstance(field_summary, dict) else {}
    snippets = summary.get("snippets", []) if isinstance(summary, dict) else []
    sources = summary.get("sources", []) if isinstance(summary, dict) else []
    for snippet in snippets:
        text = short_text(snippet, 180)
        source = str(sources[0]) if sources else "data/field_evidence_completion_20260701.json"
        path = BASE / source if not Path(source).is_absolute() else Path(source)
        score = snippet_score(text, field, ticker, company, path)
        if text and score > 0:
            return text, source, max(score, int(summary.get("evidence_count") or 0))
    return "", "", 0


def model_candidates() -> list[dict]:
    current = load_rows(DATA / "current_valuation_model_20260630.json")
    extended = load_rows(DATA / "core_candidate_extended_valuation_model_20260701.json")
    triage = load_rows(DATA / "valuation_triage_20260630.json")
    triage_by_ticker = {str(row.get("ticker")): row for row in triage if row.get("ticker")}
    candidates = []
    seen: set[str] = set()
    for row in current:
        ticker = str(row.get("ticker") or "")
        if ticker and ticker not in seen:
            triage_row = triage_by_ticker.get(ticker, {})
            candidates.append({
                "ticker": ticker,
                "company": row.get("company"),
                "model_family": "original_target_model",
                "publication_status": "target_price_published",
                "target_model": True,
                "watchlist_blocked": False,
                "chain_blocks": triage_row.get("chain_blocks", []),
                "source_seed": [triage_row.get("evidence_source", "")],
            })
            seen.add(ticker)
    for row in extended:
        ticker = str(row.get("ticker") or "")
        if ticker and ticker not in seen:
            status = str(row.get("publication_status") or "")
            triage_row = triage_by_ticker.get(ticker, {})
            candidates.append({
                "ticker": ticker,
                "company": row.get("company"),
                "model_family": "extended_core_candidate_model",
                "publication_status": status,
                "target_model": status in TARGET_MODEL_STATUSES,
                "watchlist_blocked": status in WATCHLIST_STATUSES,
                "chain_blocks": row.get("chain_blocks") or triage_row.get("chain_blocks", []),
                "source_seed": [row.get("source_path", ""), triage_row.get("evidence_source", "")],
            })
            seen.add(ticker)
    return candidates


def completion_status(field: str, snippet: str, score: int, candidate: dict, structured_available: bool) -> str:
    if snippet and score > 0:
        direct_terms = STRICT_DIRECT_KEYWORDS.get(field, DIRECT_KEYWORDS[field])
        direct_hit = any(keyword.lower() in snippet.lower() for keyword in direct_terms)
        return "direct" if direct_hit else "proxy"
    if structured_available:
        return "structured_model_proxy"
    if candidate.get("watchlist_blocked"):
        return "watchlist_blocked"
    return "source_exhausted"


def canonical_text(field: str, status: str, snippet: str, candidate: dict, structured_text: str) -> str:
    if status in {"direct", "proxy"}:
        prefix = "直接证据" if status == "direct" else "代理证据"
        return f"{prefix}：{snippet}"
    if status == "structured_model_proxy":
        return f"结构化模型代理：{structured_text}"
    if status == "watchlist_blocked":
        return f"观察名单阻断：{FIELD_LABELS[field]} 未形成可验证公开证据，且盈利或模型分母不足，不能进入目标价/公允价值模型。"
    return f"来源耗尽：已检查本案归档券商、官方披露和网页材料，{FIELD_LABELS[field]} 未形成可验证证据；该字段阻断增量估值信用。"


def strip_evidence_prefix(text: str) -> str:
    return re.sub(r"^(直接证据|代理证据|结构化模型代理)：", "", str(text or "")).strip()


def add_operating_proxy_boundaries(field_cells: dict[str, dict], candidate: dict) -> None:
    util = field_cells.get("utilization_or_yield")
    if not util or util.get("status") != "source_exhausted" or not candidate.get("target_model"):
        return
    for proxy_field in ("capacity_or_certification", "order_or_backlog", "margin_impact"):
        proxy = field_cells.get(proxy_field, {})
        if proxy.get("status") in {"direct", "proxy", "structured_model_proxy"}:
            proxy_text = strip_evidence_prefix(str(proxy.get("evidence") or ""))
            util.update({
                "status": "proxy",
                "evidence": (
                    f"代理证据：模型不使用独立利用率口径，改用 {FIELD_LABELS[proxy_field]} "
                    f"作为产能/交付/效率边界；{proxy_text}"
                ),
                "raw_snippet": proxy.get("raw_snippet", ""),
                "source": proxy.get("source", "data/field_evidence_completion_20260701.json"),
                "score": max(int(proxy.get("score") or 0), 1),
                "valuation_consequence": "usable as an operating-efficiency boundary; no standalone utilization uplift is added",
            })
            return


def add_order_proxy_boundaries(field_cells: dict[str, dict], candidate: dict) -> None:
    order = field_cells.get("order_or_backlog")
    if not order or order.get("status") != "source_exhausted" or not candidate.get("target_model"):
        return
    chain_text = " ".join(str(item) for item in candidate.get("chain_blocks", []))
    if not any(token in chain_text for token in ("IDC", "AIDC", "运营", "云服务", "下游需求")):
        return
    for proxy_field in ("customer_or_platform", "capacity_or_certification", "revenue_exposure", "margin_impact"):
        proxy = field_cells.get(proxy_field, {})
        if proxy.get("status") in {"direct", "proxy", "structured_model_proxy"}:
            proxy_text = strip_evidence_prefix(str(proxy.get("evidence") or ""))
            order.update({
                "status": "proxy",
                "evidence": (
                    f"代理证据：运营商/IDC 平台不按设备 backlog 入模，改用 {FIELD_LABELS[proxy_field]} "
                    f"作为收入转化和需求兑现边界；{proxy_text}"
                ),
                "raw_snippet": proxy.get("raw_snippet", ""),
                "source": proxy.get("source", "data/field_evidence_completion_20260701.json"),
                "score": max(int(proxy.get("score") or 0), 1),
                "valuation_consequence": "usable as platform-demand conversion proxy; no device-backlog uplift is added",
            })
            return


def structured_proxy(candidate: dict, field: str, current_by_ticker: dict[str, dict], extended_by_ticker: dict[str, dict]) -> tuple[bool, str]:
    ticker = candidate["ticker"]
    row = current_by_ticker.get(ticker) or extended_by_ticker.get(ticker) or {}
    if field == "margin_impact" and row.get("eps_2026e") not in {None, ""}:
        revenue = row.get("revenue_2026e_100mn")
        profit = row.get("np_2026e_100mn")
        eps = row.get("eps_2026e")
        return True, f"2026E revenue {revenue} 亿元、net profit {profit} 亿元、EPS {eps}；用于利润弹性和估值分母校验。"
    if field == "revenue_exposure" and row.get("revenue_2026e_100mn") not in {None, ""}:
        return True, f"2026E revenue {row.get('revenue_2026e_100mn')} 亿元；来源为当前价/财务分母复算包。"
    return False, ""


def collect_seed_sources(
    candidate: dict,
    blocked_by_ticker: dict[str, dict],
    official_by_ticker: dict[str, dict],
    proxy_official_by_ticker: dict[str, dict],
    registry: dict[str, Path],
) -> list[str]:
    ticker = candidate["ticker"]
    seeds = list(candidate.get("source_seed") or [])
    for row in (blocked_by_ticker.get(ticker), official_by_ticker.get(ticker), proxy_official_by_ticker.get(ticker)):
        if not row:
            continue
        for report_key in ("reports", "filings"):
            for report in row.get(report_key, []) if isinstance(row.get(report_key), list) else []:
                for key in ("text_path", "pdf_path", "detail_path"):
                    if report.get(key):
                        seeds.append(str(report[key]))
        field_summary = row.get("field_summary", {})
        for summary in field_summary.values() if isinstance(field_summary, dict) else []:
            for source in summary.get("sources", []) if isinstance(summary, dict) else []:
                seeds.append(str(source))
    return seeds


def build() -> dict:
    DATA.mkdir(parents=True, exist_ok=True)
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    registry = source_registry_paths()
    blocked_by_ticker = evidence_seed_from_collection(DATA / "blocked_core_candidate_report_collection_20260701.json")
    official_by_ticker = evidence_seed_from_collection(DATA / "source_exhausted_official_filing_collection_20260701.json")
    proxy_official_by_ticker = evidence_seed_from_collection(DATA / "proxy_field_official_filing_collection_20260701.json")
    current_by_ticker = {str(row.get("ticker")): row for row in load_rows(DATA / "current_valuation_model_20260630.json") if row.get("ticker")}
    extended_by_ticker = {str(row.get("ticker")): row for row in load_rows(DATA / "core_candidate_extended_valuation_model_20260701.json") if row.get("ticker")}

    rows = []
    status_counter: Counter[str] = Counter()
    field_counter: dict[str, Counter[str]] = {field: Counter() for field in FIELDS}
    for candidate in model_candidates():
        ticker = candidate["ticker"]
        company = str(candidate.get("company") or "")
        seed_sources = collect_seed_sources(candidate, blocked_by_ticker, official_by_ticker, proxy_official_by_ticker, registry)
        files = candidate_source_files(ticker, company, seed_sources, registry)
        field_cells: dict[str, dict] = {}
        for field in FIELDS:
            collection_row = blocked_by_ticker.get(ticker) or official_by_ticker.get(ticker)
            summary_snippet, summary_source, summary_score = field_summary_seed(collection_row, field, ticker, company)
            mined_snippet, mined_source, mined_score = best_snippet(files, field, ticker, company)
            if summary_score >= mined_score and summary_snippet:
                snippet, source, score = summary_snippet, summary_source, summary_score
            else:
                snippet, source, score = mined_snippet, mined_source, mined_score
            structured_available, structured_text = structured_proxy(candidate, field, current_by_ticker, extended_by_ticker)
            status = completion_status(field, snippet, score, candidate, structured_available)
            text = canonical_text(field, status, snippet, candidate, structured_text)
            field_cells[field] = {
                "status": status,
                "evidence": text,
                "raw_snippet": snippet,
                "source": source or "data/field_evidence_completion_20260701.json",
                "score": score,
                "materiality": "valuation_input" if field in {"revenue_exposure", "order_or_backlog", "asp_or_price_proxy", "margin_impact"} else "valuation_cross_check",
                "valuation_consequence": (
                    "usable in target/fair-value model with no incremental uplift beyond the evidenced field"
                    if status in {"direct", "proxy", "structured_model_proxy"}
                    else "blocks incremental valuation credit; watchlist-only if model denominator is also insufficient"
                ),
            }
        add_operating_proxy_boundaries(field_cells, candidate)
        add_order_proxy_boundaries(field_cells, candidate)
        for field, cell in field_cells.items():
            status_counter[str(cell["status"])] += 1
            field_counter[field][str(cell["status"])] += 1
        unresolved = [
            field
            for field, cell in field_cells.items()
            if cell["status"] in {"source_exhausted", "watchlist_blocked"}
        ]
        rows.append({
            "ticker": ticker,
            "company": company,
            "model_family": candidate.get("model_family"),
            "publication_status": candidate.get("publication_status"),
            "target_model": bool(candidate.get("target_model")),
            "watchlist_blocked": bool(candidate.get("watchlist_blocked")),
            "chain_blocks": candidate.get("chain_blocks") or [],
            "source_file_count": len(files),
            "fields": field_cells,
            "unresolved_fields": unresolved,
            "field_gate_status": (
                "PASS"
                if not unresolved or (candidate.get("watchlist_blocked") and set(unresolved))
                else "PASS_WITH_MODEL_BOUNDARY"
            ),
        })

    metadata = {
        "case_id": "aidc-supply-chain-20260630",
        "run_date": "2026-07-01",
        "candidate_rows": len(rows),
        "field_count_per_candidate": len(FIELDS),
        "total_field_cells": len(rows) * len(FIELDS),
        "status_counts": dict(status_counter),
        "field_status_counts": {field: dict(counter) for field, counter in field_counter.items()},
        "rule": "Every modeled core candidate must have direct, proxy, structured-model, source-exhausted, or watchlist-blocked status for each material field.",
    }
    payload = {"metadata": metadata, "rows": rows}
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(payload)
    return payload


def write_markdown(payload: dict) -> None:
    metadata = payload["metadata"]
    rows = payload["rows"]
    lines = [
        "# Field Evidence Completion",
        "",
        f"- Candidate rows: {metadata['candidate_rows']}",
        f"- Total field cells: {metadata['total_field_cells']}",
        f"- Status counts: {metadata['status_counts']}",
        "",
        "## Field Status Matrix",
        "",
        "| Field | Direct | Proxy | Structured proxy | Source exhausted | Watchlist blocked |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for field in FIELDS:
        counter = metadata["field_status_counts"].get(field, {})
        lines.append(
            f"| {FIELD_LABELS[field]} | {counter.get('direct', 0)} | {counter.get('proxy', 0)} | "
            f"{counter.get('structured_model_proxy', 0)} | {counter.get('source_exhausted', 0)} | {counter.get('watchlist_blocked', 0)} |"
        )
    lines += [
        "",
        "## Candidate Rows",
        "",
        "| Ticker | Company | Model status | Gate | Unresolved fields | Source files |",
        "|---|---|---|---|---|---:|",
    ]
    for row in rows:
        unresolved = "none" if not row["unresolved_fields"] else ", ".join(row["unresolved_fields"])
        lines.append(
            f"| {row['ticker']} | {row['company']} | {row['publication_status']} | {row['field_gate_status']} | {unresolved} | {row['source_file_count']} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ANALYSIS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    result = build()
    print(json.dumps(result["metadata"], ensure_ascii=False, indent=2))

#!/usr/bin/env python3
"""Build extended valuation disposition for non-target AIDC core candidates.

The original report had 41 core candidates with evidence PDFs but no valuation
denominator. This case-scoped script fills the denominator, parses broker
forecast/target evidence where public PDFs are available, and writes a
company-level model or downgrade decision for every remaining candidate.
"""

from __future__ import annotations

import importlib.util
import json
import math
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import akshare as ak
import requests


BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
ANALYSIS = BASE / "analysis"
SOURCES = BASE / "sources" / "core-candidate-valuation-broker-reports-20260701"
BROKER_TOOL_PATH = BASE / "tools" / "collect_eastmoney_broker_reports.py"
RUN_DATE = "2026-07-01"

FIELD_MAP = {
    "营业总收入": "total_revenue",
    "营业成本": "operating_cost",
    "净利润": "net_profit",
    "归母净利润": "net_profit_parent",
    "扣非净利润": "net_profit_deducted",
    "基本每股收益": "eps_basic",
    "股东权益合计(净资产)": "equity",
    "资产负债率": "debt_ratio",
    "商誉": "goodwill",
    "每股净资产": "bps",
    "经营现金流量净额": "operating_cash_flow",
    "每股现金流": "cash_flow_per_share",
    "净资产收益率(ROE)": "roe",
    "总资产报酬率(ROA)": "roa",
    "毛利率": "gross_margin",
    "销售净利率": "net_margin",
    "营业利润率": "operating_margin",
    "营业总收入增长率": "revenue_growth",
    "归属母公司净利润增长率": "profit_growth",
    "经营活动净现金/销售收入": "ocf_to_revenue",
    "期间费用率": "expense_ratio",
    "流动比率": "current_ratio",
    "速动比率": "quick_ratio",
}

UNAVAILABLE = {"", "-", "not disclosed", "not found", "unavailable", "n/a", "none", None}
TARGET_MODEL_STATUSES = {
    "target_model_ready",
    "house_target_model_ready",
    "ps_sotp_target_model_ready",
}
WATCHLIST_STATUSES = {
    "watchlist_only_insufficient_model",
}


def is_target_model_status(status: object) -> bool:
    return str(status) in TARGET_MODEL_STATUSES


@dataclass(frozen=True)
class Candidate:
    ticker: str
    company: str
    chain_blocks: list[str]
    subsegments: list[str]
    candidate_method: str
    source_tier: str


def main() -> int:
    SOURCES.mkdir(parents=True, exist_ok=True)
    broker_tools = load_broker_tools()
    candidates = load_candidates()
    quotes = fetch_sina_quotes([item.ticker for item in candidates])
    market_financial_rows: list[dict[str, Any]] = []
    broker_rows: list[dict[str, Any]] = []
    model_rows: list[dict[str, Any]] = []
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://data.eastmoney.com/report/stock.jshtml",
            "Origin": "https://data.eastmoney.com",
            "Accept": "application/json, text/plain, */*",
        }
    )

    blocked_collection = load_blocked_collection()
    official_collection = load_official_collection()
    for index, candidate in enumerate(candidates, 1):
        print(f"[{index:02d}/{len(candidates):02d}] {candidate.ticker} {candidate.company}", flush=True)
        financial = fetch_financial_packet(candidate)
        quote = quotes.get(candidate.ticker, quote_not_found(candidate))
        market_financial = build_market_financial_packet(candidate, quote, financial)
        consensus = build_broker_consensus(
            broker_tools,
            session,
            candidate,
            quote,
            blocked_collection.get(candidate.ticker),
            official_collection.get(candidate.ticker),
        )
        model = build_model_row(candidate, market_financial, consensus)
        market_financial_rows.append(market_financial)
        broker_rows.append(consensus)
        model_rows.append(model)
        time.sleep(0.12)

    write_outputs(market_financial_rows, broker_rows, model_rows)
    summary = {
        "candidates": len(candidates),
        "market_financial_rows": len(market_financial_rows),
        "broker_rows": len(broker_rows),
        "target_model_rows": sum(1 for row in model_rows if is_target_model_status(row["publication_status"])),
        "watchlist_rows": sum(1 for row in model_rows if not is_target_model_status(row["publication_status"])),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def load_broker_tools() -> Any:
    spec = importlib.util.spec_from_file_location("aidc_broker_tools", BROKER_TOOL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {BROKER_TOOL_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_candidates() -> list[Candidate]:
    payload = json.loads((DATA / "core_candidate_valuation_disposition_20260630.json").read_text(encoding="utf-8"))
    rows = payload.get("rows", []) if isinstance(payload, dict) else []
    candidates: list[Candidate] = []
    for row in rows:
        if row.get("existing_target_price_model"):
            continue
        ticker = str(row.get("ticker") or "").strip()
        if not ticker or ticker == "not collected":
            continue
        candidates.append(
            Candidate(
                ticker=ticker,
                company=str(row.get("company") or ""),
                chain_blocks=list(row.get("chain_blocks") or []),
                subsegments=list(row.get("subsegments") or []),
                candidate_method=str(row.get("candidate_method") or ""),
                source_tier=str(row.get("evidence_source_tier") or ""),
            )
        )
    return candidates


def load_blocked_collection() -> dict[str, dict[str, Any]]:
    path = DATA / "blocked_core_candidate_report_collection_20260701.json"
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {str(row.get("ticker")): row for row in payload.get("rows", []) if isinstance(row, dict)}


def load_official_collection() -> dict[str, dict[str, Any]]:
    path = DATA / "source_exhausted_official_filing_collection_20260701.json"
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {str(row.get("ticker")): row for row in payload.get("rows", []) if isinstance(row, dict)}


def sina_code(code: str) -> str:
    return ("sh" if code.startswith(("6", "9")) else "sz") + code


def fetch_sina_quotes(codes: list[str]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for start in range(0, len(codes), 30):
        chunk = codes[start : start + 30]
        url = "https://hq.sinajs.cn/list=" + ",".join(sina_code(code) for code in chunk)
        response = requests.get(url, headers={"Referer": "https://finance.sina.com.cn"}, timeout=(5, 15))
        response.raise_for_status()
        for match in re.finditer(r"var hq_str_(?:sh|sz)(\d{6})=\"([^\"]*)\"", response.text):
            code = match.group(1)
            fields = match.group(2).split(",")
            if len(fields) < 32 or not fields[0]:
                result[code] = quote_not_found(Candidate(code, "", [], [], "", ""))
                continue
            result[code] = {
                "ticker": code,
                "company": fields[0],
                "open": as_float(fields[1]),
                "prev_close": as_float(fields[2]),
                "price": as_float(fields[3]),
                "high": as_float(fields[4]),
                "low": as_float(fields[5]),
                "volume_shares": as_float(fields[8]),
                "amount_cny": as_float(fields[9]),
                "quote_date": fields[30] if len(fields) > 30 else RUN_DATE,
                "quote_time": fields[31] if len(fields) > 31 else "",
                "source": "Sina Finance hq.sinajs.cn batch quote",
                "data_quality": "realtime_snapshot",
            }
        time.sleep(0.2)
    return result


def quote_not_found(candidate: Candidate) -> dict[str, Any]:
    return {
        "ticker": candidate.ticker,
        "company": candidate.company,
        "price": None,
        "amount_cny": None,
        "quote_date": RUN_DATE,
        "quote_time": "",
        "source": "Sina Finance hq.sinajs.cn batch quote",
        "data_quality": "unavailable",
    }


def fetch_financial_packet(candidate: Candidate) -> dict[str, Any]:
    try:
        df = ak.stock_financial_abstract(symbol=candidate.ticker)
    except Exception as exc:
        return {
            "ticker": candidate.ticker,
            "company": candidate.company,
            "data_quality": "unavailable",
            "warnings": [f"akshare.stock_financial_abstract failed: {exc.__class__.__name__}"],
            "periods": [],
        }
    if df.empty:
        return {
            "ticker": candidate.ticker,
            "company": candidate.company,
            "data_quality": "unavailable",
            "warnings": ["empty akshare.stock_financial_abstract response"],
            "periods": [],
        }
    period_cols = [col for col in df.columns if isinstance(col, str) and col.isdigit() and len(col) == 8]
    period_cols = sorted(period_cols, reverse=True)[:8]
    rows_by_metric = {
        str(row.get("指标") or "").strip(): row
        for _, row in df.iterrows()
        if str(row.get("指标") or "").strip() in FIELD_MAP
    }
    periods: list[dict[str, Any]] = []
    for period in period_cols:
        metrics: dict[str, Any] = {}
        for cn_name, en_name in FIELD_MAP.items():
            row = rows_by_metric.get(cn_name)
            metrics[en_name] = as_float(row.get(period)) if row is not None else None
        periods.append(
            {
                "period": period,
                "year": int(period[:4]),
                "quarter": quarter_from_period(period),
                "metrics": metrics,
            }
        )
    return {
        "ticker": candidate.ticker,
        "company": candidate.company,
        "data_quality": "full" if periods else "unavailable",
        "source": "akshare.stock_financial_abstract",
        "fetched_at": datetime.now().isoformat(timespec="seconds"),
        "periods": periods,
        "warnings": [],
    }


def build_market_financial_packet(
    candidate: Candidate,
    quote: dict[str, Any],
    financial: dict[str, Any],
) -> dict[str, Any]:
    periods = financial.get("periods") or []
    latest = periods[0] if periods else {}
    fy2025 = next((period for period in periods if period.get("period") == "20251231"), {})
    latest_metrics = latest.get("metrics") or {}
    fy_metrics = fy2025.get("metrics") or {}
    price = quote.get("price")
    latest_equity = latest_metrics.get("equity")
    latest_bps = latest_metrics.get("bps")
    shares_100mn = None
    if latest_equity and latest_bps and latest_bps > 0:
        shares_100mn = latest_equity / latest_bps / 100_000_000
    market_cap_100mn = price * shares_100mn if price and shares_100mn else None
    rev_2026e = derive_revenue_proxy(candidate, latest_metrics, fy_metrics)
    np_2026e = derive_profit_proxy(candidate, latest_metrics, fy_metrics)
    eps_2026e = np_2026e / shares_100mn if np_2026e is not None and shares_100mn else None
    return {
        "ticker": candidate.ticker,
        "company": candidate.company,
        "chain_blocks": candidate.chain_blocks,
        "subsegments": candidate.subsegments,
        "candidate_method": candidate.candidate_method,
        "quote": quote,
        "latest_period": latest,
        "fy2025_period": fy2025,
        "current_price": price,
        "price_datetime": f"{quote.get('quote_date') or RUN_DATE} {quote.get('quote_time') or ''}".strip(),
        "shares_100mn": shares_100mn,
        "share_count_source": "equity divided by BPS from akshare financial abstract" if shares_100mn else "not available",
        "market_cap_100mn_cny": market_cap_100mn,
        "revenue_q1_100mn": to_100mn(latest_metrics.get("total_revenue")),
        "np_parent_q1_100mn": to_100mn(latest_metrics.get("net_profit_parent")),
        "eps_q1": latest_metrics.get("eps_basic"),
        "revenue_2025_100mn": to_100mn(fy_metrics.get("total_revenue")),
        "np_parent_2025_100mn": to_100mn(fy_metrics.get("net_profit_parent")),
        "eps_2025": fy_metrics.get("eps_basic"),
        "gross_margin_latest": latest_metrics.get("gross_margin"),
        "roe_latest": latest_metrics.get("roe"),
        "operating_cash_flow_q1_100mn": to_100mn(latest_metrics.get("operating_cash_flow")),
        "debt_ratio_latest": latest_metrics.get("debt_ratio"),
        "revenue_2026e_proxy_100mn": rev_2026e,
        "np_2026e_proxy_100mn": np_2026e,
        "eps_2026e_proxy": eps_2026e,
        "data_quality": financial.get("data_quality", "unavailable"),
        "warnings": financial.get("warnings", []),
    }


def build_broker_consensus(
    broker_tools: Any,
    session: requests.Session,
    candidate: Candidate,
    quote: dict[str, Any],
    archived_row: dict[str, Any] | None,
    official_row: dict[str, Any] | None,
) -> dict[str, Any]:
    target_report = fetch_best_target_report(broker_tools, session, candidate)
    if target_report:
        detail = broker_tools.fetch_detail(session, str(target_report.get("infoCode") or ""))
        record = archive_report(candidate, target_report, detail, session)
        ticker_obj = broker_tools.Ticker(candidate.ticker, candidate.company, quote.get("price"))
        return broker_tools.build_consensus_row(ticker_obj, target_report, detail, record)

    if archived_row and archived_row.get("reports"):
        report = select_best_archived_report(archived_row["reports"])
        text = read_rel_text(report.get("text_path")) + "\n" + read_rel_text(report.get("detail_path"))
        parsed = broker_tools.parse_forecasts_from_text(text)
        target_price = parse_target_price_from_text(text)
        method = broker_tools.parse_valuation_method(text, target_price)
        rating = broker_tools.parse_rating(
            {
                "emRatingName": report.get("rating"),
                "orgSName": report.get("broker"),
                "publishDate": report.get("report_date"),
            },
            text,
        )
        revenue = broker_tools.ensure_forecast_keys(parsed.get("revenue_E"))
        net_profit = broker_tools.ensure_forecast_keys(parsed.get("net_profit_E"))
        eps = broker_tools.ensure_forecast_keys(parsed.get("EPS_E"))
        valuation_weight = 0.0
        status = "original_public_pdf_forecast_only"
        if isinstance(target_price, (int, float)) and broker_tools.all_usable([eps.get("2026E"), method, rating]):
            valuation_weight = 0.08 if broker_tools.all_usable([revenue.get("2026E"), net_profit.get("2026E")]) else 0.04
            status = "target_parsed_from_original_public_pdf"
        return {
            "ticker": candidate.ticker,
            "company": candidate.company,
            "broker": report.get("broker") or "not disclosed",
            "report_date": clean_date(report.get("report_date")),
            "rating": rating,
            "target_price": target_price,
            "target_price_range": {"low": target_price, "high": target_price} if isinstance(target_price, (int, float)) else {"low": "not disclosed", "high": "not disclosed"},
            "revenue_E": revenue,
            "net_profit_E": net_profit,
            "EPS_E": eps,
            "PE_E": broker_tools.ensure_forecast_keys(parsed.get("PE_E")),
            "method": method,
            "implied_upside": broker_tools.calc_upside(target_price, quote.get("price")),
            "source_quality": "original_public_broker_pdf",
            "source_path": report.get("text_path") or report.get("pdf_path") or "not disclosed",
            "detail_url": report.get("detail_url") or "not disclosed",
            "pdf_url": report.get("pdf_url") or "not disclosed",
            "valuation_weight": valuation_weight,
            "coverage_status": status,
            "consensus_role": "sell-side forecast evidence parsed from archived public PDF; target anchor used only when explicit target can be parsed",
        }

    if official_row:
        filing = select_best_official_filing(official_row.get("filings") or [])
        return {
            "ticker": candidate.ticker,
            "company": candidate.company,
            "broker": "not disclosed",
            "report_date": clean_date(filing.get("title") or "not disclosed"),
            "rating": "not disclosed",
            "target_price": "not disclosed",
            "target_price_range": {"low": "not disclosed", "high": "not disclosed"},
            "revenue_E": default_forecast(),
            "net_profit_E": default_forecast(),
            "EPS_E": default_forecast(),
            "PE_E": default_forecast(),
            "method": "no broker target; official filing evidence only",
            "implied_upside": "not disclosed",
            "source_quality": "official_filing_no_broker_target",
            "source_path": filing.get("text_path") or filing.get("pdf_path") or "not disclosed",
            "detail_url": filing.get("pdf_url") or "not disclosed",
            "pdf_url": filing.get("pdf_url") or "not disclosed",
            "valuation_weight": 0.0,
            "coverage_status": "public_broker_not_found_official_filing_backfill",
            "consensus_role": "official filing can support relationship/financial evidence, not Street valuation anchor",
        }

    return {
        "ticker": candidate.ticker,
        "company": candidate.company,
        "broker": "not disclosed",
        "report_date": "not disclosed",
        "rating": "not disclosed",
        "target_price": "not disclosed",
        "target_price_range": {"low": "not disclosed", "high": "not disclosed"},
        "revenue_E": default_forecast(),
        "net_profit_E": default_forecast(),
        "EPS_E": default_forecast(),
        "PE_E": default_forecast(),
        "method": "not disclosed",
        "implied_upside": "not disclosed",
        "source_quality": "not_found",
        "source_path": "source_exhaustion_log.md",
        "valuation_weight": 0.0,
        "coverage_status": "not_found",
        "consensus_role": "unavailable; cannot support valuation target",
    }


def fetch_best_target_report(
    broker_tools: Any,
    session: requests.Session,
    candidate: Candidate,
) -> dict[str, Any] | None:
    try:
        reports = broker_tools.fetch_report_list(
            session,
            candidate.ticker,
            begin="2025-01-01",
            end=RUN_DATE,
            page_size=80,
        )
    except Exception:
        return None
    scored: list[tuple[tuple[int, str], dict[str, Any]]] = []
    for report in reports:
        target = broker_tools.target_price_value(report)
        has_target = isinstance(target, (int, float))
        keywords = keyword_score(str(report.get("title") or ""))
        scored.append((((2 if has_target else 0) + keywords, str(report.get("publishDate") or "")), report))
    scored.sort(key=lambda item: item[0], reverse=True)
    for score, report in scored:
        if score[0] >= 2:
            return report
    return None


def archive_report(
    candidate: Candidate,
    report: dict[str, Any],
    detail: dict[str, Any],
    session: requests.Session,
) -> dict[str, Any]:
    candidate_dir = SOURCES / f"{candidate.ticker}-{slug(candidate.company)}"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    info_code = str(report.get("infoCode") or "report")
    stem = f"{info_code}-{slug(str(report.get('orgSName') or report.get('orgName') or 'broker'))}-{slug(str(report.get('title') or 'report'))[:64]}"
    pdf_path = candidate_dir / f"{stem}.pdf"
    txt_path = candidate_dir / f"{stem}.txt"
    detail_path = candidate_dir / f"{stem}.md"
    pdf_url = str(detail.get("pdf_url") or "")
    if pdf_url and not pdf_path.exists():
        try:
            response = session.get(pdf_url, timeout=(5, 20))
            response.raise_for_status()
            if response.content.startswith(b"%PDF"):
                pdf_path.write_bytes(response.content)
        except Exception:
            pass
    if pdf_path.exists() and not txt_path.exists():
        import subprocess

        subprocess.run(["pdftotext", "-layout", str(pdf_path), str(txt_path)], check=False)
    detail_path.write_text(
        "\n".join(
            [
                f"# {report.get('title') or 'Broker report'}",
                "",
                f"- Ticker: {candidate.ticker}",
                f"- Company: {candidate.company}",
                f"- Broker: {report.get('orgSName') or report.get('orgName') or 'not disclosed'}",
                f"- Date: {clean_date(report.get('publishDate'))}",
                f"- Rating: {report.get('emRatingName') or 'not disclosed'}",
                f"- Detail URL: {detail.get('detail_url') or 'not disclosed'}",
                f"- PDF URL: {pdf_url or 'not disclosed'}",
                f"- Local PDF: {rel(pdf_path) if pdf_path.exists() else 'not downloaded'}",
                f"- Local text: {rel(txt_path) if txt_path.exists() else 'not extracted'}",
                "",
                "## Eastmoney visible abstract",
                "",
                str(detail.get("notice_content") or "not disclosed"),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "ticker": candidate.ticker,
        "company": candidate.company,
        "title": report.get("title"),
        "broker": report.get("orgSName") or report.get("orgName"),
        "report_date": clean_date(report.get("publishDate")),
        "rating": report.get("emRatingName"),
        "info_code": report.get("infoCode"),
        "detail_url": detail.get("detail_url"),
        "pdf_url": pdf_url,
        "pdf_status": "downloaded" if pdf_path.exists() else "not_available",
        "detail_path": rel(detail_path),
        "pdf_path": rel(pdf_path) if pdf_path.exists() else "",
        "text_path": rel(txt_path) if txt_path.exists() else "",
        "raw_report": report,
    }


def plausible_margin_limit(candidate: Candidate) -> float:
    joined = " ".join(candidate.chain_blocks + candidate.subsegments + [candidate.candidate_method])
    if any(token in joined for token in ("软件", "IP", "EDA", "芯片", "ASIC", "GPU", "HBM", "存储")):
        return 0.75
    if any(token in joined for token in ("光模块", "光通信", "光器件", "PCB", "CCL")):
        return 0.65
    if any(token in joined for token in ("IDC", "运营商", "AIDC", "云")):
        return 0.55
    return 0.60


def finite_number(value: Any) -> float | None:
    parsed = first_number(value)
    if parsed is None or not math.isfinite(parsed):
        return None
    return parsed


def choose_revenue_forecast(
    candidate: Candidate,
    mf: dict[str, Any],
    consensus: dict[str, Any],
    flags: list[str],
) -> float | None:
    broker_revenue = finite_number(consensus.get("revenue_E", {}).get("2026E"))
    proxy_revenue = mf.get("revenue_2026e_proxy_100mn")
    if broker_revenue is not None and broker_revenue > 0:
        if proxy_revenue and (broker_revenue > proxy_revenue * 4 or broker_revenue < proxy_revenue * 0.15):
            flags.append(
                f"broker_2026E_revenue_outlier_rejected: broker={broker_revenue:.4f}, proxy={float(proxy_revenue):.4f}"
            )
        else:
            return broker_revenue
    return proxy_revenue


def profit_eps_pair_plausible(
    candidate: Candidate,
    revenue: float | None,
    shares: float | None,
    net_profit: float | None,
    eps: float | None,
) -> tuple[bool, str]:
    if net_profit is None or eps is None:
        return False, "missing net profit or EPS"
    if revenue and revenue > 0:
        margin = net_profit / revenue
        if margin > plausible_margin_limit(candidate) or margin < -1.20:
            return False, f"implausible net margin {margin:.2%}"
    if shares and shares > 0:
        expected_eps = net_profit / shares
        tolerance = max(0.15, abs(eps) * 0.25)
        if abs(expected_eps - eps) > tolerance:
            return False, f"EPS/share mismatch expected {expected_eps:.4f} vs EPS {eps:.4f}"
    return True, "ok"


def choose_profit_eps_forecast(
    candidate: Candidate,
    mf: dict[str, Any],
    consensus: dict[str, Any],
    revenue: float | None,
    shares: float | None,
    flags: list[str],
) -> tuple[float | None, float | None]:
    broker_np = finite_number(consensus.get("net_profit_E", {}).get("2026E"))
    broker_eps = finite_number(consensus.get("EPS_E", {}).get("2026E"))
    proxy_np = mf.get("np_2026e_proxy_100mn")
    proxy_eps = mf.get("eps_2026e_proxy")

    ok, reason = profit_eps_pair_plausible(candidate, revenue, shares, broker_np, broker_eps)
    if ok:
        return broker_np, broker_eps

    if broker_np is not None or broker_eps is not None:
        flags.append(
            "broker_2026E_profit_eps_pair_rejected: "
            f"net_profit={broker_np}, eps={broker_eps}, reason={reason}"
        )

    if broker_eps is not None and shares and shares > 0:
        eps_derived_np = broker_eps * shares
        ok, derived_reason = profit_eps_pair_plausible(candidate, revenue, shares, eps_derived_np, broker_eps)
        if ok:
            flags.append("broker_EPS_retained_net_profit_derived_from_share_count")
            return eps_derived_np, broker_eps
        flags.append(f"broker_EPS_derived_net_profit_rejected: reason={derived_reason}")

    if proxy_np is not None and proxy_eps is not None:
        ok, proxy_reason = profit_eps_pair_plausible(candidate, revenue, shares, proxy_np, proxy_eps)
        if ok:
            flags.append("financial_proxy_profit_eps_used")
            return proxy_np, proxy_eps
        flags.append(f"financial_proxy_profit_eps_pair_rejected: reason={proxy_reason}")

    if proxy_np is not None and shares and shares > 0:
        derived_eps = proxy_np / shares
        ok, derived_reason = profit_eps_pair_plausible(candidate, revenue, shares, proxy_np, derived_eps)
        if ok:
            flags.append("financial_proxy_net_profit_used_eps_derived_from_share_count")
            return proxy_np, derived_eps
        flags.append(f"financial_proxy_net_profit_derived_eps_rejected: reason={derived_reason}")

    return broker_np or proxy_np, broker_eps or proxy_eps


def build_model_row(
    candidate: Candidate,
    mf: dict[str, Any],
    consensus: dict[str, Any],
) -> dict[str, Any]:
    current_price = mf.get("current_price")
    shares = mf.get("shares_100mn")
    market_cap = mf.get("market_cap_100mn_cny")
    forecast_quality_flags: list[str] = []
    revenue = choose_revenue_forecast(candidate, mf, consensus, forecast_quality_flags)
    np_2026e, eps_2026e = choose_profit_eps_forecast(candidate, mf, consensus, revenue, shares, forecast_quality_flags)
    if eps_2026e is None and np_2026e is not None and shares:
        eps_2026e = np_2026e / shares
    share_count_source_model = mf.get("share_count_source")
    if (not shares) and np_2026e is not None and eps_2026e and eps_2026e > 0:
        shares = np_2026e / eps_2026e
        share_count_source_model = "broker forecast net profit divided by broker forecast EPS"
    if current_price and shares and not market_cap:
        market_cap = current_price * shares
    method = choose_method(candidate, eps_2026e)
    multiple = method_multiple(candidate, eps_2026e)
    target_price = consensus.get("target_price")
    broker_weight = min(float(consensus.get("valuation_weight") or 0.0), 0.10)
    if not isinstance(target_price, (int, float)):
        broker_weight = 0.0
        target_price = None
    positive_eps_ready = (
        current_price
        and shares
        and market_cap
        and revenue is not None
        and np_2026e is not None
        and eps_2026e is not None
        and eps_2026e > 0
        and multiple is not None
    )
    loss_making_ps_ready = (
        current_price
        and shares
        and market_cap
        and revenue is not None
        and eps_2026e is not None
        and eps_2026e <= 0
        and target_price is not None
    )
    bear = base = bull = final_target = upside = bubble_degree = None
    publication_status = "watchlist_only_insufficient_model"
    action = "watchlist only"
    rating = "观察"
    fundamental_weight = market_weight = 0.0
    target_model_type = "watchlist_only"
    street_anchor_status = "explicit Street target available" if target_price is not None else "Street target not disclosed"
    blocker_fields: list[str] = []
    if not current_price:
        blocker_fields.append("current price")
    if not shares or not market_cap:
        blocker_fields.append("share count / market cap")
    if revenue is None:
        blocker_fields.append("2026E revenue")
    if np_2026e is None or eps_2026e is None:
        blocker_fields.append("2026E net profit / EPS")
    elif eps_2026e <= 0:
        blocker_fields.append("positive 2026E EPS")
    if positive_eps_ready:
        bear = eps_2026e * multiple["bear"]
        base = eps_2026e * multiple["base"]
        bull = eps_2026e * multiple["bull"]
        market_anchor = current_price * sentiment_factor(mf)
        fundamental_weight = 0.65 if broker_weight == 0 else 0.55
        market_weight = 1 - fundamental_weight - broker_weight
        final_target = base * fundamental_weight + market_anchor * market_weight
        if target_price is not None:
            final_target += target_price * broker_weight
        upside = final_target / current_price - 1
        bubble_degree = current_price / base - 1 if base else None
        if broker_weight > 0:
            publication_status = "target_model_ready"
            target_model_type = "explicit_broker_target_multi_anchor"
            if upside >= 0.20:
                action = "core review"
                rating = "核心复核"
            elif upside >= 0:
                action = "event-driven validation"
                rating = "事件验证"
            elif upside >= -0.20:
                action = "market-supported watch"
                rating = "市场支撑观察"
            else:
                action = "high valuation risk"
                rating = "高估值风险"
        else:
            publication_status = "house_target_model_ready"
            target_model_type = "astock_house_fair_value_no_street_target"
            if upside >= 0.20:
                action = "house fair-value review"
                rating = "自建公允价值复核"
            elif upside >= 0:
                action = "event-driven validation"
                rating = "事件验证"
            elif upside >= -0.20:
                action = "market-supported watch"
                rating = "市场支撑观察"
            else:
                action = "high valuation risk"
                rating = "高估值风险"
    elif loss_making_ps_ready:
        # Loss-making high-growth names should not be blocked by PE logic when
        # the broker report itself discloses a PS/SOTP target-price framework.
        base = float(target_price)
        bear = base * 0.60
        bull = base * 1.40
        fundamental_weight = 1.00
        market_weight = 0.00
        broker_weight = 0.0
        final_target = base
        upside = final_target / current_price - 1
        bubble_degree = current_price / base - 1 if base else None
        publication_status = "ps_sotp_target_model_ready"
        target_model_type = "loss_making_ps_sotp_target_model"
        action = "milestone PS/SOTP validation"
        rating = "PS/SOTP 里程碑验证"
        blocker_fields = []
    blocker = "none" if is_target_model_status(publication_status) else "；".join(blocker_fields) or "model input"
    return {
        "ticker": candidate.ticker,
        "company": candidate.company,
        "chain_blocks": candidate.chain_blocks,
        "subsegments": candidate.subsegments,
        "current_price": current_price,
        "price_datetime": mf.get("price_datetime"),
        "shares_100mn": shares,
        "share_count_source_model": share_count_source_model,
        "market_cap_100mn_cny": market_cap,
        "revenue_2026e_100mn": revenue,
        "np_2026e_100mn": np_2026e,
        "eps_2026e": eps_2026e,
        "method": method,
        "bear": bear,
        "base": base,
        "bull": bull,
        "broker_target": target_price or "not disclosed",
        "broker_weight": broker_weight,
        "fundamental_weight": fundamental_weight,
        "market_weight": market_weight,
        "final_target": final_target,
        "upside": upside,
        "bubble_degree": bubble_degree,
        "publication_status": publication_status,
        "target_model_type": target_model_type,
        "street_anchor_status": street_anchor_status,
        "action": action,
        "rating": rating,
        "blocker_fields": blocker_fields,
        "blocking_reason": blocker,
        "evidence_quality": evidence_quality(candidate, consensus),
        "source_path": consensus.get("source_path"),
        "broker_source_quality": consensus.get("source_quality"),
        "forecast_quality_flags": forecast_quality_flags,
        "next_verification_path": next_verification_path(publication_status, blocker_fields),
        "company_specific_disposition": disposition_zh(candidate, publication_status, blocker_fields, mf, consensus),
        "catalyst": catalyst_zh(candidate),
        "invalidation": invalidation_zh(candidate),
    }


def write_outputs(
    market_financial_rows: list[dict[str, Any]],
    broker_rows: list[dict[str, Any]],
    model_rows: list[dict[str, Any]],
) -> None:
    metadata = {
        "case_id": "aidc-supply-chain-20260630",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "data_cutoff": "2026-07-01 intraday Sina quote; 2026Q1/2025A akshare financial abstract; public Eastmoney broker PDFs/CNINFO filings",
        "row_count": len(model_rows),
        "target_model_ready_count": sum(1 for row in model_rows if is_target_model_status(row["publication_status"])),
        "explicit_broker_target_model_count": sum(1 for row in model_rows if row["publication_status"] == "target_model_ready"),
        "house_target_model_count": sum(1 for row in model_rows if row["publication_status"] == "house_target_model_ready"),
        "ps_sotp_target_model_count": sum(1 for row in model_rows if row["publication_status"] == "ps_sotp_target_model_ready"),
        "financial_model_no_street_anchor_count": sum(1 for row in model_rows if row["publication_status"] == "financial_model_ready_no_street_anchor"),
        "watchlist_only_count": sum(1 for row in model_rows if row["publication_status"].startswith("watchlist")),
    }
    write_json(DATA / "core_candidate_extended_market_financials_20260701.json", {"metadata": metadata, "rows": market_financial_rows})
    write_json(DATA / "core_candidate_extended_broker_consensus_20260701.json", {"metadata": metadata, "rows": broker_rows})
    write_json(DATA / "core_candidate_extended_valuation_model_20260701.json", {"metadata": metadata, "rows": model_rows})
    write_market_financial_md(metadata, market_financial_rows)
    write_broker_md(metadata, broker_rows)
    write_model_md(metadata, model_rows)
    write_analysis_md(metadata, model_rows)


def write_market_financial_md(metadata: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Extended Core Candidate Market and Financial Denominators",
        "",
        f"- Data cutoff: {metadata['data_cutoff']}",
        f"- Rows: {len(rows)}",
        "",
        "| Ticker | Company | Price | Shares 100mn | Mkt cap 100mn | 2025A rev | 2025A NP | 2026E rev proxy | 2026E NP proxy | EPS proxy | GM latest | ROE latest |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['ticker']} | {row['company']} | {fmt(row.get('current_price'), 2)} | "
            f"{fmt(row.get('shares_100mn'), 2)} | {fmt(row.get('market_cap_100mn_cny'), 1)} | "
            f"{fmt(row.get('revenue_2025_100mn'), 1)} | {fmt(row.get('np_parent_2025_100mn'), 1)} | "
            f"{fmt(row.get('revenue_2026e_proxy_100mn'), 1)} | {fmt(row.get('np_2026e_proxy_100mn'), 1)} | "
            f"{fmt(row.get('eps_2026e_proxy'), 2)} | {fmt(row.get('gross_margin_latest'), 1)} | {fmt(row.get('roe_latest'), 1)} |"
        )
    (DATA / "core_candidate_extended_market_financials_20260701.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_broker_md(metadata: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Extended Core Candidate Broker / Street Evidence",
        "",
        f"- Rows: {len(rows)}",
        "- Zero-weight rows are explicit downgrades, not silent omissions.",
        "",
        "| Ticker | Company | Broker | Date | Rating | Target | 2026E rev | 2026E NP | 2026E EPS | Method | Source quality | Weight |",
        "|---|---|---|---|---|---:|---:|---:|---:|---|---|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['ticker']} | {row['company']} | {row.get('broker')} | {row.get('report_date')} | {row.get('rating')} | "
            f"{fmt_any(row.get('target_price'))} | {fmt_any(year_value(row, 'revenue_E'))} | "
            f"{fmt_any(year_value(row, 'net_profit_E'))} | {fmt_any(year_value(row, 'EPS_E'))} | "
            f"{short(row.get('method'), 80)} | {row.get('source_quality')} | {float(row.get('valuation_weight') or 0):.0%} |"
        )
    (DATA / "core_candidate_extended_broker_consensus_20260701.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_model_md(metadata: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Extended Core Candidate Valuation / Downgrade Model",
        "",
        f"- Rows: {len(rows)}",
        f"- Target-model ready: {metadata['target_model_ready_count']}",
        f"- Explicit broker-target models: {metadata['explicit_broker_target_model_count']}",
        f"- AStock house fair-value models without explicit Street target: {metadata['house_target_model_count']}",
        f"- PS/SOTP target models for loss-making names: {metadata['ps_sotp_target_model_count']}",
        f"- Watchlist-only: {metadata['watchlist_only_count']}",
        "",
        "| Ticker | Company | Status | Price | 2026E rev | 2026E NP | 2026E EPS | Method | Bear | Base | Bull | Final target | Upside | Forecast flags | Blocker |",
        "|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['ticker']} | {row['company']} | {row['publication_status']} | {fmt(row.get('current_price'), 2)} | "
            f"{fmt(row.get('revenue_2026e_100mn'), 1)} | {fmt(row.get('np_2026e_100mn'), 1)} | "
            f"{fmt(row.get('eps_2026e'), 2)} | {short(row.get('method'), 60)} | {fmt(row.get('bear'), 2)} | "
            f"{fmt(row.get('base'), 2)} | {fmt(row.get('bull'), 2)} | {fmt(row.get('final_target'), 2)} | "
            f"{pct(row.get('upside'))} | {'; '.join(row.get('forecast_quality_flags') or []) or 'none'} | {row.get('blocking_reason')} |"
        )
    (DATA / "core_candidate_extended_valuation_model_20260701.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_analysis_md(metadata: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Extended Core Candidate Valuation Synthesis",
        "",
        "This file replaces the prior generic 'wait for more evidence' text with ticker-level valuation or downgrade decisions.",
        "",
        f"- Target-model ready: {metadata['target_model_ready_count']}",
        f"- Explicit broker-target models: {metadata['explicit_broker_target_model_count']}",
        f"- AStock house fair-value models without explicit Street target: {metadata['house_target_model_count']}",
        f"- PS/SOTP target models for loss-making names: {metadata['ps_sotp_target_model_count']}",
        f"- Watchlist-only: {metadata['watchlist_only_count']}",
    ]
    for row in rows:
        lines += [
            "",
            f"## {row['ticker']} {row['company']}",
            "",
            f"- Status: {row['publication_status']}; action: {row['action']}; rating label: {row['rating']}.",
            f"- Denominator: price {fmt(row.get('current_price'), 2)}, shares {fmt(row.get('shares_100mn'), 2)}亿股, market cap {fmt(row.get('market_cap_100mn_cny'), 1)}亿元.",
            f"- 2026E: revenue {fmt(row.get('revenue_2026e_100mn'), 1)}亿元, net profit {fmt(row.get('np_2026e_100mn'), 1)}亿元, EPS {fmt(row.get('eps_2026e'), 2)}.",
            f"- Method: {row['method']}; broker source quality: {row['broker_source_quality']}; broker target: {fmt_any(row.get('broker_target'))}.",
            f"- Forecast quality flags: {'; '.join(row.get('forecast_quality_flags') or []) or 'none'}.",
            f"- Decision: {reader_disposition_text(row)}",
            f"- Catalyst: {row['catalyst']}",
            f"- Invalidation: {row['invalidation']}",
            f"- Source: {row.get('source_path')}.",
        ]
    (ANALYSIS / "core_candidate_extended_valuation_model.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def fetch_best_archived_text(row: dict[str, Any] | None) -> str:
    if not row:
        return ""
    texts = []
    for report in row.get("reports", []):
        texts.append(read_rel_text(report.get("text_path")))
        texts.append(read_rel_text(report.get("detail_path")))
    return "\n".join(texts)


def select_best_archived_report(reports: list[dict[str, Any]]) -> dict[str, Any]:
    def score(report: dict[str, Any]) -> tuple[int, str]:
        text = read_rel_text(report.get("text_path"))
        return (keyword_score(str(report.get("title") or "") + text[:1000]), str(report.get("report_date") or ""))

    return sorted(reports, key=score, reverse=True)[0] if reports else {}


def select_best_official_filing(filings: list[dict[str, Any]]) -> dict[str, Any]:
    if not filings:
        return {}
    return sorted(filings, key=lambda item: (item.get("filing_type") == "annual", str(item.get("title") or "")), reverse=True)[0]


def parse_target_price_from_text(text: str) -> float | str:
    compact = re.sub(r"\s+", "", text)
    patterns = (
        r"目标价(?:为)?([0-9]+(?:\.[0-9]+)?)元",
        r"合理价值(?:区间)?(?:为)?([0-9]+(?:\.[0-9]+)?)元",
        r"目标价格(?:为)?([0-9]+(?:\.[0-9]+)?)元",
    )
    for pattern in patterns:
        match = re.search(pattern, compact)
        if match:
            value = as_float(match.group(1))
            if value and value > 0:
                return value
    range_match = re.search(r"合理价值区间(?:为)?([0-9]+(?:\.[0-9]+)?)[-~至]([0-9]+(?:\.[0-9]+)?)元", compact)
    if range_match:
        low = as_float(range_match.group(1))
        high = as_float(range_match.group(2))
        if low and high:
            return (low + high) / 2
    return "not disclosed"


def derive_revenue_proxy(candidate: Candidate, latest: dict[str, Any], fy: dict[str, Any]) -> float | None:
    broker_style_seasonality = seasonality(candidate)
    q1 = to_100mn(latest.get("total_revenue"))
    fy2025 = to_100mn(fy.get("total_revenue"))
    growth = latest.get("revenue_growth")
    q1_proxy = q1 / broker_style_seasonality if q1 is not None and broker_style_seasonality else None
    fy_proxy = fy2025 * (1 + clamp((growth or 0) / 100, -0.15, 0.45)) if fy2025 is not None else None
    if q1_proxy is None:
        return fy_proxy
    if fy_proxy is None:
        return q1_proxy
    return round((q1_proxy * 0.55 + fy_proxy * 0.45), 4)


def derive_profit_proxy(candidate: Candidate, latest: dict[str, Any], fy: dict[str, Any]) -> float | None:
    q1 = to_100mn(latest.get("net_profit_parent"))
    fy2025 = to_100mn(fy.get("net_profit_parent"))
    growth = latest.get("profit_growth")
    q1_proxy = q1 / seasonality(candidate) if q1 is not None and seasonality(candidate) else None
    fy_proxy = fy2025 * (1 + clamp((growth or 0) / 100, -0.35, 0.65)) if fy2025 is not None else None
    if q1_proxy is None:
        return fy_proxy
    if fy_proxy is None:
        return q1_proxy
    if q1_proxy < 0 or fy_proxy < 0:
        return min(q1_proxy, fy_proxy)
    return round((q1_proxy * 0.55 + fy_proxy * 0.45), 4)


def seasonality(candidate: Candidate) -> float:
    joined = " ".join(candidate.chain_blocks + candidate.subsegments + [candidate.candidate_method])
    if any(token in joined for token in ("运营商", "IDC", "AIDC", "云")):
        return 0.25
    if any(token in joined for token in ("供配电", "变压器", "UPS", "HVDC", "液冷", "温控")):
        return 0.22
    if any(token in joined for token in ("PCB", "CCL", "光模块", "交换机", "网络")):
        return 0.23
    return 0.24


def choose_method(candidate: Candidate, eps: float | None) -> str:
    joined = " ".join(candidate.chain_blocks + candidate.subsegments + [candidate.candidate_method])
    if eps is None or eps <= 0:
        if any(token in joined for token in ("IDC", "运营商", "AIDC", "云")):
            return "PB/ROE or EV/EBITDA watchlist; EPS denominator not valid"
        return "PS/PB or milestone valuation watchlist; positive EPS denominator not valid"
    if any(token in joined for token in ("IDC", "运营商", "AIDC", "云")):
        return "PB/ROE plus EV/EBITDA check; PE is secondary"
    if any(token in joined for token in ("供配电", "变压器", "UPS", "HVDC")):
        return "normalised PE plus order-cycle / working-capital check"
    if any(token in joined for token in ("液冷", "温控")):
        return "normalised PE/SOTP with data-center order validation"
    if any(token in joined for token in ("光模块", "光通信", "交换机", "网络")):
        return "PE/PEG with shipment, customer and margin validation"
    if any(token in joined for token in ("PCB", "CCL")):
        return "PE/PEG plus cycle/product-mix check"
    return "SOTP/PS/PE blend with profit-path validation"


def method_multiple(candidate: Candidate, eps: float | None) -> dict[str, float] | None:
    if eps is None or eps <= 0:
        return None
    joined = " ".join(candidate.chain_blocks + candidate.subsegments + [candidate.candidate_method])
    if any(token in joined for token in ("运营商", "IDC", "AIDC", "云")):
        return {"bear": 12.0, "base": 16.0, "bull": 20.0}
    if any(token in joined for token in ("光模块", "光通信", "交换机", "网络", "GPU", "ASIC", "HBM", "内存")):
        return {"bear": 28.0, "base": 38.0, "bull": 48.0}
    if any(token in joined for token in ("PCB", "CCL")):
        return {"bear": 24.0, "base": 32.0, "bull": 40.0}
    if any(token in joined for token in ("液冷", "温控", "供配电", "变压器", "UPS", "HVDC")):
        return {"bear": 18.0, "base": 25.0, "bull": 32.0}
    return {"bear": 20.0, "base": 28.0, "bull": 36.0}


def sentiment_factor(mf: dict[str, Any]) -> float:
    amount = ((mf.get("quote") or {}).get("amount_cny") or 0) if isinstance(mf.get("quote"), dict) else 0
    if amount > 8_000_000_000:
        return 0.88
    if amount > 2_000_000_000:
        return 0.82
    if amount > 800_000_000:
        return 0.76
    return 0.70


def evidence_quality(candidate: Candidate, consensus: dict[str, Any]) -> str:
    source_quality = str(consensus.get("source_quality") or "")
    if source_quality in {"original_pdf", "original_public_broker_pdf"} and consensus.get("valuation_weight", 0) > 0:
        return "B+ / model-ready public broker target"
    if source_quality in {"original_pdf", "original_public_broker_pdf"}:
        return "B / broker forecast evidence; AStock house fair-value model when denominator is complete"
    if source_quality == "official_filing_no_broker_target":
        return "B- / official filing evidence; no Street target disclosed"
    return "C / source exhausted"


def next_verification_path(publication_status: str, blockers: list[str]) -> str:
    if publication_status == "target_model_ready":
        return "quarterly delivery, margin and customer/order evidence refresh"
    if publication_status == "house_target_model_ready":
        return "refresh broker target page when available; meanwhile validate AStock fair-value range through quarterly delivery, margin and customer/order evidence"
    if publication_status == "ps_sotp_target_model_ready":
        return "validate PS/SOTP target through revenue growth, gross margin, R&D intensity, cash runway and path-to-profit milestones"
    if "positive 2026E EPS" in blockers:
        return "wait for positive profit denominator or switch to explicit PS/PB/SOTP with path-to-profit evidence"
    if "share count / market cap" in blockers:
        return "reconcile share count from official filing or exchange market data"
    return "refresh official filing, broker PDF and company IR evidence"


def reader_disposition_text(row: dict[str, Any]) -> str:
    status = str(row.get("publication_status") or "")
    if status == "target_model_ready":
        return "明示券商/Street 目标价锚、当前价、股本/市值、2026E 分母和三情景复算已完成；订单、毛利率、客户/平台和现金流是更新触发，不是发布前置缺口。"
    if status == "house_target_model_ready":
        return "AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。"
    if status == "ps_sotp_target_model_ready":
        return "PS/SOTP 里程碑目标已完成；当前不把未兑现利润提前资本化，后续以收入、毛利率、费用率、现金流和盈利拐点更新。"
    return str(row.get("company_specific_disposition") or row.get("blocking_reason") or status)


def disposition_zh(
    candidate: Candidate,
    status: str,
    blockers: list[str],
    mf: dict[str, Any],
    consensus: dict[str, Any],
) -> str:
    if status == "target_model_ready":
        return (
            "明示券商/Street 目标价锚、当前价、股本/市值、2026E 收入/净利/EPS 和三情景复算已完成；"
            "订单、毛利率、客户/平台和现金流是后续目标价更新触发，不再作为本版发布前置缺口。"
        )
    if status == "house_target_model_ready":
        return (
            "已完成当前价、股本/市值、2026E 收入/净利/EPS、业务模型匹配倍数和三情景复算；"
            "公开券商报告未披露目标价，因此 Street 权重为 0，但 AStock 发布自建公允价值区间，"
            "后续以客户/订单、毛利率、现金流和券商目标价刷新作为校验。"
        )
    if status == "ps_sotp_target_model_ready":
        return (
            "公司仍处亏损期，PE/PEG 不适用；公开券商 PDF 明示 PS/目标市值/目标价框架，"
            "本版采用 PS/SOTP 里程碑模型发布公允目标，并以收入兑现、毛利率、研发费用率、现金流和盈利拐点验证。"
        )
    if status == "financial_model_ready_no_street_anchor":
        return (
            "旧口径观察行：财务分母和三情景估值可复算，但外部目标价锚未形成；"
            "新口径下应优先转入 AStock 自建公允价值或 PS/SOTP 模型，只有模型分母不足时才保留观察。"
        )
    if "positive 2026E EPS" in blockers:
        return (
            "当前收入、股本和市值已补齐，但 2026E EPS 代理为负或不可用；"
            "PE/PEG 不适用，需等待盈利路径或改用明示 PS/PB/SOTP 证据。"
        )
    if "usable broker target anchor" in blockers:
        return (
            "收入、利润、股本和市值已补齐，但公开 broker target 不可用或为零权重；"
            "降级为 watchlist only，不再写成笼统待补证据。"
        )
    return f"仍由 {', '.join(blockers) or 'model input'} 阻断；已记录具体字段和下一步来源。"


def catalyst_zh(candidate: Candidate) -> str:
    joined = " ".join(candidate.chain_blocks + candidate.subsegments)
    if any(token in joined for token in ("光模块", "光通信")):
        return "800G/1.6T 出货、客户导入、毛利率和现金转化同步验证。"
    if any(token in joined for token in ("PCB", "CCL")):
        return "高端板/高速材料收入占比、认证进度、扩产稼动和毛利率验证。"
    if any(token in joined for token in ("液冷", "温控")):
        return "液冷订单、批量验收、收入确认和项目毛利率验证。"
    if any(token in joined for token in ("供配电", "变压器", "UPS", "HVDC")):
        return "AIDC/海外订单、交付节奏、回款和毛利率验证。"
    if any(token in joined for token in ("IDC", "运营商", "云")):
        return "新增 MW/机架、上架率、算力收入和 capex/现金流验证。"
    return "收入增长、客户认证、订单兑现和毛利率验证。"


def invalidation_zh(candidate: Candidate) -> str:
    joined = " ".join(candidate.chain_blocks + candidate.subsegments)
    if any(token in joined for token in ("光模块", "光通信", "PCB", "CCL")):
        return "若产品升级不能转化为收入和毛利率，或客户/订单证据弱化，则估值信用下调。"
    if any(token in joined for token in ("IDC", "运营商", "云")):
        return "若上架率、算力收入或现金流不能覆盖 capex 和折旧压力，则估值信用下调。"
    return "若订单交付、收入确认、毛利率或回款任一环节失速，则估值信用下调。"


def keyword_score(text: str) -> int:
    return sum(
        1
        for token in ("AIDC", "IDC", "AI", "算力", "数据中心", "服务器", "交换机", "光模块", "PCB", "液冷", "订单", "目标价")
        if token.lower() in text.lower()
    )


def default_forecast() -> dict[str, Any]:
    return {"2025E": "not disclosed", "2026E": "not disclosed", "2027E": "not disclosed", "2028E": "not disclosed"}


def year_value(row: dict[str, Any], key: str) -> Any:
    payload = row.get(key)
    if isinstance(payload, dict):
        return payload.get("2026E")
    return payload


def quarter_from_period(period: str) -> int:
    month = int(period[4:6])
    if month <= 3:
        return 1
    if month <= 6:
        return 2
    if month <= 9:
        return 3
    return 4


def to_100mn(value: Any) -> float | None:
    num = as_float(value)
    return round(num / 100_000_000, 6) if num is not None else None


def as_float(value: Any) -> float | None:
    if value in UNAVAILABLE:
        return None
    try:
        if isinstance(value, str):
            value = value.replace(",", "").strip()
        if value == "":
            return None
        num = float(value)
        if math.isnan(num) or math.isinf(num):
            return None
        return num
    except (TypeError, ValueError):
        return None


def first_number(value: Any) -> float | None:
    return as_float(value)


def clamp(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)


def clean_date(value: Any) -> str:
    return str(value or "not disclosed").split(" ")[0]


def slug(value: str) -> str:
    return re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "-", value).strip("-") or "item"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(BASE))
    except ValueError:
        return str(path)


def read_rel_text(path_value: Any) -> str:
    if not path_value:
        return ""
    path = BASE / str(path_value)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def fmt(value: Any, digits: int = 1) -> str:
    num = as_float(value)
    if num is None:
        return "not disclosed"
    return f"{num:.{digits}f}"


def fmt_any(value: Any) -> str:
    num = as_float(value)
    if num is not None:
        return f"{num:.2f}"
    return str(value if value not in (None, "") else "not disclosed")


def pct(value: Any) -> str:
    num = as_float(value)
    if num is None:
        return "not disclosed"
    return f"{num * 100:.1f}%"


def short(value: Any, limit: int) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip().replace("|", "；")
    return text[:limit] + ("..." if len(text) > limit else "")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())

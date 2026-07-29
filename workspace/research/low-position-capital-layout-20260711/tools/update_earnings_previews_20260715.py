#!/usr/bin/env python3
"""Archive and model newly disclosed 2026H1 preview notices through 2026-07-15."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

import requests


CASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = CASE_DIR / "data"
SOURCE_DIR = CASE_DIR / "sources" / "earnings-previews-20260715"
INDEX_URL = "https://np-anotice-stock.eastmoney.com/api/security/ann"
CONTENT_URL = "https://np-cnotice-stock.eastmoney.com/api/content/ann"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://data.eastmoney.com/notices/",
}
NOTICE_BEGIN = "2026-07-12"
NOTICE_END = "2026-07-15"
DATA_CUTOFF = "2026-07-15"

TARGETS = [
    {"ticker": "300223", "company": "北京君正", "sector": "AI存储", "tier": "satellite"},
    {
        "ticker": "600118",
        "company": "中国卫星",
        "sector": "国防军工与商业航天",
        "tier": "satellite",
    },
    {
        "ticker": "002185",
        "company": "华天科技",
        "sector": "先进封装",
        "tier": "core_candidate",
    },
    {
        "ticker": "002517",
        "company": "恺英网络",
        "sector": "传媒与AI应用",
        "tier": "core_candidate",
    },
    {"ticker": "001309", "company": "德明利", "sector": "AI存储", "tier": "satellite"},
    {
        "ticker": "002156",
        "company": "通富微电",
        "sector": "先进封装",
        "tier": "core_candidate",
    },
    {
        "ticker": "600584",
        "company": "长电科技",
        "sector": "先进封装",
        "tier": "core_candidate",
    },
    {
        "ticker": "600760",
        "company": "中航沈飞",
        "sector": "国防军工与商业航天",
        "tier": "core_candidate",
    },
    {
        "ticker": "600893",
        "company": "航发动力",
        "sector": "国防军工与商业航天",
        "tier": "core_candidate",
    },
]

# Official announcement values are retained as explicit source-normalized inputs.
# The parser validates that the extracted text contains each expected value.
NOTICE_METRICS: dict[str, dict[str, Any]] = {
    "300223": {
        "preview_type": "预增",
        "h1_parent_np_low_100mn": 10.786144,
        "h1_parent_np_high_100mn": 12.823526,
        "h1_deducted_np_low_100mn": 10.491132,
        "h1_deducted_np_high_100mn": 12.528514,
        "prior_parent_np_100mn": 2.031163,
        "official_h1_eps_low": None,
        "official_h1_eps_high": None,
        "quality_class": "core_operating_cycle_and_mix",
        "quality_reason": "Memory and sensor demand plus product-mix improvement drive a large operating recovery; deducted profit is close to parent profit.",
        "disposition": "earnings_validation_watch",
    },
    "600118": {
        "preview_type": "扭亏",
        "h1_parent_np_low_100mn": 0.305,
        "h1_parent_np_high_100mn": 0.365,
        "h1_deducted_np_low_100mn": 0.267,
        "h1_deducted_np_high_100mn": 0.320,
        "prior_parent_np_100mn": -0.304915,
        "official_h1_eps_low": None,
        "official_h1_eps_high": None,
        "quality_class": "turnaround_operating_delivery",
        "quality_reason": "More satellite-model contracts reached acceptance milestones, supporting a reported turnaround; the base is loss-making and H2 recognition remains the key validation.",
        "disposition": "earnings_validation_watch",
    },
    "002185": {
        "preview_type": "预增",
        "h1_parent_np_low_100mn": 7.5,
        "h1_parent_np_high_100mn": 8.5,
        "h1_deducted_np_low_100mn": 2.0,
        "h1_deducted_np_high_100mn": 2.8,
        "prior_parent_np_100mn": 2.264785,
        "official_h1_eps_low": 0.2290,
        "official_h1_eps_high": 0.2595,
        "quality_class": "operating_plus_material_nonrecurring",
        "quality_reason": "IC demand and production scale support the operating recovery, but approximately CNY460mn of fair-value and investment gains dominate the gap between parent and deducted profit.",
        "disposition": "exclude_nonrecurring_dominated",
    },
    "002517": {
        "preview_type": "预增",
        "h1_parent_np_low_100mn": 13.0,
        "h1_parent_np_high_100mn": 15.6,
        "h1_deducted_np_low_100mn": 10.2,
        "h1_deducted_np_high_100mn": 13.2,
        "prior_parent_np_100mn": 9.500366,
        "official_h1_eps_low": 0.61,
        "official_h1_eps_high": 0.73,
        "quality_class": "core_operating_delivery",
        "quality_reason": "Core game operations and new-title contribution support growth; deducted profit grows more slowly than parent profit and requires product-level follow-through.",
        "disposition": "broker_supported_no_preview",
    },
    "001309": {
        "preview_type": "扭亏",
        "h1_revenue_low_100mn": 160.0,
        "h1_revenue_high_100mn": 180.0,
        "h1_parent_np_low_100mn": 57.0,
        "h1_parent_np_high_100mn": 65.0,
        "h1_deducted_np_low_100mn": 56.4902,
        "h1_deducted_np_high_100mn": 64.4902,
        "prior_parent_np_100mn": -1.179456,
        "official_h1_eps_low": 25.35,
        "official_h1_eps_high": 28.91,
        "quality_class": "core_operating_cycle_and_mix",
        "quality_reason": "Enterprise-storage demand, scale and product mix drive a large operating turnaround; cash conversion and inventory cost layers remain binding risks.",
        "disposition": "earnings_delivered_price_advanced",
    },
    "002156": {
        "preview_type": "预增",
        "h1_parent_np_low_100mn": 16.0,
        "h1_parent_np_high_100mn": 18.0,
        "h1_deducted_np_low_100mn": 7.0,
        "h1_deducted_np_high_100mn": 8.0,
        "prior_parent_np_100mn": 4.120922,
        "official_h1_eps_low": 1.05,
        "official_h1_eps_high": 1.19,
        "quality_class": "operating_plus_material_nonrecurring",
        "quality_reason": "Packaging demand and capacity utilization improve, but parent profit is more than twice deducted profit; use the deducted range for valuation until the interim report explains the gap.",
        "disposition": "price_advanced_wait_earnings",
    },
    "600584": {
        "preview_type": "预增",
        "h1_parent_np_low_100mn": 7.7,
        "h1_parent_np_high_100mn": 9.5,
        "h1_deducted_np_low_100mn": 7.4,
        "h1_deducted_np_high_100mn": 9.1,
        "prior_parent_np_100mn": 4.71,
        "official_h1_eps_low": None,
        "official_h1_eps_high": None,
        "quality_class": "core_operating_delivery",
        "quality_reason": "AI infrastructure demand, customer orders and utilization improvement support both parent and deducted profit; margin and capex conversion still need the interim report.",
        "disposition": "price_advanced_wait_earnings",
    },
    "600760": {
        "preview_type": "预减",
        "h1_parent_np_low_100mn": 4.746559,
        "h1_parent_np_high_100mn": 4.746559,
        "h1_deducted_np_low_100mn": 4.038120,
        "h1_deducted_np_high_100mn": 4.038120,
        "prior_parent_np_100mn": 11.364133,
        "official_h1_eps_low": None,
        "official_h1_eps_high": None,
        "quality_class": "earnings_decline_delivery_timing",
        "quality_reason": "New-equipment delivery and supporting-product timing drove a sharp H1 decline; the previous positive earnings case is invalidated until delivery recovers.",
        "disposition": "earnings_decline_watch",
    },
    "600893": {
        "preview_type": "预增",
        "h1_parent_np_low_100mn": 1.4,
        "h1_parent_np_high_100mn": 1.55,
        "h1_deducted_np_low_100mn": 1.95,
        "h1_deducted_np_high_100mn": 2.10,
        "prior_parent_np_100mn": 0.917779,
        "quality_class": "core_operating_delivery_low_base",
        "quality_reason": "Production and delivery progress support growth and deducted profit, but absolute earnings remain low and require durable order recognition before any re-rating.",
        "disposition": "earnings_validation_watch",
    },
}


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n")


def fetch_notice(ticker: str) -> dict[str, Any]:
    response = requests.get(
        INDEX_URL,
        params={
            "sr": "-1",
            "page_size": "100",
            "page_index": "1",
            "ann_type": "A",
            "client_source": "web",
            "f_node": "0",
            "s_node": "0",
            "begin_time": NOTICE_BEGIN,
            "end_time": NOTICE_END,
            "stock_list": ticker,
        },
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    notices = (response.json().get("data") or {}).get("list") or []
    matches = [
        item
        for item in notices
        if "半年度业绩预" in str(item.get("title") or item.get("title_ch") or "")
        and any(
            str(code.get("stock_code") or "") == ticker
            for code in item.get("codes") or []
        )
    ]
    if len(matches) != 1:
        raise RuntimeError(f"{ticker}: expected one new H1 preview, found {len(matches)}")
    notice = matches[0]
    art_code = str(notice.get("art_code") or "")
    content_response = requests.get(
        CONTENT_URL,
        params={"art_code": art_code, "client_source": "web"},
        headers=HEADERS,
        timeout=30,
    )
    content_response.raise_for_status()
    content = content_response.json().get("data") or {}
    attach_url = str(content.get("attach_url") or content.get("attach_url_web") or "")
    if not attach_url:
        raise RuntimeError(f"{ticker}: missing attachment URL")
    raw_path = SOURCE_DIR / f"{ticker}_notice_api.json"
    write_json(
        raw_path,
        {
            "index_notice": notice,
            "content_response": content,
            "source": "Eastmoney announcement API",
            "retrieved_at": DATA_CUTOFF,
        },
    )
    return {
        "ticker": ticker,
        "art_code": art_code,
        "announcement_date": str(notice.get("notice_date") or "")[:10],
        "title": str(notice.get("title") or notice.get("title_ch") or ""),
        "notice_url": f"https://data.eastmoney.com/notices/detail/{ticker}/{art_code}.html",
        "attach_url": attach_url,
        "api_json": str(raw_path.relative_to(CASE_DIR)),
        "content_char_count": len(str(content.get("notice_content") or "")),
    }


def archive_pdf(notice: dict[str, Any], company: str) -> dict[str, Any]:
    ticker = notice["ticker"]
    pdf_path = SOURCE_DIR / f"{ticker}_preview.pdf"
    text_path = SOURCE_DIR / f"{ticker}_preview.txt"
    response = requests.get(notice["attach_url"], headers=HEADERS, timeout=60)
    response.raise_for_status()
    if not response.content.startswith(b"%PDF"):
        raise RuntimeError(f"{ticker}: attachment is not a PDF")
    pdf_path.write_bytes(response.content)
    completed = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), str(text_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"{ticker}: pdftotext failed: {completed.stderr.strip()}")
    text = text_path.read_text(errors="ignore")
    compact = re.sub(r"[\s,]", "", text)
    if ticker not in compact or company not in compact:
        raise RuntimeError(f"{ticker}: code/company validation failed")
    if "半年度业绩预" not in compact:
        raise RuntimeError(f"{ticker}: H1 preview title validation failed")
    metrics = NOTICE_METRICS[ticker]
    for field in (
        "h1_parent_np_low_100mn",
        "h1_parent_np_high_100mn",
        "h1_deducted_np_low_100mn",
        "h1_deducted_np_high_100mn",
    ):
        expected = metrics[field] * 10000
        candidates = {
            f"{expected:.2f}",
            f"{expected:.0f}",
            f"{metrics[field]:.2f}",
            f"{metrics[field]:.4f}",
            f"{metrics[field]:.0f}",
        }
        if not any(candidate in compact for candidate in candidates):
            raise RuntimeError(f"{ticker}: expected {field} not found in extracted text")
    return {
        **notice,
        "company": company,
        "local_pdf": str(pdf_path.relative_to(CASE_DIR)),
        "local_text": str(text_path.relative_to(CASE_DIR)),
        "pdf_size": pdf_path.stat().st_size,
        "text_char_count": len(text),
        "validation_status": "PASS",
    }


def load_q1(ticker: str) -> dict[str, float | None]:
    candidates = [
        DATA_DIR / "all_core_financials" / f"{ticker}_20260710.json",
        DATA_DIR / "core_financials" / f"{ticker}_20260710.json",
        DATA_DIR / "financials" / f"{ticker}_20260710.json",
    ]
    path = next((item for item in candidates if item.exists()), None)
    if path is None:
        return {"q1_net_profit_100mn": None, "q1_deducted_profit_100mn": None, "shares_100mn": None}
    payload = json.loads(path.read_text())
    for period in payload.get("periods") or []:
        if str(period.get("period")) != "20260331":
            continue
        metrics = period.get("metrics") or {}
        profit = metrics.get("net_profit_parent")
        deducted = metrics.get("net_profit_deducted")
        equity = metrics.get("equity")
        bps = metrics.get("bps")
        shares = float(equity) / 1e8 / float(bps) if equity and bps else None
        return {
            "q1_net_profit_100mn": float(profit) / 1e8 if profit is not None else None,
            "q1_deducted_profit_100mn": float(deducted) / 1e8 if deducted is not None else None,
            "shares_100mn": shares,
        }
    return {"q1_net_profit_100mn": None, "q1_deducted_profit_100mn": None, "shares_100mn": None}


def fetch_quotes(codes: list[str]) -> dict[str, dict[str, Any]]:
    symbols = ",".join(("sh" if code.startswith("6") else "sz") + code for code in codes)
    response = requests.get(f"https://qt.gtimg.cn/q={symbols}", timeout=30)
    response.raise_for_status()
    result: dict[str, dict[str, Any]] = {}
    for match in re.finditer(r'v_(?:sh|sz)(\d+)="([^"]*)"', response.text):
        code, body = match.groups()
        fields = body.split("~")
        if len(fields) < 35:
            continue
        result[code] = {
            "current_price": float(fields[3]) if fields[3] else None,
            "previous_close": float(fields[4]) if fields[4] else None,
            "daily_change_pct": float(fields[32]) if fields[32] else None,
            "quote_timestamp": fields[30] if len(fields) > 30 else None,
            "source": "Tencent quote endpoint",
        }
    return result


def build_rows(archived: list[dict[str, Any]]) -> list[dict[str, Any]]:
    quotes = fetch_quotes([row["ticker"] for row in archived])
    rows: list[dict[str, Any]] = []
    for target, archived_row in zip(TARGETS, archived):
        ticker = target["ticker"]
        metric = NOTICE_METRICS[ticker]
        q1 = load_q1(ticker)
        parent_mid = (
            metric["h1_parent_np_low_100mn"] + metric["h1_parent_np_high_100mn"]
        ) / 2
        deducted_mid = (
            metric["h1_deducted_np_low_100mn"] + metric["h1_deducted_np_high_100mn"]
        ) / 2
        shares = q1["shares_100mn"]
        h1_eps_mid = (
            (metric["official_h1_eps_low"] + metric["official_h1_eps_high"]) / 2
            if metric.get("official_h1_eps_low") is not None
            else parent_mid / shares if shares else None
        )
        q2 = parent_mid - q1["q1_net_profit_100mn"] if q1["q1_net_profit_100mn"] is not None else None
        q2_deducted = (
            deducted_mid - q1["q1_deducted_profit_100mn"]
            if q1["q1_deducted_profit_100mn"] is not None
            else None
        )
        rows.append(
            {
                **target,
                **archived_row,
                **metric,
                **q1,
                **quotes.get(ticker, {}),
                "h1_parent_np_midpoint_100mn": round(parent_mid, 4),
                "h1_deducted_np_midpoint_100mn": round(deducted_mid, 4),
                "h1_eps_midpoint": round(h1_eps_mid, 4) if h1_eps_mid is not None else None,
                "h1_eps_source": (
                    "official_preview_eps"
                    if metric.get("official_h1_eps_low") is not None
                    else "preview_parent_profit_divided_by_q1_equity_bps_shares"
                ),
                "q2_implied_net_profit_100mn": round(q2, 4) if q2 is not None else None,
                "q2_implied_deducted_profit_100mn": round(q2_deducted, 4)
                if q2_deducted is not None
                else None,
                "q2_vs_q1_pct": round(q2 / q1["q1_net_profit_100mn"] * 100, 2)
                if q2 is not None and q1["q1_net_profit_100mn"]
                else None,
                "nonrecurring_midpoint_100mn": round(parent_mid - deducted_mid, 4),
                "nonrecurring_share_pct": round((parent_mid - deducted_mid) / parent_mid * 100, 2)
                if parent_mid
                else None,
                "source_quality": "official_company_preview_pdf",
                "data_quality": "official_notice_plus_q1_financial_packet",
                "fallback_path": "Eastmoney official-announcement API after AkShare endpoint returned malformed data",
                "warnings": [
                    "Preview is unaudited and does not prove full-year earnings.",
                    "New market quote is a Tencent snapshot; use only as the 2026-07-15 price anchor.",
                ],
            }
        )
    return rows


def main() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    archived: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for target in TARGETS:
        try:
            archived.append(archive_pdf(fetch_notice(target["ticker"]), target["company"]))
            print(f"PASS {target['ticker']} {target['company']}")
        except Exception as exc:
            failures.append({"ticker": target["ticker"], "company": target["company"], "error": repr(exc)})
            print(f"FAIL {target['ticker']} {target['company']}: {exc}")
    if failures:
        write_json(DATA_DIR / "earnings_preview_update_20260715.json", {"failures": failures, "rows": []})
        raise SystemExit(1)
    rows = build_rows(archived)
    payload = {
        "schema_version": "astock.earnings_preview_update.v1",
        "data_cutoff": DATA_CUTOFF,
        "notice_window": [NOTICE_BEGIN, NOTICE_END],
        "source": "Eastmoney official-announcement API and attached company announcement PDFs",
        "fallback_path": "AkShare stock_yjyg_em endpoint returned malformed None data; official announcement API used instead",
        "target_count": len(TARGETS),
        "archived_count": len(archived),
        "failure_count": 0,
        "rows": rows,
    }
    write_json(DATA_DIR / "earnings_preview_update_20260715.json", payload)
    lines = [
        "# 2026H1 Earnings Preview Update Through 2026-07-15",
        "",
        f"- Newly archived official previews: {len(rows)}",
        "- Scope: names in the existing 54-name theme/priority universe that were absent from the 2026-07-11 capture.",
        "- Source fallback: AkShare returned malformed data; Eastmoney official-announcement API and attached company PDFs were used.",
        "",
        "| Ticker | Company | Date | H1 parent NP midpoint | H1 deducted NP midpoint | H1 EPS midpoint | Q2 implied NP | Non-recurring share | Disposition |",
        "|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        def num(value: Any) -> str:
            return "-" if value is None else f"{float(value):.2f}"

        lines.append(
            f"| {row['ticker']} | {row['company']} | {row['announcement_date']} | "
            f"{num(row['h1_parent_np_midpoint_100mn'])} | "
            f"{num(row['h1_deducted_np_midpoint_100mn'])} | {num(row['h1_eps_midpoint'])} | "
            f"{num(row['q2_implied_net_profit_100mn'])} | "
            f"{num(row['nonrecurring_share_pct'])}% | {row['disposition']} |"
        )
    lines += [
        "",
        "## Evidence Boundary",
        "",
        "All figures above are preliminary, unaudited company forecasts. Parent profit is not treated as clean earnings when the deducted-profit bridge is materially weaker. The update changes preview timing and quality classification; it does not by itself create a new formal target price.",
    ]
    write_text(DATA_DIR / "earnings_preview_update_20260715.md", "\n".join(lines))
    write_text(SOURCE_DIR / "index.md", "\n".join(lines))


if __name__ == "__main__":
    main()

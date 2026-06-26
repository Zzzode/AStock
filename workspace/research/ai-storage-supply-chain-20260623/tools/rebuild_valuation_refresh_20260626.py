#!/usr/bin/env python3
"""Rebuild the 2026-06-26 market-data and valuation reset packet.

The script intentionally separates externally observed inputs from legacy
fair-value outputs. Legacy fair values are retained only to quantify how stale
the previous recommendation package became under the latest close.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

import akshare as ak
import requests


BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
ANALYSIS = BASE / "analysis"
SOURCES = BASE / "sources"
CASE_ID = BASE.name
RUN_DATE = "2026-06-26"
RUN_TIMESTAMP = "2026-06-26T16:30:00+08:00"

CN_TZ = timezone(timedelta(hours=8))

TICKERS = [
    {
        "code": "688008",
        "market": "sh",
        "name": "澜起科技",
        "tier": "Core",
        "weight_pct": 22.0,
        "report_price": 113.40,
        "legacy_fv_mid": 118.50,
        "legacy_fv_range": "109--128",
        "report_eps_2026": 2.70,
        "report_net_profit_2026_100mn": 33.0,
        "report_revenue_2026_100mn": 76.0,
    },
    {
        "code": "002371",
        "market": "sz",
        "name": "北方华创",
        "tier": "Core",
        "weight_pct": 18.0,
        "report_price": 389.50,
        "legacy_fv_mid": 417.50,
        "legacy_fv_range": "384--451",
        "report_eps_2026": 9.50,
        "report_net_profit_2026_100mn": 70.0,
        "report_revenue_2026_100mn": 530.0,
    },
    {
        "code": "688012",
        "market": "sh",
        "name": "中微公司",
        "tier": "Core",
        "weight_pct": 10.0,
        "report_price": 220.80,
        "legacy_fv_mid": 220.50,
        "legacy_fv_range": "196--245",
        "report_eps_2026": 4.60,
        "report_net_profit_2026_100mn": 30.0,
        "report_revenue_2026_100mn": 180.0,
    },
    {
        "code": "688072",
        "market": "sh",
        "name": "拓荆科技",
        "tier": "Core",
        "weight_pct": 10.0,
        "report_price": 247.50,
        "legacy_fv_mid": 245.50,
        "legacy_fv_range": "226--265",
        "report_eps_2026": 4.50,
        "report_net_profit_2026_100mn": 15.0,
        "report_revenue_2026_100mn": 88.0,
    },
    {
        "code": "688126",
        "market": "sh",
        "name": "沪硅产业",
        "tier": "Satellite",
        "weight_pct": 6.0,
        "report_price": 26.43,
        "legacy_fv_mid": 32.25,
        "legacy_fv_range": "29--36",
        "report_eps_2026": 0.367,
        "report_net_profit_2026_100mn": 9.0,
        "report_revenue_2026_100mn": None,
    },
    {
        "code": "000021",
        "market": "sz",
        "name": "深科技",
        "tier": "Satellite",
        "weight_pct": 8.0,
        "report_price": 32.40,
        "legacy_fv_mid": 33.50,
        "legacy_fv_range": "30--37",
        "report_eps_2026": 1.35,
        "report_net_profit_2026_100mn": 25.0,
        "report_revenue_2026_100mn": 450.0,
    },
    {
        "code": "600584",
        "market": "sh",
        "name": "长电科技",
        "tier": "Satellite",
        "weight_pct": 6.0,
        "report_price": 49.40,
        "legacy_fv_mid": 51.00,
        "legacy_fv_range": "47--55",
        "report_eps_2026": 1.30,
        "report_net_profit_2026_100mn": 23.0,
        "report_revenue_2026_100mn": 440.0,
    },
    {
        "code": "002156",
        "market": "sz",
        "name": "通富微电",
        "tier": "Satellite",
        "weight_pct": 5.0,
        "report_price": 48.00,
        "legacy_fv_mid": 48.50,
        "legacy_fv_range": "43--54",
        "report_eps_2026": 1.50,
        "report_net_profit_2026_100mn": 21.0,
        "report_revenue_2026_100mn": 320.0,
    },
    {
        "code": "301308",
        "market": "sz",
        "name": "江波龙",
        "tier": "Satellite",
        "weight_pct": 7.0,
        "report_price": 439.40,
        "legacy_fv_mid": 513.00,
        "legacy_fv_range": "472--554",
        "report_eps_2026": 24.40,
        "report_net_profit_2026_100mn": 100.0,
        "report_revenue_2026_100mn": 295.0,
    },
    {
        "code": "603986",
        "market": "sh",
        "name": "兆易创新",
        "tier": "Theme",
        "weight_pct": 5.0,
        "report_price": 309.60,
        "legacy_fv_mid": 335.00,
        "legacy_fv_range": "308--362",
        "report_eps_2026": 8.60,
        "report_net_profit_2026_100mn": 62.0,
        "report_revenue_2026_100mn": 170.0,
    },
    {
        "code": "300346",
        "market": "sz",
        "name": "南大光电",
        "tier": "Theme",
        "weight_pct": 3.0,
        "report_price": 39.60,
        "legacy_fv_mid": 51.48,
        "legacy_fv_range": "47--57",
        "report_eps_2026": 0.825,
        "report_net_profit_2026_100mn": 6.7,
        "report_revenue_2026_100mn": None,
    },
]

SOURCE_URLS = [
    (
        "bis_federal_register_2024_28270.html",
        "https://www.federalregister.gov/documents/2024/12/05/2024-28270/foreign-produced-direct-product-rule-additions-and-refinements-to-controls-for-advanced-computing",
    ),
    ("bis_federal_register_2024_28270.pdf", "https://www.govinfo.gov/content/pkg/FR-2024-12-05/pdf/2024-28270.pdf"),
    (
        "bis_federal_register_2025_02655.html",
        "https://www.federalregister.gov/documents/2025/02/14/2025-02655/implementation-of-additional-due-diligence-measures-for-advanced-computing-integrated-circuits",
    ),
    (
        "ecfr_ear_774_supplement_1.html",
        "https://www.ecfr.gov/current/title-15/subtitle-B/chapter-VII/subchapter-C/part-774/supplement-1-to-part-774",
    ),
    ("nvidia_vera_rubin_nvl72.html", "https://www.nvidia.com/en-us/data-center/vera-rubin-nvl72/"),
    ("nvidia_hgx_vera_rubin.html", "https://www.nvidia.com/en-us/data-center/hgx/"),
    ("trendforce_dram_price.html", "https://www.trendforce.com/price/dram"),
    ("trendforce_flash_price.html", "https://www.trendforce.com/price/flash"),
    ("trendforce_vera_rubin_800v_20260625.html", "https://www.trendforce.com/presscenter/news/20260625-13121.html"),
    ("trendforce_20260601_13070.html", "https://www.trendforce.com/presscenter/news/20260601-13070.html"),
    (
        "gartner_semiconductor_forecast_20260408.html",
        "https://www.gartner.com/en/newsroom/press-releases/2026-04-08-gartner-forecasts-worldwide-semiconductor-revenue-to-exceed-us-dollars-one-point-3-trillion-in-2026",
    ),
    ("wsts_recent_news_release.html", "https://www.wsts.org/76/Recent-News-Release"),
    (
        "sia_april_2026_sales.html",
        "https://www.semiconductors.org/global-semiconductor-sales-increase-11-month-to-month-in-april/",
    ),
    (
        "semi_300mm_fab_spending_20260401.html",
        "https://www.semi.org/en/semi-press-release/semi-projects-double-digit-growth-in-global-300mm-fab-equipment-spending-for-2026-and-2027",
    ),
    (
        "semi_equipment_sales_record_2027.html",
        "https://www.semi.org/en/semi-press-release/global-semiconductor-equipment-sales-projected-to-reach-a-record-of-156-billion-dollars-in-2027-semi-reports",
    ),
    (
        "yole_next_gen_dram_2026.html",
        "https://www.yolegroup.com/product/report/next-gen-dram-2026---focus-on-hbm-and-3d-dram/",
    ),
    (
        "skhynix_hbm4_development.html",
        "https://news.skhynix.com/sk-hynix-completes-worlds-first-hbm4-development-and-readies-mass-production/",
    ),
    ("skhynix_q1_2026_results.html", "https://news.skhynix.com/q1-2026-business-results/"),
    (
        "micron_hbm4_vera_rubin.html",
        "https://investors.micron.com/news-releases/news-release-details/micron-high-volume-production-hbm4-designed-nvidia-vera-rubin",
    ),
    ("micron_hbm4_vera_rubin.pdf", "https://investors.micron.com/node/50236/pdf"),
    (
        "samsung_hbm4e_gtc_2026.html",
        "https://semiconductor.samsung.com/news-events/news/samsung-unveils-hbm4e-showcasing-comprehensive-ai-solutions-nvidia-partnership-and-vision-at-nvidia-gtc-2026/",
    ),
    ("samsung_q1_2026_results.html", "https://news.samsung.com/global/samsung-electronics-announces-first-quarter-2026-results"),
    (
        "cxl_4_0_release_businesswire.html",
        "https://www.businesswire.com/news/home/20251118275848/en/CXL-Consortium-Releases-the-Compute-Express-Link-4.0-Specification-Increasing-Speed-and-Bandwidth",
    ),
]


def ensure_dirs() -> None:
    for path in [
        DATA,
        ANALYSIS,
        SOURCES / "market-data-20260626",
        SOURCES / "industry-refresh-20260626",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:+.1f}%"


def fetch_text(url: str, *, headers: dict[str, str] | None = None) -> tuple[str, bytes]:
    response = requests.get(url, headers=headers or {}, timeout=30)
    response.raise_for_status()
    encoding = response.encoding or "utf-8"
    return response.text if response.text else response.content.decode(encoding, errors="replace"), response.content


def fetch_tencent_quotes() -> tuple[str, list[dict[str, Any]]]:
    q = ",".join(f"{item['market']}{item['code']}" for item in TICKERS)
    url = f"https://qt.gtimg.cn/q={q}"
    text, raw = fetch_text(url)
    (SOURCES / "market-data-20260626" / "tencent_quote_20260626.txt").write_bytes(raw)

    entries: list[dict[str, Any]] = []
    pattern = re.compile(r'v_(?:sh|sz)(\d+)="([^"]*)"')
    by_code = {item["code"]: item for item in TICKERS}
    for code, body in pattern.findall(text):
        f = body.split("~")
        meta = by_code[code]
        total_shares = int(float(f[73])) if len(f) > 73 and f[73] else None
        float_shares = int(float(f[72])) if len(f) > 72 and f[72] else None
        total_mcap = float(f[45]) if len(f) > 45 and f[45] else None
        float_mcap = float(f[44]) if len(f) > 44 and f[44] else None
        entries.append(
            {
                "code": code,
                "name": f[1],
                "market": meta["market"],
                "quote_time": f[30],
                "close_price_cny": float(f[3]),
                "prev_close_cny": float(f[4]),
                "change_pct": float(f[32]),
                "high_cny": float(f[33]),
                "low_cny": float(f[34]),
                "turnover_value_cny": float(f[57]) * 10000 if len(f) > 57 and f[57] else None,
                "total_market_cap_100mn_cny": total_mcap,
                "float_market_cap_100mn_cny": float_mcap,
                "total_shares": total_shares,
                "float_shares": float_shares,
                "total_shares_100mn": total_shares / 100000000 if total_shares else None,
                "float_shares_100mn": float_shares / 100000000 if float_shares else None,
                "source": "Tencent qt.gtimg.cn batch quote",
                "source_url": url,
            }
        )
    return url, entries


def fetch_sina_quotes() -> tuple[str, str, dict[str, dict[str, Any]]]:
    q = ",".join(f"{item['market']}{item['code']}" for item in TICKERS)
    url = f"https://hq.sinajs.cn/list={q}"
    headers = {"Referer": "https://finance.sina.com.cn", "User-Agent": "Mozilla/5.0"}
    text, raw = fetch_text(url, headers=headers)
    (SOURCES / "market-data-20260626" / "sina_quote_20260626.txt").write_bytes(raw)
    parsed: dict[str, dict[str, Any]] = {}
    pattern = re.compile(r"var hq_str_(?:sh|sz)(\d+)=\"([^\"]*)\";")
    for code, body in pattern.findall(text):
        f = body.split(",")
        if len(f) < 32:
            continue
        parsed[code] = {
            "code": code,
            "name": f[0],
            "open_cny": float(f[1]),
            "prev_close_cny": float(f[2]),
            "close_price_cny": float(f[3]),
            "high_cny": float(f[4]),
            "low_cny": float(f[5]),
            "volume_shares": int(float(f[8])),
            "turnover_value_cny": float(f[9]),
            "quote_date": f[30],
            "quote_time": f[31],
            "source": "Sina hq.sinajs.cn batch quote",
            "source_url": url,
        }
    return url, text, parsed


def fetch_ths_forecasts() -> dict[str, dict[str, Any]]:
    forecasts: dict[str, dict[str, Any]] = {}
    raw_records: dict[str, list[dict[str, Any]]] = {}
    for item in TICKERS:
        code = item["code"]
        df = ak.stock_profit_forecast_ths(symbol=code)
        records = json.loads(df.to_json(orient="records", force_ascii=False))
        raw_records[code] = records
        row = next((r for r in records if str(r.get("年度")) == "2026"), None)
        if row:
            forecasts[code] = {
                "forecast_year": 2026,
                "institution_count": row.get("预测机构数"),
                "eps_min_cny": row.get("最小值"),
                "eps_mean_cny": row.get("均值"),
                "eps_max_cny": row.get("最大值"),
                "industry_avg_eps_cny": row.get("行业平均数"),
                "source": "AKShare stock_profit_forecast_ths / 同花顺盈利预测",
            }
    write_json(SOURCES / "market-data-20260626" / "ths_profit_forecast_20260626.json", raw_records)
    return forecasts


def build_market_and_valuation() -> tuple[dict[str, Any], dict[str, Any]]:
    tencent_url, tencent_quotes = fetch_tencent_quotes()
    _, _, sina_quotes = fetch_sina_quotes()
    ths = fetch_ths_forecasts()

    tencent_by_code = {row["code"]: row for row in tencent_quotes}
    rows = []
    weighted_legacy_upside = 0.0
    weighted_old_upside = 0.0
    for meta in TICKERS:
        code = meta["code"]
        quote = tencent_by_code[code]
        sina = sina_quotes.get(code, {})
        forecast = ths.get(code, {})
        close_price = quote["close_price_cny"]
        eps_mean = forecast.get("eps_mean_cny")
        shares_100mn = quote.get("total_shares_100mn")
        legacy_upside = meta["legacy_fv_mid"] / close_price - 1
        old_upside = meta["legacy_fv_mid"] / meta["report_price"] - 1
        weighted_legacy_upside += meta["weight_pct"] * legacy_upside / 100
        weighted_old_upside += meta["weight_pct"] * old_upside / 100
        consensus_net_profit = eps_mean * shares_100mn if eps_mean is not None and shares_100mn else None
        report_consensus_gap = (
            consensus_net_profit / meta["report_net_profit_2026_100mn"] - 1
            if consensus_net_profit is not None and meta["report_net_profit_2026_100mn"]
            else None
        )
        current_pe = close_price / eps_mean if eps_mean not in (None, 0) else None
        report_price_change = close_price / meta["report_price"] - 1
        sina_price_delta = sina.get("close_price_cny", close_price) - close_price if sina else None
        legacy_status = "SUSPEND_RATING_REBUILD_REQUIRED"
        if legacy_upside <= -0.30:
            legacy_status = "LEGACY_FAIR_VALUE_DEEPLY_BELOW_CURRENT_PRICE"
        elif legacy_upside <= -0.05:
            legacy_status = "LEGACY_FAIR_VALUE_BELOW_CURRENT_PRICE"
        rows.append(
            {
                **{k: meta[k] for k in meta},
                "current_price_cny": close_price,
                "current_quote_time_tencent": quote["quote_time"],
                "sina_cross_price_delta_cny": sina_price_delta,
                "total_shares_100mn": shares_100mn,
                "float_shares_100mn": quote.get("float_shares_100mn"),
                "total_market_cap_100mn_cny": quote.get("total_market_cap_100mn_cny"),
                "float_market_cap_100mn_cny": quote.get("float_market_cap_100mn_cny"),
                "ths_institution_count": forecast.get("institution_count"),
                "ths_eps_mean_2026_cny": eps_mean,
                "ths_eps_min_2026_cny": forecast.get("eps_min_cny"),
                "ths_eps_max_2026_cny": forecast.get("eps_max_cny"),
                "ths_net_profit_mean_2026_100mn_cny": consensus_net_profit,
                "current_pe_on_ths_mean": current_pe,
                "report_price_change_since_anchor": report_price_change,
                "old_implied_upside_on_report_price": old_upside,
                "legacy_fv_implied_upside_on_20260626_close": legacy_upside,
                "weighted_legacy_upside_contribution": meta["weight_pct"] * legacy_upside / 100,
                "report_net_profit_vs_ths_gap": report_consensus_gap,
                "rating_action": "暂停评级 / 待重估",
                "investability": "watchlist_only_until_full_source_and_valuation_refresh",
                "status": legacy_status,
            }
        )

    market_packet = {
        "case_id": CASE_ID,
        "run_date": RUN_DATE,
        "generated_at": datetime.now(CN_TZ).isoformat(timespec="seconds"),
        "declared_data_cutoff": RUN_TIMESTAMP,
        "sources": [
            {
                "name": "Tencent batch quote",
                "url": tencent_url,
                "capture_file": "sources/market-data-20260626/tencent_quote_20260626.txt",
            },
            {
                "name": "Sina batch quote cross-check",
                "url": f"https://hq.sinajs.cn/list={','.join(f'{i['market']}{i['code']}' for i in TICKERS)}",
                "capture_file": "sources/market-data-20260626/sina_quote_20260626.txt",
            },
            {
                "name": "THS profit forecast via AKShare",
                "url": "https://basic.10jqka.com.cn/",
                "capture_file": "sources/market-data-20260626/ths_profit_forecast_20260626.json",
            },
        ],
        "ticker_count": len(rows),
        "tickers": rows,
    }
    valuation_packet = {
        "case_id": CASE_ID,
        "run_date": RUN_DATE,
        "generated_at": market_packet["generated_at"],
        "decision": "suspend_all_legacy_ratings_until_full_valuation_rebuild",
        "old_weighted_upside_on_report_anchor": weighted_old_upside,
        "legacy_fv_weighted_upside_on_20260626_close": weighted_legacy_upside,
        "method_note": (
            "This packet does not publish new investable target prices. It rebuilds current "
            "price/share/market-cap/consensus anchors and shows the legacy fair-value package "
            "is stale under the latest close."
        ),
        "tickers": rows,
    }
    return market_packet, valuation_packet


def write_market_markdown(packet: dict[str, Any]) -> None:
    lines = [
        "# AI Storage Market Data Refresh - 2026-06-26",
        "",
        f"- Case: `{CASE_ID}`",
        f"- Generated at: {packet['generated_at']}",
        "- Sources: Tencent batch quote, Sina quote cross-check, THS profit forecast via AKShare.",
        "- Evidence boundary: Tencent/Sina are public quote endpoints, not Wind/Choice/iFind; THS EPS is a consensus proxy. Use as current public reset anchors, not as a Wind replacement.",
        "",
        "| Code | Name | Close CNY | Quote Time | Total Shares (100mn) | Market Cap (CNY100mn) | THS 26E EPS | Inst. | Current PE | Sina Delta |",
        "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in packet["tickers"]:
        lines.append(
            "| {code} | {name} | {price:.2f} | {time} | {shares:.2f} | {mcap:.2f} | {eps} | {inst} | {pe} | {delta} |".format(
                code=row["code"],
                name=row["name"],
                price=row["current_price_cny"],
                time=row["current_quote_time_tencent"],
                shares=row["total_shares_100mn"] or 0,
                mcap=row["total_market_cap_100mn_cny"] or 0,
                eps=f"{row['ths_eps_mean_2026_cny']:.2f}" if row["ths_eps_mean_2026_cny"] is not None else "n/a",
                inst=row["ths_institution_count"] or "n/a",
                pe=f"{row['current_pe_on_ths_mean']:.1f}x" if row["current_pe_on_ths_mean"] is not None else "n/a",
                delta=f"{row['sina_cross_price_delta_cny']:.4f}" if row["sina_cross_price_delta_cny"] is not None else "n/a",
            )
        )
    (DATA / "raw_market_data_20260626.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_valuation_markdown(packet: dict[str, Any]) -> None:
    lines = [
        "# AI Storage Valuation Reset - 2026-06-26",
        "",
        f"- Case: `{CASE_ID}`",
        f"- Generated at: {packet['generated_at']}",
        f"- Decision: `{packet['decision']}`",
        f"- Old report weighted upside on old anchors: {pct(packet['old_weighted_upside_on_report_anchor'] * 100)}",
        f"- Legacy fair-value weighted upside on 2026-06-26 close: {pct(packet['legacy_fv_weighted_upside_on_20260626_close'] * 100)}",
        "- Evidence boundary: this is a reset package. It suspends old recommendations; it does not create new investable target prices before the industry-source and broker-consensus refresh is complete.",
        "",
        "| Code | Name | Weight | Old Price | 06-26 Close | Old FV Mid | Old Upside | Reset Upside | THS 26E EPS | Current PE | Action |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in packet["tickers"]:
        lines.append(
            "| {code} | {name} | {w:.0f}% | {old:.2f} | {cur:.2f} | {fv:.2f} | {old_up} | {new_up} | {eps} | {pe} | {action} |".format(
                code=row["code"],
                name=row["name"],
                w=row["weight_pct"],
                old=row["report_price"],
                cur=row["current_price_cny"],
                fv=row["legacy_fv_mid"],
                old_up=pct(row["old_implied_upside_on_report_price"] * 100),
                new_up=pct(row["legacy_fv_implied_upside_on_20260626_close"] * 100),
                eps=f"{row['ths_eps_mean_2026_cny']:.2f}" if row["ths_eps_mean_2026_cny"] is not None else "n/a",
                pe=f"{row['current_pe_on_ths_mean']:.1f}x" if row["current_pe_on_ths_mean"] is not None else "n/a",
                action=row["rating_action"],
            )
        )
    (DATA / "current_valuation_reset_20260626.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def capture_industry_sources() -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    headers = {"User-Agent": "Mozilla/5.0 AStockResearch/1.0"}
    for filename, url in SOURCE_URLS:
        rel_path = Path("sources/industry-refresh-20260626") / filename
        out_path = BASE / rel_path
        status = "captured"
        error = None
        content_type = None
        status_code = None
        try:
            response = requests.get(url, headers=headers, timeout=40)
            status_code = response.status_code
            content_type = response.headers.get("content-type")
            out_path.write_bytes(response.content)
            if response.status_code >= 400:
                status = "http_error_captured"
        except Exception as exc:  # noqa: BLE001 - keep failed probe evidence.
            status = "failed"
            error = f"{type(exc).__name__}: {exc}"
            out_path.write_text(error + "\n", encoding="utf-8")
        data = out_path.read_bytes()
        manifest.append(
            {
                "file": str(rel_path),
                "url": url,
                "status": status,
                "http_status": status_code,
                "content_type": content_type,
                "size_bytes": len(data),
                "sha256": sha256_bytes(data),
                "error": error,
            }
        )
    return manifest


def write_source_manifest(manifest: list[dict[str, Any]]) -> None:
    payload = {
        "case_id": CASE_ID,
        "run_date": RUN_DATE,
        "generated_at": datetime.now(CN_TZ).isoformat(timespec="seconds"),
        "capture_count": len(manifest),
        "captured_count": sum(1 for item in manifest if item["status"] == "captured"),
        "http_error_count": sum(1 for item in manifest if item["status"] == "http_error_captured"),
        "failed_count": sum(1 for item in manifest if item["status"] == "failed"),
        "files": manifest,
    }
    write_json(DATA / "source_capture_manifest_20260626.json", payload)
    lines = [
        "# Source Capture Manifest - 2026-06-26",
        "",
        f"- Case: `{CASE_ID}`",
        f"- Generated at: {payload['generated_at']}",
        f"- Capture count: {payload['capture_count']} / captured={payload['captured_count']} / http_error={payload['http_error_count']} / failed={payload['failed_count']}",
        "",
        "| File | Status | HTTP | Size | SHA-256 | URL |",
        "|---|---:|---:|---:|---|---|",
    ]
    for item in manifest:
        lines.append(
            f"| `{item['file']}` | {item['status']} | {item['http_status'] or ''} | {item['size_bytes']} | `{item['sha256']}` | {item['url']} |"
        )
    (DATA / "source_capture_manifest_20260626.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_valuation_audit(packet: dict[str, Any]) -> None:
    worst = sorted(
        packet["tickers"],
        key=lambda r: r["legacy_fv_implied_upside_on_20260626_close"],
    )[:5]
    lines = [
        "# Valuation Audit - AI Storage Refresh 2026-06-26",
        "",
        "## Executive Verdict",
        "",
        "- Publishability: BLOCKED",
        "- Reason: ch01/ch08/ch11 still used 2026-06-24 price anchors and old fair values. The 2026-06-26 public close turns the prior +6% weighted upside into a deep negative reset.",
        f"- Old weighted upside: {pct(packet['old_weighted_upside_on_report_anchor'] * 100)}",
        f"- Reset weighted upside using legacy FV and 2026-06-26 close: {pct(packet['legacy_fv_weighted_upside_on_20260626_close'] * 100)}",
        "",
        "## S-Level Findings",
        "",
        "1. Current-price anchor failure: all previous ratings/actions must be suspended until a complete fair-value model is rebuilt from current price, independently sourced share count, market cap, and refreshed consensus.",
        "2. Circular share-count logic: the old report used market cap divided by current price as the share-count anchor. The reset packet uses observed Tencent total-share fields and treats them as public quote data requiring Wind/Choice/iFind confirmation before publication.",
        "3. Consensus drift: THS 2026E EPS differs from the old report for several names; any AStock override must be shown as a separate scenario with bridge and haircut.",
        "",
        "## Worst Legacy Fair-Value Gaps",
        "",
        "| Code | Name | 06-26 Close | Legacy FV Mid | Reset Upside | THS 26E EPS | Current PE |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in worst:
        lines.append(
            "| {code} | {name} | {cur:.2f} | {fv:.2f} | {up} | {eps} | {pe} |".format(
                code=row["code"],
                name=row["name"],
                cur=row["current_price_cny"],
                fv=row["legacy_fv_mid"],
                up=pct(row["legacy_fv_implied_upside_on_20260626_close"] * 100),
                eps=f"{row['ths_eps_mean_2026_cny']:.2f}" if row["ths_eps_mean_2026_cny"] is not None else "n/a",
                pe=f"{row['current_pe_on_ths_mean']:.1f}x" if row["current_pe_on_ths_mean"] is not None else "n/a",
            )
        )
    lines.extend(
        [
            "",
            "## Repair Requirement",
            "",
            "- Reader-facing tables may show current price, market cap, shares, THS EPS, and legacy-FV reset gap.",
            "- They must not show investable buy/add/overweight actions until the full source refresh and valuation-model rebuild are complete.",
            "- Final target price/fair-value ranges require refreshed industry assumptions, broker target history, current overseas comps, and evidence-quality tags.",
        ]
    )
    (ANALYSIS / "valuation_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ensure_dirs()
    market_packet, valuation_packet = build_market_and_valuation()
    write_json(DATA / "raw_market_data_20260626.json", market_packet)
    write_market_markdown(market_packet)
    write_json(DATA / "current_valuation_reset_20260626.json", valuation_packet)
    write_valuation_markdown(valuation_packet)
    write_valuation_audit(valuation_packet)
    write_source_manifest(capture_industry_sources())
    print(json.dumps(
        {
            "case_id": CASE_ID,
            "run_date": RUN_DATE,
            "ticker_count": len(valuation_packet["tickers"]),
            "legacy_fv_weighted_upside": valuation_packet["legacy_fv_weighted_upside_on_20260626_close"],
        },
        ensure_ascii=False,
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

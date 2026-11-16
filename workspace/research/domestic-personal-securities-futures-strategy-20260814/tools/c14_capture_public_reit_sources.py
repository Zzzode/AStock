#!/usr/bin/env python3
"""Capture frozen primary evidence for the C14 public-infrastructure-REIT study.

The utility is deliberately read-only toward every external system.  It
collects named public documents and public SSE responses, computes a bounded
historical diagnostic from the frozen files, and writes research-only
artifacts.  It never accesses a customer account, evaluates an individual,
creates an order, or produces a portfolio allocation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import re
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import requests


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
DATE_TAG = "20260815"
SOURCE_DIR = CASE_DIR / "sources" / f"c14-public-infrastructure-reit-508000-{DATE_TAG}"
MANIFEST_JSON = SOURCE_DIR / "manifest.json"
MANIFEST_MD = SOURCE_DIR / "manifest.md"
RULEBOOK_JSON = CASE_DIR / "analysis" / f"c14_public_reit_rulebook_{DATE_TAG}.json"
RULEBOOK_MD = CASE_DIR / "analysis" / f"c14_public_reit_rulebook_{DATE_TAG}.md"
FEASIBILITY_JSON = CASE_DIR / "analysis" / f"c14_public_reit_feasibility_{DATE_TAG}.json"
FEASIBILITY_MD = CASE_DIR / "analysis" / f"c14_public_reit_feasibility_{DATE_TAG}.md"
SOURCE_FREEZE_SCHEMA = "research_source_freeze_control.v1"
PRODUCT_CODE = "508000"
PRODUCT_NAME = "华安张江产业园封闭式基础设施证券投资基金"
DATA_CUTOFF = date(2026, 8, 14)
HURDLE = 0.05

HEADERS = {
    "User-Agent": "Mozilla/5.0 (C14 public-infrastructure-REIT feasibility research; read-only)",
    "Referer": "https://www.sse.com.cn/reits/assortment/prices/detail/price/?code=508000",
    "Accept": "text/html,application/pdf,application/json,*/*;q=0.8",
}

DOCUMENTS: tuple[dict[str, str], ...] = (
    {
        "filename": "csrc_public_infrastructure_reit_guideline_announcement_20200807.html",
        "publisher": "China Securities Regulatory Commission",
        "title": "CSRC Announcement No. 54: Public Infrastructure Securities Investment Fund Guidelines (Trial)",
        "document_date": "2020-08-07",
        "url": "https://www.csrc.gov.cn/csrc/c101877/c1029531/content.shtml",
        "format": "html",
        "purpose": "Primary regulatory product-structure and distribution-framework evidence.",
    },
    {
        "filename": "sse_public_infrastructure_reit_business_rules_20210129.html",
        "publisher": "Shanghai Stock Exchange",
        "title": "SSE Public Infrastructure Securities Investment Fund (REITs) Business Rules (Trial)",
        "document_date": "2021-01-29",
        "url": "https://www.sse.com.cn/reits/regulation/rules/c/c_20210129_5314426.shtml",
        "format": "html",
        "purpose": "Primary exchange evidence for closed-end structure, exchange-trading route, risk disclosure and investor-account boundary.",
    },
    {
        "filename": "sse_first_public_reits_listing_20210621.html",
        "publisher": "Shanghai Stock Exchange",
        "title": "First five public infrastructure REITs listed on SSE",
        "document_date": "2021-06-21",
        "url": "https://www.sse.com.cn/aboutus/mediacenter/hotandd/c/c_20210621_5495045.shtml",
        "format": "html",
        "purpose": "Primary date and market-route evidence that 508000 was among the first listed SSE public infrastructure REITs.",
    },
    {
        "filename": "508000_updated_prospectus_20241104.pdf",
        "publisher": "Shanghai Stock Exchange disclosure / Huaan Fund Management",
        "title": "Updated prospectus for Huaan Zhangjiang Industrial Park REIT",
        "document_date": "2024-11-04",
        "url": "https://www.sse.com.cn/disclosure/fund/announcement/c/new/2024-11-04/508000_20241104_UHUJ.pdf",
        "format": "pdf",
        "purpose": "Representative-product legal structure, fee, cash-flow, risk and operating-arrangement evidence.",
    },
    {
        "filename": "508000_product_summary_20240628.pdf",
        "publisher": "Shanghai Stock Exchange disclosure / Huaan Fund Management",
        "title": "Updated product summary for Huaan Zhangjiang Industrial Park REIT",
        "document_date": "2024-06-28",
        "url": "https://www.sse.com.cn/disclosure/fund/announcement/c/new/2024-06-28/508000_20240628_DTAU.pdf",
        "format": "pdf",
        "purpose": "Concise dated product identity, closed-operation, exchange-listing, transfer-custody and risk evidence.",
    },
    {
        "filename": "508000_2025_annual_report_20260327.pdf",
        "publisher": "Shanghai Stock Exchange disclosure / Huaan Fund Management",
        "title": "Huaan Zhangjiang Industrial Park REIT 2025 annual report",
        "document_date": "2026-03-27",
        "url": "https://www.sse.com.cn/disclosure/fund/announcement/c/new/2026-03-27/508000_20260327_HFJ9.pdf",
        "format": "pdf",
        "purpose": "Representative-product asset, operating cash-flow, distribution, expense and risk evidence.",
    },
    {
        "filename": "508000_2024_distribution_announcement_20250415.pdf",
        "publisher": "Shanghai Stock Exchange disclosure / Huaan Fund Management",
        "title": "Huaan Zhangjiang Industrial Park REIT distribution announcement",
        "document_date": "2025-04-15",
        "url": "https://www.sse.com.cn/disclosure/fund/announcement/c/new/2025-04-15/508000_20250415_ATW2.pdf",
        "format": "pdf",
        "purpose": "Product-level cross-check for a cash-distribution amount, NAV and distribution-date mechanics.",
    },
)


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _repo_relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _record(path: Path) -> dict[str, Any]:
    return {"path": _repo_relative(path), "bytes": path.stat().st_size, "sha256": _sha256(path)}


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() == content:
        return
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(content)
    temporary.replace(path)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _atomic_write(path, (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def _write_text(path: Path, text: str) -> None:
    _atomic_write(path, text.encode("utf-8"))


def _validate_document(content: bytes, descriptor: dict[str, str]) -> None:
    if len(content) < 500:
        raise ValueError(f"document unexpectedly short: {descriptor['filename']}")
    if descriptor["format"] == "pdf" and not content.startswith(b"%PDF"):
        raise ValueError(f"document is not a PDF: {descriptor['filename']}")
    if descriptor["format"] == "html":
        head = content[:5000].decode("utf-8", errors="ignore").lower()
        if "safeline_bot_challenge" in head or "<title>web 应用防火墙" in head:
            raise ValueError(f"WAF response cannot be retained: {descriptor['filename']}")


def _price_url() -> str:
    return (
        "https://yunhq.sse.com.cn:32042/v1/sh1/dayk/508000?callback=c14price"
        "&select=date%2Copen%2Chigh%2Clow%2Cclose%2Cvolume&begin=0&end=5000"
    )


def _distribution_url() -> str:
    return (
        "https://query.sse.com.cn/commonSoaQuery.do?isPagination=true&sqlId=REITS_FH"
        "&fundCode=508000&pageHelp.pageSize=1000&pageHelp.cacheSize=1&pageHelp.pageNo=1"
        "&pageHelp.beginPage=1&pageHelp.endPage=5&jsonCallBack=c14distribution"
    )


def _nav_url() -> str:
    return (
        "https://query.sse.com.cn/commonSoaQuery.do?isPagination=true&sqlId=REITS_JZ"
        "&fundCode=508000&order=desc&pageHelp.pageSize=1000&pageHelp.cacheSize=1&pageHelp.pageNo=1"
        "&pageHelp.beginPage=1&pageHelp.endPage=5&jsonCallBack=c14nav"
    )


def _parse_jsonp(content: bytes, callback: str) -> dict[str, Any]:
    decoded = content.decode("utf-8")
    matched = re.fullmatch(rf"{re.escape(callback)}\((.*)\)", decoded, flags=re.DOTALL)
    if not matched:
        raise ValueError(f"official response is not expected JSONP callback={callback}")
    return json.loads(matched.group(1))


def _parse_price(content: bytes) -> dict[str, Any]:
    payload = _parse_jsonp(content, "c14price")
    if str(payload.get("code")) != PRODUCT_CODE or int(payload.get("begin", -1)) != 0:
        raise ValueError("SSE price response code or begin field differs")
    rows = payload.get("kline")
    if not isinstance(rows, list) or not rows or len(rows) != int(payload.get("total", -1)):
        raise ValueError("SSE price response is empty or incomplete")
    if int(payload.get("end", -1)) != len(rows):
        raise ValueError("SSE price response end count differs")
    for row in rows:
        if not isinstance(row, list) or len(row) < 6 or len(str(row[0])) != 8 or float(row[4]) <= 0:
            raise ValueError("SSE price response has an invalid row")
    return payload


def _parse_distribution(content: bytes) -> dict[str, Any]:
    payload = _parse_jsonp(content, "c14distribution")
    rows = payload.get("result")
    if not isinstance(rows, list) or not rows:
        raise ValueError("SSE distribution response is empty")
    for row in rows:
        if str(row.get("fundCode")) != PRODUCT_CODE or float(row.get("fundDividends", 0)) < 0:
            raise ValueError("SSE distribution response has an invalid row")
        date.fromisoformat(str(row.get("exrightDate")))
        date.fromisoformat(str(row.get("rightsRegistDate")))
    total = payload.get("pageHelp", {}).get("total")
    if int(total) != len(rows):
        raise ValueError("SSE distribution response is incomplete")
    return payload


def _parse_nav(content: bytes) -> dict[str, Any]:
    payload = _parse_jsonp(content, "c14nav")
    if payload.get("sqlId") != "REITS_JZ" or str(payload.get("securityCode", "")) not in {"", PRODUCT_CODE}:
        raise ValueError("SSE NAV response differs from query")
    return payload


def _runtime_provenance() -> dict[str, str]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True, check=True
        )
        git_commit = result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        git_commit = "not_available"
    return {
        "git_commit_at_runtime": git_commit,
        "script_path": _repo_relative(Path(__file__).resolve()),
        "script_sha256": _sha256(Path(__file__).resolve()),
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "requests_version": str(getattr(requests, "__version__", "not_reported")),
    }


def _capture() -> None:
    if SOURCE_DIR.exists() or MANIFEST_JSON.exists():
        raise FileExistsError("C14 source batch already exists; use --rebuild-derived or --verify-only")
    staged: list[tuple[Path, bytes, dict[str, Any]]] = []
    times: list[str] = []
    for descriptor in DOCUMENTS:
        response = requests.get(descriptor["url"], headers=HEADERS, timeout=30)
        if response.status_code != 200:
            raise RuntimeError(f"source download failed {response.status_code}: {descriptor['url']}")
        _validate_document(response.content, descriptor)
        retrieved_at = datetime.now(timezone.utc).isoformat()
        staged.append(
            (
                SOURCE_DIR / descriptor["filename"],
                response.content,
                {
                    **descriptor,
                    "retrieved_at": retrieved_at,
                    "http_status": response.status_code,
                    "content_type": response.headers.get("content-type", "not_reported"),
                },
            )
        )
        times.append(retrieved_at)

    responses = (
        (
            "sse_508000_daily_market_price_begin0_end5000.jsonp",
            _price_url(),
            "c14price",
            _parse_price,
            "SSE daily market-price response for 508000",
            "Official retrospective daily OHLCV market-price response. It does not state its adjustment basis, historic available_at, bid/ask, depth, fill, tax, account or broker-cost fields.",
        ),
        (
            "sse_508000_distribution_history_page1.jsonp",
            _distribution_url(),
            "c14distribution",
            _parse_distribution,
            "SSE public REIT distribution-history response for 508000",
            "Official retrospective public distribution-history response. It contains per-share cash distribution rows and ex-right dates, but no personal tax, cash-credit, entitlement or reinvestment record.",
        ),
        (
            "sse_508000_nav_history_page1.jsonp",
            _nav_url(),
            "c14nav",
            _parse_nav,
            "SSE public REIT NAV-history response for 508000",
            "A contemporaneously captured query response. An empty result is an endpoint observation only; it does not prove NAV never existed elsewhere or replace a historical NAV ledger.",
        ),
    )
    for filename, url, callback, parser, title, capture_note in responses:
        response = requests.get(url, headers=HEADERS, timeout=30)
        if response.status_code != 200:
            raise RuntimeError(f"SSE data response failed {response.status_code}: {url}")
        payload = parser(response.content)
        retrieved_at = datetime.now(timezone.utc).isoformat()
        metadata: dict[str, Any] = {
            "publisher": "Shanghai Stock Exchange",
            "title": title,
            "document_date": f"retrospective response captured {DATE_TAG}",
            "url": url,
            "format": "jsonp",
            "retrieved_at": retrieved_at,
            "http_status": response.status_code,
            "content_type": response.headers.get("content-type", "not_reported"),
            "jsonp_callback": callback,
            "capture_note": capture_note,
        }
        if callback == "c14price":
            metadata.update(
                {
                    "response_total": int(payload["total"]),
                    "response_rows": len(payload["kline"]),
                    "first_trade_date": str(payload["kline"][0][0]),
                    "last_trade_date": str(payload["kline"][-1][0]),
                }
            )
        elif callback == "c14distribution":
            metadata.update(
                {
                    "response_total": int(payload["pageHelp"]["total"]),
                    "response_rows": len(payload["result"]),
                    "first_exright_date": min(row["exrightDate"] for row in payload["result"]),
                    "last_exright_date": max(row["exrightDate"] for row in payload["result"]),
                }
            )
        else:
            metadata.update({"response_total": int(payload.get("pageHelp", {}).get("total", 0) or 0)})
        staged.append((SOURCE_DIR / filename, response.content, metadata))
        times.append(retrieved_at)

    SOURCE_DIR.mkdir(parents=True, exist_ok=False)
    for path, content, _ in staged:
        _atomic_write(path, content)
    files = [
        {
            **_record(path),
            **metadata,
            "capture_note": metadata.get(
                "capture_note",
                "Read-only official document capture. It supports bounded research only and does not establish historic availability, personal access, an order, a holding, a cost ledger or an action.",
            ),
        }
        for path, _, metadata in staged
    ]
    manifest = {
        "schema_version": "c14_public_infrastructure_reit_source_manifest.v1",
        "case_id": CASE_DIR.name,
        "capture_batch": SOURCE_DIR.name,
        "captured_at": min(times),
        "purpose": "Primary official public-infrastructure-REIT framework and a representative 508000 product/market-route evidence batch. It supports a strict-return feasibility review only, never an external action.",
        "source_quality": "primary_official_regulatory_exchange_manager_disclosure_and_public_market_response",
        "protocol_status": "research_only_no_personal_operability_or_return_admission",
        "files": files,
        "limitations": [
            "The named legal and product disclosures are dated and cannot establish a current individual securities-account, risk-disclosure, broker commission, tax, order-routing, settlement or fill outcome.",
            "The daily SSE response is retrospectively retrieved, has no disclosed adjustment basis or historic available_at field, and is not an entitled point-in-time total-return or execution dataset.",
            "The distribution response contains public per-share cash-distribution and ex-right-date fields, but it does not prove personal cash receipt, tax treatment, reinvestment, transfer-custody timing or transaction costs.",
            "The captured empty NAV endpoint response is not proof that no NAV data exists in any source; it only records this official public query's captured result.",
            "No source in this batch creates a return guarantee, suitability result, allocation, holding, order, account action or external contact authorization.",
        ],
        "source_freeze": {
            "schema_version": SOURCE_FREEZE_SCHEMA,
            "seal_status": "case_local_hash_control_only",
            "sealed_at": datetime.now(timezone.utc).isoformat(),
            "frozen_files": [_record(path) for path, _, _ in staged],
            "runtime_provenance": _runtime_provenance(),
            "boundary": "Local hashes reveal retained-file mismatch only. They are not external notarization, historic publication proof, data entitlement, individual-account proof, total-return proof or execution validation.",
        },
    }
    _write_json(MANIFEST_JSON, manifest)
    lines = [
        "# C14 公募基础设施 REITs 一手来源清单",
        "",
        f"- 批次：`{SOURCE_DIR.name}`",
        f"- 抓取时间：`{manifest['captured_at']}`",
        "- 方法：对列明的证监会、上交所和基金管理人披露文件及上交所公开查询接口进行匿名、只读 HTTPS 请求。",
        "- 边界：文件哈希只用于本地完整性核验；它们不证明时点可得性、净总回报、个人账户权限、费税、成交或任何外部行动。",
        "",
        "| 文件 | 发布者 | 日期／覆盖 | SHA-256 |",
        "|---|---|---|---|",
    ]
    for entry in files:
        coverage = entry.get("document_date", "not_reported")
        if entry.get("first_trade_date"):
            coverage = f"{entry['first_trade_date']}–{entry['last_trade_date']}（{entry['response_rows']} 行）"
        if entry.get("first_exright_date"):
            coverage = f"{entry['first_exright_date']}–{entry['last_exright_date']}（{entry['response_rows']} 行）"
        lines.append(
            f"| {Path(entry['path']).name} | {entry['publisher']} | {coverage} | `{entry['sha256']}` |"
        )
    lines.extend(
        [
            "",
            "`tools/verify_source_manifests.py` 会逐一核验本批保留文件的路径、字节数和 SHA-256。公开行情或分配记录不等于可审计的个人净回报或实际成交记录。",
            "",
        ]
    )
    _write_text(MANIFEST_MD, "\n".join(lines))


def _load_manifest() -> dict[str, Any]:
    if not MANIFEST_JSON.is_file():
        raise FileNotFoundError(f"C14 source manifest is absent: {MANIFEST_JSON}")
    manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    files = manifest.get("files")
    frozen = manifest.get("source_freeze", {}).get("frozen_files")
    if not isinstance(files, list) or not isinstance(frozen, list):
        raise ValueError("C14 manifest has no file or source-freeze records")
    names = {Path(str(item.get("path", ""))).name for item in files}
    expected_names = {item["filename"] for item in DOCUMENTS} | {
        "sse_508000_daily_market_price_begin0_end5000.jsonp",
        "sse_508000_distribution_history_page1.jsonp",
        "sse_508000_nav_history_page1.jsonp",
    }
    if names != expected_names:
        raise ValueError("C14 source-manifest names differ from the fixed source definition")
    frozen_by_path = {str(item.get("path")): item for item in frozen}
    manifest_by_path = {str(item.get("path")): item for item in files}
    if set(frozen_by_path) != set(manifest_by_path):
        raise ValueError("C14 source-freeze paths differ from manifest paths")
    for path_key, entry in manifest_by_path.items():
        path = (REPO_ROOT / path_key).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"C14 raw source absent: {path}")
        if path.stat().st_size != int(entry.get("bytes", -1)):
            raise ValueError(f"C14 raw source size mismatch: {path}")
        if _sha256(path) != entry.get("sha256"):
            raise ValueError(f"C14 raw source hash mismatch: {path}")
        frozen_entry = frozen_by_path[path_key]
        if {key: entry.get(key) for key in ("path", "bytes", "sha256")} != {
            key: frozen_entry.get(key) for key in ("path", "bytes", "sha256")
        }:
            raise ValueError(f"C14 frozen record mismatch: {path}")
    return manifest


def _source_file(filename: str) -> Path:
    path = SOURCE_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"C14 source is absent: {path}")
    return path


def _load_prices() -> dict[date, float]:
    payload = _parse_price(_source_file("sse_508000_daily_market_price_begin0_end5000.jsonp").read_bytes())
    prices: dict[date, float] = {}
    for row in payload["kline"]:
        raw_date = str(row[0])
        observed = date(int(raw_date[:4]), int(raw_date[4:6]), int(raw_date[6:]))
        close = float(row[4])
        if observed in prices or close <= 0:
            raise ValueError("C14 price ledger has duplicate date or non-positive close")
        prices[observed] = close
    if min(prices) != date(2021, 6, 21) or max(prices) != DATA_CUTOFF:
        raise ValueError("C14 price coverage differs from the fixed captured response boundary")
    return prices


def _load_distributions() -> list[dict[str, Any]]:
    payload = _parse_distribution(_source_file("sse_508000_distribution_history_page1.jsonp").read_bytes())
    rows: list[dict[str, Any]] = []
    seen: set[date] = set()
    for item in payload["result"]:
        exright_date = date.fromisoformat(str(item["exrightDate"]))
        if exright_date in seen:
            raise ValueError("C14 distribution ledger has duplicate ex-right date")
        seen.add(exright_date)
        cash_per_share = float(item["fundDividends"])
        if cash_per_share < 0:
            raise ValueError("C14 distribution ledger has negative cash distribution")
        rows.append(
            {
                "fund_code": str(item["fundCode"]),
                "income_year": str(item["year"]),
                "rights_registration_date": str(item["rightsRegistDate"]),
                "exright_date": exright_date.isoformat(),
                "cash_distribution_per_share_cny": cash_per_share,
            }
        )
    rows.sort(key=lambda item: item["exright_date"])
    if len(rows) != 9:
        raise ValueError("C14 distribution response has an unexpected number of rows")
    return rows


def _nav_endpoint_summary() -> dict[str, Any]:
    payload = _parse_nav(_source_file("sse_508000_nav_history_page1.jsonp").read_bytes())
    result = payload.get("result")
    total = int(payload.get("pageHelp", {}).get("total", 0) or 0)
    if result not in (None, []) or total != 0:
        raise ValueError("C14 captured NAV endpoint no longer matches its fixed empty-result observation")
    return {
        "captured_endpoint_result_rows": 0,
        "interpretation": "该上交所公开查询在本次抓取时返回空记录。它只构成端点观察，不能证明其他位置不存在历史净值，也不能替代逐日净值账本。",
    }


def _last_close_on_or_before(prices: dict[date, float], target: date) -> tuple[date, float]:
    candidates = [observed for observed in prices if observed <= target]
    if not candidates:
        raise ValueError(f"no official close exists on or before {target.isoformat()}")
    observed = max(candidates)
    return observed, prices[observed]


def _add_years(observed: date, years: int) -> date:
    try:
        return observed.replace(year=observed.year + years)
    except ValueError:
        return observed.replace(year=observed.year + years, month=2, day=28)


def _cash_between(distributions: list[dict[str, Any]], start: date, end: date) -> tuple[float, list[dict[str, Any]]]:
    included = [
        item
        for item in distributions
        if start < date.fromisoformat(item["exright_date"]) <= end
    ]
    return sum(float(item["cash_distribution_per_share_cny"]) for item in included), included


def _annual_rows(prices: dict[date, float], distributions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for year in range(2022, 2026):
        start_observation, start_close = _last_close_on_or_before(prices, date(year, 1, 1))
        end_observation, end_close = _last_close_on_or_before(prices, date(year, 12, 31))
        cash, cash_events = _cash_between(distributions, start_observation, end_observation)
        gross_return = (end_close + cash) / start_close - 1.0
        rows.append(
            {
                "year": year,
                "start_observation_date": start_observation.isoformat(),
                "start_close_cny": start_close,
                "end_observation_date": end_observation.isoformat(),
                "end_close_cny": end_close,
                "cash_distribution_per_share_cny": cash,
                "cash_event_count": len(cash_events),
                "cash_event_exright_dates": [item["exright_date"] for item in cash_events],
                "gross_cost_free_cash_return": gross_return,
                "gross_cost_free_cash_return_pct": gross_return * 100.0,
                "meets_5pct_gross_diagnostic": gross_return >= HURDLE,
            }
        )
    return rows


def _rolling_rows(prices: dict[date, float], distributions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for start_observation in sorted(prices):
        nominal_end = _add_years(start_observation, 5)
        if nominal_end > DATA_CUTOFF:
            continue
        end_observation, end_close = _last_close_on_or_before(prices, nominal_end)
        start_close = prices[start_observation]
        cash, cash_events = _cash_between(distributions, start_observation, end_observation)
        value_factor = (end_close + cash) / start_close
        if value_factor <= 0:
            raise ValueError("C14 rolling gross value factor is not positive")
        annualized_return = math.pow(value_factor, 1.0 / 5.0) - 1.0
        rows.append(
            {
                "start_observation_date": start_observation.isoformat(),
                "nominal_five_year_end_date": nominal_end.isoformat(),
                "end_observation_date": end_observation.isoformat(),
                "start_close_cny": start_close,
                "end_close_cny": end_close,
                "cash_distribution_per_share_cny": cash,
                "cash_event_count": len(cash_events),
                "gross_cost_free_cash_value_factor": value_factor,
                "gross_cost_free_cash_annualized_return": annualized_return,
                "gross_cost_free_cash_annualized_return_pct": annualized_return * 100.0,
                "meets_5pct_gross_diagnostic": annualized_return >= HURDLE,
            }
        )
    if not rows:
        raise ValueError("C14 has no available five-calendar-year diagnostic window")
    return rows


def _replay(prices: dict[date, float], distributions: list[dict[str, Any]]) -> dict[str, Any]:
    annual = _annual_rows(prices, distributions)
    rolling = _rolling_rows(prices, distributions)
    annual_failures = [row for row in annual if not row["meets_5pct_gross_diagnostic"]]
    rolling_failures = [row for row in rolling if not row["meets_5pct_gross_diagnostic"]]
    worst_annual = min(annual, key=lambda row: row["gross_cost_free_cash_return"])
    worst_rolling = min(rolling, key=lambda row: row["gross_cost_free_cash_annualized_return"])
    first_rolling = rolling[0]
    return {
        "replay_id": "DPSFS-C14-508000-GROSS-CASH-v1",
        "classification": "post_observation_fixed_product_bounded_gross_cash_diagnostic",
        "data_cutoff": DATA_CUTOFF.isoformat(),
        "selection_rule": "代表品种固定为上交所首批上市的 508000；不在公募 REITs、基础资产类别、代码、起止日或费用假设之间作事后替换。该选择只用于代表性路线审查，不覆盖整个公募 REITs 市场。",
        "annual_protocol": {
            "population": "2022–2025 四个完整日历年；2021 年上市后不完整、2026 年截至数据日不完整，均不纳入年度检验。",
            "start_rule": "每年 1 月 1 日当日或之前的最后一个官方收盘价；对 2022 年即 2021-12-31 收盘价。",
            "end_rule": "每年 12 月 31 日当日或之前的最后一个官方收盘价。",
            "cash_rule": "在起点观察日之后、终点观察日当天或之前的每笔官方除权日现金分配，按每份累加并保留为现金；不做红利再投资。",
            "formula": "(期末收盘价 + 区间每份现金分配之和) / 起点收盘价 - 1。",
        },
        "rolling_five_year_protocol": {
            "population": "在 2026-08-14 数据日之前，所有能够从官方交易日起点走满五个日历年的窗口；终点若非交易日，使用该日或之前最后一个官方收盘价并持有至名义终点。",
            "cash_rule": "从起点观察日之后至终点观察日当天或之前的官方除权日现金分配按每份累加并保留为现金；不做红利再投资。",
            "formula": "[((期末收盘价 + 区间每份现金分配之和) / 起点收盘价)^(1/5)] - 1。",
        },
        "cost_model": "零交易成本、零税费、零账户费用、零滑点；不是个人净成本模型。",
        "interpretation_boundary": "结果是冻结官方价格与分配行的有界、成本为零、现金不再投资诊断。上交所日价端点未说明复权口径，且没有个人费税、账户、报价或成交账本；因此这些结果不构成净总回报、业绩承诺、可执行性或正式策略回放。",
        "annual_rows": annual,
        "available_rolling_five_year_rows": rolling,
        "summary": {
            "annual_window_count": len(annual),
            "annual_gross_failure_count": len(annual_failures),
            "annual_all_pass_gross_diagnostic": not annual_failures,
            "worst_annual_gross_row": worst_annual,
            "rolling_five_year_window_count": len(rolling),
            "rolling_five_year_gross_failure_count": len(rolling_failures),
            "rolling_five_year_all_pass_gross_diagnostic": not rolling_failures,
            "first_available_rolling_five_year_row": first_rolling,
            "worst_rolling_five_year_gross_row": worst_rolling,
        },
    }


def _rulebook_payload(manifest: dict[str, Any], replay: dict[str, Any], nav_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": "DPSFS-C14-PUBLIC-REIT-RULEBOOK-v1",
        "as_of": DATE_TAG,
        "status": "RESEARCH_ONLY_BOUNDED_GROSS_DIAGNOSTIC",
        "portfolio_q": 0,
        "research_only": True,
        "representative_route": {
            "product_code": PRODUCT_CODE,
            "product_name": PRODUCT_NAME,
            "market_route": "上交所上市封闭式基础设施 REITs 的场内份额价格与公开现金分配记录。",
            "why_this_product": "508000 于 2021-06-21 作为上交所首批五只基础设施公募 REITs 之一上市，拥有本次公开端点能够冻结的上市后日价与分配行；这不是全市场筛选或个人操作指令。",
        },
        "strict_standard": {
            "hurdle": HURDLE,
            "definition": "每个完整日历年度的个人净后成本回报，以及每个可得滚动五年窗口的个人净后成本年化回报，均须不低于 5%。",
            "gross_diagnostic_not_substitute": "成本为零的价格加现金诊断不是个人净后成本回报；任何费用、税负、点差、延迟、无法成交或账户限制均未被抵销。",
        },
        "frozen_replay": replay,
        "nav_endpoint_observation": nav_summary,
        "source_manifest": {
            "path": _repo_relative(MANIFEST_JSON),
            "sha256": _sha256(MANIFEST_JSON),
            "capture_batch": manifest["capture_batch"],
        },
        "no_action_statement": "本规则书不授权开户、风险测评、转托管、买卖、委托、联系券商、现金划转或任何外部行动。",
    }


def _feasibility_payload(manifest: dict[str, Any], replay: dict[str, Any], nav_summary: dict[str, Any]) -> dict[str, Any]:
    annual_summary = replay["summary"]
    annual_failures = [
        {"year": row["year"], "gross_cost_free_cash_return": row["gross_cost_free_cash_return"]}
        for row in replay["annual_rows"]
        if not row["meets_5pct_gross_diagnostic"]
    ]
    return {
        "artifact_class": "research_feasibility_conclusion",
        "schema_version": "c14_public_reit_feasibility.v1",
        "as_of": DATE_TAG,
        "status": "NOT_FEASIBLE_FOR_STRICT_5PCT_OR_PERSONAL_EXECUTION",
        "portfolio_q": 0,
        "research_only": True,
        "formal_decision_eligible": False,
        "backtest_run": True,
        "backtest_definition": "已运行固定品种、固定端点、成本为零且现金不再投资的有限历史诊断；它不是个人净后成本回测，也不是策略或行动资格。",
        "return_result": None,
        "return_result_reason": "个人净后成本回报不可测：冻结来源没有个人账户费税、经纪佣金、报价、成交、转托管、现金到账或数据复权口径的完整历史账本。",
        "strict_5pct_test": {
            "hurdle": HURDLE,
            "net_after_cost_status": "NOT_ESTABLISHED_AND_NOT_ADMITTED",
            "net_after_cost_decision": "没有任何净后成本年度或滚动五年结果可通过严格门槛；因此 q=0。",
            "gross_cost_free_diagnostic": {
                "status": "FAILS_IN_MULTIPLE_COMPLETE_YEARS_AND_ALL_AVAILABLE_FIVE_YEAR_WINDOWS",
                "annual_failure_count": annual_summary["annual_gross_failure_count"],
                "annual_failures": annual_failures,
                "rolling_five_year_window_count": annual_summary["rolling_five_year_window_count"],
                "rolling_five_year_failure_count": annual_summary["rolling_five_year_gross_failure_count"],
                "first_available_rolling_five_year_row": annual_summary["first_available_rolling_five_year_row"],
                "worst_rolling_five_year_gross_row": annual_summary["worst_rolling_five_year_gross_row"],
                "boundary": "此诊断不把现金分配、现金流分派率或净值当作总回报，也不把成本为零的结果当作个人净回报。上交所日价端点未披露复权口径，故这些失败是进一步否决信号，而不是已验证个人净后成本绩效。",
            },
        },
        "representative_product_diligence": {
            "product": {
                "code": PRODUCT_CODE,
                "name": PRODUCT_NAME,
                "route": "上交所上市的封闭式基础设施 REITs 场内份额；不开放常规申购、赎回。",
                "structure": "基金主要投资基础设施资产支持证券并持有其全部份额，经专项计划和项目公司取得不动产项目权益。2025 年报披露项目为张江光大园和张润大厦；份额持有人持有基金份额而非直接持有项目物业。",
            },
            "distribution_and_cash_flow": {
                "legal_distribution_mechanism": "在符合条件前提下，年度可供分配金额的 90% 以上以现金形式分配，原则上每年不少于一次；这是分配约束，不是回报下限。",
                "reported_2025_income_cny": 142324217.65,
                "reported_2024_income_cny": 162730347.50,
                "reported_2025_operating_cash_flow_cny": 105192467.08,
                "reported_2024_operating_cash_flow_cny": 103567336.23,
                "reported_2025_cash_flow_distribution_rate_pct": 4.65,
                "reported_2025_distributable_amount_cny": 112685654.50,
                "reported_2025_distributable_amount_per_share_cny": 0.1173,
                "reported_2025_actual_distribution_per_share_cny": 0.1250,
                "cash_flow_readthrough": "现金流主要来自园区租赁及相关收入。2025 年整体期末出租率为 87.38%，张江光大园为 80.50%，对应 2024 年分别为 91.90% 和 91.37%；租金、出租率、续租和费用都会影响可供分配金额与估值。",
                "separation_rule": "4.65% 的年化现金流分派率和 0.1250 元的单位实际分配均不是二级市场总回报，也不能与收盘价、净值或个人净后成本互相替代。",
            },
            "fees": {
                "dated_2024_product_summary": "2024-06-28 产品资料概要列示首发项目固定管理费公式含 E×P1×0.55%/年，扩募项目含 E×P2×0.15%/年，另有项目现金流挂钩的浮动管理费；托管费为最近一期经审计基金净资产的 0.01%/年，审计和信息披露费用以年金额列示，证券交易、账户和税负按实际发生额承担。",
                "dated_2025_annual_report": "2025 年报披露的本期计提口径含基金管理人项目权重 0.10% 与 0.12%、两家专项计划管理人 0.05% 与 0.03%、托管费 0.01%，以及运营管理机构固定费和浮动费；本期计提管理费、专项计划管理费、托管费和运营管理费均有实际金额披露。",
                "fee_boundary": "不同日期披露的费率／公式并非可机械拼成一条个人总成本曲线；基金层费用也不包括个人经纪佣金、税费、点差、转托管和成交失败成本。",
            },
            "risks": [
                "二级市场价格波动、流动性不足、做市与可交易份额不足风险",
                "封闭式运作、不开放常规申购赎回、可能终止上市或停牌的风险",
                "张江区域租赁需求、租金、出租率、租户续约与集中度风险",
                "物业改造、资本开支、运营管理、关联交易和扩募／新购项目风险",
                "评估值、现金流预测、税收政策及项目处置风险",
                "个人账户适当性、风险揭示、券商费用、报价深度、部分成交和结算路径风险",
            ],
            "account_and_trading_boundary": "公开文件表明这是一条可能存在的场内基金交易路径，但产品为封闭式；场外认购份额需转托管至场内证券经营机构才能场内交易。具体个人证券账户、风险揭示、券商产品权限、费率、转托管时效、订单可成交性和结算状态均未由本研究验证，不能据公开规则认定个人可操作。",
        },
        "blocking_requirements": [
            {
                "id": "C14-B1",
                "blocker": "validated investor total-return ledger",
                "reader_label_cn": "可验证的个人总回报账本",
                "missing": "逐日明确复权口径的二级市场价格或净值、公司行为、除权、现金到账与再投资／现金持有的可审计账本。",
                "impact": "不能把本次公开日价与分配行诊断升级为个人净总回报。",
            },
            {
                "id": "C14-B2",
                "blocker": "dated personal after-cost ledger",
                "reader_label_cn": "日期明确的个人净成本账本",
                "missing": "每个相关时期的个人经纪佣金、交易所及登记结算费用、适用税负、转托管、现金划转、账户维护、点差和未成交处理。",
                "impact": "严格门槛要求净后成本，零成本诊断不能代替。",
            },
            {
                "id": "C14-B3",
                "blocker": "personal account and broker-route confirmation",
                "reader_label_cn": "个人账户与券商路径确认",
                "missing": "具体个人账户、风险揭示、券商会员路径、权限、适当性、转托管和结算的日期明确证明。",
                "impact": "公开规则只描述市场机制，不能认定个人能够操作。",
            },
            {
                "id": "C14-B4",
                "blocker": "execution and liquidity ledger",
                "reader_label_cn": "执行与流动性账本",
                "missing": "逐笔可验证的买卖报价、深度、成交、部分成交、拒单、停牌和结算状态。",
                "impact": "官方收盘价和成交量不能转化为个人实际可成交价格。",
            },
            {
                "id": "C14-B5",
                "blocker": "dated fee and rule-version continuity",
                "reader_label_cn": "费用和规则版本连续性",
                "missing": "基金费率／费用公式、交易规则、税费和券商条款在所有检验日的有效版本。",
                "impact": "不能以一份更新产品资料概要或单年年报反推五年净成本。",
            },
            {
                "id": "C14-B6",
                "blocker": "universe-level admissibility",
                "reader_label_cn": "全市场总体准入性",
                "missing": "覆盖公募 REITs 全部候选、上市时间、存续／扩募、历史价格与分配数据及统一成本规则的时点正确总体。",
                "impact": "单一代表品种不能推出整个公募 REITs 市场存在或不存在符合严格标准的路线。",
            },
            {
                "id": "C14-B7",
                "blocker": "gross diagnostic failure witness",
                "reader_label_cn": "宽松诊断下的失败见证",
                "missing": "这不是净回报证明：固定 508000 路线在本次公开价格加现金分配、成本为零的诊断中，多个完整年度和全部可得滚动五年窗口低于 5%。",
                "impact": "它只能作为额外否决信号；严格净后成本结果仍因其他阻断项而未建立，代表路线不准入。",
            },
        ],
        "next_research_gate": [
            "仅在取得有权使用、时点正确且复权口径明确的公募 REITs 价格／净值／分配／公司行动总体后，才能建立统一的单品种或全市场回放总体。",
            "在查看任何结果前，冻结现金分配处理、再投资或现金持有、交易时点、停牌、费用、税费、点差、部分成交、转托管和异常状态规则。",
            "取得日期明确且不含个人敏感信息的券商费率、账户路径和结算说明；缺任一字段继续保持 q=0。",
            "由独立复核方逐年和逐个滚动五年窗口重算净后成本结果；任一窗口低于 5% 或数据不可验证即不准入。",
        ],
        "source_manifest": {
            "path": _repo_relative(MANIFEST_JSON),
            "sha256": _sha256(MANIFEST_JSON),
            "capture_batch": manifest["capture_batch"],
        },
        "nav_endpoint_observation": nav_summary,
        "no_action_statement": "本工件不授权开户、风险测评、转托管、购买、出售、委托、联系券商、现金划转或任何外部行动。",
        "orders_or_positions": "none",
    }


def _render_rulebook(payload: dict[str, Any]) -> str:
    replay = payload["frozen_replay"]
    annual = replay["annual_rows"]
    rolling = replay["summary"]
    annual_table = "\n".join(
        "| {year} | {start} | {end} | CNY{cash:.5f} | {result:.2f}% | {pass_flag} |".format(
            year=row["year"],
            start=row["start_observation_date"],
            end=row["end_observation_date"],
            cash=row["cash_distribution_per_share_cny"],
            result=row["gross_cost_free_cash_return_pct"],
            pass_flag="是" if row["meets_5pct_gross_diagnostic"] else "否",
        )
        for row in annual
    )
    first_rolling = rolling["first_available_rolling_five_year_row"]
    worst_rolling = rolling["worst_rolling_five_year_gross_row"]
    return f"""# C14 公募基础设施 REITs：508000 固定有界诊断规则书 — 2026-08-15

- 状态：**仅研究用途**；`portfolio_q=0`。
- 固定代表路线：上交所上市的 `{PRODUCT_CODE}`，不在代码、基础资产类别、起止日、费用或分配处理间作事后替换。它只审查一个可公开冻结数据的代表性路径，绝不代表整个公募 REITs 市场。
- 严格门槛：每个完整日历年的个人净后成本回报，以及每个可得滚动五年窗口的个人净后成本年化回报，均须不低于 5%。

## 冻结的有界计算

日价来自上交所官方日线响应；分配来自上交所官方 REITs 分配历史响应。年度检验覆盖 2022–2025：起点为当年 1 月 1 日当日或之前最后一个官方收盘价，终点为当年 12 月 31 日当日或之前最后一个官方收盘价；区间现金分配按官方除权日累加并保留为现金，不作再投资。公式为：

`（期末收盘价 + 区间每份现金分配）/ 起点收盘价 - 1`

| 年份 | 起点观察日 | 终点观察日 | 区间现金分配／份 | 成本为零现金诊断 | ≥5% |
|---:|---|---|---:|---:|---|
{annual_table}

滚动五年规则使用所有可从官方交易日走满五个日历年的窗口；若名义终点不是交易日，则使用当日或之前最后一个官方收盘价并持有至名义终点。共得到 `{rolling['rolling_five_year_window_count']}` 个窗口；其中 `{rolling['rolling_five_year_gross_failure_count']}` 个低于 5%。首个窗口为 `{first_rolling['start_observation_date']}` 至 `{first_rolling['nominal_five_year_end_date']}`，年化成本为零现金诊断为 `{first_rolling['gross_cost_free_cash_annualized_return_pct']:.2f}%`；最弱窗口为 `{worst_rolling['start_observation_date']}` 至 `{worst_rolling['nominal_five_year_end_date']}`，为 `{worst_rolling['gross_cost_free_cash_annualized_return_pct']:.2f}%`。

## 不可越界的解释

这不是个人净后成本回报：计算设定为零交易成本、零税费、零账户费用、零点差、零滑点，且现金不再投资。上交所日价端点也未披露复权口径；分配行不证明现金到账、适用税负、账户权限或成交。因此，表中数值只能作为固定路线的宽松历史诊断，不能作为业绩承诺、可执行策略或个人回报结论。

上交所净值查询端点在本次抓取时返回 `{payload['nav_endpoint_observation']['captured_endpoint_result_rows']}` 行，{payload['nav_endpoint_observation']['interpretation']}

完整来源和哈希见 [来源清单](../sources/c14-public-infrastructure-reit-508000-20260815/manifest.md)；机器副本见 [规则书 JSON](c14_public_reit_rulebook_20260815.json)。本工件不授权任何外部行动。
"""


def _render_feasibility(payload: dict[str, Any]) -> str:
    strict = payload["strict_5pct_test"]
    product = payload["representative_product_diligence"]
    gross = strict["gross_cost_free_diagnostic"]
    failures = "；".join(
        f"{row['year']} 年 {row['gross_cost_free_cash_return'] * 100:.2f}%"
        for row in gross["annual_failures"]
    )
    blockers = "\n".join(
        f"| {item['id']} | {item['reader_label_cn']} | {item['impact']} |"
        for item in payload["blocking_requirements"]
    )
    gates = "\n".join(f"{index}. {item}" for index, item in enumerate(payload["next_research_gate"], start=1))
    risks = "\n".join(f"- {item}" for item in product["risks"])
    return f"""# C14 可行性结论：公募基础设施 REITs 代表性路线 — 2026-08-15

## 结论

**{payload['status']}。** `portfolio_q=0`，`formal_decision_eligible=false`。本研究不生成个人净后成本回报、持有、配置或任何外部行动。

严格标准要求每个完整日历年、以及每个滚动五年窗口的**个人净后成本**回报均不低于 5%。本次冻结的公开资料无法构造这样的个人净账本，故 `return_result=null`。同时，预先固定的 508000 成本为零现金诊断在多个完整年度已低于 5%（{failures}），本次可得的 `{gross['rolling_five_year_window_count']}` 个滚动五年窗口亦全部低于 5%。这进一步否决该单品种代表路线，但不被误写成已验证的个人净绩效。

## 代表品种与市场路径

选取 `{PRODUCT_CODE}`（{PRODUCT_NAME}）作为代表，是因为它于 2021-06-21 位列上交所首批基础设施公募 REITs，且公开端点可冻结上市后日价与分配行。产品采用封闭式基础设施 REITs 结构：基金主要持有基础设施资产支持证券，经专项计划和项目公司取得项目权益；2025 年报披露底层为张江光大园和张润大厦。份额持有人持有的是基金份额，并非直接持有项目物业。

该产品的封闭期限内不开放常规申购、赎回，场外认购份额需转托管至场内证券经营机构才能进行场内交易。公开规则和产品文件只能说明一条可能存在的市场路径；它们不证明任何特定个人已满足账户、风险揭示、券商权限、费率、转托管、报价深度、成交或结算条件。

## 分配、现金流和费用不能互相替代

- 法定／合同层面的现金分配约束为年度可供分配金额 90% 以上、原则上每年不少于一次；它是分配机制，不是总回报下限。
- 2025 年报披露收入 CNY142.324m、经营活动现金流净额 CNY105.192m、可供分配金额 CNY112.686m（每份 CNY0.1173），本期单位实际分配 CNY0.1250，年化现金流分派率 4.65%。这些均不能替代二级市场总回报或个人净后成本回报。
- 2025 年整体期末出租率为 87.38%，张江光大园为 80.50%，低于 2024 年的 91.90% 和 91.37%。租金、出租率、续租、维护和费用会同时影响可供分配金额与估值。
- 费用不是一个可安全外推的单一费率：2024 产品资料概要与 2025 年报披露了不同日期的固定／浮动管理费公式、专项计划管理费、托管费及运营管理费；另有审计、信息披露、交易、账户和税负。基金层费用仍不等于个人经纪费、点差和税费。

## 风险与账户边界

{risks}

公开端点在本次抓取时没有返回 508000 的净值历史行；这仅是端点观察，不能证明其他来源不存在净值，也不能把二级市场收盘价、净值、分配或现金流分派率混同。

## 核心一手依据

| 主题 | 冻结的一手文件 | 使用边界 |
|---|---|---|
| 产品结构、封闭运作与场内／场外边界 | `508000_updated_prospectus_20241104.pdf`、`508000_product_summary_20240628.pdf` | 说明产品机制与日期明确条款；不证明任何特定个人账户结果。 |
| 项目、租赁现金流、出租率、分配和基金层费用 | `508000_2025_annual_report_20260327.pdf` | 反映 2025 报告期披露；不替代未来现金流、总回报或个人成本。 |
| 单次现金分配、权益登记和现金方式 | `508000_2024_distribution_announcement_20250415.pdf` | 用于交叉核验分配机制；分配不等于回报。 |
| 二级市场收盘价与历史分配行 | `sse_508000_daily_market_price_begin0_end5000.jsonp`、`sse_508000_distribution_history_page1.jsonp` | 是回溯抓取的官方响应，未披露复权口径，也没有个人执行字段。 |
| 监管与交易所制度背景 | `csrc_public_infrastructure_reit_guideline_announcement_20200807.html`、`sse_public_infrastructure_reit_business_rules_20210129.html` | 说明制度沿革和市场机制；当前个人资格仍须逐账户核验。 |

## 主要阻断项

| ID | 阻断项 | 对严格标准的后果 |
|---|---|---|
{blockers}

## 唯一允许的后续研究门槛

{gates}

来源与哈希见 [C14 来源清单](../sources/c14-public-infrastructure-reit-508000-20260815/manifest.md)，固定规则见 [C14 规则书](c14_public_reit_rulebook_20260815.md)。本工件不授权开户、风险测评、转托管、购买、出售、委托、联系券商、现金划转或任何外部行动。
"""


def _build() -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = _load_manifest()
    prices = _load_prices()
    distributions = _load_distributions()
    nav_summary = _nav_endpoint_summary()
    replay = _replay(prices, distributions)
    rulebook = _rulebook_payload(manifest, replay, nav_summary)
    feasibility = _feasibility_payload(manifest, replay, nav_summary)
    _write_json(RULEBOOK_JSON, rulebook)
    _write_text(RULEBOOK_MD, _render_rulebook(rulebook))
    _write_json(FEASIBILITY_JSON, feasibility)
    _write_text(FEASIBILITY_MD, _render_feasibility(feasibility))
    return rulebook, feasibility


def _verify_output() -> None:
    manifest = _load_manifest()
    if not RULEBOOK_JSON.is_file() or not RULEBOOK_MD.is_file() or not FEASIBILITY_JSON.is_file() or not FEASIBILITY_MD.is_file():
        raise FileNotFoundError("C14 derived output is absent")
    rulebook = json.loads(RULEBOOK_JSON.read_text(encoding="utf-8"))
    feasibility = json.loads(FEASIBILITY_JSON.read_text(encoding="utf-8"))
    manifest_sha = _sha256(MANIFEST_JSON)
    for payload, name in ((rulebook, "rulebook"), (feasibility, "feasibility")):
        if payload.get("source_manifest", {}).get("sha256") != manifest_sha:
            raise ValueError(f"C14 {name} source-manifest hash differs")
        if payload.get("portfolio_q") != 0:
            raise ValueError(f"C14 {name} must retain portfolio_q=0")
    if feasibility.get("status") != "NOT_FEASIBLE_FOR_STRICT_5PCT_OR_PERSONAL_EXECUTION":
        raise ValueError("C14 feasibility status differs")
    if feasibility.get("formal_decision_eligible") is not False or feasibility.get("return_result") is not None:
        raise ValueError("C14 feasibility must remain non-admissible with no net return result")
    strict = feasibility.get("strict_5pct_test", {})
    if strict.get("net_after_cost_status") != "NOT_ESTABLISHED_AND_NOT_ADMITTED":
        raise ValueError("C14 strict net-after-cost state differs")
    gross = strict.get("gross_cost_free_diagnostic", {})
    if gross.get("annual_failure_count", 0) < 1 or gross.get("rolling_five_year_failure_count", 0) < 1:
        raise ValueError("C14 gross diagnostic must retain at least one failure witness")
    if not rulebook.get("frozen_replay", {}).get("annual_rows") or not rulebook.get("frozen_replay", {}).get("available_rolling_five_year_rows"):
        raise ValueError("C14 fixed replay rows are absent")
    prohibited = ("本金", "初始资金", "initial capital", "initial_capital", "starting amount", "principal")
    for path in (RULEBOOK_JSON, RULEBOOK_MD, FEASIBILITY_JSON, FEASIBILITY_MD):
        text = path.read_text(encoding="utf-8").lower()
        for term in prohibited:
            if term.lower() in text:
                raise ValueError(f"forbidden monetary-scope phrase {term!r} in {path.name}")
    if manifest.get("capture_batch") != SOURCE_DIR.name:
        raise ValueError("C14 manifest capture batch differs")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture", action="store_true")
    parser.add_argument("--rebuild-derived", action="store_true")
    parser.add_argument("--verify-only", action="store_true")
    arguments = parser.parse_args()
    if sum((arguments.capture, arguments.rebuild_derived, arguments.verify_only)) != 1:
        parser.error("choose exactly one mode")
    if arguments.capture:
        _capture()
        _build()
        print("C14 SOURCE CAPTURE + BOUNDED DIAGNOSTIC: PASS")
    elif arguments.rebuild_derived:
        _build()
        print("C14 BOUNDED DIAGNOSTIC: PASS")
    else:
        _verify_output()
        print("C14 PUBLIC REIT: PASS")

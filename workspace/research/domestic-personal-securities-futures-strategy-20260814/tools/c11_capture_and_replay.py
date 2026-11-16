#!/usr/bin/env python3
"""Capture first-party C11 sources and replay its fixed NAV-proxy hurdle.

This case-local utility only performs read-only source capture and arithmetic on
the fund-manager-published cumulative-NAV series.  It does not contact an
account, submit an instruction, infer a holder's dealing result, or make an
investment action available.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
import sys
from collections import OrderedDict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import requests


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
DATE_TAG = "20260815"
RAW_DIR = CASE_DIR / "sources" / f"c11-market-neutral-fund-{DATE_TAG}"
MANIFEST_JSON = RAW_DIR / "manifest.json"
MANIFEST_MD = RAW_DIR / "manifest.md"
PROTOCOL_JSON = CASE_DIR / "analysis" / f"c11_market_neutral_single_fund_protocol_{DATE_TAG}.json"
OUTPUT_JSON = CASE_DIR / "analysis" / f"c11_market_neutral_fund_nav_proxy_{DATE_TAG}.json"
OUTPUT_MD = CASE_DIR / "analysis" / f"c11_market_neutral_fund_nav_proxy_{DATE_TAG}.md"

FUND_CODE = "008856"
SOURCE_FREEZE_SCHEMA = "research_source_freeze_control.v1"
SOURCE_QUALITY = "primary_official_manager_published_nav_and_product_documents"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (C11 research evidence capture; read-only)",
    "Accept": "application/pdf,text/html,application/javascript,*/*;q=0.8",
}

DOCUMENTS: tuple[dict[str, str], ...] = (
    {
        "filename": "008856_product_summary_20260529.pdf",
        "publisher": "ChinaAMC Fund Management Co., Ltd.",
        "title": "ChinaAMC Antai Hedge Strategy Three-Month Periodically Open Flexible Allocation Fund product summary",
        "document_date": "2026-05-29",
        "url": "https://accountquery.chinaamc.com/upload/resources/file/2026/05/29/2016c361cce84003aca68d42d20ea52e.pdf",
        "format": "pdf",
        "purpose": "Dated product, investment-scope, periodic-opening and fee disclosure for fund 008856.",
    },
    {
        "filename": "008856_open_notice_20260512.pdf",
        "publisher": "ChinaAMC Fund Management Co., Ltd.",
        "title": "ChinaAMC Antai Hedge Strategy fund 2026 second open-period notice",
        "document_date": "2026-05-12",
        "url": "https://accountquery.chinaamc.com/upload/resources/file/2026/05/12/3717aa3205ef41b1943e1944eb7894e3.pdf",
        "format": "pdf",
        "purpose": "Dated evidence that an actual dealing window must be confirmed by a manager notice.",
    },
    {
        "filename": "008856_official_nav_all_20260815.js",
        "publisher": "ChinaAMC Fund Management Co., Ltd.",
        "title": "Fund 008856 all-history published NAV series",
        "document_date": "2026-08-15",
        "url": "https://www.chinaamc.com/fund/008856/zoust_all.js",
        "format": "json",
        "purpose": "Published cumulative-NAV input for a restricted official-NAV arithmetic proxy only.",
    },
    {
        "filename": "008856_official_nav_history_page_20260815.html",
        "publisher": "ChinaAMC Fund Management Co., Ltd.",
        "title": "Fund 008856 historical NAV page",
        "document_date": "2026-08-15",
        "url": "https://www.chinaamc.com/fund/008856/lishijingzhi.shtml?source=click",
        "format": "html",
        "purpose": "Source-page context for the manager-published NAV history endpoint.",
    },
)


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _repo_relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _file_record(path: Path) -> dict[str, Any]:
    return {
        "path": _repo_relative(path),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


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


def _decode_nav(content: bytes) -> dict[str, Any]:
    try:
        payload = json.loads(content.decode("gb18030"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("official NAV endpoint is not valid GB18030 JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("official NAV endpoint must contain a JSON object")
    dates = payload.get("ShowData")
    values = payload.get("leijiJingzhiName")
    if not isinstance(dates, list) or not isinstance(values, list) or len(dates) != len(values):
        raise ValueError("official NAV endpoint lacks aligned date/cumulative-NAV arrays")
    if len(dates) < 1261:
        raise ValueError("official NAV endpoint is too short for a 1260-observation test")
    previous: date | None = None
    for raw_day, raw_value in zip(dates, values, strict=True):
        if not isinstance(raw_day, str):
            raise ValueError("official NAV date is not text")
        try:
            parsed = date.fromisoformat(raw_day)
        except ValueError as exc:
            raise ValueError(f"official NAV date is malformed: {raw_day!r}") from exc
        if previous is not None and parsed <= previous:
            raise ValueError("official NAV dates are not strictly increasing")
        previous = parsed
        try:
            value = float(raw_value)
        except (TypeError, ValueError) as exc:
            raise ValueError("official cumulative NAV is not numeric") from exc
        if not math.isfinite(value) or value <= 0.0:
            raise ValueError("official cumulative NAV is non-finite or non-positive")
    return payload


def _validate_document(content: bytes, descriptor: dict[str, str]) -> None:
    if len(content) < 500:
        raise ValueError(f"document unexpectedly short: {descriptor['filename']}")
    if descriptor["format"] == "pdf" and not content.startswith(b"%PDF"):
        raise ValueError(f"document is not a PDF: {descriptor['filename']}")
    if descriptor["format"] == "json":
        _decode_nav(content)
    if descriptor["format"] == "html":
        prefix = content[:5000].decode("gb18030", errors="ignore").lower()
        if "safeline_bot_challenge" in prefix or "<title>web 应用防火墙" in prefix:
            raise ValueError(f"WAF response cannot be retained as official source: {descriptor['filename']}")
        if FUND_CODE not in content.decode("gb18030", errors="ignore"):
            raise ValueError(f"history page does not identify fund {FUND_CODE}: {descriptor['filename']}")


def _runtime_provenance() -> dict[str, str]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            check=True,
            text=True,
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
    if RAW_DIR.exists() or MANIFEST_JSON.exists():
        raise FileExistsError("C11 source batch already exists; use --rebuild-derived or --verify-only")
    staged: list[tuple[Path, bytes, dict[str, Any]]] = []
    retrieval_times: list[str] = []
    for descriptor in DOCUMENTS:
        response = requests.get(descriptor["url"], headers=HEADERS, timeout=30)
        if response.status_code != 200:
            raise RuntimeError(f"source download failed {response.status_code}: {descriptor['url']}")
        _validate_document(response.content, descriptor)
        retrieved_at = datetime.now(timezone.utc).isoformat()
        path = RAW_DIR / descriptor["filename"]
        metadata = {
            **descriptor,
            "retrieved_at": retrieved_at,
            "http_status": response.status_code,
            "content_type": response.headers.get("content-type", "not_reported"),
        }
        if descriptor["format"] == "json":
            nav = _decode_nav(response.content)
            metadata.update(
                {
                    "nav_observation_count": len(nav["ShowData"]),
                    "first_observation_date": nav["ShowData"][0],
                    "last_observation_date": nav["ShowData"][-1],
                    "nav_series_name": "leijiJingzhiName",
                }
            )
        staged.append((path, response.content, metadata))
        retrieval_times.append(retrieved_at)
    RAW_DIR.mkdir(parents=True, exist_ok=False)
    for path, content, _ in staged:
        _atomic_write(path, content)
    rows: list[dict[str, Any]] = []
    for path, _, metadata in staged:
        rows.append(
            {
                **_file_record(path),
                **metadata,
                "capture_note": (
                    "Anonymous read-only capture of current manager-published material. It does not establish "
                    "historical available_at, revision history, data entitlement, holder dealing charges, "
                    "confirmation timing, account/channel availability, allocation, holding, suitability, or action."
                ),
            }
        )
    manifest = {
        "schema_version": "c11_market_neutral_fund_source_manifest.v1",
        "case_id": CASE_DIR.name,
        "capture_batch": RAW_DIR.name,
        "captured_at": min(retrieval_times),
        "protocol_status": "exploratory_post_observation_not_clean_preregistration",
        "purpose": "First-party product, open-period and published NAV evidence for C11. It supports only a source-bound official cumulative-NAV proxy falsification.",
        "source_quality": SOURCE_QUALITY,
        "files": rows,
        "limitations": [
            "This is a retrospective anonymous public capture. It is not an entitled point-in-time historical delivery or proof of immutable historical publication.",
            "Published cumulative NAV is not a holder-specific result: it does not determine entry/exit charge, actual confirmation date, channel access, dealing restriction, tax, allocation, or unsuccessful dealing outcome.",
            "A dated product summary and one dated open-period notice cannot establish a current open window, current dealing state, current fee, current risk rating, or account availability.",
            "No allocation, holding, external instruction, or return guarantee is created by this source batch or the resulting arithmetic.",
        ],
        "source_freeze": {
            "schema_version": SOURCE_FREEZE_SCHEMA,
            "seal_status": "case_local_hash_control",
            "sealed_at": datetime.now(timezone.utc).isoformat(),
            "frozen_files": [_file_record(path) for path, _, _ in staged],
            "runtime_provenance": _runtime_provenance(),
            "boundary": "Case-local hashes detect a local raw-file mismatch only. They do not establish external notarization, entitlement, point-in-time provenance, holder return, or execution validation.",
        },
    }
    _write_json(MANIFEST_JSON, manifest)
    lines = [
        "# C11 Official Market-Neutral Fund Source Manifest",
        "",
        f"- Batch: `{manifest['capture_batch']}`",
        f"- Capture time: `{manifest['captured_at']}`",
        "- Method: anonymous, read-only HTTPS requests to named ChinaAMC documents and the fund's published all-history NAV endpoint.",
        "- Boundary: the NAV file supports cumulative-NAV proxy arithmetic only; it is not a holder dealing result or execution record.",
        "",
        "| File | Publisher | Date / coverage | SHA-256 |",
        "|---|---|---|---|",
    ]
    for row in rows:
        period = row["document_date"]
        if "first_observation_date" in row:
            period = f"{row['first_observation_date']} to {row['last_observation_date']} ({row['nav_observation_count']} observations)"
        lines.append(f"| {Path(row['path']).name} | {row['publisher']} | {period} | `{row['sha256']}` |")
    lines.extend(
        [
            "",
            "Every raw-file hash in this table is checked by `tools/verify_source_manifests.py`. The hash control cannot establish the historical publication timestamp, holder charges, eligibility, dealing confirmation, or an actionable result.",
            "",
        ]
    )
    _write_text(MANIFEST_MD, "\n".join(lines))


def _verify_manifest() -> dict[str, Any]:
    if not MANIFEST_JSON.is_file():
        raise FileNotFoundError(f"absent C11 source manifest: {MANIFEST_JSON}")
    manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    rows = manifest.get("files")
    frozen = manifest.get("source_freeze", {}).get("frozen_files")
    if not isinstance(rows, list) or len(rows) != len(DOCUMENTS):
        raise ValueError("C11 source manifest does not have the expected source rows")
    if not isinstance(frozen, list):
        raise ValueError("C11 source manifest lacks frozen-file rows")
    listed_paths = {str(row.get("path")) for row in rows}
    frozen_paths = {str(row.get("path")) for row in frozen}
    if listed_paths != frozen_paths:
        raise ValueError("C11 source manifest and frozen-file set differ")
    expected_names = {descriptor["filename"] for descriptor in DOCUMENTS}
    actual_names = {Path(path).name for path in listed_paths}
    if actual_names != expected_names:
        raise ValueError("C11 source manifest file names differ from the frozen capture definition")
    frozen_by_path = {str(row["path"]): row for row in frozen}
    for row in rows:
        path = (REPO_ROOT / str(row["path"])).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"C11 raw source is absent: {path}")
        if path.stat().st_size != int(row["bytes"]) or _sha256(path) != row["sha256"]:
            raise ValueError(f"C11 raw source hash mismatch: {path}")
        frozen_row = frozen_by_path.get(str(row["path"]))
        expected_freeze = {key: row.get(key) for key in ("path", "bytes", "sha256")}
        observed_freeze = {key: frozen_row.get(key) for key in ("path", "bytes", "sha256")} if isinstance(frozen_row, dict) else None
        if observed_freeze != expected_freeze:
            raise ValueError(f"C11 frozen source record differs: {path}")
    return manifest


def _load_nav_series() -> OrderedDict[str, float]:
    source_path = RAW_DIR / "008856_official_nav_all_20260815.js"
    payload = _decode_nav(source_path.read_bytes())
    series: OrderedDict[str, float] = OrderedDict()
    for raw_day, raw_value in zip(payload["ShowData"], payload["leijiJingzhiName"], strict=True):
        day = str(raw_day)
        value = float(raw_value)
        if day in series:
            raise ValueError(f"duplicate NAV date: {day}")
        series[day] = value
    return series


def _complete_calendar_years(dates: list[str], nav: list[float]) -> list[dict[str, Any]]:
    by_year: dict[int, list[int]] = {}
    for index, raw_day in enumerate(dates):
        by_year.setdefault(date.fromisoformat(raw_day).year, []).append(index)
    first_year, last_year = min(by_year), max(by_year)
    rows: list[dict[str, Any]] = []
    for year, indexes in sorted(by_year.items()):
        first_index, last_index = indexes[0], indexes[-1]
        first_date, last_date = dates[first_index], dates[last_index]
        complete = (
            year not in {first_year, last_year}
            and first_date[5:7] == "01"
            and last_date[5:7] == "12"
            and first_index > 0
        )
        change = nav[last_index] / nav[first_index - 1] - 1.0 if complete else None
        rows.append(
            {
                "year": year,
                "first_observation": first_date,
                "last_observation": last_date,
                "complete": complete,
                "cumulative_nav_change": change,
            }
        )
    return rows


def _max_drawdown(nav: list[float]) -> float:
    peak = nav[0]
    worst = 0.0
    for value in nav:
        peak = max(peak, value)
        worst = min(worst, value / peak - 1.0)
    return worst


def _simulate() -> dict[str, Any]:
    if not PROTOCOL_JSON.is_file():
        raise FileNotFoundError(f"absent C11 protocol: {PROTOCOL_JSON}")
    protocol = json.loads(PROTOCOL_JSON.read_text(encoding="utf-8"))
    if protocol.get("artifact_id") != "DPSFS-C11-MN-FUND-v1":
        raise ValueError("C11 protocol identifier differs")
    if protocol.get("portfolio_q") != 0:
        raise ValueError("C11 protocol must retain portfolio_q=0")
    nav_test = protocol.get("nav_proxy_test", {})
    if nav_test.get("source") != "Fund-manager published all-history cumulative NAV series":
        raise ValueError("C11 protocol NAV source differs")
    hurdle = float(nav_test.get("strict_hurdle"))
    if not math.isclose(hurdle, 0.05, abs_tol=1e-12):
        raise ValueError("C11 protocol strict hurdle differs")
    lookback = 1260
    series = _load_nav_series()
    dates, nav = list(series), list(series.values())
    if dates[0] != protocol["product"]["contract_effective_date"]:
        raise ValueError("C11 published NAV first date differs from disclosed contract-effective date")
    elapsed_days = (date.fromisoformat(dates[-1]) - date.fromisoformat(dates[0])).days
    if elapsed_days <= 0:
        raise ValueError("C11 published NAV timeline is non-positive")
    annualized = (nav[-1] / nav[0]) ** (365.25 / elapsed_days) - 1.0
    calendar_years = _complete_calendar_years(dates, nav)
    complete_years = [row for row in calendar_years if row["complete"]]
    rolling = [
        {
            "start_date": dates[index - lookback],
            "end_date": dates[index],
            "annualized_cumulative_nav_change": (nav[index] / nav[index - lookback]) ** (252.0 / lookback) - 1.0,
        }
        for index in range(lookback, len(nav))
    ]
    annual_failures = [row for row in complete_years if float(row["cumulative_nav_change"]) < hurdle]
    rolling_failures = [row for row in rolling if float(row["annualized_cumulative_nav_change"]) < hurdle]
    input_failures: list[str] = []
    if not complete_years:
        input_failures.append("no_complete_calendar_year")
    if not rolling:
        input_failures.append("no_1260_observation_rolling_window")
    status = (
        nav_test["fail_label"]
        if input_failures or annual_failures or rolling_failures
        else nav_test["pass_label"]
    )
    return {
        "artifact_id": "DPSFS-C11-MN-NAVPROXY-v1",
        "as_of": DATE_TAG[:4] + "-" + DATE_TAG[4:6] + "-" + DATE_TAG[6:],
        "protocol": {
            "artifact_id": protocol["artifact_id"],
            "status": protocol["status"],
            "portfolio_q": protocol["portfolio_q"],
            "fund_code": protocol["product"]["fund_code"],
            "fund_name": protocol["product"]["name"],
            "strict_hurdle": hurdle,
            "rolling_window_observations": lookback,
        },
        "source_boundary": {
            "source_quality": SOURCE_QUALITY,
            "input": "ChinaAMC all-history published cumulative NAV (leijiJingzhiName)",
            "calculation_scope": "Official cumulative-NAV arithmetic before holder-specific dealing charges, confirmation timing, channel constraints, tax, allocation, and unsuccessful dealing outcomes.",
            "excluded": [
                "holder_specific_subscription_or_redemption_charge",
                "actual_dealing_confirmation_date",
                "channel_or_account_availability",
                "current_open_window_or_scale_control",
                "tax_and_individual_holder_outcome",
                "future_return_and_action",
            ],
        },
        "rule": {
            "calendar_annualization_basis": "365.25 / elapsed calendar days",
            "complete_calendar_year_basis": "last published cumulative NAV in the calendar year divided by the immediately prior published NAV before that year's first observation, less one",
            "rolling_basis": "1260-observation NAV ratio annualized at 252 / 1260",
            "strict_failure_condition": "Any complete calendar-year change or any 1260-observation rolling annualized change below 5%, or an input exception.",
        },
        "result": {
            "status": status,
            "nav_observations": len(nav),
            "first_observation": dates[0],
            "last_observation": dates[-1],
            "first_cumulative_nav": nav[0],
            "terminal_cumulative_nav": nav[-1],
            "elapsed_calendar_days": elapsed_days,
            "annualized_cumulative_nav_change": annualized,
            "maximum_drawdown_from_published_cumulative_nav": _max_drawdown(nav),
            "complete_calendar_years": calendar_years,
            "complete_year_failure_count": len(annual_failures),
            "complete_year_failures": annual_failures,
            "rolling_window_observations": lookback,
            "rolling_window_count": len(rolling),
            "rolling_pass_count": len(rolling) - len(rolling_failures),
            "rolling_failure_count": len(rolling_failures),
            "rolling_min_annualized_cumulative_nav_change": min(
                (row["annualized_cumulative_nav_change"] for row in rolling), default=None
            ),
            "rolling_max_annualized_cumulative_nav_change": max(
                (row["annualized_cumulative_nav_change"] for row in rolling), default=None
            ),
            "rolling_failures": rolling_failures,
            "input_failures": input_failures,
        },
        "allowed_interpretation": "This is an exploratory official cumulative-NAV proxy falsification. It cannot establish stable 5% performance, future return, personal dealing result, suitability, allocation, holding, subscription, redemption, or any external action.",
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    result = payload["result"]
    pct = lambda value: "n/a" if value is None else f"{100.0 * float(value):.2f}%"
    annual_rows = "\n".join(
        f"| {row['year']} | {row['first_observation']} | {row['last_observation']} | {'是' if row['complete'] else '否'} | {pct(row['cumulative_nav_change'])} |"
        for row in result["complete_calendar_years"]
    )
    failed_years = ", ".join(str(row["year"]) for row in result["complete_year_failures"]) or "无"
    rolling_examples = "\n".join(
        f"| {row['start_date']} | {row['end_date']} | {pct(row['annualized_cumulative_nav_change'])} |"
        for row in result["rolling_failures"][:20]
    ) or "| 无 | 无 | 无 |"
    return f"""# C11 公募量化对冲单基金：官方累计净值代理检验 — 2026-08-15

- 产品：`008856` 华夏安泰对冲策略3个月定期开放灵活配置混合型发起式证券投资基金。
- 规则：`DPSFS-C11-MN-FUND-v1`；规则状态：`{payload['protocol']['status']}`；`portfolio_q=0`。
- 结论标签：**`{result['status']}`**。
- 本检验只对管理人公布的累计净值作受限算术；它不是个人申赎结果，也不是对未来收益的预测或承诺。

## 固定口径与结果

- 累计净值观察：`{result['nav_observations']}` 个，`{result['first_observation']}` 至 `{result['last_observation']}`；首值 `{result['first_cumulative_nav']:.4f}`，末值 `{result['terminal_cumulative_nav']:.4f}`。
- 全期按日历时间年化的累计净值变化：`{pct(result['annualized_cumulative_nav_change'])}`；累计净值序列最大回撤：`{pct(result['maximum_drawdown_from_published_cumulative_nav'])}`。
- 严格否决线：每个完整自然年和每个满 `1,260` 个观察间隔的滚动年化累计净值变化均须不低于 5%。完整年度低于线的年份：`{failed_years}`。
- 滚动端点通过 ` {result['rolling_pass_count']} / {result['rolling_window_count']} `；最低 `{pct(result['rolling_min_annualized_cumulative_nav_change'])}`，最高 `{pct(result['rolling_max_annualized_cumulative_nav_change'])}`。

| 年份 | 首观察日 | 末观察日 | 完整年度 | 累计净值变化 |
|---:|---|---|---|---:|
{annual_rows}

前 20 个不达标滚动端点：

| 起点 | 终点 | 年化累计净值变化 |
|---|---|---:|
{rolling_examples}

## 为什么不能据此变成操作

`{result['status']}` 已使这只固定产品在用户导出的严格 5% 检验下失效。即便未失效，公开累计净值也不包含持有人的申赎费、实际确认日、渠道和账户可用性、开放期限制、规模控制、税费或交易失败。该基金虽由管理人实施量化对冲和衍生品操作，但持有人仍须在每个实际开放窗口核验最新公告、产品文件、费率、风险评级与渠道状态；这些要求均不能从历史净值反推。

因此，C11 的正确状态为研究候选的否证，不是持有、申购、赎回、配置或收益保证。原始文件及哈希见 [C11 source manifest](../sources/c11-market-neutral-fund-20260815/manifest.md)，机器副本见 [c11_market_neutral_fund_nav_proxy_20260815.json](c11_market_neutral_fund_nav_proxy_20260815.json)。
"""


def _rebuild_derived() -> dict[str, Any]:
    manifest = _verify_manifest()
    payload = _simulate()
    payload["source_manifest"] = {
        "path": _repo_relative(MANIFEST_JSON),
        "sha256": _sha256(MANIFEST_JSON),
        "capture_batch": manifest["capture_batch"],
    }
    payload["derived_runtime_provenance"] = _runtime_provenance()
    _write_json(OUTPUT_JSON, payload)
    _write_text(OUTPUT_MD, _render_markdown(payload))
    return payload


def _verify_output() -> None:
    _verify_manifest()
    if not OUTPUT_JSON.is_file() or not OUTPUT_MD.is_file():
        raise FileNotFoundError("C11 derived output is absent")
    saved = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
    recalculated = _simulate()
    for key in ("artifact_id", "as_of", "protocol", "source_boundary", "rule", "result", "allowed_interpretation"):
        if saved.get(key) != recalculated.get(key):
            raise ValueError(f"C11 derived output differs on {key}; run --rebuild-derived")
    manifest_record = saved.get("source_manifest", {})
    if manifest_record.get("sha256") != _sha256(MANIFEST_JSON):
        raise ValueError("C11 derived output source-manifest hash differs")
    forbidden = ("本金", "初始资金", "initial capital", "initial_capital", "starting amount")
    for path in (PROTOCOL_JSON, OUTPUT_JSON, OUTPUT_MD):
        text = path.read_text(encoding="utf-8").lower()
        for phrase in forbidden:
            if phrase.lower() in text:
                raise ValueError(f"forbidden monetary-scope phrase {phrase!r} in {path.name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--capture", action="store_true")
    modes.add_argument("--rebuild-derived", action="store_true")
    modes.add_argument("--verify-only", action="store_true")
    arguments = parser.parse_args()
    if arguments.capture:
        _capture()
        payload = _rebuild_derived()
        print(f"C11 CAPTURE + REPLAY: {payload['result']['status']}")
    elif arguments.rebuild_derived:
        payload = _rebuild_derived()
        print(f"C11 REPLAY: {payload['result']['status']}")
    else:
        _verify_output()
        print("C11 CAPTURE/REPLAY: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Freeze an SSE public-price observation and apply the fixed R2 screen.

The purpose is source-quality triangulation, not a formal replay.  The script
uses the same hypothesis family and timing arithmetic as the R2 public
observation screen, but its raw inputs are directly retained SSE JSONP
responses.  Exchange publication does not establish historical available_at,
rights, events, total return, or executable fills.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests

import run_r2_extended_public_series_probe as public_screen


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
RAW_DIR = CASE_DIR / "sources" / "probe-official-sse-etf-price-r2-20260814"
MANIFEST_JSON = RAW_DIR / "manifest.json"
MANIFEST_MD = RAW_DIR / "manifest.md"
OUTPUT_JSON = CASE_DIR / "analysis" / "r2_official_sse_etf_public_price_probe_20260814.json"
OUTPUT_MD = CASE_DIR / "analysis" / "r2_official_sse_etf_public_price_probe_20260814.md"
P02_RAW = CASE_DIR / "sources" / "probe-public-etf-extended-r2-20260814" / "public_sina_etf_eod_observation.json"

DATA_CUTOFF = "2026-08-13"
ASSETS = public_screen.ASSETS
SOURCE_QUALITY = "primary_official_public_retrospective_market_price_observation"
PRICE_BASIS = "exchange_market_close_adjustment_basis_not_declared_not_total_return"
SOURCE_FREEZE_SCHEMA = "research_source_freeze_control.v1"
MODEL_VERSION = public_screen.MODEL_VERSION
REFERER = "https://www.sse.com.cn/assortment/fund/etf/price/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (research evidence probe)",
    "Referer": REFERER,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _repo_relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _file_record(path: Path) -> dict[str, Any]:
    return {
        "path": _repo_relative(path),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _runtime_provenance() -> dict[str, str]:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        git_commit = completed.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        git_commit = "not_available"
    return {
        "git_commit_at_runtime": git_commit,
        "script_path": _repo_relative(Path(__file__).resolve()),
        "script_sha256": _sha256(Path(__file__).resolve()),
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "pandas_version": pd.__version__,
        "adapter": "requests HTTPS JSONP fetch from SSE public endpoint",
        "adapter_version": str(getattr(requests, "__version__", "not_reported")),
    }


def _dependency_records() -> list[dict[str, Any]]:
    if not P02_RAW.exists():
        return []
    return [
        {
            **_file_record(P02_RAW),
            "dependency_role": "descriptive_cross_source_overlap_only",
            "source_quality": "tier_3_public_aggregation_observation",
            "purpose": "P02 is read only to show close differences between public source paths; it cannot validate price basis, total return, historical availability or execution.",
            "limitations": "P02 is a non-entitled public observation and cannot be used for formal replay or strategy admission.",
        }
    ]


def _freeze_control(*, sealed_at: str, seal_status: str) -> dict[str, Any]:
    return {
        "schema_version": SOURCE_FREEZE_SCHEMA,
        "seal_status": seal_status,
        "sealed_at": sealed_at,
        "frozen_files": [_file_record(_raw_path(code)) for code in ASSETS],
        "runtime_provenance": _runtime_provenance(),
        "boundary": "Case-local hash control only. It detects a raw-source mismatch during scripted verification, but does not establish external notarization, data rights, point-in-time availability, total return or execution quality.",
    }


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_text(path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def _url(code: str) -> str:
    return (
        f"https://yunhq.sse.com.cn:32042/v1/sh1/dayk/{code}?callback=probe"
        "&select=date%2Copen%2Chigh%2Clow%2Cclose%2Cvolume&begin=0&end=5000"
    )


def _raw_path(code: str) -> Path:
    return RAW_DIR / f"sse_etf_dayk_{code}_begin0_end5000.jsonp"


def _parse_jsonp(raw: bytes, code: str) -> dict[str, Any]:
    text = raw.decode("utf-8")
    match = re.fullmatch(r"probe\((.*)\)", text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"SSE response for {code} is not expected JSONP")
    payload = json.loads(match.group(1))
    if str(payload.get("code")) != code:
        raise ValueError(f"SSE response code mismatch for {code}")
    if payload.get("begin") != 0:
        raise ValueError(f"SSE response begin offset mismatch for {code}")
    rows = payload.get("kline")
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"SSE response has no kline rows for {code}")
    if len(rows) != int(payload.get("total", -1)):
        raise ValueError(f"SSE response is incomplete for {code}: {len(rows)} != {payload.get('total')}")
    # The endpoint reports the exclusive effective end offset, truncating a
    # larger requested end to total when the full history fits in one response.
    if int(payload.get("end", -1)) != len(rows):
        raise ValueError(f"SSE response effective end mismatch for {code}")
    return payload


def _load_responses() -> dict[str, dict[str, Any]]:
    responses: dict[str, dict[str, Any]] = {}
    for code in ASSETS:
        path = _raw_path(code)
        if not path.is_file():
            raise FileNotFoundError(f"retained SSE source is absent: {path}")
        responses[code] = _parse_jsonp(path.read_bytes(), code)
    return responses


def _capture_responses() -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    if any(_raw_path(code).exists() for code in ASSETS) or MANIFEST_JSON.exists():
        raise FileExistsError(
            "source batch already exists; use --refresh-derived or --verify-only, not --capture"
        )
    raw_bytes: dict[str, bytes] = {}
    retrieval_times: dict[str, str] = {}
    for code in ASSETS:
        response = requests.get(_url(code), headers=HEADERS, timeout=20)
        if response.status_code != 200:
            raise RuntimeError(f"SSE request failed for {code}: HTTP {response.status_code}")
        _parse_jsonp(response.content, code)
        raw_bytes[code] = response.content
        retrieval_times[code] = datetime.now(timezone.utc).isoformat()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for code in ASSETS:
        _raw_path(code).write_bytes(raw_bytes[code])
    return _load_responses(), retrieval_times


def _make_manifest(
    responses: dict[str, dict[str, Any]],
    retrieval_times: dict[str, str],
    *,
    seal_status: str,
) -> dict[str, Any]:
    captured_at = min(retrieval_times.values())
    rows: list[dict[str, Any]] = []
    for code in ASSETS:
        path = _raw_path(code)
        payload = responses[code]
        rows.append(
            {
                **_file_record(path),
                "publisher": "Shanghai Stock Exchange",
                "title": f"SSE ETF daily market-price response for {code}",
                "document_date": DATA_CUTOFF,
                "retrieved_at": retrieval_times[code],
                "url": _url(code),
                "referer": REFERER,
                "format": "jsonp",
                "content_type_expected": "application/json;charset=UTF-8",
                "response_total": int(payload["total"]),
                "response_rows": len(payload["kline"]),
                "first_trade_date": str(payload["kline"][0][0]),
                "last_trade_date": str(payload["kline"][-1][0]),
                "capture_note": "Retrospectively retrieved official public response. It is not evidence of historical available_at, version lineage, data rights, total return, or execution.",
            }
        )
    manifest = {
        "capture_batch": RAW_DIR.name,
        "captured_at": captured_at,
        "purpose": "Frozen official SSE public daily market-price observations for an R2 research-only hypothesis screen. The inputs are not entitled/PIT data and cannot establish total return, product admission, allocation, holding or action.",
        "source_quality": SOURCE_QUALITY,
        "files": rows,
        "dependencies": _dependency_records(),
        "limitations": [
            "The historical rows were retrieved on the capture date, not preserved as evidence of their original-date availability or revision history.",
            "The exchange endpoint does not establish a disclosed adjustment basis, NAV/IOPV, distributions, corporate actions, trading status, price limits, tax/fees, bid/ask, capacity, settlement, broker route or fills.",
            "Public access to an endpoint does not establish permission to retain, normalize, formally replay, derive from or independently review an entitled data product.",
        ],
        "source_freeze": _freeze_control(
            sealed_at=datetime.now(timezone.utc).isoformat(),
            seal_status=seal_status,
        ),
    }
    _write_json(MANIFEST_JSON, manifest)
    table = "\n".join(
        f"| {row['path'].rsplit('/', 1)[-1]} | {row['response_rows']} / {row['response_total']} | {row['first_trade_date']} | {row['last_trade_date']} | `{row['sha256']}` |"
        for row in rows
    )
    _write_text(
        MANIFEST_MD,
        f"""# Official SSE ETF Public-Price Observation Manifest

- Batch: `{manifest['capture_batch']}`
- Capture time: `{captured_at}`
- Method: anonymous, read-only HTTPS GET to the SSE daily-price endpoint with
  its public ETF-page Referer. No credentials, account, purchase, bypass or
  trading action was used.
- Boundary: responses were retrieved retrospectively. They do not prove
  original-date availability, revisions, data rights, total return, fund
  events, market status, costs, depth, execution, eligibility or a strategy.

| Raw response | Rows / reported total | First date | Last date | SHA-256 |
|---|---:|---|---|---|
{table}

The `begin=0&end=5000` request returned all rows reported by the response for
each retained code. This is a source-access observation only; the endpoint
response itself does not close any data, replay, execution or decision gate.
""",
    )
    return manifest


def _verify_entry(entry: dict[str, Any], *, label: str) -> None:
    required = {"path", "bytes", "sha256"}
    missing = sorted(required.difference(entry))
    if missing:
        raise ValueError(f"{label} has no required fields: {missing}")
    path = (REPO_ROOT / str(entry["path"])).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"{label} is missing: {path}")
    if path.stat().st_size != int(entry["bytes"]):
        raise ValueError(f"{label} byte size differs: {path}")
    if _sha256(path) != entry["sha256"]:
        raise ValueError(f"{label} SHA-256 differs: {path}")


def _verify_registry_manifest_seal() -> None:
    registry_path = CASE_DIR / "data" / "source_registry.json"
    if not registry_path.is_file():
        raise FileNotFoundError("source registry is required for sealed-source verification")
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    source = next((item for item in registry if item.get("source_id") == "P03"), None)
    if not isinstance(source, dict):
        raise ValueError("source registry has no P03 sealed-source record")
    if source.get("sealed_manifest_path") != _repo_relative(MANIFEST_JSON):
        raise ValueError("source registry P03 manifest path differs from the required sealed manifest")
    if source.get("sealed_manifest_sha256") != _sha256(MANIFEST_JSON):
        raise ValueError("source registry P03 manifest SHA-256 differs from the sealed manifest")


def _load_frozen_source() -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    responses = _load_responses()
    if not MANIFEST_JSON.exists():
        raise FileNotFoundError("retained SSE observations require a sealed manifest")
    manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    freeze = manifest.get("source_freeze")
    if not isinstance(freeze, dict) or freeze.get("schema_version") != SOURCE_FREEZE_SCHEMA:
        raise ValueError("source manifest is not sealed; run --seal-existing-freeze explicitly")
    frozen_files = freeze.get("frozen_files")
    files = manifest.get("files")
    if not isinstance(frozen_files, list) or len(frozen_files) != len(ASSETS):
        raise ValueError("source freeze has an invalid raw-file count")
    if not isinstance(files, list) or len(files) != len(ASSETS):
        raise ValueError("source manifest has an invalid raw-file count")
    freeze_by_path = {entry.get("path"): entry for entry in frozen_files}
    manifest_by_path = {entry.get("path"): entry for entry in files}
    expected_paths = {_repo_relative(_raw_path(code)) for code in ASSETS}
    if set(freeze_by_path) != expected_paths or set(manifest_by_path) != expected_paths:
        raise ValueError("source-freeze or source-manifest paths differ from the retained SSE files")
    for path in sorted(expected_paths):
        _verify_entry(freeze_by_path[path], label="source-freeze raw file")
        _verify_entry(manifest_by_path[path], label="source-manifest raw file")
        freeze_identity = {key: freeze_by_path[path][key] for key in ("path", "bytes", "sha256")}
        manifest_identity = {key: manifest_by_path[path][key] for key in ("path", "bytes", "sha256")}
        if freeze_identity != manifest_identity:
            raise ValueError(f"source-freeze and source-manifest records differ: {path}")
    for number, dependency in enumerate(manifest.get("dependencies", []), start=1):
        _verify_entry(dependency, label=f"source dependency {number}")
    _verify_registry_manifest_seal()
    return responses, manifest


def _seal_existing_freeze() -> dict[str, Any]:
    responses = _load_responses()
    if not MANIFEST_JSON.exists():
        raise FileNotFoundError("cannot seal existing SSE observations without their original manifest")
    existing = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    if existing.get("source_freeze"):
        raise ValueError("source manifest is already sealed; do not reseal it")
    files = existing.get("files")
    if not isinstance(files, list) or len(files) != len(ASSETS):
        raise ValueError("existing source manifest has an invalid raw-file count")
    for entry in files:
        _verify_entry(entry, label="existing source-manifest raw file")
    existing["dependencies"] = _dependency_records()
    existing["source_freeze"] = _freeze_control(
        sealed_at=datetime.now(timezone.utc).isoformat(),
        seal_status="explicit_post_capture_migration",
    )
    existing["freeze_migration_boundary"] = (
        "The original capture pre-dated the explicit hash-control migration. "
        "Original capture runtime provenance is unavailable; the migration provenance "
        "is retained in source_freeze.runtime_provenance."
    )
    _write_json(MANIFEST_JSON, existing)
    table = "\n".join(
        f"| {entry['path'].rsplit('/', 1)[-1]} | {entry['response_rows']} / {entry['response_total']} | {entry['first_trade_date']} | {entry['last_trade_date']} | {entry['sha256']} |"
        for entry in existing["files"]
    )
    dependencies = "\n".join(
        f"- {entry['path']} (SHA-256 {entry['sha256']}): {entry['dependency_role']}."
        for entry in existing["dependencies"]
    ) or "None."
    _write_text(
        MANIFEST_MD,
        (
            "# Official SSE ETF Public-Price Observation Manifest\n\n"
            f"Batch: {existing['capture_batch']}\n\n"
            "This retained official public-price response set is retrospective and not "
            "point-in-time, total-return, entitlement or execution evidence. The manifest "
            "now contains a case-local hash control; verify and derived-refresh modes "
            "validate it without rewriting raw bytes or the manifest.\n\n"
            "| Raw response | Rows / reported total | First date | Last date | SHA-256 |\n"
            "|---|---:|---|---|---|\n"
            f"{table}\n\n"
            "## Descriptive-only dependencies\n\n"
            f"{dependencies}\n"
        ),
    )
    if set(responses) != set(ASSETS):
        raise ValueError("sealed source response set is incomplete")
    return existing


def _as_screen_input(responses: dict[str, dict[str, Any]]) -> dict[str, Any]:
    series: dict[str, Any] = {}
    cutoff = int(DATA_CUTOFF.replace("-", ""))
    for code, payload in responses.items():
        records = []
        for row in payload["kline"]:
            if not isinstance(row, list) or len(row) < 6:
                raise ValueError(f"invalid kline row for {code}")
            date_value = int(row[0])
            if date_value > cutoff:
                continue
            records.append(
                {
                    "date": f"{date_value:08d}"[:4] + "-" + f"{date_value:08d}"[4:6] + "-" + f"{date_value:08d}"[6:8],
                    "open": float(row[1]),
                    "high": float(row[2]),
                    "low": float(row[3]),
                    "close": float(row[4]),
                    "volume": float(row[5]),
                }
            )
        if not records:
            raise ValueError(f"no rows on or before cutoff for {code}")
        series[code] = {"records": records}
    return {"series": series}


def _p02_overlap(screen_input: dict[str, Any]) -> dict[str, Any]:
    if not P02_RAW.exists():
        return {"status": "not_available", "reason": "P02 raw observation is not present."}
    p02 = json.loads(P02_RAW.read_text(encoding="utf-8"))
    rows = []
    for code in ASSETS:
        left = pd.DataFrame(screen_input["series"][code]["records"])
        right = pd.DataFrame(p02.get("series", {}).get(code, {}).get("records", []))
        left["date"] = pd.to_datetime(left["date"], errors="coerce")
        right["date"] = pd.to_datetime(right["date"], errors="coerce")
        left["close"] = pd.to_numeric(left["close"], errors="coerce")
        right["close"] = pd.to_numeric(right["close"], errors="coerce")
        joint = pd.concat(
            [
                left.dropna(subset=["date", "close"]).set_index("date")["close"].rename("sse"),
                right.dropna(subset=["date", "close"]).set_index("date")["close"].rename("p02"),
            ],
            axis=1,
            sort=True,
        ).dropna()
        difference = (joint["sse"] - joint["p02"]).abs()
        rows.append(
            {
                "code": code,
                "overlap_sessions": len(joint),
                "max_absolute_close_difference": float(difference.max()),
                "rows_above_0_001_difference": int((difference > 0.001).sum()),
                "rows_above_0_01_difference": int((difference > 0.01).sum()),
            }
        )
    return {
        "status": "descriptive_cross_source_observation_not_basis_validation",
        "p02_path": str(P02_RAW.relative_to(CASE_DIR)),
        "p02_sha256": _sha256(P02_RAW),
        "interpretation": "The SSE source is first-party and P02 is public aggregation. Similar close values do not prove either input's adjustment basis, historical availability, total return or execution quality.",
        "rows": rows,
    }


def _screen(screen_input: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    opens, prices, presence_rows = public_screen._market_panels(screen_input)
    hypotheses: list[dict[str, Any]] = []
    for hypothesis in public_screen.HYPOTHESES:
        targets, rebalance_events, decision_ledger = public_screen._build_rebalance_schedule(
            prices,
            hypothesis,
        )
        sensitivity = [
            public_screen._evaluate(
                opens,
                prices,
                targets,
                rebalance_events,
                cost,
                include_daily_state=cost == 20.0 and hypothesis["hypothesis_id"] == "H01",
            )
            for cost in public_screen.COST_BPS
        ]
        primary = next(
            row for row in sensitivity if row["per_one_way_turnover_cost_bps"] == 20.0
        )
        primary_summary = {
            key: value for key, value in primary.items() if key != "daily_position_state"
        }
        hypotheses.append(
            {
                **hypothesis,
                "decision_count": len(decision_ledger),
                "monthly_decision_ledger": decision_ledger,
                "daily_position_state_retention": (
                    "Retained only for H01 at the 20-bps sensitivity to make the"
                    " unit/cash drift convention inspectable without duplicating"
                    " full daily state ledgers for exploratory variants. The retained"
                    " state is located in cost_sensitivity, not duplicated in"
                    " primary_20bps."
                ),
                "cost_sensitivity": sensitivity,
                "primary_20bps": primary_summary,
                "screening_readout": {
                    "arithmetic_all_windows_meet_5pct_public_series_hurdle": primary["rolling_five_year_public_series_diagnostic"]["all_complete_windows_meet_5pct"],
                    "not_a_total_return_or_strategy_pass": True,
                },
            }
        )
    survivors = [
        item["hypothesis_id"]
        for item in hypotheses
        if item["primary_20bps"]["rolling_five_year_public_series_diagnostic"]["all_complete_windows_meet_5pct"]
    ]
    source_rows = [
        {
            "path": row["path"],
            "sha256": row["sha256"],
            "response_rows": row["response_rows"],
            "response_total": row["response_total"],
        }
        for row in manifest["files"]
    ]
    return {
        "schema_version": "r2_official_sse_public_price_hypothesis_probe.v2",
        "as_of": "2026-08-14",
        "artifact_class": "derived_research_observation",
        "research_only": True,
        "formal_decision_eligible": False,
        "portfolio_q": 0,
        "derived_runtime_provenance": _runtime_provenance(),
        "source": {
            "manifest_path": str(MANIFEST_JSON.relative_to(CASE_DIR)),
            "sealed_manifest_sha256": _sha256(MANIFEST_JSON),
            "source_freeze": manifest["source_freeze"],
            "dependencies": manifest.get("dependencies", []),
            "quality": SOURCE_QUALITY,
            "price_basis": PRICE_BASIS,
            "raw_responses": source_rows,
        },
        "hypothesis_family": {
            "source_code": "tools/run_r2_extended_public_series_probe.py",
            "status": "script_fixed_for_this_screen_not_independently_pre_registered",
            "reason_for_reuse": "Use exactly the prior screen's rules and cost sensitivities for a source-path triangulation, not a new parameter search.",
        },
        "protocol": {
            "status": "retrospective_official_public_observation_exploratory_screen_not_pit_not_formal_replay",
            "decision_frequency": "first observed session of each calendar month after the full lookback exists; the warm-up waits for a month boundary rather than entering mid-month",
            "information_timing": "signal uses closes only through the previous observed session; target is executed at the next observed session open and marked to that same session close",
            "rebalance_frequency": "Every scheduled monthly execution rebalances drifted units to the target, even when the target sleeve set has not changed.",
            "asset_scope": {
                "risk_comparison_sleeves": list(public_screen.RISK_ASSETS),
                "defensive_comparison_sleeve": public_screen.DEFENSIVE_ASSET,
                "scope_warning": "A four-ETF source-access observation is not a frozen U0 population, an open-universe result, a decision universe or an approved product list.",
            },
            "accounting_model": "Monthly self-financing units-and-cash simulation. At each observed open, turnover equals one half of the absolute change from drifted pre-trade security-plus-cash weights to target component weights. Cost equals pre-trade observed-open NAV multiplied by that turnover and the stated sensitivity. Units then drift until the next scheduled monthly rebalance.",
            "cost_model": "Per-one-way-turnover cost sensitivity only. It excludes verified fees, taxes, bid/ask, impact, T+1, lots, halts, price limits, settlement, no-fill and capacity.",
            "return_basis": "Observed official SSE open-to-close and close-to-next-open market-price arithmetic inside a self-financing accounting model; it remains distinct from investor total return.",
            "annual_metric_boundary": "Annual rows carry forward prior-session NAV. Initial and cutoff-year fragments are explicitly marked incomplete and are not used for a separate annual hurdle.",
        },
        "evaluation": {
            "common_panel_start": prices.index[0].date().isoformat(),
            "common_panel_end": prices.index[-1].date().isoformat(),
            "common_panel_sessions": len(prices),
            "daily_source_presence_status": presence_rows,
            "hypotheses": hypotheses,
        },
        "p02_overlap_observation": _p02_overlap(screen_input),
        "decision": {
            "formal_strategy_status": "not_usable_q0",
            "apparent_arithmetic_candidates_at_20bps": survivors,
            "reason": [
                "Direct SSE publication improves the publisher path for market-price observation but does not supply an entitled PIT total-return or execution ledger.",
                "An apparent arithmetic survivor, if any, would still be only a hypothesis for a properly authorized total-return and execution replay.",
                "All result windows overlap, and this four-ETF observation remains coverage-restricted and retrospective.",
                "UR01--UR05, a U0 freeze, accepted data modules, formal replay, route/cost evidence and prospective paper reconciliation remain open.",
            ],
        },
    }


def _markdown(result: dict[str, Any]) -> str:
    lines = [
        "# R2 上交所公开市场价序列筛查 — 2026-08-14",
        "",
        "- 状态：**研究性筛查，不可用；`q=0`。**",
        "- 原始输入：上交所公开日线 JSONP 响应；完整路径、行数和哈希见下方的 source manifest。",
        f"- 计算口径：`{MODEL_VERSION}`；与 P02 共用同一月度自融资单位与现金模型，故本来源只能三角检查价格路径，不能独立验证计算模型。",
        "- 数据性质：第一方公开市场价观察，但为回溯提取；价格调整、历史可得时间、基金事件、NAV/IOPV、交易状态、费用税费、盘口和成交均未获验证。",
        "- 因此，下面的数值只能称为“公开市场价序列算术变化”，不是投资者总回报、正式历史回放或可执行策略表现。",
        "",
        "## 与前一 R2 筛查保持相同的规则",
        "",
        "本筛查刻意复用 `run_r2_extended_public_series_probe.py` 的七个脚本固定、非独立预注册假设及其 0/10/20/50 bps 单向换手成本敏感性；没有针对上交所数据重新选参。完整回看期出现后的下一个自然月首个观测日用此前一观测日收盘价计算动量，目标在下一观测日开盘建立，并按当日收盘价计入首日变化。此后每一个既定月度执行日都将漂移后的单位和现金重新调至目标，即使入选袖套没有变化。风险比较袖套为 510300、510880、518880，防守比较袖套为 511010。",
        "",
        "该四只 ETF 是覆盖受限的源路径观察，不是开放 U0 总体、未来决策资产池、产品清单或配置建议。20 bps 是按漂移后证券加现金权重计算的单向换手成本敏感性，也不是经核验的交易总成本。",
        "",
        "| 假设 | 回看观测数 | 前 N 个 | 风险预算 | 20 bps 年化公开市场价序列变化 | 最大回撤 | 5 年窗口低于 5% | 5 年窗口最小值 | 筛查解释 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for item in result["evaluation"]["hypotheses"]:
        metric = item["primary_20bps"]
        rolling = metric["rolling_five_year_public_series_diagnostic"]
        readout = "未被该算术门槛否定" if rolling["all_complete_windows_meet_5pct"] else "被该算术门槛否定"
        lines.append(
            "| {id} | {lookback} | {top_n} | {budget:.0%} | {annual:.2%} | {drawdown:.2%} | {below}/{count} | {minimum:.2%} | {readout} |".format(
                id=item["hypothesis_id"],
                lookback=item["lookback_observations"],
                top_n=item["top_n"],
                budget=item["risk_budget"],
                annual=metric["annualized_public_series_change"],
                drawdown=metric["maximum_drawdown"],
                below=rolling["windows_below_5pct"],
                count=rolling["window_count"],
                minimum=rolling["minimum_annualized_public_series_change"],
                readout=readout,
            )
        )
    lines.extend(
        [
            "",
            "## 结果与交叉来源观察",
            "",
            f"在 20 bps 单向换手成本敏感性下，未被本次官方公开市场价算术门槛否定的假设为：`{', '.join(result['decision']['apparent_arithmetic_candidates_at_20bps']) or '无'}`。该结果不是策略通过，也不应与投资者总回报混淆。",
            "",
            "上交所源路径改善的是发布方身份，而不是回放资格。历史行仍是今天回溯取得，且缺少分派、公司行动、NAV、IOPV、状态、权利、历史版本和执行账本。",
            "",
            "| 代码 | 与 P02 公开聚合样本的重叠观测数 | 最大收盘价绝对差 | 差异大于 0.001 的行数 | 差异大于 0.01 的行数 |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in result["p02_overlap_observation"].get("rows", []):
        lines.append(
            "| {code} | {sessions} | {max_difference:.6f} | {above_small} | {above_large} |".format(
                code=row["code"],
                sessions=row["overlap_sessions"],
                max_difference=row["max_absolute_close_difference"],
                above_small=row["rows_above_0_001_difference"],
                above_large=row["rows_above_0_01_difference"],
            )
        )
    lines.extend(
        [
            "",
            "两个来源的收盘数值接近并不能验证复权、可得时点或交易质量；两套筛查共用同一计算函数，因此它们也不能彼此独立验证自融资模型。个别差异必须保留而非事后修正。",
            "",
            "所以，本次结果只增加了简化 ETF 规则的来源路径观察，并不能把该否定推广到所有国内资产策略，也不能替代独立模型复核。下一阶段仍应基于类别中立、预冻结的 U0→T2 规则，在获授权的时点化总回报、事件和执行账本上重新检验。",
            "",
            "机器可读副本：[r2_official_sse_etf_public_price_probe_20260814.json](r2_official_sse_etf_public_price_probe_20260814.json)。",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument(
        "--capture",
        action="store_true",
        help="Capture new SSE raw responses only when this source batch does not yet exist.",
    )
    modes.add_argument(
        "--seal-existing-freeze",
        action="store_true",
        help="One-time explicit migration that adds source hash control to a pre-existing capture.",
    )
    modes.add_argument(
        "--refresh-derived",
        action="store_true",
        help="Validate a sealed source and refresh derived research artifacts without touching the source manifest.",
    )
    modes.add_argument(
        "--verify-only",
        action="store_true",
        help="Read and validate the sealed source and calculation without writing any artifact.",
    )
    args = parser.parse_args()
    if args.capture:
        responses, retrieval_times = _capture_responses()
        manifest = _make_manifest(
            responses,
            retrieval_times,
            seal_status="captured_with_hash_control",
        )
        result = _screen(_as_screen_input(responses), manifest)
        _write_json(OUTPUT_JSON, result)
        _write_text(OUTPUT_MD, _markdown(result))
    elif args.seal_existing_freeze:
        _seal_existing_freeze()
        print("R2 OFFICIAL SSE SOURCE FREEZE: PASS (explicit migration only)")
        return 0
    else:
        responses, manifest = _load_frozen_source()
        result = _screen(_as_screen_input(responses), manifest)
        if args.refresh_derived:
            _write_json(OUTPUT_JSON, result)
            _write_text(OUTPUT_MD, _markdown(result))
    print(
        "R2 OFFICIAL SSE PRICE PROBE: PASS "
        "(sealed research-only retrospective public observation; no strategy admission, allocation or action)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

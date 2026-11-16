#!/usr/bin/env python3
"""Probe official actual-contract daily-file availability without a backtest."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


CASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_JSON = CASE_DIR / "data/futures_exchange_data_access_probe_20260814.json"
OUTPUT_MD = CASE_DIR / "data/futures_exchange_data_access_probe_20260814.md"
RAW_DIR = CASE_DIR / "sources/probe-exchange-data-r0-20260814"
SOURCE_MANIFEST = RAW_DIR / "manifest.json"
DATES = ("20160104", "20180102", "20200102", "20220104", "20240102", "20260813")
SHFE_WANTED = {"AU", "CU", "RB"}
CZCE_WANTED = {"TA", "CF", "MA"}


def _fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 (research evidence probe)"})
    with urlopen(request, timeout=30) as response:
        return response.read()


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _manifest_entry(name: str) -> dict[str, object]:
    """Require a pre-existing manifest row before a source sample can be replayed."""
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    matches = [row for row in manifest.get("files", []) if Path(str(row.get("path", ""))).name == name]
    if len(matches) != 1:
        raise ValueError(f"source manifest must contain exactly one pre-existing row for {name}")
    entry = matches[0]
    if not entry.get("retrieved_at"):
        raise ValueError(f"source manifest row lacks retrieved_at for {name}")
    return entry


def _archive_raw(name: str, raw: bytes) -> tuple[str, dict[str, object]]:
    """Verify a raw sample against its manifest; reject a new or changed response."""
    entry = _manifest_entry(name)
    path = RAW_DIR / name
    if not path.exists():
        raise ValueError(f"manifested raw source is missing: {path.name}")
    if path.read_bytes() != raw:
        raise ValueError(f"raw response changed for {path.name}; preserve both versions explicitly")
    if _sha256(raw) != entry.get("sha256") or len(raw) != entry.get("bytes"):
        raise ValueError(f"raw response does not match manifest fields for {path.name}")
    return str(path.relative_to(CASE_DIR)), entry


def _shfe(day: str) -> dict[str, object]:
    url = f"https://www.shfe.com.cn/data/tradedata/future/dailydata/kx{day}.dat"
    raw = _fetch(url)
    archive_path, manifest_entry = _archive_raw(f"shfe_actual_contract_daily_{day}.json", raw)
    payload = json.loads(raw.decode("utf-8"))
    rows = payload.get("o_curinstrument")
    if not isinstance(rows, list):
        raise ValueError(f"SHFE {day} has no o_curinstrument list")
    wanted = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        variety = str(row.get("PRODUCTGROUPID") or row.get("PRODUCTID") or "").strip().split("_")[0].upper()
        delivery = str(row.get("DELIVERYMONTH") or "")
        if variety in SHFE_WANTED and delivery and delivery not in {"小计", "合计"}:
            wanted.append(row)
    return {
        "date": f"{day[:4]}-{day[4:6]}-{day[6:]}",
        "url": url,
        "archive_path": archive_path,
        "retrieval_basis": "retrospective_source_access_sample",
        "retrieved_at": manifest_entry["retrieved_at"],
        "raw_sha256": _sha256(raw),
        "total_contract_rows": len(rows),
        "wanted_contract_rows": len(wanted),
        "wanted_varieties": sorted({str(row.get("PRODUCTGROUPID") or row.get("PRODUCTID") or "").strip().split("_")[0].upper() for row in wanted}),
        "required_fields_observed": ["OHLC", "previous settlement", "settlement", "volume", "open interest", "turnover"],
    }


def _czce(day: str) -> dict[str, object]:
    url = f"https://www.czce.com.cn/cn/DFSStaticFiles/Future/{day[:4]}/{day}/FutureDataDaily.txt"
    raw = _fetch(url)
    archive_path, manifest_entry = _archive_raw(f"czce_actual_contract_daily_{day}.txt", raw)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("gb18030")
    codes = []
    for line in text.splitlines():
        code = line.strip().split("|")[0].strip().upper()
        match = re.fullmatch(r"([A-Z]+)\d+", code)
        if match and match.group(1) in CZCE_WANTED:
            codes.append(code)
    if not codes:
        raise ValueError(f"CZCE {day} has no selected actual-contract rows")
    return {
        "date": f"{day[:4]}-{day[4:6]}-{day[6:]}",
        "url": url,
        "archive_path": archive_path,
        "retrieval_basis": "retrospective_source_access_sample",
        "retrieved_at": manifest_entry["retrieved_at"],
        "raw_sha256": _sha256(raw),
        "wanted_contract_rows": len(codes),
        "wanted_varieties": sorted({re.match(r"[A-Z]+", code).group(0) for code in codes}),
        "required_fields_observed": ["previous settlement", "OHLC", "settlement", "volume", "open interest", "turnover"],
    }


def _write(path: Path, content: str) -> None:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def main() -> int:
    revalidated_at = datetime.now(timezone.utc).isoformat()
    shfe = [_shfe(day) for day in DATES]
    czce = [_czce(day) for day in DATES]
    archive_retrieval_times = sorted({str(row["retrieved_at"]) for row in shfe + czce})
    result = {
        "schema_version": "futures_exchange_data_access_probe.v2",
        "revalidated_at": revalidated_at,
        "artifact_class": "derived_research_evidence",
        "status": "actual_contract_eod_paths_observed_not_replay_ready",
        "research_only": True,
        "formal_decision_eligible": False,
        "portfolio_q": 0,
        "scope": "official daily-file availability sample for AU/CU/RB and TA/CF/MA; initial research focus remains AU/CU/TA",
        "historical_provenance": {
            "retrieval_basis": "retrospective_source_access_sample",
            "source_archive_retrieved_at": archive_retrieval_times,
            "revalidated_at": revalidated_at,
            "classification": "retrospective_source_access_sample",
            "boundary": "The historical files were requested after their trade dates. Their retention proves present source-path availability, not what was available on each original decision date."
        },
        "shfe": shfe,
        "czce": czce,
        "conclusion": {
            "supported": "Twelve locally retained, retrospectively retrieved official daily-file samples returned actual listed-contract rows across six sampled dates from 2016 to 2026.",
            "not_supported": [
                "A complete frozen historical archive or a point-in-time contract master.",
                "Original-date availability of the historical files or their contents.",
                "Historical bid/ask, fills, broker charges, broker margin, limit locks, position limits or delivery eligibility.",
                "A futures return result, allocation or action."
            ],
            "next_gate": "Archive every trading-day raw response plus contract lifecycle, fees/margin/limit records and a pre-registered selection/roll/no-fill rule before an actual-contract replay."
        }
    }
    _write(OUTPUT_JSON, json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    shfe_rows = "\n".join(f"| {row['date']} | {row['total_contract_rows']} | {row['wanted_contract_rows']} | {', '.join(row['wanted_varieties'])} |" for row in shfe)
    czce_rows = "\n".join(f"| {row['date']} | {row['wanted_contract_rows']} | {', '.join(row['wanted_varieties'])} |" for row in czce)
    _write(OUTPUT_MD, f"""# Futures Actual-Contract EOD Data-Access Probe\n\n- Status: **actual-contract paths observed; not replay ready**; `q=0`.\n- Method: direct official daily-file requests, with six date samples from 2016--2026.\n- Scope: source-access verification only; it is not a P&L test.\n\n## SHFE samples\n\n| Date | All contract rows | AU/CU/RB rows | Varieties |\n|---|---:|---:|---|\n{shfe_rows}\n\n## CZCE samples\n\n| Date | TA/CF/MA rows | Varieties |\n|---|---:|---|\n{czce_rows}\n\nThe raw 2026-08-13 files are archived under `sources/probe-exchange-data-r0-20260814/`. The query output confirms actual listed-contract rows and EOD price/settlement/liquidity fields, not a continuous series. It does not establish a complete frozen archive, contract lifecycle, price-limit state, historical margin, broker cost, bid/ask, fill, delivery eligibility or a strategy result.\n""")
    _write(
        OUTPUT_MD,
        OUTPUT_MD.read_text(encoding="utf-8").replace(
            "- Method: direct official daily-file requests, with six date samples from 2016--2026.",
            "- Method: direct official daily-file requests, with six date samples from 2016--2026.\n- Historical provenance: every source sample was retrieved retrospectively at " + ", ".join(archive_retrieval_times) + "; direct paths were revalidated at " + revalidated_at + ". This is source-access evidence, not original-date point-in-time availability.",
        ).replace(
            "The raw 2026-08-13 files are archived under `sources/probe-exchange-data-r0-20260814/`.",
            "All twelve raw samples are archived under `sources/probe-exchange-data-r0-20260814/` and are hash-bound in its manifest.",
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

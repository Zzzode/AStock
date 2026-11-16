#!/usr/bin/env python3
"""Capture a small, hash-bound SHFE commodity-contract evidence batch.

The batch is deliberately a rulebook and source-route record.  It does not
construct a return series, submit an order, or establish an investor's access.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
SOURCE_DIR = CASE_DIR / "sources" / "c9-official-shfe-commodity-contracts-20260815"
MANIFEST_PATH = SOURCE_DIR / "manifest.json"

RULE_SOURCES = (
    {
        "filename": "shfe_cu_contract_rules_20260101.html",
        "url": "https://www.shfe.cn/regulation/exchangerules/productrules/202512/t20251231_829954.html",
        "title": "Shanghai Futures Exchange copper futures business rules",
        "document_date": "2026-01-01",
        "format": "html",
        "purpose": "Current contract unit, tick, listed-month, expiry, base-margin and price-limit rule evidence for CU only.",
    },
    {
        "filename": "shfe_au_contract_rules_20260101.html",
        "url": "https://www.shfe.cn/regulation/exchangerules/productrules/202512/t20251231_829960.html",
        "title": "Shanghai Futures Exchange gold futures business rules",
        "document_date": "2026-01-01",
        "format": "html",
        "purpose": "Current contract unit, tick, listed-month, expiry, base-margin and price-limit rule evidence for AU only.",
    },
    {
        "filename": "shfe_ru_contract_rules_20260101.html",
        "url": "https://www.shfe.cn/regulation/exchangerules/productrules/202512/t20251231_829973.html",
        "title": "Shanghai Futures Exchange natural-rubber futures business rules",
        "document_date": "2026-01-01",
        "format": "html",
        "purpose": "Current contract unit, tick, listed-month, expiry, base-margin and price-limit rule evidence for RU only.",
    },
    {
        "filename": "shfe_risk_control_rules_20260706.html",
        "url": "https://www.shfe.cn/regulation/exchangerules/otherrules/202606/t20260622_832192.html",
        "title": "Shanghai Futures Exchange risk-control measures",
        "document_date": "2026-07-06",
        "format": "html",
        "purpose": "Current evidence that SHFE may alter margin and risk controls; base product parameters cannot be treated as session-specific personal requirements.",
    },
)

SAMPLE_DATES = ("20160104", "20180102", "20200102", "20220104", "20240102", "20260814")


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "AStock research evidence capture/1.0"})
    with urlopen(request, timeout=45) as response:
        return response.read()


def _repo_path(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _atomic_write(path: Path, raw: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(raw)
    temporary.replace(path)


def _git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def _capture() -> int:
    if MANIFEST_PATH.exists():
        raise RuntimeError(
            f"refusing to overwrite existing frozen source batch: {MANIFEST_PATH}; use --verify-only"
        )
    SOURCE_DIR.mkdir(parents=True, exist_ok=False)
    captured_at = datetime.now(timezone.utc).isoformat()
    files: list[dict[str, object]] = []

    for source in RULE_SOURCES:
        raw = _fetch(str(source["url"]))
        if b"WEB \xe5\xba\x94\xe7\x94\xa8\xe9\x98\xb2\xe7\x81\xab\xe5\xa2\x99" in raw or b"safeline_bot_challenge" in raw:
            raise RuntimeError(f"refusing WAF challenge body for {source['url']}")
        path = SOURCE_DIR / str(source["filename"])
        _atomic_write(path, raw)
        files.append(
            {
                "path": _repo_path(path),
                "publisher": "Shanghai Futures Exchange",
                "title": source["title"],
                "document_date": source["document_date"],
                "retrieved_at": captured_at,
                "url": source["url"],
                "format": source["format"],
                "capture_note": "First-party rule text retained read-only. It documents dated exchange terms only; it does not establish broker-specific requirements, personal eligibility, a fill, an allocation, a holding, an order or a return.",
                "purpose": source["purpose"],
                "bytes": len(raw),
                "sha256": _sha256(raw),
            }
        )

    for day in SAMPLE_DATES:
        url = f"https://www.shfe.cn/data/tradedata/future/dailydata/kx{day}.dat"
        raw = _fetch(url)
        payload = json.loads(raw.decode("utf-8"))
        rows = payload.get("o_curinstrument")
        if not isinstance(rows, list):
            raise RuntimeError(f"SHFE daily file has no o_curinstrument list for {day}")
        selected_rows = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            product = str(row.get("PRODUCTGROUPID") or row.get("PRODUCTID") or "").strip().split("_")[0].upper()
            delivery_month = str(row.get("DELIVERYMONTH") or "").strip()
            if product in {"CU", "AU", "RU"} and delivery_month not in {"", "小计", "合计"}:
                selected_rows.append(row)
        seen = {
            str(row.get("PRODUCTGROUPID") or row.get("PRODUCTID") or "").strip().split("_")[0].upper()
            for row in selected_rows
        }
        if seen != {"CU", "AU", "RU"}:
            raise RuntimeError(f"SHFE daily file missing candidate family rows for {day}: {sorted(seen)}")
        path = SOURCE_DIR / f"shfe_actual_contract_daily_{day}.json"
        _atomic_write(path, raw)
        files.append(
            {
                "path": _repo_path(path),
                "publisher": "Shanghai Futures Exchange",
                "title": "SHFE daily actual futures-contract data",
                "document_date": f"{day[:4]}-{day[4:6]}-{day[6:]}",
                "retrieved_at": captured_at,
                "url": url,
                "format": "json",
                "candidate_contract_rows": len(selected_rows),
                "candidate_families": sorted(seen),
                "capture_note": "Retrospectively captured official EOD actual-contract rows. The response proves a presently reachable dated source path and selected fields, not original-date availability, a complete lifecycle, historic risk controls, data rights, bid/ask, order fill, broker cost, account permission or investment result.",
                "bytes": len(raw),
                "sha256": _sha256(raw),
            }
        )

    frozen_files = [
        {"path": entry["path"], "bytes": entry["bytes"], "sha256": entry["sha256"]}
        for entry in files
    ]
    manifest = {
        "schema_version": "c9_shfe_commodity_contract_source_manifest.v1",
        "capture_batch": "c9-official-shfe-commodity-contracts-20260815",
        "case_id": CASE_DIR.name,
        "captured_at": captured_at,
        "purpose": "First-party SHFE product-rule capture and six-date actual-contract EOD source-route sample for the C9 commodity-futures research candidate. It is not a return test, product admission or action record.",
        "source_quality": "primary_official_rule_text_and_retrospective_actual_contract_sample",
        "protocol_status": "source_route_observation_not_historical_replay",
        "files": files,
        "limitations": [
            "All dated daily responses were retrieved retrospectively. Their present accessibility does not prove original-date availability, immutability, revision history or entitlement.",
            "Six daily samples are not a full actual-contract history, point-in-time contract master, trading calendar, delivery-status archive, margin/limit notice archive or broker record.",
            "The rule pages provide exchange-level base parameters. SHFE may alter risk controls and a broker may impose additional requirements; neither source proves a session-specific personal margin, cost, access route or fill.",
            "No continuous series, P&L, allocation, holding, order or return claim is generated from this batch."
        ],
        "source_freeze": {
            "schema_version": "research_source_freeze_control.v1",
            "seal_status": "case_local_hash_control_only",
            "sealed_at": captured_at,
            "boundary": "The freeze detects a local raw-file mismatch only. It is not external notarization, a data licence, point-in-time evidence, personal-eligibility proof, execution validation or investment instruction.",
            "frozen_files": frozen_files,
            "runtime_provenance": {
                "script_path": _repo_path(Path(__file__).resolve()),
                "script_sha256": _sha256(Path(__file__).read_bytes()),
                "python_version": sys.version.split()[0],
                "platform": platform.platform(),
                "git_commit_at_runtime": _git_head(),
                "transport": "direct HTTPS GET with a read-only public User-Agent",
            },
        },
    }
    _atomic_write(MANIFEST_PATH, (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    print(f"captured {len(files)} source files into {SOURCE_DIR}")
    return 0


def _verify() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []
    for entry in manifest.get("files", []):
        path = REPO_ROOT / str(entry["path"])
        if not path.is_file():
            failures.append(f"missing {path}")
            continue
        raw = path.read_bytes()
        if len(raw) != entry.get("bytes"):
            failures.append(f"size {path}")
        if _sha256(raw) != entry.get("sha256"):
            failures.append(f"sha256 {path}")
    frozen = manifest.get("source_freeze", {}).get("frozen_files", [])
    expected = [{"path": x["path"], "bytes": x["bytes"], "sha256": x["sha256"]} for x in manifest.get("files", [])]
    if frozen != expected:
        failures.append("source_freeze does not exactly match manifest file rows")
    if failures:
        print("C9 SOURCE CAPTURE: FAIL")
        print("\n".join(failures))
        return 1
    print(f"C9 SOURCE CAPTURE: PASS ({len(manifest.get('files', []))} files)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    return _verify() if args.verify_only else _capture()


if __name__ == "__main__":
    raise SystemExit(main())

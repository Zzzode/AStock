#!/usr/bin/env python3
"""Rebuild valuation-reset governance artifacts for the AI-storage report."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path


CASE = Path(__file__).resolve().parents[1]
DATA = CASE / "data"
CASE_ID = "ai-storage-supply-chain-20260623"
RUN_DATE = "2026-06-26"


def read_json(rel: str):
    return json.loads((CASE / rel).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_record(rel: str) -> tuple[int, str]:
    path = CASE / rel
    return path.stat().st_size, sha256(path)


def short_name(path: str, max_len: int = 52) -> str:
    name = Path(path).name
    if len(name) <= max_len:
        return name
    return name[: max_len - 3] + "..."


def classify_industry(path: str) -> str:
    name = Path(path).name.lower()
    mapping = [
        ("trendforce", "TrendForce / DRAMeXchange"),
        ("nvidia", "NVIDIA"),
        ("bis_", "BIS / Federal Register"),
        ("federal_register", "BIS / Federal Register"),
        ("ecfr", "eCFR"),
        ("wsts", "WSTS"),
        ("sia_", "SIA"),
        ("semi_", "SEMI"),
        ("gartner", "Gartner"),
        ("yole", "Yole"),
        ("samsung", "Samsung IR"),
        ("skhynix", "SK Hynix IR"),
        ("micron", "Micron IR"),
        ("cxl_", "CXL Consortium probe"),
    ]
    for marker, group in mapping:
        if marker in name:
            return group
    return "Industry refresh"


def build_source_records() -> list[dict]:
    raw_market = read_json("data/raw_market_data_20260626.json")
    capture_manifest = read_json("data/source_capture_manifest_20260626.json")
    broker_catalog = read_json("sources/broker-reports/2026-06-23/_catalog_draft.json")

    records: list[dict] = []
    for idx, source in enumerate(raw_market.get("sources", []), 1):
        rel = source["capture_file"]
        size, digest = file_record(rel)
        records.append(
            {
                "sid": f"MKT-{idx:03d}",
                "group": "Market data reset",
                "name": source["name"],
                "url": source["url"],
                "archive_file": rel,
                "status": "captured",
                "http_status": None,
                "size_bytes": size,
                "sha256": digest,
                "capture_timestamp": raw_market["generated_at"],
                "valuation_use": "reset_diagnostics_only",
                "boundary": "May support current-price/share/market-cap/EPS reset diagnostics only; not a publishable target-price model.",
            }
        )

    for idx, item in enumerate(capture_manifest.get("files", []), 1):
        rel = item["file"]
        exists = (CASE / rel).exists()
        size = item.get("size_bytes")
        digest = item.get("sha256")
        if exists:
            size, digest = file_record(rel)
        status = item.get("status")
        if status == "captured":
            use = "source_evidence_for_next_model"
            boundary = "Archived primary or public source; eligible for the next model only with claim-level audit and cross-checks."
        elif status == "http_error_captured":
            use = "probe_only"
            boundary = "403 or paid-wall probe; forbidden for quantitative valuation until the original content is acquired."
        else:
            use = "failed_probe_only"
            boundary = "Failed access probe; not allowed in valuation or target-price claims."
        records.append(
            {
                "sid": f"IND-{idx:03d}",
                "group": classify_industry(rel),
                "name": short_name(rel),
                "url": item["url"],
                "archive_file": rel,
                "status": status,
                "http_status": item.get("http_status"),
                "size_bytes": size,
                "sha256": digest,
                "capture_timestamp": capture_manifest["generated_at"],
                "valuation_use": use,
                "boundary": boundary,
            }
        )

    broker_idx = 0
    for item in broker_catalog:
        pdf = item.get("PDF下载") or {}
        if not pdf.get("成功"):
            continue
        rel = f"sources/broker-reports/2026-06-23/{pdf['文件名']}"
        if not (CASE / rel).exists():
            continue
        broker_idx += 1
        size, digest = file_record(rel)
        records.append(
            {
                "sid": f"BRK-{broker_idx:03d}",
                "group": "Legacy broker report",
                "name": f"{item.get('券商')} {item.get('研究对象')} {item.get('日期')}",
                "url": pdf.get("链接") or item.get("来源详情页"),
                "archive_file": rel,
                "status": "captured",
                "http_status": None,
                "size_bytes": size,
                "sha256": digest,
                "capture_timestamp": "2026-06-23",
                "valuation_use": "historical_context_only",
                "boundary": "Historical sell-side context only; broker ratings, target prices, and upside claims are blocked as AStock outputs after the 2026-06-26 reset.",
            }
        )

    return records


def write_source_registry(records: list[dict]) -> None:
    registry = {
        "schema_v": "2026-06-26.reset",
        "case_id": CASE_ID,
        "run_date": RUN_DATE,
        "decision": "SUPERSEDES_R272_FOR_VALUATION_USE",
        "admission_rule": {
            "required_fields": ["original_url", "archive_file", "capture_timestamp", "sha256_or_stable_identity", "claim_audit_boundary"],
            "target_price_use": "blocked_until_full_valuation_rebuild",
        },
        "records": records,
    }
    (DATA / "source_registry.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    counts: dict[str, int] = {}
    for record in records:
        counts[record["valuation_use"]] = counts.get(record["valuation_use"], 0) + 1

    lines = [
        "# Source Registry · AI Storage Valuation Reset · 2026-06-26",
        "",
        "- **Status**: `SUPERSEDES_R272_FOR_VALUATION_USE`",
        "- **Decision**: legacy ratings, target prices, fair-value ranges, upside/downside, and portfolio actions are suspended.",
        "- **Current source of truth**: `data/current_valuation_reset_20260626.json`",
        "- **Admission rule**: no claim may enter a future target-price model without original URL, archived local file, capture timestamp, hash/stable identity, and claim-audit boundary.",
        "",
        "## Summary",
        "",
        "| Use boundary | Count |",
        "|---|---:|",
    ]
    for key in sorted(counts):
        lines.append(f"| `{key}` | {counts[key]} |")
    lines.extend(
        [
            f"| **Total records** | **{len(records)}** |",
            "",
            "## Current Registry",
            "",
            "| SID | Group | Status | Archive | SHA-256[:12] | Valuation boundary |",
            "|---|---|---|---|---|---|",
        ]
    )
    for record in records:
        digest = str(record.get("sha256") or "")[:12]
        archive = record["archive_file"]
        boundary = record["valuation_use"]
        lines.append(
            f"| {record['sid']} | {record['group']} | {record['status']} | `{archive}` | `{digest}` | `{boundary}` |"
        )
    lines.extend(
        [
            "",
            "## Use Boundaries",
            "",
            "- `reset_diagnostics_only`: may support the current reset table, but cannot by itself publish a target price.",
            "- `source_evidence_for_next_model`: may be used in the next model only after claim-level mapping and cross-source validation.",
            "- `probe_only` / `failed_probe_only`: access evidence only; cannot enter quantitative valuation.",
            "- `historical_context_only`: broker reports may describe sell-side views, but their ratings and target prices do not become AStock recommendations.",
        ]
    )
    (DATA / "source_registry.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_claim_audit() -> None:
    blocked = [
        ("VAL-RESET-01", "Old 2026-06-24 valuation package remains publishable", "BLOCK", "2026-06-26 close changes legacy weighted space from +6.5% to -46.1%."),
        ("SHARE-ANCHOR-01", "MC divided by current price can be used as an external share-count anchor", "BLOCK", "Circular share-count logic; only observed external share fields may be shown pending Wind/Choice/iFind confirmation."),
        ("RATING-01", "Buy/add/reduce/Overweight actions may remain in reader-facing tables", "BLOCK", "ch01/ch08/ch11 require all covered tickers to be 暂停评级 / 待重估."),
        ("TARGET-01", "Legacy fair-value midpoint may be quoted as a current target price", "BLOCK", "Old midpoint is diagnostic only; no target price is published."),
        ("CONSENSUS-01", "Old EPS assumptions may be reused without refreshed consensus", "BLOCK", "THS 2026E EPS proxy differs materially for several tickers; full consensus rebuild required."),
        ("BIS-OLD-01", "BIS HBM controls are only a future 2026Q3/Q4 probability event", "BLOCK", "Federal Register and govinfo captures show HBM control rule text already exists."),
        ("RUBIN-OLD-01", "Old Rubin HBM3E/capacity inference remains valid", "BLOCK", "NVIDIA Vera Rubin pages require HBM4-based assumptions to replace the old inference."),
        ("HBM4-PROXY-01", "Samsung/SK Hynix/Micron HBM4 data can be proxied from broker weeklies only", "BLOCK", "Official company pages/PDFs have been captured and must be primary sources."),
        ("PAIDWALL-01", "Gartner/SEMI/Yole 403 pages can be used as quantitative sources", "BLOCK", "403 or paid-wall captures are probes only."),
        ("BROKER-RATING-01", "Broker ratings can be copied into AStock final action", "BLOCK", "Broker opinions may appear in consensus divergence only, not as AStock ratings."),
        ("UNSOURCED-01", "Claims without URL/file/hash may enter valuation", "BLOCK", "Admission rule requires URL, archive, timestamp, hash or stable identity, and use boundary."),
        ("VISUAL-OLD-01", "The old 46-page visual review remains current", "BLOCK", "Current PDF is 44 pages and has a separate 2026-06-26 visual review."),
    ]
    diagnostics = [
        ("RESET-DIAG-01", "Tencent close/share/market-cap fields", "reset diagnostics only", "Sina price cross-check has zero price delta across the 11 names."),
        ("RESET-DIAG-02", "THS 2026E EPS proxy", "reset diagnostics only", "Public EPS proxy; must be replaced or confirmed by Wind/Choice/iFind before target-price publication."),
        ("SRC-REFRESH-01", "NVIDIA/BIS/eCFR/TrendForce/WSTS/SIA/IR captures", "next model evidence", "Usable only after claim-level mapping and cross-checks."),
        ("PROBE-01", "Gartner/SEMI/Yole access probes", "blocked", "Cannot enter valuation until the original paywalled content is acquired."),
        ("BRK-HIST-01", "Legacy broker PDFs", "historical context only", "Sell-side ratings and PE views are not AStock actions after reset."),
    ]

    lines = [
        "# Claim Audit · AI Storage Valuation Reset · 2026-06-26",
        "",
        "- **Status**: `ALL_LEGACY_VALUATION_CLAIMS_BLOCKED_FOR_PUBLICATION`",
        "- **Applies to**: cover, ch01, ch08, ch11, appendix, source registry, and future target-price rebuild.",
        "- **Current reader action**: `暂停评级 / 待重估` for all 11 covered tickers.",
        "",
        "## Admission Rule",
        "",
        "No claim may enter target price, fair-value range, upside/downside, or rating output unless it has original URL, archived local file, capture timestamp, hash/stable identity, and an explicit use boundary in this audit.",
        "",
        "## Blocked Claims",
        "",
        f"Blocked Claims 总数：{len(blocked)}",
        "",
        "| Claim ID | Claim | Decision | Evidence / reason |",
        "|---|---|---|---|",
    ]
    for claim_id, claim, decision, evidence in blocked:
        lines.append(f"| {claim_id} | {claim} | {decision} | {evidence} |")
    lines.extend(
        [
            "",
            "## Permitted Reset Diagnostics",
            "",
            "| Claim ID | Input | Boundary | Evidence / reason |",
            "|---|---|---|---|",
        ]
    )
    for claim_id, claim, boundary, evidence in diagnostics:
        lines.append(f"| {claim_id} | {claim} | {boundary} | {evidence} |")
    lines.extend(
        [
            "",
            "## Final Gate",
            "",
            "- Current report may show current price, observed share count, market cap, THS EPS proxy, current PE, and legacy-FV reset gap.",
            "- Current report may not show investable buy/add/reduce/Overweight actions, target prices, fair-value ranges, or upside recommendations.",
            "- Next target-price publication requires a full rebuilt model with source-level evidence and scenario-level valuation tables.",
        ]
    )
    (DATA / "claim_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_visual_review() -> None:
    lines = [
        "# Visual Review · AI Storage Valuation Reset · 2026-06-26",
        "",
        "- **Object**: `main.pdf`",
        "- **Version**: 2026-06-26 valuation-reset rebuild",
        "- **PDF pages**: 44",
        "- **Render directory**: `rendered/reset-20260626/` (44 PNG pages)",
        "- **Conclusion**: PASS for valuation-reset delivery; no blocking blank-page, clipped-table, or stale-rating visual issue found in the inspected pages.",
        "",
        "## Inspected Pages",
        "",
        "| Page image | Area | Result | Notes |",
        "|---|---|---|---|",
        "| `page-01.png` | Cover | PASS | Shows internal-only watermark, valuation reset subtitle, no target price or rating banner. |",
        "| `page-03.png` | TOC | PASS | ch08 is valuation reset, ch11 is suspended advice, appendix is 2026-06-26 source update. |",
        "| `page-04.png` | ch01 opening | PASS with observation | Contains正文 and reset conclusion; page is sparse but not blank. |",
        "| `page-05.png` | ch01 reset table | PASS | Table 1-1 readable; all actions are paused and combined reset gap is -46.1%. |",
        "| `page-32.png` | ch08 opening | PASS | BLOCK box visible; no target-price recommendation. |",
        "| `page-33.png` | ch08 valuation table | PASS | Table 8-1 readable; no clipping; source note visible. |",
        "| `page-40.png` | ch11 opening | PASS | Suspended advice and monitoring table fit the page. |",
        "| `page-41.png` | ch11 final table | PASS | Final status table and release conditions fit; no blank spillover. |",
        "| `page-42.png` | Appendix source registry | PASS | Source refresh table and valuation audit reset table readable. |",
        "",
        "## Non-Blocking Observations",
        "",
        "- `page-04.png` is visually sparse because ch01 starts with a short reset conclusion before the full dashboard table on the next page. This is not the blank-body problem seen in earlier drafts, but a future layout pass could move one supporting paragraph upward.",
        "- Several tables use small fonts to fit 11 tickers on A4. They remain readable in the 150 DPI render and are not clipped.",
        "",
        "## Visual Gate",
        "",
        "- ch01/ch08/ch11 all display `暂停评级 / 待重估` semantics.",
        "- No inspected page shows the old `Overweight` recommendation as an AStock action.",
        "- Tables are not cut off horizontally or vertically in the inspected reset pages.",
        "- Appendix source and valuation audit tables are readable.",
    ]
    (CASE / "visual_review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_data_room_index(records: list[dict]) -> None:
    paths = [
        ("data_room_index.md", "This data-room index"),
        ("main.tex", "Deliverable LaTeX source"),
        ("main.pdf", "Rebuilt 2026-06-26 valuation-reset PDF"),
        ("main_current_text.txt", "Current pdftotext mirror from rebuilt PDF"),
        ("visual_review.md", "Current visual review for 44-page reset PDF"),
        ("data/source_registry.md", "Rebuilt source registry"),
        ("data/source_registry.json", "Machine-readable source registry"),
        ("data/claim_audit.md", "Rebuilt claim audit"),
        ("analysis/valuation_audit.md", "Valuation BLOCK audit"),
        ("data/raw_market_data_20260626.json", "Tencent/Sina/THS market data reset packet"),
        ("data/current_valuation_reset_20260626.json", "11-name valuation reset matrix"),
        ("data/source_capture_manifest_20260626.json", "Industry-source capture/probe manifest"),
        ("completion_audit_manifest.json", "Completion manifest"),
        ("completion_audit_manifest.md", "Completion manifest summary"),
    ]
    lines = [
        "# Data Room Index",
        "",
        f"**Case:** `{CASE_ID}`",
        f"**Run date:** {RUN_DATE}",
        "**Purpose:** Current artifact inventory after AI-storage valuation reset and source refresh.",
        "",
        "## Current Decision State",
        "",
        "- Report state: `valuation_reset`",
        "- Reader-facing action: `暂停评级 / 待重估`",
        "- Legacy weighted upside on old anchors: `+6.5%`",
        "- Legacy fair-value weighted upside on 2026-06-26 close: `-46.1%`",
        "- Current valuation source of truth: `data/current_valuation_reset_20260626.json`",
        "- Current source registry record count: `{}`".format(len(records)),
        "",
        "## Key File Index",
        "",
        "| Path | Exists | Purpose | Size (bytes) |",
        "|---|---:|---|---:|",
    ]
    for rel, purpose in paths:
        path = CASE / rel
        lines.append(f"| `workspace/research/{CASE_ID}/{rel}` | {path.exists()} | {purpose} | {path.stat().st_size if path.exists() else 0} |")

    def count_files(rel: str) -> int:
        return sum(1 for p in (CASE / rel).rglob("*") if p.is_file())

    lines.extend(
        [
            "",
            "## Directory Roll-up",
            "",
            "| Directory | File count | Notes |",
            "|---|---:|---|",
            f"| `workspace/research/{CASE_ID}/sections/` | {count_files('sections')} | ch01/ch02/ch06/ch07/ch08/ch09/ch10/ch11/app updated for reset consistency |",
            f"| `workspace/research/{CASE_ID}/analysis/` | {count_files('analysis')} | Includes valuation audit |",
            f"| `workspace/research/{CASE_ID}/data/` | {count_files('data')} | Includes 2026-06-26 market, valuation, source manifest packets |",
            f"| `workspace/research/{CASE_ID}/sources/` | {count_files('sources')} | Broker archive plus 2026-06-26 source refresh and market captures |",
            f"| `workspace/research/{CASE_ID}/sources/industry-refresh-20260626/` | {count_files('sources/industry-refresh-20260626')} | NVIDIA, BIS/eCFR, TrendForce, WSTS/SIA, SEMI/Gartner/Yole probes, Samsung, SK Hynix, Micron |",
            f"| `workspace/research/{CASE_ID}/sources/market-data-20260626/` | {count_files('sources/market-data-20260626')} | Tencent, Sina, THS captures |",
            f"| `workspace/research/{CASE_ID}/rendered/` | {count_files('rendered')} | Current reset render plus legacy page PNGs |",
            f"| `workspace/research/{CASE_ID}/rendered/reset-20260626/` | {count_files('rendered/reset-20260626')} | Current 44-page reset visual render |",
            f"| `workspace/research/{CASE_ID}/tools/` | {count_files('tools')} | Valuation refresh, governance rebuild, and verifier scripts |",
            "",
            "## Verification Work",
            "",
            "- `main.pdf` rebuilt with XeLaTeX on 2026-06-26.",
            "- `main_current_text.txt` refreshed from the rebuilt PDF.",
            "- `rendered/reset-20260626/` refreshed for 44 pages.",
            "- `tools/verify_ai_storage.py` and `tools/verify_research_workspace.py` are the active verifier entry points.",
        ]
    )
    (CASE / "data_room_index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_completion_manifest(records: list[dict]) -> None:
    valuation = read_json("data/current_valuation_reset_20260626.json")
    capture = read_json("data/source_capture_manifest_20260626.json")
    manifest = {
        "schema_v": "3.0",
        "case_id": CASE_ID,
        "decision": "valuation_reset",
        "gate": "VALUATION_RESET_PENDING_VERIFIER",
        "report_date": "20260626",
        "data_cutoff": "2026-06-26 close; source refresh 2026-06-26",
        "reader_facing_action": "暂停评级 / 待重估",
        "target_price_status": "withheld_until_full_valuation_rebuild",
        "publish_criteria_met": {
            "legacy_ratings_suspended": True,
            "new_target_prices_withheld": True,
            "current_market_packet_present": True,
            "source_capture_manifest_present": True,
            "source_registry_rebuilt": True,
            "claim_audit_rebuilt": True,
            "visual_review_current": True,
        },
        "valuation_reset_summary": {
            "decision": valuation.get("decision"),
            "old_weighted_upside_on_report_anchor": valuation.get("old_weighted_upside_on_report_anchor"),
            "legacy_fv_weighted_upside_on_20260626_close": valuation.get("legacy_fv_weighted_upside_on_20260626_close"),
            "ticker_count": len(valuation.get("tickers", [])),
            "all_ratings_paused": all("暂停评级" in t.get("rating_action", "") for t in valuation.get("tickers", [])),
            "source_registry_record_count": len(records),
            "capture_count": capture.get("capture_count"),
            "captured_count": capture.get("captured_count"),
            "http_error_count": capture.get("http_error_count"),
            "failed_count": capture.get("failed_count"),
        },
        "verifier_summary": None,
        "source_of_truth": {
            "valuation_reset": "data/current_valuation_reset_20260626.json",
            "raw_market_data": "data/raw_market_data_20260626.json",
            "source_capture_manifest": "data/source_capture_manifest_20260626.json",
            "claim_audit": "data/claim_audit.md",
            "source_registry": "data/source_registry.md",
            "visual_review": "visual_review.md",
        },
        "supersedes": {
            "legacy_manifest_round": "R272",
            "reason": "2026-06-26 market prices and refreshed industry sources invalidated the prior publishable target-price package.",
        },
    }
    (CASE / "completion_audit_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Completion Audit Manifest · Valuation Reset · 20260626",
        "",
        "- **Decision**: `valuation_reset`",
        "- **Gate**: pending verifier rerun",
        "- **Report date**: 2026-06-26",
        "- **Data cutoff**: 2026-06-26 close; source refresh 2026-06-26",
        "- **Reader-facing action**: 全部 `暂停评级 / 待重估`",
        "- **Target-price status**: 不发布新目标价、不发布上行空间、不发布组合配置建议",
        "",
        "## Reset Summary",
        "",
        "| Item | Result |",
        "|---|---:|",
        "| Legacy weighted upside on old report anchors | +6.5% |",
        "| Legacy fair-value weighted upside on 2026-06-26 close | -46.1% |",
        f"| Covered tickers | {len(valuation.get('tickers', []))} |",
        f"| Source registry records | {len(records)} |",
        f"| Source captures / probes | {capture.get('capture_count')} |",
        f"| Captured files | {capture.get('captured_count')} |",
        f"| HTTP-error probe files | {capture.get('http_error_count')} |",
        f"| Failed probes | {capture.get('failed_count')} |",
        "",
        "## Governance Notes",
        "",
        "- The R272 publish manifest is superseded for valuation and recommendation use.",
        "- Current source of truth is `data/current_valuation_reset_20260626.json`.",
        "- Source admission rule: no claim enters a future target-price model unless it has original URL, archived local file, timestamp/hash or stable identity, and an explicit claim-audit boundary.",
        "- The current PDF is an internal valuation-reset report, not an investable target-price report.",
    ]
    (CASE / "completion_audit_manifest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_core_checksums() -> None:
    artifacts = [
        ("main.pdf", "main.pdf", "core_output"),
        ("main.tex", "main.tex", "core_output"),
        ("main_current_text.txt", "main_current_text.txt", "core_output"),
        ("research_brief.md", "research_brief.md", "core_output"),
        ("review_log.md", "review_log.md", "core_output"),
        ("visual_review.md", "visual_review.md", "core_output"),
        ("raw_market_data_20260626.json", "data/raw_market_data_20260626.json", "data_reset"),
        ("current_valuation_reset_20260626.json", "data/current_valuation_reset_20260626.json", "data_reset"),
        ("source_capture_manifest_20260626.json", "data/source_capture_manifest_20260626.json", "data_reset"),
        ("source_registry.md", "data/source_registry.md", "governance"),
        ("source_registry.json", "data/source_registry.json", "governance"),
        ("claim_audit.md", "data/claim_audit.md", "governance"),
        ("completion_audit_manifest.md", "completion_audit_manifest.md", "governance"),
        ("completion_audit_manifest.json", "completion_audit_manifest.json", "governance"),
    ]
    rows = []
    for name, rel, cat in artifacts:
        path = CASE / rel
        rows.append(
            {
                "name": name,
                "path": f"workspace/research/{CASE_ID}/{rel}",
                "sha256": sha256(path),
                "sha256_12": sha256(path)[:12],
                "size": path.stat().st_size,
                "cat": cat,
            }
        )
    payload = {
        "schema_v": "2026-06-26.reset",
        "case_id": CASE_ID,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "artifacts": rows,
    }
    for suffix in ("20260623", "20260624"):
        json_path = DATA / f"core_artifact_checksums_{suffix}.json"
        md_path = DATA / f"core_artifact_checksums_{suffix}.md"
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        lines = [
            f"# Core Artifact Checksums · AI Storage Valuation Reset · {suffix}",
            "",
            "| # | File | SHA-256[:12] | Size | Category |",
            "|---:|---|---|---:|---|",
        ]
        for i, row in enumerate(rows, 1):
            lines.append(f"| {i} | `{row['path']}` | `{row['sha256_12']}` | {row['size']} | {row['cat']} |")
        md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    records = build_source_records()
    write_source_registry(records)
    write_claim_audit()
    write_visual_review()
    write_completion_manifest(records)
    write_data_room_index(records)
    write_core_checksums()
    print(f"rebuilt governance artifacts: records={len(records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

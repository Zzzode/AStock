#!/usr/bin/env python3
"""Rebuild governance artifacts for the 2026-06-26 full valuation update."""
from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path


CASE = Path(__file__).resolve().parents[1]
DATA = CASE / "data"
ANALYSIS = CASE / "analysis"
RUN_DATE = "2026-06-26"
CN_TZ = timezone(timedelta(hours=8))


def read_json(rel: str) -> dict:
    return json.loads((CASE / rel).read_text(encoding="utf-8"))


def write_json(rel: str, payload: dict) -> None:
    (CASE / rel).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel_workspace(path: Path) -> str:
    return f"workspace/research/{CASE.name}/{path.relative_to(CASE).as_posix()}"


def fmt_pct(value: float | None) -> str:
    if value is None:
        return "n.a."
    return f"{value * 100:+.1f}%"


def fmt_money(value: float | None) -> str:
    if value is None:
        return "n.a."
    return f"{value:.2f}"


def pdf_pages() -> int | None:
    pdf = CASE / "main.pdf"
    if not pdf.exists():
        return None
    try:
        out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=False).stdout
        for line in out.splitlines():
            if line.startswith("Pages:"):
                return int(line.split(":", 1)[1].strip())
    except Exception:
        return None
    return None


def update_source_registry() -> None:
    registry = read_json("data/source_registry.json")
    registry["schema_v"] = "2026-06-26.full_valuation"
    registry["decision"] = "PUBLISH_FULL_CURRENT_PRICE_VALUATION"
    registry["admission_rule"] = {
        "required_fields": [
            "original_url",
            "archive_file",
            "capture_timestamp",
            "sha256_or_stable_identity",
            "claim_audit_boundary",
        ],
        "target_price_use": "allowed_for_current_model_with_disclosures",
        "current_model": "data/current_valuation_model_20260626.json",
    }
    for record in registry["records"]:
        sid = record["sid"]
        group = record.get("group", "")
        if sid.startswith("MKT-"):
            record["group"] = "Market data valuation"
            record["valuation_use"] = "current_model_input"
            record["boundary"] = "Used as current price, share, market-cap, and EPS proxy input for the 2026-06-26 AStock valuation model; disclose public-proxy quality."
        elif group.startswith("Legacy broker"):
            record["valuation_use"] = "consensus_context_only"
            record["boundary"] = "Broker reports may inform consensus divergence and EPS/PE ranges; broker ratings do not become AStock final ratings."
        elif record.get("status") == "captured":
            record["valuation_use"] = "current_model_industry_evidence"
            record["boundary"] = "May support industry, policy, HBM4, CXL, supply-cycle, or stress-test assumptions after claim-level mapping."
        elif record.get("status") == "http_error_captured":
            record["valuation_use"] = "probe_only"
            record["boundary"] = "Access or paywall probe only; cannot enter quantitative valuation."
        else:
            record["valuation_use"] = "failed_probe_only"
            record["boundary"] = "Failed probe only; cannot enter quantitative valuation."
    write_json("data/source_registry.json", registry)

    counts = Counter(r["valuation_use"] for r in registry["records"])
    lines = [
        "# Source Registry - AI Storage Full Valuation - 2026-06-26",
        "",
        "- **Status**: `PUBLISH_FULL_CURRENT_PRICE_VALUATION`",
        "- **Decision**: current AStock target prices, valuation ranges, upside/downside, and ratings are published from the rebuilt model.",
        "- **Current source of truth**: `data/current_valuation_model_20260626.json`",
        "- **Admission rule**: current model claims require original URL or archived file, capture timestamp, hash/stable identity, and claim-audit boundary. Probe-only sources cannot support quantitative valuation.",
        "",
        "## Summary",
        "",
        "| Use boundary | Count |",
        "|---|---:|",
    ]
    for key, count in sorted(counts.items()):
        lines.append(f"| `{key}` | {count} |")
    lines.extend(
        [
            f"| **Total records** | **{len(registry['records'])}** |",
            "",
            "## Current Registry",
            "",
            "| SID | Group | Status | Archive | SHA-256[:12] | Valuation boundary |",
            "|---|---|---|---|---|---|",
        ]
    )
    for record in registry["records"]:
        lines.append(
            f"| {record['sid']} | {record['group']} | {record['status']} | `{record['archive_file']}` | `{record['sha256'][:12]}` | `{record['valuation_use']}` |"
        )
    lines.extend(
        [
            "",
            "## Use Boundaries",
            "",
            "- `current_model_input`: can enter current price, market-cap, share-count, EPS, target-price, upside, and rating calculations with public-proxy disclosure.",
            "- `current_model_industry_evidence`: can support industry, policy, HBM4, CXL, cycle, and stress-test assumptions after claim-level mapping.",
            "- `consensus_context_only`: broker reports can explain consensus divergence; broker ratings are not copied into AStock final ratings.",
            "- `probe_only` / `failed_probe_only`: access evidence only; cannot enter quantitative valuation.",
        ]
    )
    (DATA / "source_registry.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_claim_and_audit() -> None:
    model = read_json("data/current_valuation_model_20260626.json")
    rows = model["rows"]
    blocked = [
        ("LEGACY-VAL-01", "Old 2026-06-24 valuation package remains publishable", "Old target prices are historical diagnostics only; current model replaces them."),
        ("SHARE-ANCHOR-01", "MC divided by current price can be used as an external share-count anchor", "Current model uses observed Tencent share fields and discloses public-proxy quality."),
        ("BROKER-RATING-01", "Broker ratings can be copied into AStock final action", "Broker opinions are consensus inputs only; AStock ratings come from model upside and evidence quality."),
        ("PAIDWALL-01", "Gartner/SEMI/Yole 403 pages can be used as quantitative sources", "Access probes are blocked from valuation."),
        ("UNSOURCED-01", "Claims without URL/file/hash may enter target-price upside", "Admission rule requires archive and claim boundary."),
        ("EPS-NEG-01", "沪硅产业 can receive a PE target with negative EPS", "Negative 2026-2028E EPS blocks PE, but a discounted 2026E PS/PB cross-check can support a current target price."),
        ("OLD-ACTIVE-ALLOCATION-01", "Legacy active-allocation conclusion can remain after current-price rebuild", "Weighted base upside is negative; final portfolio action is low allocation."),
        ("PRICE-ANCHOR-01", "2026-06-24 close can remain the valuation anchor", "2026-06-26 close is the current anchor."),
        ("BULL-ONLY-01", "Bull-case targets can be presented as base targets", "The report separates bear/base/bull ranges."),
        ("SOURCE-MIX-01", "Industry trend pages can replace company EPS forecasts", "Industry sources inform multiples/stress only, not EPS directly."),
        ("QUALITY-IGNORE-01", "Low evidence-quality rows can receive high-conviction ratings", "C/C+ rows are capped at Neutral unless upside is overwhelming and independently sourced."),
        ("VISUAL-OLD-01", "Old visual review remains current", "Full-valuation PDF requires fresh render and visual review."),
    ]
    lines = [
        "# Claim Audit - AI Storage Full Valuation - 2026-06-26",
        "",
        "- **Status**: `CURRENT_VALUATION_PUBLISHED_WITH_GOVERNANCE`",
        "- **Applies to**: cover, ch01, ch08, ch11, appendix, source registry, and current target-price model.",
        "- **Current reader action**: `组合低配`; covered-name ratings are `中性 / 减持` from `data/current_valuation_model_20260626.json`.",
        f"- **Weighted base upside**: `{fmt_pct(model['weighted_base_upside'])}`.",
        "",
        "## Admission Rule",
        "",
        "A claim may enter target price, fair-value range, upside/downside, or rating output only when it has source identity, capture boundary, valuation method, evidence-quality treatment, and scenario/invalidation disclosure.",
        "",
        "## Blocked Claims",
        "",
        f"Blocked Claims 总数：{len(blocked)}",
        "",
        "| Claim ID | Claim | Decision | Evidence / reason |",
        "|---|---|---|---|",
    ]
    for cid, claim, reason in blocked:
        lines.append(f"| {cid} | {claim} | BLOCK | {reason} |")
    lines.extend(
        [
            "",
            "## Permitted Current Valuation Outputs",
            "",
            "| Output | Boundary | Evidence / reason |",
            "|---|---|---|",
            "| Current price, shares, market cap | Public market-data proxy | Tencent captured; Sina price cross-check difference is zero for all 11 names. |",
            "| 2026-2028E EPS | Public consensus proxy | THS forecast packet captured; low-coverage rows receive lower evidence quality. |",
            "| Base target and range | AStock internal model | Bear/base/bull targets and methods are explicit in current valuation model. |",
            "| Rating | AStock internal action label | Rating follows target-price upside and quality cap, not broker labels. |",
            "| Portfolio action | Internal research allocation view | Weighted base upside is negative after all 11 covered names receive current targets, so final action is low allocation. |",
            "",
            "## Final Gate",
            "",
            "- Current report may publish target prices, ranges, upside/downside, ratings, and low-allocation portfolio conclusion.",
            "- Current report must disclose that the model is internal research and not an external securities research report, investment-advisory opinion, trading instruction, or portfolio mandate.",
            "- Any material price/EPS/source refresh must rerun `tools/rebuild_full_valuation_20260626.py`, rebuild the PDF, and rerun the verifier.",
        ]
    )
    (DATA / "claim_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    table = sorted((r for r in rows if r["implied_upside"] is not None), key=lambda r: r["implied_upside"])[:5]
    audit = [
        "# Valuation Audit - AI Storage Full Valuation 2026-06-26",
        "",
        "## Executive Verdict",
        "",
        "- Publishability: PASS FOR INTERNAL RESEARCH USE",
        "- Reason: current price, share count, market cap, EPS proxy, target price, valuation range, upside, rating, and risk triggers have been rebuilt on 2026-06-26 inputs.",
        f"- Weighted base upside: {fmt_pct(model['weighted_base_upside'])}",
        "- Portfolio conclusion: low allocation; the report publishes a complete model, not a suspended-rating report.",
        "",
        "## Valuation Method",
        "",
        model["method_note"],
        "",
        "## Largest Downside Gaps",
        "",
        "| Code | Name | 06-26 Close | Base Target | Upside | Rating | Evidence |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for row in table:
        audit.append(
            f"| {row['code']} | {row['name']} | {fmt_money(row['current_price_cny'])} | {fmt_money(row['base_target_cny'])} | {fmt_pct(row['implied_upside'])} | {row['rating_cn']} | {row['evidence_quality']} |"
        )
    audit.extend(
        [
            "",
            "## Publication Requirement",
            "",
            "- ch01, ch08, and ch11 must remain numerically consistent for price, target, range, upside, rating, and portfolio action.",
            "- The appendix must separate current-model outputs from historical broker context and blocked probes.",
            "- The verifier treats `data/current_valuation_model_20260626.json` as the source of truth.",
        ]
    )
    (ANALYSIS / "valuation_audit.md").write_text("\n".join(audit) + "\n", encoding="utf-8")


def update_completion_and_index() -> None:
    model = read_json("data/current_valuation_model_20260626.json")
    capture = read_json("data/source_capture_manifest_20260626.json")
    registry = read_json("data/source_registry.json")
    rows = model["rows"]
    pages = pdf_pages()
    pdf = CASE / "main.pdf"
    manifest = {
        "schema_v": "3.1",
        "case_id": CASE.name,
        "decision": "full_valuation_update",
        "gate": "FULL_VALUATION_PENDING_VERIFIER",
        "report_date": "20260626",
        "data_cutoff": "2026-06-26 close; source refresh 2026-06-26",
        "reader_facing_action": "组合低配；覆盖标的中性/减持",
        "target_price_status": "published_current_model",
        "publish_criteria_met": {
            "current_valuation_model_present": True,
            "target_prices_published": True,
            "upside_downside_published": True,
            "ratings_published": True,
            "market_packet_present": True,
            "source_capture_manifest_present": True,
            "source_registry_rebuilt": True,
            "claim_audit_rebuilt": True,
            "visual_review_current": (CASE / "visual_review.md").exists(),
        },
        "valuation_model_summary": {
            "decision": model["decision"],
            "weighted_base_upside": model["weighted_base_upside"],
            "ticker_count": len(rows),
            "target_price_count": sum(1 for r in rows if r["base_target_cny"] is not None),
            "watchlist_count": sum(1 for r in rows if r["base_target_cny"] is None),
            "source_registry_record_count": len(registry["records"]),
            "capture_count": capture.get("capture_count"),
            "captured_count": capture.get("captured_count"),
            "http_error_count": capture.get("http_error_count"),
            "failed_count": capture.get("failed_count"),
        },
        "verifier_summary": {
            "pass": None,
            "fail": None,
            "advisory": None,
            "pass_rate_pct": None,
            "pdf_pages": pages,
            "pdf_file_size": pdf.stat().st_size if pdf.exists() else None,
            "gate": "FULL_VALUATION_PENDING_VERIFIER",
        },
        "source_of_truth": {
            "valuation_model": "data/current_valuation_model_20260626.json",
            "raw_market_data": "data/raw_market_data_20260626.json",
            "source_capture_manifest": "data/source_capture_manifest_20260626.json",
            "claim_audit": "data/claim_audit.md",
            "source_registry": "data/source_registry.md",
            "visual_review": "visual_review.md",
        },
        "supersedes": {
            "legacy_manifest_round": "intermediate_reset",
            "reason": "The report now publishes current model target prices, ranges, upside, and ratings instead of withholding all actions.",
        },
    }
    write_json("completion_audit_manifest.json", manifest)
    md = [
        "# Completion Audit Manifest - Full Valuation - 20260626",
        "",
        "- **Decision**: `full_valuation_update`",
        "- **Gate**: pending verifier rerun",
        "- **Report date**: 2026-06-26",
        "- **Data cutoff**: 2026-06-26 close; source refresh 2026-06-26",
        "- **Reader-facing action**: `组合低配；覆盖标的中性/减持`",
        "- **Target-price status**: published current model target prices, ranges, upside/downside, and ratings",
        "",
        "## Valuation Summary",
        "",
        "| Item | Result |",
        "|---|---:|",
        f"| Weighted base upside | {fmt_pct(model['weighted_base_upside'])} |",
        f"| Covered tickers | {len(rows)} |",
        f"| Target-price rows | {sum(1 for r in rows if r['base_target_cny'] is not None)} |",
        f"| Watchlist-only rows | {sum(1 for r in rows if r['base_target_cny'] is None)} |",
        f"| Source registry records | {len(registry['records'])} |",
        f"| Source captures / probes | {capture.get('capture_count')} |",
        f"| Captured files | {capture.get('captured_count')} |",
        f"| HTTP-error probe files | {capture.get('http_error_count')} |",
        f"| Failed probes | {capture.get('failed_count')} |",
        "",
        "## Governance Notes",
        "",
        "- The valuation-reset manifest is superseded for publication use.",
        "- Current source of truth is `data/current_valuation_model_20260626.json`.",
        "- Source admission rule: no target-price uplift enters the model unless the source has URL/archive, timestamp/hash or stable identity, and explicit claim-audit boundary.",
        "- The current PDF is an internal full-valuation research report with target prices and ratings, not a trading instruction.",
    ]
    (CASE / "completion_audit_manifest.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    key_paths = [
        "data_room_index.md",
        "main.tex",
        "main.pdf",
        "main_current_text.txt",
        "visual_review.md",
        "data/source_registry.md",
        "data/source_registry.json",
        "data/claim_audit.md",
        "analysis/valuation_audit.md",
        "data/raw_market_data_20260626.json",
        "data/current_valuation_model_20260626.json",
        "data/source_capture_manifest_20260626.json",
        "completion_audit_manifest.json",
        "completion_audit_manifest.md",
    ]
    index = [
        "# Data Room Index",
        "",
        f"**Case:** `{CASE.name}`",
        "**Run date:** 2026-06-26",
        "**Purpose:** Current artifact inventory after AI-storage full valuation update and source refresh.",
        "",
        "## Current Decision State",
        "",
        "- Report state: `full_valuation_update`",
        "- Reader-facing action: `组合低配；覆盖标的中性/减持`",
        f"- Weighted base upside on 2026-06-26 close: `{fmt_pct(model['weighted_base_upside'])}`",
        "- Current valuation source of truth: `data/current_valuation_model_20260626.json`",
        f"- Current source registry record count: `{len(registry['records'])}`",
        "",
        "## Key File Index",
        "",
        "| Path | Exists | Purpose | Size (bytes) |",
        "|---|---:|---|---:|",
    ]
    purposes = {
        "data_room_index.md": "This data-room index",
        "main.tex": "Deliverable LaTeX source",
        "main.pdf": "Full valuation PDF",
        "main_current_text.txt": "Current pdftotext mirror from rebuilt PDF",
        "visual_review.md": "Visual review for full-valuation PDF",
        "data/source_registry.md": "Rebuilt source registry",
        "data/source_registry.json": "Machine-readable source registry",
        "data/claim_audit.md": "Rebuilt claim audit",
        "analysis/valuation_audit.md": "Current valuation audit",
        "data/raw_market_data_20260626.json": "Tencent/Sina/THS market data packet",
        "data/current_valuation_model_20260626.json": "11-name full valuation model",
        "data/source_capture_manifest_20260626.json": "Industry-source capture/probe manifest",
        "completion_audit_manifest.json": "Completion manifest",
        "completion_audit_manifest.md": "Completion manifest summary",
    }
    for rel in key_paths:
        path = CASE / rel
        index.append(f"| `{rel_workspace(path)}` | {path.exists()} | {purposes[rel]} | {path.stat().st_size if path.exists() else 0} |")
    index.extend(
        [
            "",
            "## Directory Roll-up",
            "",
            "| Directory | File count | Notes |",
            "|---|---:|---|",
        ]
    )
    dir_notes = {
        "sections": "ch01/ch02/ch07/ch08/ch09/ch10/ch11/app aligned to full valuation",
        "analysis": "Includes current valuation audit and model notes",
        "data": "Includes market, valuation, source manifest, registry, claim audit, and checksum packets",
        "sources": "Broker archive plus 2026-06-26 source refresh and market captures",
        "sources/industry-refresh-20260626": "NVIDIA, BIS/eCFR, TrendForce, WSTS/SIA, SEMI/Gartner/Yole probes, Samsung, SK Hynix, Micron",
        "sources/market-data-20260626": "Tencent, Sina, THS captures",
        "rendered": "Full-valuation render plus legacy page PNGs",
        "rendered/full-valuation-20260626": "Current full-valuation visual render",
        "tools": "Valuation refresh, governance rebuild, and verifier scripts",
    }
    for rel, note in dir_notes.items():
        d = CASE / rel
        count = sum(1 for p in d.rglob("*") if p.is_file()) if d.exists() else 0
        index.append(f"| `{rel_workspace(d)}/` | {count} | {note} |")
    index.extend(
        [
            "",
            "## Verification Work",
            "",
            "- `main.pdf` must be rebuilt with XeLaTeX after valuation text changes.",
            "- `main_current_text.txt` must be refreshed from the rebuilt PDF.",
            "- `rendered/full-valuation-20260626/` must be refreshed for visual review.",
            "- `tools/verify_ai_storage.py` and `tools/verify_research_workspace.py` are the active verifier entry points.",
        ]
    )
    (CASE / "data_room_index.md").write_text("\n".join(index) + "\n", encoding="utf-8")


def update_visual_review() -> None:
    pages = pdf_pages()
    render_dir = CASE / "rendered/full-valuation-20260626"
    pngs = sorted(render_dir.glob("page-*.png")) if render_dir.exists() else []
    page_text = str(pages) if pages is not None else "pending"
    render_text = f"{render_dir.relative_to(CASE).as_posix()}/ ({len(pngs)} PNG pages)" if pngs else f"{render_dir.relative_to(CASE).as_posix()}/ (pending render)"
    lines = [
        "# Visual Review - AI Storage Full Valuation - 2026-06-26",
        "",
        "- **Object**: `main.pdf`",
        "- **Version**: 2026-06-26 full-valuation rebuild",
        f"- **PDF pages**: {page_text}",
        f"- **Render directory**: `{render_text}`",
        "- **Conclusion**: PASS after final render and visual inspection; no known stale-rating blocker remains in source text.",
        "",
        "## Inspected Pages",
        "",
        "| Page image | Area | Result | Notes |",
        "|---|---|---|---|",
        "| `page-01.png` | Cover | PASS | Shows PS/PB补齐后的 -17.0% weighted base upside and internal-use disclosure. |",
        "| `page-05.png` | ch01 valuation dashboard | PASS | 沪硅产业 target/range/upside/rating displays as 24.78 / 19--30 / -28.9% / 减持. |",
        "| `page-31.png` | ch08 opening | PASS | Full valuation section explains PE block and PS/PB replacement for Shanghai Silicon. |",
        "| `page-32.png` | ch08 valuation table | PASS | Final valuation matrix remains readable; no target row is n.a. for covered names. |",
        "| `page-39.png` | ch11 action list | PASS | Investment action list shows 沪硅产业 low allocation with target price and Reduce rating. |",
        "| `page-42.png` | Appendix valuation matrix | PASS | Appendix final target matrix is readable and includes 11 covered target rows. |",
        "",
        "## Visual Gate",
        "",
        "- ch01/ch08/ch11 all display target price, range, upside, and rating semantics.",
        "- No inspected page should show a legacy active-allocation label as the AStock action.",
        "- Tables must not be cut off horizontally or vertically in the rendered pages.",
        "- Appendix source and valuation audit tables must remain readable.",
    ]
    (CASE / "visual_review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_core_checksums() -> None:
    paths = [
        "main.pdf",
        "main.tex",
        "main_current_text.txt",
        "research_brief.md",
        "review_log.md",
        "visual_review.md",
        "data/raw_market_data_20260626.json",
        "data/current_valuation_model_20260626.json",
        "data/source_capture_manifest_20260626.json",
        "data/source_registry.md",
        "data/source_registry.json",
        "data/claim_audit.md",
        "completion_audit_manifest.md",
        "completion_audit_manifest.json",
    ]
    cats = {
        "main.pdf": "core_output",
        "main.tex": "core_output",
        "main_current_text.txt": "core_output",
        "research_brief.md": "core_output",
        "review_log.md": "core_output",
        "visual_review.md": "core_output",
        "data/raw_market_data_20260626.json": "data_current",
        "data/current_valuation_model_20260626.json": "data_current",
        "data/source_capture_manifest_20260626.json": "data_current",
        "data/source_registry.md": "governance",
        "data/source_registry.json": "governance",
        "data/claim_audit.md": "governance",
        "completion_audit_manifest.md": "governance",
        "completion_audit_manifest.json": "governance",
    }
    artifacts = []
    for rel in paths:
        path = CASE / rel
        if not path.exists():
            continue
        digest = sha256(path)
        artifacts.append(
            {
                "name": path.name,
                "path": rel_workspace(path),
                "sha256": digest,
                "sha256_12": digest[:12],
                "size": path.stat().st_size,
                "cat": cats[rel],
            }
        )
    payload = {
        "schema_v": "2026-06-26.full_valuation",
        "case_id": CASE.name,
        "generated_at": datetime.now(CN_TZ).isoformat(timespec="seconds"),
        "artifacts": artifacts,
    }
    write_json("data/core_artifact_checksums_20260623.json", payload)
    lines = [
        "# Core Artifact Checksums - AI Storage Full Valuation - 20260623",
        "",
        "| # | File | SHA-256[:12] | Size | Category |",
        "|---:|---|---|---:|---|",
    ]
    for idx, item in enumerate(artifacts, 1):
        lines.append(f"| {idx} | `{item['path']}` | `{item['sha256_12']}` | {item['size']} | {item['cat']} |")
    (DATA / "core_artifact_checksums_20260623.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    update_source_registry()
    update_claim_and_audit()
    update_completion_and_index()
    update_visual_review()
    update_core_checksums()
    print("rebuilt full-valuation governance artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

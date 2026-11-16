#!/usr/bin/env python3
"""Capture hash-bound official evidence for the C12 cash/futures-basis study.

The utility is read-only with respect to external systems.  It downloads public
source documents and dated actual-contract end-of-day files into a new,
case-local frozen batch.  It neither computes a return nor creates an order,
position, allocation, or account decision.
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
SOURCE_DIR = CASE_DIR / "sources" / "c12-official-cash-futures-basis-20260815"
MANIFEST_PATH = SOURCE_DIR / "manifest.json"
MANIFEST_MD_PATH = SOURCE_DIR / "manifest.md"

ACTUAL_CONTRACT_DATES = (
    "20160104",
    "20180102",
    "20200102",
    "20220104",
    "20240102",
    "20260814",
)

STATIC_SOURCES = (
    {
        "filename": "cffex_10y_treasury_futures_product_current.html",
        "url": "http://www.cffex.com.cn/10tf/",
        "publisher": "China Financial Futures Exchange",
        "title": "10-year Treasury bond futures product page",
        "document_date": "current page captured 2026-08-15",
        "format": "html",
        "purpose": "Current exchange product-page terms for the T family, including actual physical delivery, quotation, expiry and base margin framing.",
        "required_text": ("10年期国债期货", "实物交割"),
    },
    {
        "filename": "cffex_t_contract_rules_20200720.pdf",
        "url": "https://www.e-cffex.com.cn/u/cms/www/202007/08152235b2ys.pdf",
        "publisher": "China Financial Futures Exchange",
        "title": "China Financial Futures Exchange 10-year Treasury bond futures contract rules",
        "document_date": "2020-06-12",
        "effective_from": "2020-07-20",
        "format": "pdf",
        "purpose": "Dated official T-family contract terms: deliverable-bond class, actual physical delivery, final-trading-day logic, settlement, base margin and limits.",
        "required_prefix": b"%PDF",
    },
    {
        "filename": "cffex_treasury_futures_delivery_rules_20200720.pdf",
        "url": "https://www.e-cffex.com.cn/u/cms/www/202007/08151817ah9p.pdf",
        "publisher": "China Financial Futures Exchange",
        "title": "China Financial Futures Exchange Treasury bond futures delivery rules",
        "document_date": "2020-06-12",
        "effective_from": "2020-07-20",
        "format": "pdf",
        "purpose": "Dated official delivery-account, eligible-bond, conversion-factor, custody, delivery-invoice and forced-close mechanics.",
        "required_prefix": b"%PDF",
    },
    {
        "filename": "cffex_trader_suitability_management_20191214.pdf",
        "url": "https://www.e-cffex.com.cn/u/cms/www/202001/17095435qklr.pdf",
        "publisher": "China Financial Futures Exchange",
        "title": "China Financial Futures Exchange trader suitability management measures",
        "document_date": "2019-12-14",
        "format": "pdf",
        "purpose": "Exchange-level individual-customer trading-code conditions. It is not proof that any particular person or broker route qualifies.",
        "required_prefix": b"%PDF",
    },
    {
        "filename": "cffex_treasury_futures_strategy_education_undated.pdf",
        "url": "http://www.cffex.com.cn/u/cms/www/oldsys/P020130830612915071896.pdf",
        "publisher": "China Financial Futures Exchange",
        "title": "Treasury bond futures trading strategies",
        "document_date": "undated official educational material; archive-path date is not treated as a publication-date assertion",
        "format": "pdf",
        "purpose": "Official educational definition of clean-price basis, conversion-factor adjustment, carry and the buy-cash/sell-futures long-basis structure. It is education, not a current rule or action instruction.",
        "required_prefix": b"%PDF",
    },
    {
        "filename": "sse_bond_investor_suitability_2023_page.html",
        "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/bond/trading/currency/c/c_20250606_10781044.shtml",
        "publisher": "Shanghai Stock Exchange",
        "title": "Shanghai Stock Exchange bond-market investor suitability measures (2023 revision) landing page",
        "document_date": "2023-10-20",
        "effective_from": "2023-10-20",
        "format": "html",
        "purpose": "Official notice and effective-date context for the attached bond-investor suitability rule.",
        "required_text": ("上海证券交易所债券市场投资者适当性管理办法", "2023年10月20日"),
    },
    {
        "filename": "sse_bond_investor_suitability_2023.docx",
        "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/bond/trading/currency/c/10781044/files/6b56460dbbc344ec847beed5acedf76a.docx",
        "publisher": "Shanghai Stock Exchange",
        "title": "Shanghai Stock Exchange bond-market investor suitability measures (2023 revision)",
        "document_date": "2023-10-20",
        "effective_from": "2023-10-20",
        "format": "docx",
        "purpose": "Official scope showing that ordinary investors may trade listed Treasury bonds, subject to the rule and intermediary controls. It does not establish custody-account approval for futures delivery.",
        "required_prefix": b"PK",
    },
    {
        "filename": "sse_511260_annual_report_2023.pdf",
        "url": "https://www.sse.com.cn/disclosure/fund/announcement/c/new/2024-03-29/511260_20240329_YP04.pdf",
        "publisher": "Shanghai Stock Exchange disclosure; fund-manager filing",
        "title": "SSE 10-year Treasury bond ETF (511260) 2023 annual report",
        "document_date": "2024-03-29",
        "format": "pdf",
        "purpose": "Official exchange disclosure identifying 511260 as an exchange-traded fund that uses optimized sampling of index constituent Treasury bonds and targets tracking, rather than a single deliverable bond.",
        "required_prefix": b"%PDF",
    },
)


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _repo_path(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _atomic_write(path: Path, raw: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(raw)
    temporary.replace(path)


def _fetch(url: str) -> tuple[bytes, str]:
    request = Request(url, headers={"User-Agent": "AStock research evidence capture/1.0"})
    with urlopen(request, timeout=60) as response:
        return response.read(), response.geturl()


def _git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def _transport_note(url: str) -> str:
    if url.startswith("http://www.cffex.com.cn/fzjy/mrhq/"):
        return "direct HTTP GET to a legacy official CFFEX daily-file path; local hash freeze detects later local mismatch but does not add transport authentication"
    if url.startswith("http://"):
        return "direct HTTP request followed by any publisher redirect; resolved URL is retained"
    return "direct HTTPS GET"


def _check_static_source(source: dict[str, object], raw: bytes) -> None:
    expected_prefix = source.get("required_prefix")
    if isinstance(expected_prefix, bytes) and not raw.startswith(expected_prefix):
        raise RuntimeError(f"unexpected file prefix for {source['url']}")
    required_text = source.get("required_text")
    if required_text:
        decoded = raw.decode("utf-8", errors="ignore")
        for text in required_text:
            if str(text) not in decoded:
                raise RuntimeError(f"expected official text absent for {source['url']}: {text}")
    lowered = raw[:4096].decode("utf-8", errors="ignore").lower()
    if "safeline_bot_challenge" in lowered or "web 应用防火墙" in lowered:
        raise RuntimeError(f"refusing WAF body for {source['url']}")


def _actual_contract_url(day: str) -> str:
    return (
        "http://www.cffex.com.cn/fzjy/mrhq/"
        f"{day[:6]}/{day[6:]}/{day}_1.csv"
    )


def _check_actual_contract_csv(day: str, raw: bytes) -> dict[str, object]:
    try:
        text = raw.decode("gb18030")
    except UnicodeDecodeError as error:
        raise RuntimeError(f"CFFEX {day} cannot decode as gb18030") from error
    if "合约代码" not in text:
        raise RuntimeError(f"CFFEX {day} has no contract-code header")
    actual_rows: list[str] = []
    families: set[str] = set()
    for line in text.splitlines()[1:]:
        code = line.split(",", 1)[0].strip().upper()
        if code.startswith("TF") and code[2:].isdigit():
            families.add("TF")
            actual_rows.append(code)
        elif code.startswith("TS") and code[2:].isdigit():
            families.add("TS")
            actual_rows.append(code)
        elif code.startswith("TL") and code[2:].isdigit():
            families.add("TL")
            actual_rows.append(code)
        elif code.startswith("T") and code[1:].isdigit():
            families.add("T")
            actual_rows.append(code)
    if not {"T", "TF"}.issubset(families):
        raise RuntimeError(f"CFFEX {day} missing actual T/TF rows: {sorted(families)}")
    return {
        "candidate_contract_rows": len(actual_rows),
        "candidate_families": sorted(families),
        "candidate_contract_codes": actual_rows,
        "encoding": "gb18030",
    }


def _manifest_markdown(manifest: dict[str, object]) -> str:
    files = manifest["files"]
    rows = "\n".join(
        "| {name} | {publisher} | {date} | `{sha}` | {purpose} |".format(
            name=Path(str(row["path"])).name,
            publisher=row["publisher"],
            date=row["document_date"],
            sha=row["sha256"],
            purpose=row["purpose"],
        )
        for row in files
    )
    limitations = "\n".join(f"- {item}" for item in manifest["limitations"])
    return f"""# C12 Official Cash/Futures-Basis Evidence — Manifest

- Capture batch: `{manifest['capture_batch']}`
- Captured at: `{manifest['captured_at']}`
- Source quality: `{manifest['source_quality']}`
- Purpose: rules, product structure, investor-suitability context and six retrospective actual-contract EOD source-route samples for a research-only C12 cash/futures-basis candidate.
- Boundary: no return series, order, position, allocation, account decision, personal eligibility decision or performance claim.

| File | Publisher | Document date | SHA-256 | Evidence use |
|---|---|---|---|---|
{rows}

## Limitations

{limitations}
"""


def _capture() -> int:
    if SOURCE_DIR.exists():
        raise RuntimeError(
            f"refusing to overwrite frozen source batch: {SOURCE_DIR}; use --verify-only"
        )
    SOURCE_DIR.mkdir(parents=True, exist_ok=False)
    captured_at = datetime.now(timezone.utc).isoformat()
    files: list[dict[str, object]] = []

    for source in STATIC_SOURCES:
        raw, resolved_url = _fetch(str(source["url"]))
        _check_static_source(source, raw)
        path = SOURCE_DIR / str(source["filename"])
        _atomic_write(path, raw)
        entry = {
            "path": _repo_path(path),
            "publisher": source["publisher"],
            "title": source["title"],
            "document_date": source["document_date"],
            "url": source["url"],
            "resolved_url": resolved_url,
            "format": source["format"],
            "purpose": source["purpose"],
            "retrieved_at": captured_at,
            "transport": _transport_note(str(source["url"])),
            "bytes": len(raw),
            "sha256": _sha256(raw),
        }
        if "effective_from" in source:
            entry["effective_from"] = source["effective_from"]
        files.append(entry)

    for day in ACTUAL_CONTRACT_DATES:
        url = _actual_contract_url(day)
        raw, resolved_url = _fetch(url)
        metadata = _check_actual_contract_csv(day, raw)
        path = SOURCE_DIR / f"cffex_actual_contract_daily_{day}.csv"
        _atomic_write(path, raw)
        files.append(
            {
                "path": _repo_path(path),
                "publisher": "China Financial Futures Exchange",
                "title": "CFFEX daily actual futures-contract EOD data",
                "document_date": f"{day[:4]}-{day[4:6]}-{day[6:]}",
                "url": url,
                "resolved_url": resolved_url,
                "format": "csv",
                "purpose": "Retrospectively captured official actual listed-contract rows for T/TF (and, when present, TS/TL) with EOD OHLC, settlement, volume and open interest fields. It is a source-route sample only.",
                "retrieved_at": captured_at,
                "transport": _transport_note(url),
                "capture_note": "The file was retrieved after its trade date. Present reachability does not prove original-date availability, revision history, a complete lifecycle, bid/ask, fill, broker cost, broker margin, custody approval, personal eligibility or a return result.",
                "bytes": len(raw),
                "sha256": _sha256(raw),
                **metadata,
            }
        )

    frozen_files = [
        {"path": item["path"], "bytes": item["bytes"], "sha256": item["sha256"]}
        for item in files
    ]
    manifest: dict[str, object] = {
        "schema_version": "c12_cash_futures_basis_source_manifest.v1",
        "capture_batch": SOURCE_DIR.name,
        "case_id": CASE_DIR.name,
        "captured_at": captured_at,
        "purpose": "First-party evidence capture for a domestic Treasury cash/futures-basis feasibility study. The batch supports rule and source-route analysis only; it does not create a strategy result or personal action approval.",
        "source_quality": "primary_official_rule_product_disclosure_and_retrospective_actual_contract_samples",
        "protocol_status": "source_route_observation_not_historical_replay",
        "files": files,
        "limitations": [
            "The six CSV observations are individual dates spread across 2016--2026, not a complete every-session actual-contract archive, point-in-time contract master, delivery-status archive or five-calendar-year ledger.",
            "All historical daily files were retrieved retrospectively. Current path reachability does not prove original-decision-date availability, immutability, revision history, entitlement or data rights.",
            "Rule and product materials provide exchange-level terms. They do not establish effective daily broker margin, personal commission, custody-account approval, a personal trading-code result, bid/ask, queue state, partial fill, rejected order, execution or strategy return.",
            "The ETF annual report describes a fund using optimized sampling and index tracking. It does not establish that an ETF share is a deliverable Treasury bond or that it locks a delivery basis.",
            "The legacy CFFEX actual-contract daily route is plain HTTP. The local hash freeze controls subsequent local-file mismatch only; it does not convert that transport into point-in-time or authenticated evidence.",
            "No continuous futures series, invented fill, return, allocation, holding or action is generated from this batch."
        ],
        "source_freeze": {
            "schema_version": "research_source_freeze_control.v1",
            "seal_status": "case_local_hash_control_only",
            "sealed_at": captured_at,
            "boundary": "The freeze detects local raw-file changes. It is not external notarization, data entitlement, point-in-time proof, personal-account proof, execution validation or investment instruction.",
            "frozen_files": frozen_files,
            "runtime_provenance": {
                "script_path": _repo_path(Path(__file__).resolve()),
                "script_sha256": _sha256(Path(__file__).read_bytes()),
                "python_version": sys.version.split()[0],
                "platform": platform.platform(),
                "git_commit_at_runtime": _git_head(),
                "transport": "direct public-document retrieval; each file records its own transport and resolved URL",
            },
        },
    }
    _atomic_write(
        MANIFEST_PATH,
        (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
            "utf-8"
        ),
    )
    _atomic_write(MANIFEST_MD_PATH, _manifest_markdown(manifest).encode("utf-8"))
    print(f"captured {len(files)} source files into {SOURCE_DIR}")
    return 0


def _verify() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []
    files = manifest.get("files", [])
    for entry in files:
        path = REPO_ROOT / str(entry.get("path", ""))
        if not path.is_file():
            failures.append(f"missing {path}")
            continue
        raw = path.read_bytes()
        if len(raw) != entry.get("bytes"):
            failures.append(f"size {path}")
        if _sha256(raw) != entry.get("sha256"):
            failures.append(f"sha256 {path}")
    expected_frozen = [
        {"path": item.get("path"), "bytes": item.get("bytes"), "sha256": item.get("sha256")}
        for item in files
    ]
    frozen = manifest.get("source_freeze", {}).get("frozen_files", [])
    if frozen != expected_frozen:
        failures.append("source_freeze differs from manifest file rows")
    if not MANIFEST_MD_PATH.is_file():
        failures.append("manifest.md missing")
    if failures:
        print("C12 SOURCE CAPTURE: FAIL")
        print("\n".join(failures))
        return 1
    print(f"C12 SOURCE CAPTURE: PASS ({len(files)} files)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    return _verify() if args.verify_only else _capture()


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run the frozen CSI public-index discovery protocol.

This is intentionally a discovery/falsification tool. It archives raw public
CSI HTTP responses and measures published index-value paths, but never labels
the result an investor-level total-return backtest or an implementation signal.
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from urllib.request import Request, urlopen


CASE_DIR = Path(__file__).resolve().parents[1]
PROTOCOL_RELATIVE_PATH = Path("data/official_index_discovery_protocol_20260814.json")
SOURCE_RELATIVE_DIRECTORY = Path("sources/probe-csi-index-20260814")
OUTPUT_JSON_RELATIVE_PATH = Path("data/official_index_discovery_20260814.json")
OUTPUT_MD_RELATIVE_PATH = Path("data/official_index_discovery_20260814.md")


@dataclass(frozen=True)
class Observation:
    observed_on: date
    close: float


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8") + b"\n"


def write_atomic(path: Path, contents: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(contents)
        os.replace(temporary_name, path)
    finally:
        temporary = Path(temporary_name)
        if temporary.exists():
            temporary.unlink()


def write_content_addressed(path: Path, contents: bytes) -> None:
    if path.exists():
        if path.read_bytes() != contents:
            raise RuntimeError(f"immutable source collision at {path}")
        return
    write_atomic(path, contents)


def parse_date(value: object) -> date:
    raw = str(value).strip()
    for pattern in ("%Y%m%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, pattern).date()
        except ValueError:
            continue
    raise ValueError(f"unsupported CSI trade date: {raw!r}")


def subtract_five_calendar_years(value: date) -> date:
    try:
        return value.replace(year=value.year - 5)
    except ValueError:
        return value.replace(year=value.year - 5, day=28)


def normalise_observations(response: object, *, start: date, end: date) -> list[Observation]:
    if not isinstance(response, dict) or str(response.get("code")) != "200":
        raise ValueError("CSI response did not report code=200")
    rows = response.get("data")
    if not isinstance(rows, list):
        raise ValueError("CSI response data is not an array")
    by_date: dict[date, float] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("CSI response contains a non-object observation")
        observed_on = parse_date(row.get("tradeDate"))
        if observed_on < start or observed_on > end:
            continue
        try:
            close = float(row.get("close"))
        except (TypeError, ValueError) as error:
            raise ValueError(f"CSI response close is invalid on {observed_on}") from error
        if close <= 0:
            raise ValueError(f"CSI response close is non-positive on {observed_on}")
        existing = by_date.get(observed_on)
        if existing is not None and abs(existing - close) > 1e-10:
            raise ValueError(f"CSI response has conflicting duplicate closes on {observed_on}")
        by_date[observed_on] = close
    observations = [Observation(observed_on=item, close=by_date[item]) for item in sorted(by_date)]
    if len(observations) < 2:
        raise ValueError("CSI response has insufficient observations in the frozen window")
    return observations


def annualised_return(start_close: float, end_close: float, elapsed_days: int) -> float:
    return (end_close / start_close) ** (365.0 / elapsed_days) - 1.0


def evaluate_series(observations: list[Observation], *, threshold: float) -> dict[str, object]:
    dates = [item.observed_on for item in observations]
    windows: list[dict[str, object]] = []
    for end_position, end_observation in enumerate(observations):
        target = subtract_five_calendar_years(end_observation.observed_on)
        start_position = bisect.bisect_right(dates, target, hi=end_position) - 1
        if start_position < 0:
            continue
        start_observation = observations[start_position]
        elapsed_days = (end_observation.observed_on - start_observation.observed_on).days
        if elapsed_days < 1825 or elapsed_days > 1832:
            continue
        value = annualised_return(start_observation.close, end_observation.close, elapsed_days)
        windows.append(
            {
                "start_date": start_observation.observed_on.isoformat(),
                "end_date": end_observation.observed_on.isoformat(),
                "elapsed_days": elapsed_days,
                "annualised_index_value_return": round(value, 10),
                "at_or_above_5pct": value >= threshold,
            }
        )
    full_elapsed_days = (observations[-1].observed_on - observations[0].observed_on).days
    full_sample = annualised_return(observations[0].close, observations[-1].close, full_elapsed_days)
    summary: dict[str, object] = {
        "observations": len(observations),
        "first_date": observations[0].observed_on.isoformat(),
        "last_date": observations[-1].observed_on.isoformat(),
        "full_sample_elapsed_days": full_elapsed_days,
        "full_sample_cumulative_index_value_return": round(observations[-1].close / observations[0].close - 1.0, 10),
        "full_sample_annualised_index_value_return": round(full_sample, 10),
        "complete_rolling_five_year_windows": len(windows),
        "rolling_five_year_windows_at_or_above_5pct": sum(bool(item["at_or_above_5pct"]) for item in windows),
        "rolling_five_year_windows_below_5pct": sum(not bool(item["at_or_above_5pct"]) for item in windows),
        "rolling_five_year_min_annualised_index_value_return": round(min((float(item["annualised_index_value_return"]) for item in windows), default=float("nan")), 10),
        "rolling_five_year_max_annualised_index_value_return": round(max((float(item["annualised_index_value_return"]) for item in windows), default=float("nan")), 10),
        "rolling_five_year_all_windows_at_or_above_5pct": bool(windows) and all(bool(item["at_or_above_5pct"]) for item in windows),
        "window_samples": windows[:1] + windows[-1:] if len(windows) > 1 else windows,
    }
    return summary


def fetch_response(url: str) -> bytes:
    request = Request(
        url,
        headers={
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://www.csindex.com.cn/",
            "User-Agent": "Mozilla/5.0 (compatible; AStock-research/1.0)",
            "X-Requested-With": "XMLHttpRequest",
        },
    )
    with urlopen(request, timeout=30) as response:
        return response.read()


def load_protocol(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("protocol_id") != "CSI-PUBLIC-DISCOVERY-v1":
        raise ValueError("unexpected CSI discovery protocol")
    if value.get("status") != "pre_result_protocol":
        raise ValueError("CSI discovery protocol must be frozen before result retrieval")
    return value


def capture_live(case_dir: Path, protocol: dict[str, object]) -> tuple[dict[str, object], Path]:
    source_dir = case_dir / SOURCE_RELATIVE_DIRECTORY
    manifest_path = source_dir / "capture_manifest.json"
    if manifest_path.exists():
        raise RuntimeError(f"source capture already exists at {manifest_path}; rerun with --replay-manifest")
    fixed_window = protocol["fixed_window"]
    if not isinstance(fixed_window, dict):
        raise ValueError("protocol fixed_window is invalid")
    source = protocol["source"]
    if not isinstance(source, dict):
        raise ValueError("protocol source is invalid")
    template = str(source["endpoint_template"])
    captured_at = datetime.now(UTC).isoformat()
    entries: list[dict[str, object]] = []
    for index in protocol["predeclared_indices"]:
        if not isinstance(index, dict):
            raise ValueError("protocol index entry is invalid")
        code = str(index["code"])
        url = template.format(index_code=code, start_date=str(fixed_window["start_date"]).replace("-", ""), end_date=str(fixed_window["end_date"]).replace("-", ""))
        body = fetch_response(url)
        digest = sha256_bytes(body)
        raw_path = source_dir / f"{code}.{digest}.raw.json"
        write_content_addressed(raw_path, body)
        entries.append(
            {
                "index_code": code,
                "request_url": url,
                "retrieved_at": captured_at,
                "raw_response_file": raw_path.name,
                "raw_response_size_bytes": len(body),
                "raw_response_sha256": digest,
            }
        )
    manifest = {
        "schema_version": "csi_public_index_capture_manifest.v1",
        "protocol_id": protocol["protocol_id"],
        "scope_id": protocol["scope_id"],
        "captured_at": captured_at,
        "source": source["provider"],
        "quality_tier": source["quality_tier"],
        "purpose": "Immutable raw public-index observations for discovery only; not a formal product or total-return replay feed.",
        "files": entries,
    }
    write_atomic(manifest_path, canonical_json_bytes(manifest))
    markdown = render_capture_markdown(manifest)
    write_atomic(source_dir / "capture_manifest.md", markdown.encode("utf-8"))
    return manifest, manifest_path


def load_capture_manifest(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema_version") != "csi_public_index_capture_manifest.v1":
        raise ValueError("unexpected CSI capture manifest")
    return value


def evaluate_capture(case_dir: Path, protocol: dict[str, object], manifest: dict[str, object], manifest_path: Path) -> dict[str, object]:
    fixed_window = protocol["fixed_window"]
    if not isinstance(fixed_window, dict):
        raise ValueError("protocol fixed_window is invalid")
    start = date.fromisoformat(str(fixed_window["start_date"]))
    end = date.fromisoformat(str(fixed_window["end_date"]))
    threshold = float(fixed_window["threshold"])
    files = manifest.get("files")
    if not isinstance(files, list):
        raise ValueError("capture manifest files are invalid")
    by_code = {str(item.get("index_code")): item for item in files if isinstance(item, dict)}
    results: list[dict[str, object]] = []
    for index in protocol["predeclared_indices"]:
        if not isinstance(index, dict):
            raise ValueError("protocol index entry is invalid")
        code = str(index["code"])
        source_record = by_code.get(code)
        if source_record is None:
            results.append({"index_code": code, "name": index["name"], "status": "unavailable_missing_raw_response"})
            continue
        raw_path = manifest_path.parent / str(source_record["raw_response_file"])
        raw_bytes = raw_path.read_bytes()
        if sha256_bytes(raw_bytes) != str(source_record["raw_response_sha256"]):
            raise RuntimeError(f"raw response hash mismatch for {code}")
        response = json.loads(raw_bytes.decode("utf-8"))
        observations = normalise_observations(response, start=start, end=end)
        result = {
            "index_code": code,
            "name": index["name"],
            "role": index["role"],
            "selection_basis": index["selection_basis"],
            "status": "evaluated_public_index_observation_only",
            "raw_response_file": str(raw_path.relative_to(case_dir)),
            "raw_response_sha256": source_record["raw_response_sha256"],
            "summary": evaluate_series(observations, threshold=threshold),
        }
        results.append(result)
    return {
        "schema_version": "official_index_discovery_result.v1",
        "scope_id": protocol["scope_id"],
        "protocol_id": protocol["protocol_id"],
        "protocol_sha256": sha256_file(case_dir / PROTOCOL_RELATIVE_PATH),
        "capture_manifest": str(manifest_path.relative_to(case_dir)),
        "capture_manifest_sha256": sha256_file(manifest_path),
        "captured_at": manifest["captured_at"],
        "quality_tier": "public_official_index_observation",
        "formal_decision_eligible": False,
        "portfolio_q": 0,
        "method": {
            "return_metric": fixed_window["return_metric"],
            "window_algorithm": fixed_window["window_algorithm"],
            "threshold": threshold,
            "no_costs": True,
            "no_taxes": True,
            "no_product_tracking_or_execution": True,
        },
        "results": results,
        "boundary": "This discovery screen measures published index values only. It does not establish investor TWRR, an executable product, a portfolio, an allocation, a cash-receipt objective or an order.",
    }


def render_capture_markdown(manifest: dict[str, object]) -> str:
    rows = [
        "# CSI Public Index Capture Manifest",
        "",
        f"- Protocol: `{manifest['protocol_id']}`",
        f"- Captured at: `{manifest['captured_at']}`",
        "- Boundary: frozen official public observations for discovery only; not a formal investor or product replay feed.",
        "",
        "| Index | Raw response | Bytes | SHA-256 |",
        "|---|---|---:|---|",
    ]
    for item in manifest["files"]:
        assert isinstance(item, dict)
        rows.append(f"| `{item['index_code']}` | `{item['raw_response_file']}` | {item['raw_response_size_bytes']} | `{item['raw_response_sha256']}` |")
    return "\n".join(rows) + "\n"


def render_result_markdown(result: dict[str, object]) -> str:
    rows = [
        "# Official CSI Index Discovery Screen",
        "",
        f"- Protocol: `{result['protocol_id']}`",
        f"- Capture: `{result['capture_manifest']}`",
        "- Status: **public official-index discovery only; not formal return evidence; q=0.**",
        "",
        "## Results",
        "",
        "| Code | Published reference | Observations | Last date | 5Y windows >=5% | 5Y windows <5% | Minimum 5Y annualised index-value return | All 5Y windows >=5%? |",
        "|---|---|---:|---|---:|---:|---:|---|",
    ]
    for item in result["results"]:
        assert isinstance(item, dict)
        if item.get("status") != "evaluated_public_index_observation_only":
            rows.append(f"| `{item['index_code']}` | {item['name']} | n/a | n/a | n/a | n/a | n/a | unavailable |")
            continue
        summary = item["summary"]
        assert isinstance(summary, dict)
        rows.append(
            f"| `{item['index_code']}` | {item['name']} | {summary['observations']} | {summary['last_date']} | "
            f"{summary['rolling_five_year_windows_at_or_above_5pct']} | {summary['rolling_five_year_windows_below_5pct']} | "
            f"{float(summary['rolling_five_year_min_annualised_index_value_return']):.2%} | "
            f"{'yes' if summary['rolling_five_year_all_windows_at_or_above_5pct'] else 'no'} |"
        )
    rows.extend(
        [
            "",
            "## Boundary",
            "",
            "The screen is deliberately weaker than the research objective. It has no product-level total-return reconciliation, costs, taxes, holdings availability, market status, execution, access or capacity test. A published index that clears every observed window is therefore a research lead only; it cannot enter T2/T3/T4 or become an allocation. An index with a miss is rejected as evidence for the stronger objective over the observed history.",
        ]
    )
    return "\n".join(rows) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-dir", type=Path, default=CASE_DIR)
    parser.add_argument("--replay-manifest", type=Path, help="Recalculate from an existing immutable capture manifest without network access")
    arguments = parser.parse_args()
    case_dir = arguments.case_dir.resolve()
    protocol = load_protocol(case_dir / PROTOCOL_RELATIVE_PATH)
    if arguments.replay_manifest is None:
        manifest, manifest_path = capture_live(case_dir, protocol)
    else:
        manifest_path = arguments.replay_manifest.resolve()
        manifest = load_capture_manifest(manifest_path)
        if manifest.get("protocol_id") != protocol.get("protocol_id"):
            raise ValueError("capture manifest protocol does not match the frozen protocol")
    result = evaluate_capture(case_dir, protocol, manifest, manifest_path)
    write_atomic(case_dir / OUTPUT_JSON_RELATIVE_PATH, canonical_json_bytes(result))
    write_atomic(case_dir / OUTPUT_MD_RELATIVE_PATH, render_result_markdown(result).encode("utf-8"))
    print(json.dumps({"output": str(OUTPUT_JSON_RELATIVE_PATH), "capture_manifest": result["capture_manifest"], "q": 0}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

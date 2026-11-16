#!/usr/bin/env python3
"""Freeze and screen a bounded public ETF price-only research vector.

This tool exists to make a negative research result reproducible.  It never
places an order and deliberately keeps the raw public price series separate
from a total-return or execution-grade portfolio test.

The fetched archive is an immutable, content-addressed public observation.  A
rerun without ``--fetch`` reads that archive only, so the derived metrics do
not silently change when a vendor revises history.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
SRC_ROOT = REPO_ROOT / "src" / "python"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from astock.backtest.frozen_portfolio import build_frozen_portfolio_replay_input


SCOPE_ID = "total-return-open-universe-v3-20260814"
EVALUATION_START = pd.Timestamp("2019-01-02")
EVALUATION_END = pd.Timestamp("2026-08-13")
SCREEN_CODES = ("510300", "510880", "511010", "518880")
SCREEN_LABELS = {
    "510300": "CSI 300 equity ETF price sleeve",
    "510880": "SSE Dividend equity ETF price sleeve",
    "511010": "SSE 5-year Treasury ETF price sleeve",
    "518880": "gold ETF price sleeve",
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == value:
        return
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(value, encoding="utf-8")
    temporary.replace(path)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fetch_raw_etf_history(code: str, start: str, end: str) -> pd.DataFrame:
    """Fetch raw (unadjusted) public ETF observations with bounded retries."""
    import akshare as ak

    errors: list[str] = []
    for attempt in range(4):
        try:
            raw = ak.fund_etf_hist_em(
                symbol=code,
                period="daily",
                start_date=start,
                end_date=end,
                adjust="",
            )
            frame = raw.rename(
                columns={
                    "日期": "date",
                    "开盘": "open",
                    "收盘": "close",
                    "成交量": "volume",
                    "成交额": "amount",
                }
            )
            required = ["date", "open", "close", "volume", "amount"]
            if not set(required).issubset(frame.columns):
                raise ValueError(f"unexpected public ETF fields: {list(raw.columns)}")
            frame = frame[required].copy()
            frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
            for column in ("open", "close", "volume", "amount"):
                frame[column] = pd.to_numeric(frame[column], errors="coerce")
            frame = frame.dropna(subset=["date", "open", "close"]).sort_values("date")
            if frame.empty or (frame[["open", "close"]] <= 0).any().any():
                raise ValueError("public ETF response has no positive open/close observations")
            frame["tradable"] = True
            frame["execution_status"] = "tradable"
            return frame.reset_index(drop=True)
        except Exception as error:  # A public probe may be transiently rate limited.
            errors.append(f"attempt {attempt + 1}: {type(error).__name__}: {error}")
            if attempt < 3:
                time.sleep(attempt + 1)
    raise RuntimeError(f"unable to fetch raw public ETF history for {code}: {'; '.join(errors)}")


def _quarterly_targets(calendar: list[pd.Timestamp]) -> dict[str, dict[str, float]]:
    targets: dict[str, dict[str, float]] = {}
    previous_quarter: pd.Period | None = None
    equal_weight = 1.0 / len(SCREEN_CODES)
    for day in calendar:
        quarter = day.to_period("Q")
        if previous_quarter is None or quarter != previous_quarter:
            targets[day.date().isoformat()] = {code: equal_weight for code in SCREEN_CODES}
            previous_quarter = quarter
    return targets


def _freeze_public_observation(source_directory: Path) -> tuple[Path, Path, Path]:
    """Fetch the public observations and bind the exact bytes to a hash."""
    source_directory.mkdir(parents=True, exist_ok=True)
    frames = {
        code: _fetch_raw_etf_history(code, "20180101", "20260813")
        for code in SCREEN_CODES
    }
    common_dates = sorted(
        set.intersection(*(set(pd.to_datetime(frame["date"])) for frame in frames.values()))
    )
    if len(common_dates) < 1_500:
        raise ValueError("the public screening universe has insufficient common observations")
    normalized = {
        code: frame[frame["date"].isin(common_dates)].copy()
        for code, frame in frames.items()
    }
    calendar = [day.date().isoformat() for day in common_dates]
    targets = _quarterly_targets(common_dates)
    references = {
        day: "public_screening_set_20260814:not_point_in_time_universe"
        for day in targets
    }
    observed_at = datetime.now(timezone.utc).isoformat()
    packet = build_frozen_portfolio_replay_input(
        normalized,
        targets,
        trading_calendar=calendar,
        universe_references=references,
        source="akshare_public",
        trading_calendar_source="public_common_price_dates_not_official_exchange_calendar",
        observed_at=observed_at,
    )
    archive_path = packet.write_frozen_archive(source_directory)
    replay_path = packet.write_replay_input(source_directory)
    capture_manifest = {
        "schema_version": "public_price_screening_capture.v1",
        "scope_id": SCOPE_ID,
        "retrieved_at": observed_at,
        "provider": "AkShare public observation adapter",
        "upstream_endpoint": "Eastmoney fund_etf_hist_em",
        "request": {
            "period": "daily",
            "start_date": "20180101",
            "end_date": "20260813",
            "adjust": "",
            "price_interpretation": "raw or unadjusted market-price observations only",
        },
        "instruments": [
            {
                "code": code,
                "label": SCREEN_LABELS[code],
                "rows": int(len(normalized[code])),
                "first_date": str(normalized[code]["date"].min().date()),
                "last_date": str(normalized[code]["date"].max().date()),
            }
            for code in SCREEN_CODES
        ],
        "common_price_dates": len(common_dates),
        "archive_id": packet.archive_id,
        "archive_file": archive_path.name,
        "archive_sha256": _sha256(archive_path),
        "replay_input_file": replay_path.name,
        "replay_input_sha256": _sha256(replay_path),
        "quality_tier": "tier_3_frozen_public_observation",
        "warnings": [
            "This is a public aggregation capture, not an official or licensed point-in-time data archive.",
            "The calendar is the intersection of available price dates, not an official exchange calendar.",
            "No adjusted-price, distribution, corporate-action, halt, price-limit, delisting, bid/ask, or fill coverage is claimed.",
        ],
    }
    manifest_path = source_directory / "capture_manifest.json"
    _write_text(manifest_path, _canonical_json(capture_manifest))
    return archive_path, replay_path, manifest_path


def _load_close_panel(replay_path: Path) -> tuple[pd.DataFrame, dict[str, dict[str, float]]]:
    payload = json.loads(replay_path.read_text(encoding="utf-8"))
    raw_market_data = payload.get("market_data")
    raw_targets = payload.get("target_weights")
    if not isinstance(raw_market_data, dict) or not isinstance(raw_targets, dict):
        raise ValueError("frozen public input has no market_data or target_weights")
    series: dict[str, pd.Series] = {}
    for code in SCREEN_CODES:
        records = raw_market_data.get(code)
        if not isinstance(records, list):
            raise ValueError(f"frozen public input lacks {code}")
        frame = pd.DataFrame(records)
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
        frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
        series[code] = frame.dropna(subset=["date", "close"]).set_index("date")["close"]
    panel = pd.concat(series, axis=1).dropna().sort_index()
    targets = {
        str(day): {str(code): float(weight) for code, weight in row.items()}
        for day, row in raw_targets.items()
        if isinstance(row, dict)
    }
    return panel, targets


def _screen_static_vector(replay_path: Path, archive_path: Path, capture_path: Path) -> dict[str, Any]:
    """Calculate a unitized, cost-free price-only diagnostic from frozen bytes."""
    close, targets = _load_close_panel(replay_path)
    close = close.loc[(close.index >= EVALUATION_START) & (close.index <= EVALUATION_END)]
    if close.index.min() != EVALUATION_START or close.index.max() != EVALUATION_END:
        raise ValueError("frozen input does not cover the declared evaluation window")
    all_close, _ = _load_close_panel(replay_path)
    target_rows = pd.DataFrame.from_dict(targets, orient="index").reindex(columns=SCREEN_CODES)
    target_rows.index = pd.to_datetime(target_rows.index)
    weights = target_rows.reindex(all_close.index).ffill().fillna(0.0).reindex(close.index).ffill().fillna(0.0)
    returns = close.pct_change().fillna(0.0)
    portfolio_returns = (weights.shift(1).fillna(0.0) * returns).sum(axis=1)
    portfolio_returns.iloc[0] = 0.0
    nav = (1.0 + portfolio_returns).cumprod()
    elapsed_days = int((nav.index[-1] - nav.index[0]).days)
    annualized_return = float(nav.iloc[-1] ** (365.25 / elapsed_days) - 1.0)
    drawdown = nav / nav.cummax() - 1.0
    rolling: list[dict[str, Any]] = []
    for end in nav.index:
        prior = nav.index[nav.index <= end - pd.DateOffset(years=5)]
        if prior.empty:
            continue
        start = prior[-1]
        days = int((end - start).days)
        if days < 1_820:
            continue
        value = float((nav.loc[end] / nav.loc[start]) ** (365.25 / days) - 1.0)
        rolling.append(
            {
                "start": start.date().isoformat(),
                "end": end.date().isoformat(),
                "days": days,
                "annualized_price_return": value,
                "meets_5pct_price_threshold": value >= 0.05,
            }
        )
    if not rolling:
        raise ValueError("no complete rolling five-year observations were calculated")
    annual_rows: list[dict[str, Any]] = []
    for year, value in nav.groupby(nav.index.year):
        annual_rows.append(
            {
                "year": int(year),
                "start": value.index[0].date().isoformat(),
                "end": value.index[-1].date().isoformat(),
                "price_return": float(value.iloc[-1] / value.iloc[0] - 1.0),
            }
        )
    capture = json.loads(capture_path.read_text(encoding="utf-8"))
    return {
        "schema_version": "public_price_screening_replay.v1",
        "scope_id": SCOPE_ID,
        "run_date": "2026-08-14",
        "artifact_class": "derived_research_evidence",
        "status": "screening_complete_static_vector_rejected_as_5pct_evidence",
        "research_only": True,
        "formal_decision_eligible": False,
        "investment_implementation_approved": False,
        "portfolio_q": 0,
        "purpose": "A frozen public price-only diagnostic that tests whether a simple, predeclared static cross-asset screen can support the existing 5% total-return research objective. It cannot do so.",
        "screening_universe": [
            {"code": code, "label": SCREEN_LABELS[code], "weight": 0.25}
            for code in SCREEN_CODES
        ],
        "universe_boundary": "This finite four-ETF screening set is not a dated T2 decision universe, does not permanently exclude direct equities, REITs, sovereign instruments or other lawful products, and does not admit any instrument to T3 or T4.",
        "rulebook": {
            "version": "R1-static-public-price-screen-v1",
            "weighting": "equal 25% target weight per screened ETF",
            "rebalancing_mark": "first common price observation of each calendar quarter; the unitized calculation applies the marked weight only to the following price interval",
            "return_type": "unadjusted secondary-market price return only",
            "external_flows": "none modelled",
            "distribution_treatment": "not modelled; no distribution is added to or inferred from the price series",
            "cash_residual": "none; target weights sum to 100%",
            "costs_and_taxes": "not modelled",
            "execution": "no fill, lot, settlement, spread, market-impact, suspension or price-limit assertion",
        },
        "frozen_input": {
            "provider_quality_tier": "tier_3_frozen_public_observation",
            "capture_manifest_path": str(capture_path.relative_to(CASE_DIR)),
            "capture_manifest_sha256": _sha256(capture_path),
            "archive_path": str(archive_path.relative_to(CASE_DIR)),
            "archive_id": capture["archive_id"],
            "archive_sha256": _sha256(archive_path),
            "replay_input_path": str(replay_path.relative_to(CASE_DIR)),
            "replay_input_sha256": _sha256(replay_path),
        },
        "evaluation_window": {
            "start": nav.index[0].date().isoformat(),
            "end": nav.index[-1].date().isoformat(),
            "elapsed_days": elapsed_days,
            "common_price_sessions": int(len(nav)),
        },
        "price_only_results": {
            "cumulative_price_return": float(nav.iloc[-1] - 1.0),
            "annualized_price_return": annualized_return,
            "annualized_daily_price_volatility": float(portfolio_returns.std(ddof=1) * (252.0**0.5)),
            "maximum_mark_to_market_drawdown": float(drawdown.min()),
            "annual_price_rows": annual_rows,
        },
        "rolling_five_year_price_diagnostic": {
            "window_count": len(rolling),
            "overlapping_windows_warning": "These daily-end windows overlap extensively and are not independent samples.",
            "windows_meeting_5pct": sum(1 for row in rolling if row["meets_5pct_price_threshold"]),
            "windows_below_5pct": sum(1 for row in rolling if not row["meets_5pct_price_threshold"]),
            "minimum_annualized_price_return": min(row["annualized_price_return"] for row in rolling),
            "maximum_annualized_price_return": max(row["annualized_price_return"] for row in rolling),
            "all_complete_windows_meet_5pct": all(row["meets_5pct_price_threshold"] for row in rolling),
            "representative_windows": [
                row
                for row in rolling
                if row["end"] in {"2024-01-02", "2024-12-31", "2025-12-31", "2026-08-13"}
            ],
        },
        "decision": {
            "static_vector_supports_5pct_total_return_objective": False,
            "reason": [
                "The price-only diagnostic has complete rolling five-year windows below 5%, so even this weaker proxy does not clear the all-window threshold.",
                "Unadjusted price observations omit or leave ambiguous distributions and corporate actions; they are not a total-return ledger.",
                "Costs, taxes, execution, point-in-time universe membership and liquidity constraints are absent.",
            ],
            "current_action": "Do not promote this static vector to T2, T3, T4 or an allocation instruction. Continue with a frozen rulebook, structure-specific dossiers and licensed or authoritative point-in-time total-return evidence.",
        },
        "warnings": [
            "A favorable full-window annualized price result is not a forecast, probability estimate, return floor or guarantee.",
            "Do not combine this price series with fund distributions or NAV returns without a single source-consistent total-return convention; that would risk double counting.",
            "The set deliberately excludes no asset class permanently. It is a limited discovery screen only.",
            "No cash-receipt objective or automatic reinvestment is used in this diagnostic.",
        ],
    }


def _render_markdown(result: dict[str, Any]) -> str:
    price = result["price_only_results"]
    rolling = result["rolling_five_year_price_diagnostic"]
    rows = "\n".join(
        f"| {item['code']} | {item['label']} | {item['weight']:.0%} |"
        for item in result["screening_universe"]
    )
    representative = "\n".join(
        f"| {item['start']} | {item['end']} | {item['annualized_price_return']:.2%} | {'是' if item['meets_5pct_price_threshold'] else '否'} |"
        for item in rolling["representative_windows"]
    )
    frozen = result["frozen_input"]
    return f"""# R1 Public Price Screening Replay

- Scope ID: `{result['scope_id']}`
- Status: `{result['status']}`
- Research-only / formal decision eligible / portfolio q: `true / false / 0`

## Result

The limited static four-ETF screen is **rejected as evidence for the 5% total-return objective**.  Its full-period annualized *price* return is {price['annualized_price_return']:.2%}, but {rolling['windows_below_5pct']} of {rolling['window_count']} complete, overlapping rolling five-year price windows are below 5%; the minimum is {rolling['minimum_annualized_price_return']:.2%}.  The result is not total return, does not include costs or taxes, and is not an investable allocation.

## Screening set

| Code | Role in this diagnostic | Marked weight |
|---|---|---:|
{rows}

This finite set is a public-data discovery screen, not a T2 decision universe. It does not exclude direct equities, public REITs, direct sovereign instruments or other lawful products from later research.

## Frozen public input

- Capture manifest: `{frozen['capture_manifest_path']}` (`SHA-256 {frozen['capture_manifest_sha256']}`)
- Raw public archive: `{frozen['archive_path']}` (`{frozen['archive_id']}`)
- Replay input: `{frozen['replay_input_path']}`
- Window: {result['evaluation_window']['start']} to {result['evaluation_window']['end']} ({result['evaluation_window']['common_price_sessions']} common price observations).

The provider is a public aggregation path and the calendar is the intersection of observed prices, not an official exchange calendar. The series use the unadjusted market-price setting. No distribution, corporate action, halt, limit-lock, delisting, bid/ask, spread, fill, tax or capacity claim is made.

## Diagnostic mechanics

- Equal 25% marked weights; reset at the first common price observation of each calendar quarter.
- The marked weight applies only to the next price interval.
- Unitized price path only; no external flow, cash-receipt objective, or automatic reinvestment.
- No cost, tax, lot, settlement, slippage or market-impact model.

## Results

| Metric | Result |
|---|---:|
| Cumulative price return | {price['cumulative_price_return']:.2%} |
| Annualized price return | {price['annualized_price_return']:.2%} |
| Annualized daily price volatility | {price['annualized_daily_price_volatility']:.2%} |
| Maximum marked drawdown | {price['maximum_mark_to_market_drawdown']:.2%} |
| Five-year windows at or above 5% price return | {rolling['windows_meeting_5pct']} / {rolling['window_count']} |
| Five-year windows below 5% price return | {rolling['windows_below_5pct']} / {rolling['window_count']} |
| Minimum five-year annualized price return | {rolling['minimum_annualized_price_return']:.2%} |

| Window start | Window end | Annualized price return | At or above 5%? |
|---|---|---:|---|
{representative}

## Boundary and next gate

The failure of an unadjusted, cost-free price proxy is sufficient to reject this static vector as supporting evidence. It does **not** demonstrate the performance of a total-return strategy, nor does it test a future model. Before any later T2/T3/T4 review, the research must freeze a versioned selection and rebalancing rule; obtain a source-consistent total-return and corporate-action ledger; model dated product-specific costs, taxes, settlement and liquidity; and complete equity-research-grade item dossiers plus portfolio-level risk review.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="Fetch and freeze a new public observation archive.")
    parser.add_argument(
        "--source-directory",
        type=Path,
        default=CASE_DIR / "sources" / "probe-public-market-20260814",
    )
    parser.add_argument("--replay-input", type=Path, help="Existing frozen replay input for a no-fetch rerun.")
    args = parser.parse_args()

    if args.fetch:
        archive_path, replay_path, capture_path = _freeze_public_observation(args.source_directory)
    else:
        if args.replay_input is None:
            raise SystemExit("use --fetch or provide --replay-input")
        replay_path = args.replay_input.resolve()
        payload = json.loads(replay_path.read_text(encoding="utf-8"))
        manifest = payload.get("source_manifest") if isinstance(payload, dict) else {}
        archive_id = str(manifest.get("archive_id") or "").removeprefix("sha256:")
        archive_path = replay_path.parent / f"{archive_id}.json"
        capture_path = replay_path.parent / "capture_manifest.json"
        if not archive_path.is_file() or not capture_path.is_file():
            raise SystemExit("replay input requires its sibling raw archive and capture_manifest.json")

    result = _screen_static_vector(replay_path, archive_path, capture_path)
    result_path = CASE_DIR / "data" / "public_price_screening_replay_20260814.json"
    markdown_path = result_path.with_suffix(".md")
    _write_text(result_path, _canonical_json(result))
    _write_text(markdown_path, _render_markdown(result))
    print(json.dumps({"result_path": str(result_path), "status": result["status"], "portfolio_q": 0}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

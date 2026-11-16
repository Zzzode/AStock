#!/usr/bin/env python3
"""Run a frozen public-price observation for one personal ETF rule.

The purpose is falsification, not performance marketing.  It uses the already
archived, unadjusted ETF prices under ``sources/probe-public-market-20260814``
and deliberately reports every rolling five-year price window.  The source is
not a total-return, point-in-time, or execution-grade data set, so this script
cannot approve an investment strategy or infer an investor outcome.

No network request occurs in this script.  A rerun reads the same frozen bytes
and regenerates only the derived Markdown/JSON pair.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


CASE_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = CASE_DIR / "sources" / "probe-public-market-20260814"
REPLAY_INPUT = SOURCE_DIR / (
    "e69a5fc85d6b19f71a5ace6738bc0c3c0b32835b7829fc54fcc7d34453640dda"
    ".portfolio.replay.json"
)
CAPTURE_MANIFEST = SOURCE_DIR / "capture_manifest.json"
JSON_OUTPUT = CASE_DIR / "data" / "personal_etf_strategy_public_observation_20260814.json"
MARKDOWN_OUTPUT = CASE_DIR / "data" / "personal_etf_strategy_public_observation_20260814.md"

SCOPE_ID = "total-return-open-universe-v3-20260814"
RUN_DATE = "2026-08-14"
EVALUATION_START = pd.Timestamp("2019-02-01")
EVALUATION_END = pd.Timestamp("2026-08-13")
RISK_ASSETS = ("510300", "510880", "518880")
DEFENSIVE_ASSET = "511010"
ALL_ASSETS = RISK_ASSETS + (DEFENSIVE_ASSET,)
ASSET_LABELS = {
    "510300": "CSI 300 equity ETF price sleeve",
    "510880": "SSE Dividend equity ETF price sleeve",
    "518880": "gold ETF price sleeve",
    "511010": "SSE 5-year Treasury ETF price sleeve",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == value:
        return
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(value, encoding="utf-8")
    temporary.replace(path)


def _load_frozen_panel() -> pd.DataFrame:
    payload = json.loads(REPLAY_INPUT.read_text(encoding="utf-8"))
    raw_market_data = payload.get("market_data")
    if not isinstance(raw_market_data, dict):
        raise ValueError("frozen ETF replay input has no market_data mapping")
    series: dict[str, pd.Series] = {}
    for code in ALL_ASSETS:
        records = raw_market_data.get(code)
        if not isinstance(records, list):
            raise ValueError(f"frozen ETF replay input is missing {code}")
        frame = pd.DataFrame(records)
        frame["date"] = pd.to_datetime(frame.get("date"), errors="coerce")
        frame["close"] = pd.to_numeric(frame.get("close"), errors="coerce")
        frame = frame.dropna(subset=["date", "close"]).sort_values("date", kind="stable")
        if frame.empty or frame["date"].duplicated().any() or (frame["close"] <= 0).any():
            raise ValueError(f"frozen ETF replay input has invalid close observations for {code}")
        series[code] = frame.set_index("date")["close"]
    panel = pd.concat(series, axis=1).dropna().sort_index()
    if panel.index.min() > EVALUATION_START or panel.index.max() < EVALUATION_END:
        raise ValueError("frozen ETF replay input does not cover the declared evaluation window")
    return panel.loc[:EVALUATION_END]


def _monthly_target_weights(prices: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """Freeze one conservative, low-turnover public-price rule.

    At each first observed session of a calendar month, information only
    through the previous session is used.  Up to two positive-trend sleeves
    receive a combined 50% allocation; the remainder is the Treasury-ETF
    sleeve.  If no risk sleeve passes, the Treasury sleeve receives 100%.
    The marked target is applied only after a one-session delay.
    """

    target_weights = pd.DataFrame(0.0, index=prices.index, columns=ALL_ASSETS)
    current = pd.Series(0.0, index=ALL_ASSETS, dtype=float)
    decisions: list[dict[str, Any]] = []
    prior_month: tuple[int, int] | None = None
    for position, session in enumerate(prices.index):
        if position < 253:
            target_weights.loc[session] = current
            continue
        month = (int(session.year), int(session.month))
        if month == prior_month:
            target_weights.loc[session] = current
            continue
        prior_month = month
        history = prices.iloc[:position]
        previous_close = history.iloc[-1]
        momentum_252 = previous_close / history.iloc[-253] - 1.0
        moving_average_200 = history.iloc[-200:].mean()
        eligible = [
            code
            for code in RISK_ASSETS
            if momentum_252[code] > 0.0 and previous_close[code] > moving_average_200[code]
        ]
        selected = sorted(eligible, key=lambda code: float(momentum_252[code]), reverse=True)[:2]
        current = pd.Series(0.0, index=ALL_ASSETS, dtype=float)
        if selected:
            current.loc[selected] = 0.50 / len(selected)
            current.loc[DEFENSIVE_ASSET] = 0.50
            regime = "risk_on_guardrailed"
        else:
            current.loc[DEFENSIVE_ASSET] = 1.0
            regime = "defensive_only"
        target_weights.loc[session] = current
        decisions.append(
            {
                "decision_session": session.date().isoformat(),
                "information_through": history.index[-1].date().isoformat(),
                "effective_after": "one following observed session",
                "regime": regime,
                "selected_risk_sleeves": selected,
                "momentum_252": {code: float(momentum_252[code]) for code in RISK_ASSETS},
                "above_moving_average_200": {
                    code: bool(previous_close[code] > moving_average_200[code]) for code in RISK_ASSETS
                },
                "target_weights": {code: float(current[code]) for code in ALL_ASSETS},
            }
        )
    effective = target_weights.shift(1).ffill().fillna(0.0)
    return effective, decisions


def _rolling_five_year(nav: pd.Series) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for end in nav.index:
        available_starts = nav.index[nav.index <= end - pd.DateOffset(years=5)]
        if available_starts.empty:
            continue
        start = available_starts[-1]
        days = int((end - start).days)
        if days < 1_820:
            continue
        annualized = float((nav.loc[end] / nav.loc[start]) ** (365.25 / days) - 1.0)
        rows.append(
            {
                "start": start.date().isoformat(),
                "end": end.date().isoformat(),
                "days": days,
                "annualized_price_return": annualized,
                "meets_5pct_price_threshold": annualized >= 0.05,
            }
        )
    if not rows:
        raise ValueError("no complete rolling five-year observations were calculated")
    return rows


def _performance_metrics(net_return: pd.Series) -> dict[str, Any]:
    nav = (1.0 + net_return).cumprod()
    elapsed_days = int((nav.index[-1] - nav.index[0]).days)
    annualized = float(nav.iloc[-1] ** (365.25 / elapsed_days) - 1.0)
    annualized_volatility = float(net_return.std(ddof=1) * np.sqrt(252.0))
    drawdown = nav / nav.cummax() - 1.0
    sharpe_like = (
        float(net_return.mean() / net_return.std(ddof=1) * np.sqrt(252.0))
        if float(net_return.std(ddof=1)) > 0.0
        else 0.0
    )
    rolling = _rolling_five_year(nav)
    annual_rows: list[dict[str, Any]] = []
    for year, values in nav.groupby(nav.index.year):
        annual_rows.append(
            {
                "year": int(year),
                "start": values.index[0].date().isoformat(),
                "end": values.index[-1].date().isoformat(),
                "net_price_return": float(values.iloc[-1] / values.iloc[0] - 1.0),
            }
        )
    return {
        "cumulative_price_return": float(nav.iloc[-1] - 1.0),
        "annualized_price_return": annualized,
        "annualized_daily_price_volatility": annualized_volatility,
        "maximum_mark_to_market_drawdown": float(drawdown.min()),
        "sharpe_like_zero_cash_rate": sharpe_like,
        "annual_price_rows": annual_rows,
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
                if row["end"] in {"2024-02-01", "2024-12-31", "2025-12-31", "2026-08-13"}
            ],
        },
    }


def _run_observation() -> dict[str, Any]:
    prices = _load_frozen_panel()
    effective_weights, decisions = _monthly_target_weights(prices)
    prices = prices.loc[EVALUATION_START:EVALUATION_END]
    effective_weights = effective_weights.reindex(prices.index).ffill().fillna(0.0)
    returns = prices.pct_change().fillna(0.0)
    gross_price_return = (effective_weights * returns).sum(axis=1)
    turnover = (
        effective_weights.diff().abs().sum(axis=1).fillna(effective_weights.abs().sum(axis=1)) / 2.0
    )
    cost_sensitivity: list[dict[str, Any]] = []
    for cost_bps in (0.0, 5.0, 10.0, 20.0):
        net_price_return = gross_price_return - turnover * cost_bps / 10_000.0
        metrics = _performance_metrics(net_price_return)
        cost_sensitivity.append(
            {
                "one_way_turnover_cost_bps": cost_bps,
                "metrics": metrics,
            }
        )
    primary = next(row for row in cost_sensitivity if row["one_way_turnover_cost_bps"] == 10.0)
    capture = json.loads(CAPTURE_MANIFEST.read_text(encoding="utf-8"))
    return {
        "schema_version": "personal_etf_strategy_public_observation.v1",
        "scope_id": SCOPE_ID,
        "run_date": RUN_DATE,
        "artifact_class": "derived_research_evidence",
        "status": "candidate_rule_rejected_as_stable_5pct_evidence",
        "research_only": True,
        "formal_decision_eligible": False,
        "investment_implementation_approved": False,
        "portfolio_q": 0,
        "purpose": (
            "Test one predeclared low-frequency ETF rule against the frozen public "
            "price archive. It is a falsification screen for a stable 5% target, "
            "not a total-return backtest or investment instruction."
        ),
        "universe": [
            {"code": code, "label": ASSET_LABELS[code], "role": "risk_screen"}
            for code in RISK_ASSETS
        ]
        + [{"code": DEFENSIVE_ASSET, "label": ASSET_LABELS[DEFENSIVE_ASSET], "role": "defensive_price_sleeve"}],
        "rulebook": {
            "version": "personal-etf-absolute-momentum-v1",
            "rebalance_frequency": "first observed market session of each calendar month",
            "information_timing": "previous observed close only; the marked target applies after one following observed session",
            "risk_sleeve_eligibility": "252-observation price momentum > 0 and prior close > 200-observation simple moving average",
            "selection": "Rank eligible 510300, 510880 and 518880 by 252-observation price momentum; hold at most the top two.",
            "risk_sleeve_weight": "50% combined; split equally among one or two selected sleeves",
            "defensive_sleeve_weight": "50% when any risk sleeve is selected; 100% when no risk sleeve is selected",
            "return_type": "unadjusted secondary-market price return only",
            "distribution_treatment": "not modelled; no fund distribution, dividend, interest or NAV accrual is added or inferred",
            "cost_sensitivity": "0, 5, 10 and 20 basis points per one-way turnover; these are generic analytical sensitivities, not broker-fee assertions",
            "execution": "No lot, spread, market-impact, T+1, suspension, price-limit, tax, settlement, ETF creation/redemption or fill claim is made.",
            "cash_treatment": "No cash-receipt objective or automatic reinvestment is used. The defensive sleeve is a market instrument, not a cash target.",
        },
        "frozen_input": {
            "provider_quality_tier": "tier_3_frozen_public_observation",
            "capture_manifest_path": str(CAPTURE_MANIFEST.relative_to(CASE_DIR)),
            "capture_manifest_sha256": _sha256(CAPTURE_MANIFEST),
            "archive_id": capture["archive_id"],
            "archive_path": str((SOURCE_DIR / capture["archive_file"]).relative_to(CASE_DIR)),
            "archive_sha256": _sha256(SOURCE_DIR / capture["archive_file"]),
            "replay_input_path": str(REPLAY_INPUT.relative_to(CASE_DIR)),
            "replay_input_sha256": _sha256(REPLAY_INPUT),
        },
        "evaluation_window": {
            "start": prices.index[0].date().isoformat(),
            "end": prices.index[-1].date().isoformat(),
            "elapsed_days": int((prices.index[-1] - prices.index[0]).days),
            "common_price_sessions": int(len(prices)),
            "decision_count": len(decisions),
        },
        "observed_turnover": {
            "mean_daily_one_way_turnover": float(turnover.mean()),
            "annualized_one_way_turnover_proxy": float(turnover.mean() * 252.0),
        },
        "cost_sensitivity": cost_sensitivity,
        "primary_10bps_observation": primary,
        "last_observed_rule_state": decisions[-1] if decisions else None,
        "decision": {
            "supports_stable_5pct_total_return_objective": False,
            "reason": [
                "At the 10-basis-point turnover sensitivity, complete rolling five-year price windows remain below 5%; the all-window stability condition fails.",
                "The frozen input is unadjusted public price data, not a total-return ledger, and therefore cannot prove an investor's net return.",
                "Execution, taxes, product distributions, corporate actions, liquidity and point-in-time eligibility are not modelled.",
            ],
            "current_action": (
                "Do not activate this rule as a live allocation. It is a candidate research design only; "
                "a formal strategy requires total-return inputs, product dossiers, costs, tax/settlement and independent review."
            ),
        },
        "warnings": [
            "A favorable full-period annualized price result is not a forecast, annual floor, probability estimate or guarantee.",
            "The limited four-ETF set is not an open-universe selection process and cannot establish that other domestic instruments would not improve or worsen results.",
            "Do not add distributions to this price series without a source-consistent total-return convention; that could double count cash flows.",
            "The rule is deliberately not a futures result. Futures require actual-contract, margin, roll, limit and fill-quality evidence under a separate research gate.",
        ],
    }


def _render_markdown(result: dict[str, Any]) -> str:
    primary = result["primary_10bps_observation"]["metrics"]
    rolling = primary["rolling_five_year_price_diagnostic"]
    cost_rows = "\n".join(
        "| {cost:.0f} | {annualized:.2%} | {volatility:.2%} | {drawdown:.2%} | {passes} / {windows} | {minimum:.2%} |".format(
            cost=row["one_way_turnover_cost_bps"],
            annualized=row["metrics"]["annualized_price_return"],
            volatility=row["metrics"]["annualized_daily_price_volatility"],
            drawdown=row["metrics"]["maximum_mark_to_market_drawdown"],
            passes=row["metrics"]["rolling_five_year_price_diagnostic"]["windows_meeting_5pct"],
            windows=row["metrics"]["rolling_five_year_price_diagnostic"]["window_count"],
            minimum=row["metrics"]["rolling_five_year_price_diagnostic"]["minimum_annualized_price_return"],
        )
        for row in result["cost_sensitivity"]
    )
    annual_rows = "\n".join(
        f"| {row['year']} | {row['net_price_return']:.2%} |"
        for row in primary["annual_price_rows"]
    )
    selected = result["last_observed_rule_state"]
    state = "N/A" if selected is None else (
        f"{selected['decision_session']}：{selected['regime']}；"
        f"风险筛选 {', '.join(selected['selected_risk_sleeves']) or '无'}。"
    )
    return f"""# Personal ETF Rule — Frozen Public Observation

- Scope ID: `{result['scope_id']}`
- Status: `{result['status']}`
- Research-only / formal decision eligible / portfolio q: `true / false / 0`

## Result

The predeclared ETF rule is **rejected as evidence for a stable 5% total-return
objective**. At the primary 10-basis-point one-way-turnover sensitivity, its
full-period annualized *price* return is
{primary['annualized_price_return']:.2%}, but
{rolling['windows_below_5pct']} of {rolling['window_count']} complete,
overlapping rolling five-year price windows fall below 5%; the minimum is
{rolling['minimum_annualized_price_return']:.2%}. It is not total return and
is not an allocation instruction.

## Frozen rule

- At the first observed session of each calendar month, use only the preceding
  observed close.
- A risk sleeve must have positive 252-observation price momentum and close
  above its 200-observation simple moving average.
- Rank 510300, 510880 and 518880 by momentum; hold at most two. Their combined
  marked weight is 50%, split equally. The remainder is 511010; if none pass,
  511010 is 100%.
- Apply a marked target only after one following observed session. No future
  observation is used in the rule calculation.
- This is price-only and uses no cash-receipt target or automatic reinvestment.

## Sensitivity result

| One-way turnover cost (bps) | Annualized price return | Annualized price volatility | Maximum drawdown | 5Y windows at/above 5% | Minimum 5Y annualized price return |
|---:|---:|---:|---:|---:|---:|
{cost_rows}

The windows overlap and are not independent observations. The 0/5/10/20-bps
rows are generic price-impact sensitivities, not assertions about a broker's
charges or execution quality.

## Calendar price rows at 10 bps

| Year | Net price return |
|---:|---:|
{annual_rows}

## Boundary

- Frozen input: `{result['frozen_input']['replay_input_path']}`
  (`SHA-256 {result['frozen_input']['replay_input_sha256']}`).
- The provider is a public aggregation path and values are unadjusted
  secondary-market observations. Product distributions, corporate actions,
  taxes, spreads, T+1, suspensions, limits, lots, settlement, capacity and
  fills are not modelled.
- Latest rule observation: {state}
- Current action: **do not activate**. The rule remains a research design until
  it has a source-consistent total-return ledger, product-level diligence,
  cost/tax/settlement evidence and independent validation.
"""


def main() -> int:
    result = _run_observation()
    _write_text(JSON_OUTPUT, _canonical_json(result))
    _write_text(MARKDOWN_OUTPUT, _render_markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Reproduce an exploratory diagnostic on a frozen public ETF daily-bar series.

The input itself declares ``price_basis=forward_adjusted_or_unknown``. This
script therefore cannot classify its returns as a known market-price basis,
an independently verified adjustment basis or investor total return. It exists
to preserve a non-admissible diagnostic and cannot approve a strategy.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


CASE_DIR = Path(__file__).resolve().parents[1]
SOURCE = CASE_DIR / "sources/probe-public-etf-price-r0-20260814" / (
    "e69a5fc85d6b19f71a5ace6738bc0c3c0b32835b7829fc54fcc7d34453640dda"
    ".portfolio.replay.json"
)
OUTPUT_JSON = CASE_DIR / "data/etf_public_price_falsification_20260814.json"
OUTPUT_MD = CASE_DIR / "data/etf_public_price_falsification_20260814.md"
RISK = ("510300", "510880", "518880")
DEFENSIVE = "511010"
ASSETS = RISK + (DEFENSIVE,)
START = pd.Timestamp("2019-02-01")
END = pd.Timestamp("2026-08-13")
EXPECTED_BASIS = "forward_adjusted_or_unknown"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, content: str) -> None:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def _load_public_series() -> tuple[pd.DataFrame, str]:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    public_series_basis = payload.get("price_basis")
    if public_series_basis != EXPECTED_BASIS:
        raise ValueError(
            "frozen replay input basis changed; do not silently reinterpret "
            f"{public_series_basis!r} as a known return basis"
        )
    raw = payload.get("market_data")
    if not isinstance(raw, dict):
        raise ValueError("frozen replay input lacks market_data")
    series: dict[str, pd.Series] = {}
    for code in ASSETS:
        frame = pd.DataFrame(raw.get(code))
        frame["date"] = pd.to_datetime(frame.get("date"), errors="coerce")
        frame["close"] = pd.to_numeric(frame.get("close"), errors="coerce")
        frame = frame.dropna(subset=["date", "close"]).sort_values("date", kind="stable")
        if frame.empty or frame["date"].duplicated().any() or (frame["close"] <= 0).any():
            raise ValueError(f"invalid frozen daily-bar history for {code}")
        series[code] = frame.set_index("date")["close"]
    panel = pd.concat(series, axis=1).dropna().sort_index()
    if panel.index.min() > START or panel.index.max() < END:
        raise ValueError("frozen panel does not cover the declared diagnostic window")
    return panel.loc[:END], public_series_basis


def _weights(prices: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    marked = pd.DataFrame(0.0, index=prices.index, columns=ASSETS)
    current = pd.Series(0.0, index=ASSETS)
    decisions: list[dict[str, object]] = []
    last_month: tuple[int, int] | None = None
    for position, session in enumerate(prices.index):
        if position < 253:
            marked.loc[session] = current
            continue
        month = (int(session.year), int(session.month))
        if month == last_month:
            marked.loc[session] = current
            continue
        last_month = month
        history = prices.iloc[:position]
        last_close = history.iloc[-1]
        momentum = last_close / history.iloc[-253] - 1.0
        average = history.iloc[-200:].mean()
        eligible = [code for code in RISK if momentum[code] > 0.0 and last_close[code] > average[code]]
        selected = sorted(eligible, key=lambda code: float(momentum[code]), reverse=True)[:2]
        current = pd.Series(0.0, index=ASSETS)
        if selected:
            current.loc[selected] = 0.50 / len(selected)
            current.loc[DEFENSIVE] = 0.50
            regime = "exploratory_risk_on_mapping"
        else:
            current.loc[DEFENSIVE] = 1.0
            regime = "exploratory_defensive_mapping"
        marked.loc[session] = current
        decisions.append(
            {
                "decision_session": session.date().isoformat(),
                "information_through": history.index[-1].date().isoformat(),
                "effective_after": "one following observed session",
                "regime": regime,
                "selected_risk_sleeves": selected,
            }
        )
    return marked.shift(1).ffill().fillna(0.0), decisions


def _rolling(nav: pd.Series) -> dict[str, object]:
    annualized: list[float] = []
    for end in nav.index:
        starts = nav.index[nav.index <= end - pd.DateOffset(years=5)]
        if starts.empty:
            continue
        start = starts[-1]
        days = int((end - start).days)
        if days >= 1820:
            annualized.append(float((nav.loc[end] / nav.loc[start]) ** (365.25 / days) - 1.0))
    if not annualized:
        raise ValueError("no complete rolling five-year public-series windows")
    return {
        "window_count": len(annualized),
        "windows_meeting_5pct": sum(value >= 0.05 for value in annualized),
        "windows_below_5pct": sum(value < 0.05 for value in annualized),
        "minimum_annualized_public_series_change": min(annualized),
        "maximum_annualized_public_series_change": max(annualized),
        "all_complete_windows_meet_5pct": all(value >= 0.05 for value in annualized),
        "warning": "Daily-end five-year windows overlap and are not independent observations."
    }


def _metrics(returns: pd.Series) -> dict[str, object]:
    nav = (1.0 + returns).cumprod()
    elapsed = int((nav.index[-1] - nav.index[0]).days)
    annual_rows = []
    for year, values in nav.groupby(nav.index.year):
        annual_rows.append({"year": int(year), "public_series_change": float(values.iloc[-1] / values.iloc[0] - 1.0)})
    return {
        "annualized_public_series_change": float(nav.iloc[-1] ** (365.25 / elapsed) - 1.0),
        "annualized_public_series_volatility": float(returns.std(ddof=1) * np.sqrt(252.0)),
        "maximum_drawdown": float((nav / nav.cummax() - 1.0).min()),
        "rolling_five_year_public_series_diagnostic": _rolling(nav),
        "annual_public_series_rows": annual_rows,
    }


def main() -> int:
    prices, public_series_basis = _load_public_series()
    weights, decisions = _weights(prices)
    prices = prices.loc[START:END]
    weights = weights.reindex(prices.index).ffill().fillna(0.0)
    public_series_changes = prices.pct_change().fillna(0.0)
    gross = (weights * public_series_changes).sum(axis=1)
    turnover = weights.diff().abs().sum(axis=1).fillna(weights.abs().sum(axis=1)) / 2.0
    sensitivity = []
    for bps in (0.0, 5.0, 10.0, 20.0):
        sensitivity.append({"one_way_turnover_cost_bps": bps, "metrics": _metrics(gross - turnover * bps / 10000.0)})
    primary = next(row for row in sensitivity if row["one_way_turnover_cost_bps"] == 10.0)
    rolling = primary["metrics"]["rolling_five_year_public_series_diagnostic"]
    result = {
        "schema_version": "etf_public_series_admissibility_diagnostic.v2",
        "as_of": "2026-08-14",
        "artifact_class": "derived_research_evidence",
        "status": "not_admissible_as_stable_5pct_total_return_evidence",
        "research_only": True,
        "formal_decision_eligible": False,
        "portfolio_q": 0,
        "source": {
            "path": str(SOURCE.relative_to(CASE_DIR)),
            "sha256": _sha256(SOURCE),
            "quality": "tier_3_frozen_public_observation",
            "source_declared_basis": public_series_basis,
        },
        "protocol": {
            "status": "exploratory_post_source_diagnostic_not_predeclared_not_frozen",
            "decision_frequency": "first observed session of each month",
            "information_timing": "previous observed close; one observed-session implementation delay",
            "risk_filter": "positive 252-observation public-series momentum and prior public-series close above its 200-observation moving average",
            "risk_selection": "top two of 510300, 510880 and 518880 by 252-observation public-series momentum",
            "exploratory_mapping": "50% combined selected risk sleeves and 50% 511010; 100% 511010 if none passes",
            "return_basis": "frozen public daily-bar series with source-declared forward_adjusted_or_unknown basis; neither independent market-price nor total-return classification is established",
            "not_independently_modelled": ["NAV accrual", "distribution ledger", "corporate-action ledger", "tax", "spread", "T+1", "limits", "halts", "lots", "settlement", "fills"],
        },
        "evaluation": {
            "start": prices.index[0].date().isoformat(),
            "end": prices.index[-1].date().isoformat(),
            "common_sessions": len(prices),
            "decision_count": len(decisions),
            "cost_sensitivity": sensitivity,
            "primary_10bps": primary,
        },
        "decision": {
            "supports_stable_5pct_total_return_objective": False,
            "reason": [
                f"The exploratory 10-bps diagnostic has {rolling['windows_below_5pct']} of {rolling['window_count']} complete rolling five-year public-series windows below 5%, with a {rolling['minimum_annualized_public_series_change']:.2%} minimum.",
                "Its unresolved adjustment basis and missing independent event/execution ledger make it inadmissible as total-return or execution evidence in either direction.",
            ],
            "current_action": "No activation; retain only as a non-admissible exploratory public-series diagnostic.",
        },
    }
    _write(OUTPUT_JSON, json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    rows = "\n".join(
        f"| {row['one_way_turnover_cost_bps']:.0f} | {row['metrics']['annualized_public_series_change']:.2%} | {row['metrics']['maximum_drawdown']:.2%} | {row['metrics']['rolling_five_year_public_series_diagnostic']['windows_below_5pct']} / {row['metrics']['rolling_five_year_public_series_diagnostic']['window_count']} |"
        for row in sensitivity
    )
    _write(OUTPUT_MD, f"""# ETF Public-Series Admissibility Diagnostic

- Status: **not admissible** as stable-5% total-return evidence; `q=0`.
- Source: `{result['source']['path']}` (`SHA-256 {result['source']['sha256']}`).
- Source-declared basis: `{public_series_basis}`.
- Protocol: exploratory post-source diagnostic; neither predeclared nor frozen.
- Boundary: frozen tier-3 public daily bars. No independently verified market-price,
  NAV, distribution, corporate-action, tax, tradability or execution ledger exists.

At the 10-bps turnover sensitivity, the arithmetic public-series diagnostic is
{primary['metrics']['annualized_public_series_change']:.2%}; {rolling['windows_below_5pct']}
of {rolling['window_count']} complete rolling five-year public-series windows
are below 5%, with a {rolling['minimum_annualized_public_series_change']:.2%}
minimum. These descriptive outputs cannot confirm or reject an investor
total-return result because the source adjustment basis is unresolved.

| One-way turnover cost (bps) | Annualized public-series change | Maximum drawdown | 5Y windows below 5% |
|---:|---:|---:|---:|
{rows}

The diagnostic uses the previous observed close at the first observed session
of each month, applies a one-session delay, and mechanically maps up to two
risk sleeves from 510300/510880/518880 alongside 511010. It is not an
allocation instruction, a pre-registered test or a strategy result.
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

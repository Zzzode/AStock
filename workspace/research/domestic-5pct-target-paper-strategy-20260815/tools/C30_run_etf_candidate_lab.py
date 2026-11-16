#!/usr/bin/env python3
"""Recompute C30's fixed ETF market-price diagnostic from retained SSE inputs.

This tool is intentionally narrow.  It reads a pre-recorded protocol and the
five hash-checked SSE JSONP responses, then produces a research-only proxy
calculation.  It never accesses a broker, sends an order, fetches fresh data,
or treats daily bars as total return or fills.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


DATE_TAG = "20260815"
CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]
ANALYSIS_DIR = CASE_DIR / "analysis"
PROTOCOL_PATH = ANALYSIS_DIR / f"c30_etf_candidate_protocol_{DATE_TAG}.json"
PROTOCOL_MD = ANALYSIS_DIR / f"c30_etf_candidate_protocol_{DATE_TAG}.md"
OUTPUT_JSON = ANALYSIS_DIR / f"c30_etf_candidate_rule_and_diagnostic_{DATE_TAG}.json"
OUTPUT_MD = ANALYSIS_DIR / f"c30_etf_candidate_rule_and_diagnostic_{DATE_TAG}.md"
HURDLE = 0.05
EPSILON = 1e-12


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(REPO_ROOT))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_weight_vector(weights: dict[str, Any], codes: tuple[str, ...], label: str) -> pd.Series:
    if set(weights) != set(codes):
        raise ValueError(f"{label}: target-code set differs from frozen protocol")
    vector = pd.Series({code: float(weights[code]) for code in codes}, dtype=float)
    if not np.isfinite(vector.to_numpy()).all() or (vector < -EPSILON).any():
        raise ValueError(f"{label}: invalid target weights")
    if abs(float(vector.sum()) - 1.0) > EPSILON:
        raise ValueError(f"{label}: target weights do not sum to 1")
    return vector


def load_protocol() -> tuple[dict[str, Any], tuple[str, ...], pd.Series]:
    if not PROTOCOL_PATH.is_file():
        raise FileNotFoundError(f"C30 protocol must exist before calculation: {PROTOCOL_PATH}")
    if not PROTOCOL_MD.is_file():
        raise FileNotFoundError(f"C30 protocol Markdown mirror is missing: {PROTOCOL_MD}")
    protocol = read_json(PROTOCOL_PATH)
    if protocol.get("status") != "frozen_for_research_only_calculation":
        raise ValueError("C30 protocol is not frozen for research-only calculation")
    if protocol.get("external_investment_action_authorized") is not False:
        raise ValueError("C30 protocol must explicitly prohibit external investment action")
    codes = tuple(str(code) for code in protocol["source"]["allowed_codes"])
    if len(codes) != 5 or len(set(codes)) != 5:
        raise ValueError("C30 requires exactly five distinct, predeclared ETF codes")
    target = assert_weight_vector(protocol["candidate"]["target_weights"], codes, "base candidate")
    if set(int(month) for month in protocol["candidate"]["rebalance_months"]) != {6, 12}:
        raise ValueError("C30 base cadence differs from the frozen June/December protocol")
    if float(protocol["illustrative_cost"]["base_one_way_bps"]) != 20.0:
        raise ValueError("C30 base cost differs from frozen protocol")
    protocol_markdown = PROTOCOL_MD.read_text(encoding="utf-8")
    for marker in ("C30 ETF Candidate", "510300", "510880", "511010", "518880", "511990", "20%", "40%"):
        if marker not in protocol_markdown:
            raise ValueError(f"C30 protocol Markdown mirror lacks required frozen marker: {marker}")
    return protocol, codes, target


def validate_and_load_source(protocol: dict[str, Any], codes: tuple[str, ...]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    manifest_path = REPO_ROOT / str(protocol["source"]["manifest_path"])
    if not manifest_path.is_file():
        raise FileNotFoundError(f"retained SSE manifest is missing: {manifest_path}")
    manifest = read_json(manifest_path)
    source_rows = {str(row.get("code")): row for row in manifest.get("files", [])}
    if not set(codes).issubset(source_rows):
        raise ValueError("retained SSE manifest lacks a frozen C30 code")

    open_series: dict[str, pd.Series] = {}
    close_series: dict[str, pd.Series] = {}
    raw_records: list[dict[str, Any]] = []
    for code in codes:
        source = source_rows[code]
        raw_path = REPO_ROOT / str(source["path"])
        if not raw_path.is_file():
            raise FileNotFoundError(f"retained SSE response is missing: {raw_path}")
        actual_hash = sha256_file(raw_path)
        actual_size = raw_path.stat().st_size
        if actual_hash != source.get("sha256") or actual_size != int(source.get("bytes", -1)):
            raise ValueError(f"retained SSE response failed manifest hash/size verification: {code}")
        decoded = raw_path.read_text(encoding="utf-8").strip()
        match = re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*\((.*)\)", decoded, flags=re.DOTALL)
        if not match:
            raise ValueError(f"unexpected JSONP syntax for {code}")
        payload = json.loads(match.group(1))
        if str(payload.get("code")) != code or int(payload.get("begin", -1)) != 0:
            raise ValueError(f"source identity/begin mismatch for {code}")
        rows = payload.get("kline")
        if not isinstance(rows, list) or not rows:
            raise ValueError(f"source has no daily rows for {code}")
        if len(rows) != int(payload.get("total", -1)) or int(payload.get("end", -1)) != len(rows):
            raise ValueError(f"source reports incomplete response for {code}")
        frame = pd.DataFrame(rows, columns=["date", "open", "high", "low", "close", "volume"])
        dates = pd.to_numeric(frame["date"], errors="coerce")
        frame["date"] = pd.to_datetime(dates.round().astype("Int64").astype(str), format="%Y%m%d", errors="coerce")
        frame["open"] = pd.to_numeric(frame["open"], errors="coerce")
        frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
        frame = frame.dropna(subset=["date", "open", "close"]).sort_values("date", kind="stable")
        if frame.empty or frame["date"].duplicated().any() or (frame[["open", "close"]] <= 0).any().any():
            raise ValueError(f"source has invalid date/open/close fields for {code}")
        open_series[code] = frame.set_index("date")["open"]
        close_series[code] = frame.set_index("date")["close"]
        raw_records.append(
            {
                "code": code,
                "path": str(source["path"]),
                "bytes": actual_size,
                "sha256": actual_hash,
                "response_rows": int(payload["total"]),
                "first_trade_date": frame["date"].iloc[0].date().isoformat(),
                "last_trade_date": frame["date"].iloc[-1].date().isoformat(),
            }
        )

    opens = pd.concat(open_series, axis=1, sort=True).dropna().sort_index()
    closes = pd.concat(close_series, axis=1, sort=True).dropna().sort_index()
    common = opens.index.intersection(closes.index)
    opens = opens.loc[common, list(codes)]
    closes = closes.loc[common, list(codes)]
    if len(opens) < 2 or not opens.index.equals(closes.index) or opens.index.duplicated().any():
        raise ValueError("C30 common open/close panel is invalid")
    if (opens <= 0).any().any() or (closes <= 0).any().any():
        raise ValueError("C30 common panel contains non-positive prices")
    source_info = {
        "manifest_path": repo_path(manifest_path),
        "manifest_sha256": sha256_file(manifest_path),
        "quality": protocol["source"]["quality"],
        "price_basis": protocol["source"]["basis"],
        "raw_responses": raw_records,
        "common_panel": {
            "observations": int(len(opens)),
            "first_common_session": opens.index[0].date().isoformat(),
            "last_common_session": opens.index[-1].date().isoformat(),
            "excluded_rows_after_common_intersection": {
                code: int(source_rows[code]["response_rows"]) - int(len(opens)) for code in codes
            },
        },
    }
    return opens, closes, source_info


def effective_rebalance_positions(index: pd.DatetimeIndex, review_months: tuple[int, ...]) -> set[int]:
    positions: set[int] = set()
    for position in range(1, len(index)):
        decision = index[position - 1]
        effective = index[position]
        if decision.month in review_months and effective.month != decision.month:
            positions.add(position)
    return positions


def drawdown_details(nav: pd.Series) -> dict[str, Any]:
    running_peak = nav.cummax()
    drawdowns = nav / running_peak - 1.0
    trough_date = drawdowns.idxmin()
    peak_candidates = nav.loc[:trough_date]
    peak_date = peak_candidates[peak_candidates == peak_candidates.max()].index[0]
    peak_value = float(nav.loc[peak_date])
    recovery = nav.loc[trough_date:]
    recovered = recovery[recovery >= peak_value]
    recovery_date = None if recovered.empty else recovered.index[0].date().isoformat()
    return {
        "maximum_drawdown": float(drawdowns.loc[trough_date]),
        "peak_date": peak_date.date().isoformat(),
        "trough_date": trough_date.date().isoformat(),
        "recovery_date": recovery_date,
    }


def loss_window(nav: pd.Series, periods: int) -> dict[str, Any]:
    changes = nav / nav.shift(periods) - 1.0
    changes = changes.dropna()
    if changes.empty:
        return {"periods": periods, "return": None, "start": None, "end": None}
    end = changes.idxmin()
    start = nav.index[nav.index.get_loc(end) - periods]
    return {
        "periods": periods,
        "return": float(changes.loc[end]),
        "start": start.date().isoformat(),
        "end": end.date().isoformat(),
    }


def complete_year_metrics(nav: pd.Series) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    terminal_year = int(nav.index[-1].year)
    for year in sorted(set(int(value) for value in nav.index.year)):
        group = nav.loc[nav.index.year == year]
        months = sorted(set(int(value) for value in group.index.month))
        complete = year < terminal_year and months == list(range(1, 13))
        prior = nav.loc[nav.index < group.index[0]]
        if complete and prior.empty:
            raise ValueError(f"complete calendar year has no prior unit value: {year}")
        starting_value = float(prior.iloc[-1]) if complete else float(group.iloc[0])
        change = float(group.iloc[-1] / starting_value - 1.0)
        rows.append(
            {
                "year": year,
                "start": group.index[0].date().isoformat(),
                "end": group.index[-1].date().isoformat(),
                "months_present": months,
                "complete_calendar_year": complete,
                "market_price_proxy_change_after_illustrative_cost": change,
                "at_or_above_5pct_limited_proxy_screen": bool(change >= HURDLE) if complete else None,
            }
        )
    return rows


def rolling_five_year_metrics(nav: pd.Series) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    month_end_positions = [
        position
        for position, date in enumerate(nav.index)
        if position == len(nav.index) - 1 or nav.index[position + 1].month != date.month
    ]
    for end_position in month_end_positions:
        end_date = nav.index[end_position]
        cutoff = end_date - pd.DateOffset(years=5)
        prior_dates = nav.index[nav.index <= cutoff]
        if len(prior_dates) == 0:
            continue
        start_date = prior_dates[-1]
        days = int((end_date - start_date).days)
        if days <= 0:
            continue
        annualized = float((nav.loc[end_date] / nav.loc[start_date]) ** (365.25 / days) - 1.0)
        rows.append(
            {
                "start": start_date.date().isoformat(),
                "end": end_date.date().isoformat(),
                "calendar_days": days,
                "annualized_market_price_proxy_change_after_illustrative_cost": annualized,
                "at_or_above_5pct_limited_proxy_screen": bool(annualized >= HURDLE),
            }
        )
    if not rows:
        return {
            "endpoint_frequency": "month_end_only",
            "window_count": 0,
            "rows": [],
            "warning": "No full rolling five-calendar-year market-price-proxy windows.",
        }
    values = [float(row["annualized_market_price_proxy_change_after_illustrative_cost"]) for row in rows]
    return {
        "endpoint_frequency": "month_end_only",
        "window_count": len(rows),
        "at_or_above_5pct_count": sum(value >= HURDLE for value in values),
        "below_5pct_count": sum(value < HURDLE for value in values),
        "minimum_annualized_market_price_proxy_change_after_illustrative_cost": min(values),
        "maximum_annualized_market_price_proxy_change_after_illustrative_cost": max(values),
        "rows": rows,
        "warning": "Overlapping endpoints are descriptive, not independent observations; this is not a total-return or execution test.",
    }


def simulate_variant(
    opens: pd.DataFrame,
    closes: pd.DataFrame,
    target: pd.Series,
    review_months: tuple[int, ...],
    one_way_bps: float,
    variant_id: str,
) -> dict[str, Any]:
    if one_way_bps < 0:
        raise ValueError(f"{variant_id}: a negative illustrative cost is invalid")
    if tuple(opens.columns) != tuple(target.index) or tuple(closes.columns) != tuple(target.index):
        raise ValueError(f"{variant_id}: data panel and target vector differ")
    index = opens.index
    if len(index) < 3:
        raise ValueError(f"{variant_id}: insufficient common sessions")
    cost_rate = float(one_way_bps) / 10_000.0
    first_decision_position = 0
    first_effective_position = 1
    initial_decision = index[first_decision_position]
    initial_effective = index[first_effective_position]
    values = target.copy() * (1.0 - cost_rate)
    values = values * (closes.iloc[first_effective_position] / opens.iloc[first_effective_position])
    nav_rows: list[tuple[pd.Timestamp, float]] = [(initial_effective, float(values.sum()))]
    weights_rows: list[tuple[pd.Timestamp, *tuple[float, ...]]] = [
        (initial_effective, *(float(values[code] / values.sum()) for code in target.index))
    ]
    events: list[dict[str, Any]] = [
        {
            "event_type": "initial_entry",
            "decision_session": initial_decision.date().isoformat(),
            "effective_session": initial_effective.date().isoformat(),
            "information_through": initial_decision.date().isoformat(),
            "timing": "initial allocation at next-common-session reported open; same-session execution prohibited",
            "pre_trade_weights": {code: 0.0 for code in target.index},
            "target_weights": {code: float(target[code]) for code in target.index},
            "one_way_turnover": 1.0,
            "illustrative_cost_fraction_of_pre_trade_nav": cost_rate,
            "proxy_fill_status": "not_observed_market_price_proxy",
        }
    ]
    rebalancing_positions = effective_rebalance_positions(index, review_months)
    for position in range(first_effective_position + 1, len(index)):
        session = index[position]
        prior_close = closes.iloc[position - 1]
        current_open = opens.iloc[position]
        # Existing positions absorb the overnight D-close-to-E-open proxy move
        # before a scheduled effective-open rebalance can take place.
        values = values * (current_open / prior_close)
        if position in rebalancing_positions:
            decision = index[position - 1]
            pre_trade_nav = float(values.sum())
            pre_trade_weights = values / pre_trade_nav
            turnover = float((pre_trade_weights - target).abs().sum() / 2.0)
            cost = pre_trade_nav * turnover * cost_rate
            values = target * (pre_trade_nav - cost)
            events.append(
                {
                    "event_type": "scheduled_rebalance",
                    "decision_session": decision.date().isoformat(),
                    "effective_session": session.date().isoformat(),
                    "information_through": decision.date().isoformat(),
                    "timing": "decision after prior close; trade at next-common-session reported open before that session's open-to-close proxy move",
                    "pre_trade_weights": {code: float(pre_trade_weights[code]) for code in target.index},
                    "target_weights": {code: float(target[code]) for code in target.index},
                    "one_way_turnover": turnover,
                    "illustrative_cost_fraction_of_pre_trade_nav": float(cost / pre_trade_nav),
                    "proxy_fill_status": "not_observed_market_price_proxy",
                }
            )
        values = values * (closes.iloc[position] / current_open)
        nav_rows.append((session, float(values.sum())))
        weights = values / float(values.sum())
        weights_rows.append((session, *(float(weights[code]) for code in target.index)))

    nav = pd.Series({date: value for date, value in nav_rows}, dtype=float).sort_index()
    weights = pd.DataFrame(weights_rows, columns=["date", *target.index]).set_index("date")
    if nav.empty or not np.isfinite(nav.to_numpy()).all() or (nav <= 0).any():
        raise ValueError(f"{variant_id}: simulation generated invalid proxy NAV")
    if any(event["decision_session"] >= event["effective_session"] for event in events):
        raise AssertionError(f"{variant_id}: a simulated event violates strictly next-session timing")

    years = complete_year_metrics(nav)
    complete_years = [row for row in years if row["complete_calendar_year"]]
    rolling = rolling_five_year_metrics(nav)
    elapsed_days = int((nav.index[-1] - nav.index[0]).days)
    if elapsed_days <= 0:
        raise ValueError(f"{variant_id}: no elapsed time")
    daily_changes = nav.pct_change().dropna()
    initial_cost = cost_rate
    total_turnover = sum(float(event["one_way_turnover"]) for event in events)
    total_cost_fraction = sum(float(event["illustrative_cost_fraction_of_pre_trade_nav"]) for event in events)
    complete_below = sum(
        1
        for row in complete_years
        if not bool(row["at_or_above_5pct_limited_proxy_screen"])
    )
    rolling_below = int(rolling.get("below_5pct_count", 0))
    if not complete_years or rolling.get("window_count", 0) == 0:
        screen_state = "NOT_EVALUABLE_IN_LIMITED_PROXY"
    elif complete_below == 0 and rolling_below == 0:
        screen_state = "NOT_REJECTED_BY_LIMITED_PRICE_PROXY_SCREEN_ONLY"
    else:
        screen_state = "REJECTED_BY_LIMITED_PRICE_PROXY_SCREEN"
    return {
        "variant_id": variant_id,
        "settings": {
            "target_weights": {code: float(target[code]) for code in target.index},
            "scheduled_review_months": list(review_months),
            "effective_timing": "following common session at reported open",
            "illustrative_one_way_bps": float(one_way_bps),
        },
        "metrics": {
            "initial_decision_session": initial_decision.date().isoformat(),
            "initial_effective_session": initial_effective.date().isoformat(),
            "terminal_session": nav.index[-1].date().isoformat(),
            "proxy_nav_observations": int(len(nav)),
            "final_unitized_market_price_proxy_value": float(nav.iloc[-1]),
            "annualized_market_price_proxy_change_after_illustrative_cost": float(nav.iloc[-1] ** (365.25 / elapsed_days) - 1.0),
            "annualized_market_price_proxy_volatility": float(daily_changes.std(ddof=1) * math.sqrt(252.0)),
            "maximum_drawdown_detail": drawdown_details(nav),
            "worst_one_session_proxy_change": loss_window(nav, 1),
            "worst_twenty_session_proxy_change": loss_window(nav, 20),
            "scheduled_rebalance_count": sum(event["event_type"] == "scheduled_rebalance" for event in events),
            "aggregate_one_way_turnover_including_initial_entry": total_turnover,
            "illustrative_cost_arithmetic_sum_of_pretrade_nav_fractions": total_cost_fraction,
            "initial_entry_illustrative_cost_fraction": initial_cost,
            "complete_calendar_years": years,
            "complete_calendar_year_summary": {
                "count": len(complete_years),
                "at_or_above_5pct_count": len(complete_years) - complete_below,
                "below_5pct_count": complete_below,
            },
            "rolling_five_calendar_year": rolling,
            "terminal_proxy_weights": {code: float(weights.iloc[-1][code]) for code in target.index},
            "limited_price_proxy_hurdle_screen": screen_state,
        },
        "events": events,
    }


def result_summary(result: dict[str, Any]) -> dict[str, Any]:
    metrics = result["metrics"]
    rolling = metrics["rolling_five_calendar_year"]
    return {
        "variant_id": result["variant_id"],
        "settings": result["settings"],
        "annualized_market_price_proxy_change_after_illustrative_cost": metrics[
            "annualized_market_price_proxy_change_after_illustrative_cost"
        ],
        "maximum_drawdown": metrics["maximum_drawdown_detail"]["maximum_drawdown"],
        "complete_calendar_year_below_5pct_count": metrics["complete_calendar_year_summary"]["below_5pct_count"],
        "complete_calendar_year_count": metrics["complete_calendar_year_summary"]["count"],
        "rolling_five_year_below_5pct_count": rolling.get("below_5pct_count"),
        "rolling_five_year_count": rolling.get("window_count"),
        "limited_price_proxy_hurdle_screen": metrics["limited_price_proxy_hurdle_screen"],
    }


def build_result() -> dict[str, Any]:
    protocol, codes, base_target = load_protocol()
    opens, closes, source_info = validate_and_load_source(protocol, codes)
    base = simulate_variant(
        opens,
        closes,
        base_target,
        tuple(int(month) for month in protocol["candidate"]["rebalance_months"]),
        float(protocol["illustrative_cost"]["base_one_way_bps"]),
        "base",
    )
    mutations: list[dict[str, Any]] = []
    for mutation in protocol["mutations"]:
        mutation_id = str(mutation["id"])
        mutation_target = assert_weight_vector(mutation["target_weights"], codes, mutation_id)
        result = simulate_variant(
            opens,
            closes,
            mutation_target,
            tuple(int(month) for month in mutation["rebalance_months"]),
            float(mutation["one_way_bps"]),
            mutation_id,
        )
        mutations.append(result)

    base_metrics = base["metrics"]
    base_rolling = base_metrics["rolling_five_calendar_year"]
    low_equity_summary = next(item for item in mutations if item["variant_id"] == "low_equity_30")
    high_equity_summary = next(item for item in mutations if item["variant_id"] == "high_equity_50")
    stress_results = [
        {
            "scenario": "Observed maximum drawdown in the limited market-price proxy",
            "assumption": "The fixed C30 base vector is mechanically rebalanced at next-session reported opens with a 20 bp illustrative turnover load; unadjusted-or-undisclosed close prices stand in for marks.",
            "impact": base_metrics["maximum_drawdown_detail"],
            "boundary": "This is not an investor drawdown, execution loss, or bound on future loss.",
        },
        {
            "scenario": "Illustrative simultaneous 10 percent gap in non-money sleeves",
            "assumption": "510300, 510880, 511010, and 518880 each fall 10 percent before any scheduled rebalance; 511990 is unchanged; no price limit, halt, spread, cost, tax, or recovery is modelled.",
            "impact": {
                "arithmetic_base_weight_loss": -float(
                    base_target["510300"] + base_target["510880"] + base_target["511010"] + base_target["518880"]
                ) * 0.10,
                "meaning": "A one-period arithmetic sensitivity only, using target weights rather than a forecast or a loss cap.",
            },
            "boundary": "Actual gaps, correlations, price limits, suspension, liquidity and ability to exit are unknown; loss cannot be bounded from this source.",
        },
        {
            "scenario": "Allocation mutation directional exposure check",
            "assumption": "Compare the frozen low-equity and high-equity mutations, neither selected as a winner, under their own 20 bp semiannual proxy arithmetic.",
            "impact": {
                "low_equity_30_maximum_drawdown": low_equity_summary["metrics"]["maximum_drawdown_detail"]["maximum_drawdown"],
                "high_equity_50_maximum_drawdown": high_equity_summary["metrics"]["maximum_drawdown_detail"]["maximum_drawdown"],
            },
            "boundary": "A finite set of historical proxy variations cannot establish correlation, capacity, a risk budget, or future protection.",
        },
        {
            "scenario": "Limit-down, suspension, and no-fill stress",
            "assumption": "None may be inferred from retained daily OHLCV rows because the inputs have no product status, price-limit, order-book, depth, or execution record.",
            "impact": "UNAVAILABLE: inability to trade, delayed rebalancing, and loss amplification cannot be quantified from this source.",
            "boundary": "Do not assume a daily close, a next-session open, or an indicated target can be filled during a stressed market.",
        },
    ]
    formal_status = "NOT_ADJUDICABLE"
    limited_screen = base_metrics["limited_price_proxy_hurdle_screen"]
    result = {
        "schema_version": "d5pt_c30_etf_candidate_rule_and_diagnostic.v1",
        "artifact_id": "D5PT-C30-ETF-LAB-v1",
        "as_of": opens.index[-1].date().isoformat(),
        "artifact_class": "exploratory_retrospective_market_price_proxy",
        "research_only": True,
        "external_investment_action_authorized": False,
        "formal_decision_eligible": False,
        "portfolio_q": 0,
        "protocol": {
            "path": repo_path(PROTOCOL_PATH),
            "sha256": sha256_file(PROTOCOL_PATH),
            "markdown_mirror_path": repo_path(PROTOCOL_MD),
            "markdown_mirror_sha256": sha256_file(PROTOCOL_MD),
            "recorded_before_calculation": protocol["recorded_before_calculation"],
            "status": protocol["status"],
            "predeclared_no_winner_selection": True,
        },
        "data_quality": {
            **source_info,
            "degradation": "Retrospective official daily market-price observations only; no point-in-time availability, adjustment/total-return, distribution/event, quote, liquidity, costs, execution, settlement, tax, account, or capacity evidence.",
        },
        "candidate_action_card": {
            "status": "research_candidate_not_admitted_not_a_live_action_card",
            "name": protocol["candidate"]["name"],
            "exact_products_and_weights": [
                {
                    "code": code,
                    "target_weight": float(base_target[code]),
                    "dated_p01_role": {
                        "510300": "broad China equity; one half of equity sleeve",
                        "510880": "dividend-style China equity; other half of equity sleeve",
                        "511010": "five-year government-bond exposure",
                        "518880": "domestic gold-spot-related exposure",
                        "511990": "money-market-tool exposure; not account cash",
                    }[code],
                }
                for code in codes
            ],
            "base_action": "After the final common close in June and December, retain the frozen vector and model any rebalance no earlier than the following common-session reported open. It does not replace or modify R01's monthly dynamic paper rule.",
            "forward_paper_only_order_protection": protocol["forward_paper_order_protection"],
            "no_action_conditions": protocol["no_action_conditions"],
            "prohibited": [
                "automatic ETF substitution",
                "assumed fill or synthetic close fill",
                "same-session close execution",
                "leverage, borrowing, short sale, or derivatives",
                "use of unsettled proceeds or same-day equity-ETF resale assumptions",
                "external investment action",
            ],
        },
        "calculation_design": {
            "timing": protocol["timing"],
            "illustrative_cost": protocol["illustrative_cost"],
            "market_price_proxy_only": True,
            "not_modelled": [
                "total return or distributions",
                "fund events or corporate actions",
                "NAV or IOPV history",
                "bid/ask, depth, market impact, actual fee, tax, or capacity",
                "halt, price limit, partial fill, no fill, settlement, or account constraints",
                "100-share lot rounding and cash residuals",
            ],
        },
        "base_diagnostic": base,
        "predeclared_mutations": mutations,
        "mutation_summary_no_winner_selection": [result_summary(base), *[result_summary(item) for item in mutations]],
        "hurdle_assessment": {
            "research_hurdle": protocol["research_hurdle"],
            "base_limited_market_price_proxy_screen": limited_screen,
            "formal_total_return_and_execution_hurdle_verdict": formal_status,
            "meaning": "A 5 percent guarantee is not established. A passing market-price-proxy screen would not authorize use; the actual base proxy screen is reported only as a constrained diagnostic.",
        },
        "scenario_results": stress_results,
        "risk_model": {
            "role": "quant-risk-modeler",
            "risk_model_status": "VETO",
            "conclusion": "The fixed five-ETF price proxy may describe a transparent historical arithmetic path, but missing total-return, liquidity, execution, portfolio-loss-budget and forward-paper inputs prevent a bounded-loss or personally operable-strategy conclusion.",
            "exposure_findings": [
                "Single-name target concentration reaches 40 percent in 511010; the base also has 40 percent domestic equity exposure split across broad and dividend styles, which remain correlated equity risk rather than proven diversification.",
                "The base has 40 percent five-year Treasury-rate exposure, 10 percent domestic-gold-related exposure, and 10 percent money-market-tool exposure; none is a capital, liquidity, or correlation guarantee.",
                "The five retained inputs have common daily price rows, but no contemporaneous quote/depth, halt, price-limit, capacity, or account-access record.",
            ],
            "scenario_results": [
                "Historical proxy maximum drawdown and the frozen 10 percent simultaneous-gap arithmetic are reported above; neither bounds actual losses.",
                "A missing portfolio value, risk budget, position limit, user liquidity need, and implementation ledger makes dollar loss, concentration tolerance, and capacity unavailable.",
            ],
            "model_limits": [
                "SSE historical bars were captured retrospectively and do not establish point-in-time availability or a documented adjustment basis.",
                "Market-price proxies are not investor total returns and cannot prove costs, taxes, bid/ask, fills, settlement, lots, account eligibility, or personal operability.",
                "The mutations are a finite robustness family, not out-of-sample proof, alpha evidence, correlation estimate, VaR, or capacity model.",
            ],
            "required_controls": [
                "Keep status at research-only / portfolio_q=0; do not use the proxy to authorize an external action.",
                "Obtain a rights-cleared point-in-time total-return and fund-event ledger, with an execution/cost/tax/settlement ledger, before testing the 5 percent hurdle formally.",
                "Before any future paper action, record current product status, account/appropriateness, bid/ask/depth, IOPV where applicable, lots, fees/taxes, settlement, and no-fill outcomes; fail closed to no_action.",
                "Define the actual portfolio value, loss budget, concentration limits, liquidity needs, and a six-month forward paper ledger before any review of operability.",
            ],
            "confidence": 94,
            "degradation": "Retrospective official market-price input only; actual total-return and execution data are absent.",
        },
        "runtime_provenance": {
            "script_path": repo_path(Path(__file__).resolve()),
            "script_sha256": sha256_file(Path(__file__).resolve()),
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "pandas_version": pd.__version__,
            "numpy_version": np.__version__,
            "command": "PYTHONDONTWRITEBYTECODE=1 .venv/bin/python workspace/research/domestic-5pct-target-paper-strategy-20260815/tools/C30_run_etf_candidate_lab.py --write",
        },
    }
    return result


def percent(value: float | None, precision: int = 2) -> str:
    if value is None:
        return "—"
    return f"{value * 100:.{precision}f}%"


def render_markdown(result: dict[str, Any]) -> str:
    base = result["base_diagnostic"]
    metrics = base["metrics"]
    years = metrics["complete_calendar_years"]
    rolling = metrics["rolling_five_calendar_year"]
    candidate = result["candidate_action_card"]
    year_rows = "\n".join(
        "| {year} | {start} | {end} | {complete} | {change} | {screen} |".format(
            year=row["year"],
            start=row["start"],
            end=row["end"],
            complete="是" if row["complete_calendar_year"] else "否",
            change=percent(row["market_price_proxy_change_after_illustrative_cost"]),
            screen=("是" if row["at_or_above_5pct_limited_proxy_screen"] else "否")
            if row["complete_calendar_year"]
            else "—",
        )
        for row in years
    )
    product_rows = "\n".join(
        f"| `{row['code']}` | {row['dated_p01_role']} | {row['target_weight']:.0%} |"
        for row in candidate["exact_products_and_weights"]
    )
    mutation_rows = "\n".join(
        "| {id} | {annualized} | {drawdown} | {calendar_below}/{calendar_count} | {rolling_below}/{rolling_count} | {screen} |".format(
            id=row["variant_id"],
            annualized=percent(row["annualized_market_price_proxy_change_after_illustrative_cost"]),
            drawdown=percent(row["maximum_drawdown"]),
            calendar_below=row["complete_calendar_year_below_5pct_count"],
            calendar_count=row["complete_calendar_year_count"],
            rolling_below=row["rolling_five_year_below_5pct_count"],
            rolling_count=row["rolling_five_year_count"],
            screen=row["limited_price_proxy_hurdle_screen"],
        )
        for row in result["mutation_summary_no_winner_selection"]
    )
    rolling_text = (
        "没有形成完整的月末滚动五年窗口。"
        if rolling["window_count"] == 0
        else (
            f"月末滚动五年端点共 {rolling['window_count']} 个，其中 "
            f"{rolling['at_or_above_5pct_count']} 个不低于 5%、{rolling['below_5pct_count']} 个低于 5%，"
            f"年化市场价代理区间为 "
            f"{percent(rolling['minimum_annualized_market_price_proxy_change_after_illustrative_cost'])} 至 "
            f"{percent(rolling['maximum_annualized_market_price_proxy_change_after_illustrative_cost'])}。"
        )
    )
    drawdown = metrics["maximum_drawdown_detail"]
    one_day = metrics["worst_one_session_proxy_change"]
    twenty_day = metrics["worst_twenty_session_proxy_change"]
    veto = result["risk_model"]
    no_actions = "\n".join(f"- {item}" for item in candidate["no_action_conditions"])
    required_controls = "\n".join(f"- {item}" for item in veto["required_controls"])
    return f"""# C30：五 ETF 静态候选规则与市场价代理诊断

- 工件 ID：`{result['artifact_id']}`
- 截止日：`{result['as_of']}`
- 角色：`quant-risk-modeler`
- 风险模型状态：`VETO`
- 当前处置：`research_only`、`portfolio_q=0`、`external_investment_action_authorized=false`。
- 结论：C30 形成了明确、低频、五只 ETF 的纸面研究候选；但公开日线只能支持受限市场价代理算术，不能证明投资者总回报、成交、个人可操作性或稳定 5%，因此不准入、更不授权任何实际投资动作。

## 1. 预先冻结的候选与动作卡

本计算前冻结的协议：[c30_etf_candidate_protocol_20260815.md](c30_etf_candidate_protocol_20260815.md)。其哈希为 `{result['protocol']['sha256']}`；候选由经济暴露预算确定，**未按本次或既有历史得分选出**。

| 产品 | P01 中的角色 | 固定目标 |
|---|---|---:|
{product_rows}

经济意图是 40% 国内权益、40% 五年期国债相关暴露、10% 国内黄金相关暴露和 10% 货币市场工具暴露；它不是相关性、流动性、避险、分红、现金流或 5% 结果的承诺。`511990` 是 ETF 暴露，不是账户现金。

**冻结动作：** 在每年六月和十二月最后一个共同交易日收盘后记录已有漂移权重；最早于下一共同交易日的开盘价代理恢复上述固定权重。计算没有使用市场信号、择时、排名或事后换产品。该 C30 静态诊断**不替代、不修改** R01 的月度动态纸面动作卡。

## 2. 严格的次交易日代理时序与成本边界

若决策日为 `D`，有效日为 `E`，现有持仓先承受 `D` 收盘至 `E` 开盘的市场价代理变化；仅在 `E` 开盘时计算目标交易与成本；新目标才承受 `E` 开盘至收盘变化。首次建仓同样在共同面板第一天收盘之后的下一共同开盘。每条事件均通过严格的 `D < E` 断言，禁止同日收盘成交和同一根 K 线前视。

基准成本是每次单边换手 `20 bp` 的机械算术载荷（首次 100% 入场也计入），并非已观察到的佣金、税费、点差、冲击、基金费用、结算或成交。原始输入为回溯抓取的上交所日线，来源清单与哈希见 `{result['data_quality']['manifest_path']}`；共同面板为 {result['data_quality']['common_panel']['first_common_session']} 至 {result['data_quality']['common_panel']['last_common_session']} 的 {result['data_quality']['common_panel']['observations']} 个交易日。

**降级说明：** 这些输入没有点时点可得性、复权/总回报、分配和基金事件账本，也没有买卖价、深度、IOPV 历史、停复牌、涨跌停、费用税费、成交、结算、账户或容量资料。因此下列数值是“未确认调整口径的市场价代理”，不是总回报或可执行净回报。

## 3. 基准市场价代理结果（不可当作总回报）

| 指标 | 受限代理值 |
|---|---:|
| 首次有效日 / 终止日 | {metrics['initial_effective_session']} / {metrics['terminal_session']} |
| 期末单位值 | {metrics['final_unitized_market_price_proxy_value']:.4f} |
| 年化市场价代理变化（含示例成本） | {percent(metrics['annualized_market_price_proxy_change_after_illustrative_cost'])} |
| 年化日度代理波动 | {percent(metrics['annualized_market_price_proxy_volatility'])} |
| 最大回撤代理 | {percent(drawdown['maximum_drawdown'])}（峰值 {drawdown['peak_date']}，谷值 {drawdown['trough_date']}） |
| 最差单交易日代理变化 | {percent(one_day['return'])}（{one_day['start']} 至 {one_day['end']}） |
| 最差 20 交易日代理变化 | {percent(twenty_day['return'])}（{twenty_day['start']} 至 {twenty_day['end']}） |
| 调仓次数 / 单边换手（含首次） | {metrics['scheduled_rebalance_count']} / {metrics['aggregate_one_way_turnover_including_initial_entry']:.4f} |
| 累计示例成本分数算术和 | {percent(metrics['illustrative_cost_arithmetic_sum_of_pretrade_nav_fractions'])} |
| 受限 5% 价格代理筛查 | `{metrics['limited_price_proxy_hurdle_screen']}` |

### 完整自然年

| 年份 | 首个 / 最后代理点 | 完整 | 市场价代理变化（含示例成本） | ≥5%（仅受限筛查） |
|---:|---|:---:|---:|:---:|
{year_rows}

### 月末滚动五年

{rolling_text}

“≥5%”只描述这个代理数值与研究线的关系，绝不表示稳定、保底、未来预测或个人净收益。若任一完整年度或滚动五年窗口低于 5%，协议将其记为**有限市场价代理筛查的拒绝**；即便全数高于 5%，也不能绕过总回报和执行缺口。

## 4. 预先声明的鲁棒性 / 突变族（不选优）

以下全部是在看结果前冻结的离散变体。`base` 始终是候选，其他结果仅显示对权重、日历和成本算术的依赖；不得从中挑选年化最高者、回撤最低者或“幸存者”。

| 变体 | 年化市场价代理变化 | 最大回撤 | 完整年度 <5% | 滚动五年 <5% | 有限筛查 |
|---|---:|---:|---:|---:|---|
{mutation_rows}

该族没有估计 alpha、相关性、VaR、容量或未来回报；它也不是干净样本外研究，因为协议是在已有公开观察之后形成。

## 5. 场景与无法界定的损失

1. **历史最大回撤代理：** 依据基准机械路径为 {percent(drawdown['maximum_drawdown'])}。这不是投资者回撤，也不是未来损失上限。
2. **同步 10% 风险腿跳空的纯算术敏感性：** 若 510300、510880、511010 与 518880 都在任何再平衡前同步下跌 10%，而 511990 不变，按目标权重的单期算术损失为 {percent(result['scenario_results'][1]['impact']['arithmetic_base_weight_loss'])}。价格限制、停牌、流动性、关联性、点差和退出能力均未被假设为已知。
3. **权重突变方向性检查：** `low_equity_30` 与 `high_equity_50` 的最大回撤代理分别为 {percent(result['scenario_results'][2]['impact']['low_equity_30_maximum_drawdown'])} 与 {percent(result['scenario_results'][2]['impact']['high_equity_50_maximum_drawdown'])}；这些不证明更低或更高权益具有稳定风险优势。
4. **跌停、停牌与未成交压力：** `UNAVAILABLE`。留存日线没有产品状态、涨跌停、订单簿、深度或实际成交记录，不能计算无法调仓或无法退出时的损失扩大；不得把日收盘或次日开盘代理当作可成交事实。

缺失真实组合规模、损失预算、流动性需求、仓位上限、可成交价格与未成交账本，故无法把这些百分比转换为可界定的个人损失或容量结论。

## 6. 纸面操作的 `no_action` 闸门

历史代理没有测试以下分支。未来任何纸面动作必须先获得当前正式文件、状态、账户/适当性、可用资金和份额、费用税费、结算、带时间戳的报价与深度，以及适用的 IOPV。买入只在 `ask ≤ IOPV × 1.003`、卖出只在 `bid ≥ IOPV × 0.997` 时才可提交限价纸面订单；100 份最小申报单位和 0.001 元最小变动只是需要再次核验的类别参考。

{no_actions}

任何失败都保持既有纸面持仓并记录 `no_action`；不得自动替换 ETF、假设成交、用收盘价补写成交、预支未结算款或把类别性 T+0/T+1 提示当成具体账户事实。

## 7. 量化风险闸门

**Role:** quant-risk-modeler  
**Risk Model Status:** VETO  
**Conclusion:** {veto['conclusion']}  
**Confidence:** {veto['confidence']} / 100  
**Degradation:** {veto['degradation']}

**Exposure Findings:**

- 单一代码 `511010` 的目标集中度为 40%；40% 权益中的两只产品均为中国股票风险来源，不可视为已证明的低相关分散。
- 债券、黄金与货币市场 ETF 各有利率、估值、信用、折溢价、流动性和产品事件风险；本文件不把它们称为无风险或自动避险。
- 公开日价代理没有任何盘口、容量或实际交易记录，因此不能作为交易许可。

**Required Controls:**

{required_controls}

**最终边界：** 5% 不是保证；本工件不授权实际投资、下单、开户、申购、赎回或任何外部行动。
"""


def write_outputs(result: dict[str, Any]) -> None:
    OUTPUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(result), encoding="utf-8")


def verify_outputs(result: dict[str, Any]) -> None:
    if not OUTPUT_JSON.is_file() or not OUTPUT_MD.is_file():
        raise FileNotFoundError("C30 derived outputs are absent; run --write first")
    expected_json = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    expected_md = render_markdown(result)
    if OUTPUT_JSON.read_text(encoding="utf-8") != expected_json:
        raise AssertionError("C30 JSON output differs from a fresh recomputation")
    if OUTPUT_MD.read_text(encoding="utf-8") != expected_md:
        raise AssertionError("C30 Markdown output differs from a fresh recomputation")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--write", action="store_true", help="write the C30 Markdown and JSON artifacts")
    action.add_argument("--verify", action="store_true", help="recompute and require byte-identical C30 artifacts")
    args = parser.parse_args()
    result = build_result()
    if args.verify:
        verify_outputs(result)
        print("PASS: C30 ETF candidate diagnostic recomputes byte-identically from the frozen protocol and SSE source hashes.")
    else:
        write_outputs(result)
        print(f"WROTE: {repo_path(OUTPUT_MD)}")
        print(f"WROTE: {repo_path(OUTPUT_JSON)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

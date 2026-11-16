#!/usr/bin/env python3
"""Recompute the C34 dynamic ETF price-proxy diagnostic from frozen inputs.

The calculation reads a protocol recorded before computation and five retained
SSE daily-price responses. It is a research-only proxy: it does not connect to
an account, fetch fresh data, submit an order, or represent total return or a
fill.
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
PROTOCOL_JSON = ANALYSIS_DIR / f"c34_dual_horizon_inverse_vol_etf_protocol_{DATE_TAG}.json"
PROTOCOL_MD = ANALYSIS_DIR / f"c34_dual_horizon_inverse_vol_etf_protocol_{DATE_TAG}.md"
OUTPUT_JSON = ANALYSIS_DIR / f"c34_dual_horizon_inverse_vol_etf_candidate_{DATE_TAG}.json"
OUTPUT_MD = ANALYSIS_DIR / f"c34_dual_horizon_inverse_vol_etf_candidate_{DATE_TAG}.md"
HURDLE = 0.05
EPSILON = 1e-12


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(REPO_ROOT))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_protocol() -> tuple[dict[str, Any], tuple[str, ...]]:
    if not PROTOCOL_JSON.is_file() or not PROTOCOL_MD.is_file():
        raise FileNotFoundError("C34 protocol JSON and Markdown must exist before calculation")
    protocol = read_json(PROTOCOL_JSON)
    if protocol.get("status") != "frozen_for_research_only_calculation":
        raise ValueError("C34 protocol is not frozen for research-only calculation")
    if protocol.get("external_orders") is not False:
        raise ValueError("C34 protocol must prohibit external orders")
    codes = tuple(str(code) for code in protocol["source"]["allowed_codes"])
    expected_codes = ("510300", "510880", "511010", "518880", "511990")
    if codes != expected_codes:
        raise ValueError("C34 exact five-code universe differs from the frozen protocol")
    base = protocol["base_rule"]
    if base["score_horizons_common_observations"] != [126, 252]:
        raise ValueError("C34 base score horizons differ from the frozen protocol")
    if int(base["realized_volatility"]["return_observations"]) != 60:
        raise ValueError("C34 base realized-volatility lookback differs from the frozen protocol")
    if float(protocol["illustrative_cost"]["one_way_bps"]) != 20.0:
        raise ValueError("C34 illustrative cost differs from the frozen protocol")
    mirror = PROTOCOL_MD.read_text(encoding="utf-8")
    for marker in ("C34 Dual-Horizon", "510300", "510880", "511010", "518880", "511990", "126", "252", "60"):
        if marker not in mirror:
            raise ValueError(f"C34 protocol Markdown mirror lacks frozen marker: {marker}")
    return protocol, codes


def load_source(protocol: dict[str, Any], codes: tuple[str, ...]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    manifest_path = REPO_ROOT / str(protocol["source"]["manifest_path"])
    if not manifest_path.is_file():
        raise FileNotFoundError(f"C34 source manifest is missing: {manifest_path}")
    manifest = read_json(manifest_path)
    by_code = {str(row.get("code")): row for row in manifest.get("files", [])}
    if not set(codes).issubset(by_code):
        raise ValueError("C34 source manifest lacks a required code")
    open_series: dict[str, pd.Series] = {}
    close_series: dict[str, pd.Series] = {}
    raw_records: list[dict[str, Any]] = []
    for code in codes:
        source = by_code[code]
        path = REPO_ROOT / str(source["path"])
        if not path.is_file():
            raise FileNotFoundError(f"C34 retained source is missing: {path}")
        observed_hash = sha256_file(path)
        observed_bytes = path.stat().st_size
        if observed_hash != source.get("sha256") or observed_bytes != int(source.get("bytes", -1)):
            raise ValueError(f"C34 retained source failed manifest validation: {code}")
        text = path.read_text(encoding="utf-8").strip()
        match = re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*\((.*)\)", text, flags=re.DOTALL)
        if not match:
            raise ValueError(f"C34 unexpected JSONP syntax: {code}")
        payload = json.loads(match.group(1))
        if str(payload.get("code")) != code or int(payload.get("begin", -1)) != 0:
            raise ValueError(f"C34 source identity mismatch: {code}")
        rows = payload.get("kline")
        if not isinstance(rows, list) or not rows:
            raise ValueError(f"C34 source has no rows: {code}")
        if len(rows) != int(payload.get("total", -1)) or int(payload.get("end", -1)) != len(rows):
            raise ValueError(f"C34 source response is incomplete: {code}")
        frame = pd.DataFrame(rows, columns=["date", "open", "high", "low", "close", "volume"])
        numeric_dates = pd.to_numeric(frame["date"], errors="coerce")
        frame["date"] = pd.to_datetime(
            numeric_dates.round().astype("Int64").astype(str), format="%Y%m%d", errors="coerce"
        )
        frame["open"] = pd.to_numeric(frame["open"], errors="coerce")
        frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
        frame = frame.dropna(subset=["date", "open", "close"]).sort_values("date", kind="stable")
        if frame.empty or frame["date"].duplicated().any() or (frame[["open", "close"]] <= 0).any().any():
            raise ValueError(f"C34 invalid date/open/close rows: {code}")
        open_series[code] = frame.set_index("date")["open"]
        close_series[code] = frame.set_index("date")["close"]
        raw_records.append(
            {
                "code": code,
                "path": str(source["path"]),
                "bytes": observed_bytes,
                "sha256": observed_hash,
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
    if len(opens) < 254 or not opens.index.equals(closes.index) or opens.index.duplicated().any():
        raise ValueError("C34 common panel is invalid or too short")
    if (opens <= 0).any().any() or (closes <= 0).any().any():
        raise ValueError("C34 common panel has non-positive prices")
    info = {
        "manifest_path": repo_path(manifest_path),
        "manifest_sha256": sha256_file(manifest_path),
        "quality": protocol["source"]["quality"],
        "price_basis": protocol["source"]["price_basis"],
        "raw_responses": raw_records,
        "common_panel": {
            "observations": int(len(opens)),
            "first_common_session": opens.index[0].date().isoformat(),
            "last_common_session": opens.index[-1].date().isoformat(),
            "excluded_rows_after_common_intersection": {
                code: int(by_code[code]["response_rows"]) - int(len(opens)) for code in codes
            },
        },
    }
    return opens, closes, info


def final_month_positions(index: pd.DatetimeIndex) -> set[int]:
    return {
        position
        for position in range(1, len(index))
        if index[position - 1].month != index[position].month
    }


def daily_sleeve_returns(closes: pd.DataFrame) -> pd.DataFrame:
    daily = closes.pct_change()
    result = pd.DataFrame(index=closes.index)
    result["equity"] = 0.5 * daily["510300"] + 0.5 * daily["510880"]
    result["bond"] = daily["511010"]
    result["gold"] = daily["518880"]
    result["fallback"] = daily["511990"]
    return result


def sleeve_horizon_return(closes: pd.DataFrame, position: int, horizon: int, sleeve: str) -> float:
    if position < horizon:
        return math.nan
    if sleeve == "equity":
        left = float(closes.iloc[position]["510300"] / closes.iloc[position - horizon]["510300"] - 1.0)
        right = float(closes.iloc[position]["510880"] / closes.iloc[position - horizon]["510880"] - 1.0)
        return 0.5 * left + 0.5 * right
    code = {"bond": "511010", "gold": "518880", "fallback": "511990"}[sleeve]
    return float(closes.iloc[position][code] / closes.iloc[position - horizon][code] - 1.0)


def signal_target(
    closes: pd.DataFrame,
    sleeve_daily_returns: pd.DataFrame,
    position: int,
    score_horizons: tuple[int, ...],
    volatility_observations: int,
    eligibility_threshold_excess: float,
) -> dict[str, Any]:
    sleeves = ("equity", "bond", "gold", "fallback")
    minimum_position = max(max(score_horizons), volatility_observations)
    if position < minimum_position:
        return {
            "signal_state": "warmup_fallback",
            "score_horizons": list(score_horizons),
            "scores": {sleeve: None for sleeve in sleeves},
            "realized_volatility": {sleeve: None for sleeve in ("equity", "bond", "gold")},
            "eligible_sleeves": [],
            "target_weights": {"510300": 0.0, "510880": 0.0, "511010": 0.0, "518880": 0.0, "511990": 1.0},
        }
    horizon_returns: dict[str, list[float]] = {
        sleeve: [sleeve_horizon_return(closes, position, horizon, sleeve) for horizon in score_horizons]
        for sleeve in sleeves
    }
    scores = {sleeve: float(np.mean(values)) for sleeve, values in horizon_returns.items()}
    if not all(math.isfinite(value) for value in scores.values()):
        return {
            "signal_state": "invalid_no_action",
            "score_horizons": list(score_horizons),
            "scores": scores,
            "realized_volatility": {sleeve: None for sleeve in ("equity", "bond", "gold")},
            "eligible_sleeves": [],
            "target_weights": None,
        }
    eligible = [
        sleeve
        for sleeve in ("equity", "bond", "gold")
        if scores[sleeve] > scores["fallback"] + eligibility_threshold_excess
    ]
    if not eligible:
        return {
            "signal_state": "no_active_risk_sleeve_fallback",
            "score_horizons": list(score_horizons),
            "horizon_returns": horizon_returns,
            "scores": scores,
            "realized_volatility": {sleeve: None for sleeve in ("equity", "bond", "gold")},
            "eligible_sleeves": [],
            "target_weights": {"510300": 0.0, "510880": 0.0, "511010": 0.0, "518880": 0.0, "511990": 1.0},
        }
    window = sleeve_daily_returns.iloc[position - volatility_observations + 1 : position + 1]
    realized_volatility: dict[str, float] = {}
    for sleeve in eligible:
        series = window[sleeve].dropna()
        if len(series) != volatility_observations:
            return {
                "signal_state": "invalid_no_action",
                "score_horizons": list(score_horizons),
                "horizon_returns": horizon_returns,
                "scores": scores,
                "realized_volatility": {name: None for name in ("equity", "bond", "gold")},
                "eligible_sleeves": eligible,
                "target_weights": None,
            }
        volatility = float(series.std(ddof=1))
        if not math.isfinite(volatility) or volatility <= 0:
            return {
                "signal_state": "invalid_no_action",
                "score_horizons": list(score_horizons),
                "horizon_returns": horizon_returns,
                "scores": scores,
                "realized_volatility": {name: None for name in ("equity", "bond", "gold")},
                "eligible_sleeves": eligible,
                "target_weights": None,
            }
        realized_volatility[sleeve] = volatility
    inverse = {sleeve: 1.0 / realized_volatility[sleeve] for sleeve in eligible}
    inverse_total = sum(inverse.values())
    active_weights = {sleeve: inverse[sleeve] / inverse_total for sleeve in eligible}
    target = {"510300": 0.0, "510880": 0.0, "511010": 0.0, "518880": 0.0, "511990": 0.0}
    if "equity" in active_weights:
        target["510300"] = 0.5 * active_weights["equity"]
        target["510880"] = 0.5 * active_weights["equity"]
    if "bond" in active_weights:
        target["511010"] = active_weights["bond"]
    if "gold" in active_weights:
        target["518880"] = active_weights["gold"]
    if abs(sum(target.values()) - 1.0) > EPSILON:
        raise AssertionError("C34 inverse-vol target does not sum to 1")
    volatility_with_missing = {name: realized_volatility.get(name) for name in ("equity", "bond", "gold")}
    return {
        "signal_state": "active_inverse_vol",
        "score_horizons": list(score_horizons),
        "horizon_returns": horizon_returns,
        "scores": scores,
        "realized_volatility": volatility_with_missing,
        "eligible_sleeves": eligible,
        "active_sleeve_weights": active_weights,
        "target_weights": target,
    }


def drawdown_detail(nav: pd.Series) -> dict[str, Any]:
    high = nav.cummax()
    drawdown = nav / high - 1.0
    trough = drawdown.idxmin()
    pre_trough = nav.loc[:trough]
    peak = pre_trough[pre_trough == pre_trough.max()].index[0]
    recovered = nav.loc[trough:]
    recovered = recovered[recovered >= float(nav.loc[peak])]
    return {
        "maximum_drawdown": float(drawdown.loc[trough]),
        "peak_date": peak.date().isoformat(),
        "trough_date": trough.date().isoformat(),
        "recovery_date": None if recovered.empty else recovered.index[0].date().isoformat(),
    }


def loss_window(nav: pd.Series, periods: int) -> dict[str, Any]:
    changes = (nav / nav.shift(periods) - 1.0).dropna()
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
            raise ValueError(f"C34 complete year lacks prior value: {year}")
        start_value = float(prior.iloc[-1]) if complete else float(group.iloc[0])
        change = float(group.iloc[-1] / start_value - 1.0)
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
    month_ends = [
        position
        for position, date in enumerate(nav.index)
        if position == len(nav.index) - 1 or nav.index[position + 1].month != date.month
    ]
    for position in month_ends:
        end = nav.index[position]
        start_candidates = nav.index[nav.index <= end - pd.DateOffset(years=5)]
        if len(start_candidates) == 0:
            continue
        start = start_candidates[-1]
        days = int((end - start).days)
        if days <= 0:
            continue
        annualized = float((nav.loc[end] / nav.loc[start]) ** (365.25 / days) - 1.0)
        rows.append(
            {
                "start": start.date().isoformat(),
                "end": end.date().isoformat(),
                "calendar_days": days,
                "annualized_market_price_proxy_change_after_illustrative_cost": annualized,
                "at_or_above_5pct_limited_proxy_screen": bool(annualized >= HURDLE),
            }
        )
    if not rows:
        return {
            "endpoint_frequency": "month_end_only",
            "window_count": 0,
            "at_or_above_5pct_count": 0,
            "below_5pct_count": 0,
            "rows": [],
            "warning": "No rolling five-calendar-year price-proxy endpoints.",
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
        "warning": "Overlapping endpoints are descriptive rather than independent and are not a total-return or execution test.",
    }


def period_summary(
    nav: pd.Series,
    calendar_years: list[dict[str, Any]],
    rolling: dict[str, Any],
    start_text: str,
    end_text: str,
    label: str,
) -> dict[str, Any]:
    start_bound = pd.Timestamp(start_text)
    end_bound = pd.Timestamp(end_text)
    baseline_dates = nav.index[nav.index <= start_bound]
    terminal_dates = nav.index[nav.index <= end_bound]
    if len(baseline_dates) == 0 or len(terminal_dates) == 0:
        return {
            "label": label,
            "requested_start": start_text,
            "requested_end": end_text,
            "status": "UNAVAILABLE",
            "reason": "No proxy NAV endpoints cover the requested period.",
        }
    baseline = baseline_dates[-1]
    terminal = terminal_dates[-1]
    elapsed_days = int((terminal - baseline).days)
    if elapsed_days <= 0:
        return {
            "label": label,
            "requested_start": start_text,
            "requested_end": end_text,
            "status": "UNAVAILABLE",
            "reason": "Requested period has no elapsed proxy sessions.",
        }
    eligible_years = [
        row
        for row in calendar_years
        if row["complete_calendar_year"]
        and pd.Timestamp(row["start"]) > start_bound
        and pd.Timestamp(row["end"]) <= end_bound
    ]
    eligible_rolling = [
        row
        for row in rolling["rows"]
        if pd.Timestamp(row["start"]) >= start_bound and pd.Timestamp(row["end"]) <= end_bound
    ]
    year_below = sum(not bool(row["at_or_above_5pct_limited_proxy_screen"]) for row in eligible_years)
    rolling_below = sum(not bool(row["at_or_above_5pct_limited_proxy_screen"]) for row in eligible_rolling)
    if not eligible_years or not eligible_rolling:
        screen = "NOT_EVALUABLE_IN_LIMITED_PROXY"
    elif year_below == 0 and rolling_below == 0:
        screen = "NOT_REJECTED_BY_LIMITED_PRICE_PROXY_SCREEN_ONLY"
    else:
        screen = "REJECTED_BY_LIMITED_PRICE_PROXY_SCREEN"
    return {
        "label": label,
        "requested_start": start_text,
        "requested_end": end_text,
        "baseline_proxy_date": baseline.date().isoformat(),
        "terminal_proxy_date": terminal.date().isoformat(),
        "annualized_market_price_proxy_change_after_illustrative_cost": float(
            (nav.loc[terminal] / nav.loc[baseline]) ** (365.25 / elapsed_days) - 1.0
        ),
        "complete_calendar_year_count": len(eligible_years),
        "complete_calendar_year_below_5pct_count": year_below,
        "complete_calendar_years": eligible_years,
        "rolling_five_year_endpoint_count": len(eligible_rolling),
        "rolling_five_year_below_5pct_count": rolling_below,
        "rolling_five_year_endpoints": eligible_rolling,
        "limited_price_proxy_hurdle_screen": screen,
    }


def summary_without_rows(period: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "label",
        "requested_start",
        "requested_end",
        "baseline_proxy_date",
        "terminal_proxy_date",
        "annualized_market_price_proxy_change_after_illustrative_cost",
        "complete_calendar_year_count",
        "complete_calendar_year_below_5pct_count",
        "rolling_five_year_endpoint_count",
        "rolling_five_year_below_5pct_count",
        "limited_price_proxy_hurdle_screen",
        "status",
        "reason",
    )
    return {field: period[field] for field in fields if field in period}


def simulate_variant(
    opens: pd.DataFrame,
    closes: pd.DataFrame,
    score_horizons: tuple[int, ...],
    volatility_observations: int,
    eligibility_threshold_excess: float,
    one_way_bps: float,
    variant_id: str,
    include_events: bool,
) -> dict[str, Any]:
    if not score_horizons or min(score_horizons) <= 0 or volatility_observations <= 1:
        raise ValueError(f"C34 {variant_id}: invalid frozen lookback")
    if one_way_bps < 0:
        raise ValueError(f"C34 {variant_id}: invalid illustrative cost")
    index = closes.index
    codes = tuple(str(code) for code in closes.columns)
    if tuple(opens.columns) != codes or len(index) < max(score_horizons) + 2:
        raise ValueError(f"C34 {variant_id}: source panel and parameters do not align")
    daily = daily_sleeve_returns(closes)
    cost_rate = one_way_bps / 10_000.0
    fallback_target = pd.Series({code: 0.0 for code in codes}, dtype=float)
    fallback_target["511990"] = 1.0
    initial_decision = index[0]
    initial_effective = index[1]
    values = fallback_target * (1.0 - cost_rate)
    values = values * (closes.iloc[1] / opens.iloc[1])
    nav_rows: list[tuple[pd.Timestamp, float]] = [(initial_effective, float(values.sum()))]
    weight_rows: list[tuple[Any, ...]] = [
        (initial_effective, *(float(values[code] / values.sum()) for code in codes))
    ]
    events: list[dict[str, Any]] = [
        {
            "event_type": "initial_warmup_fallback_entry",
            "decision_session": initial_decision.date().isoformat(),
            "effective_session": initial_effective.date().isoformat(),
            "information_through": initial_decision.date().isoformat(),
            "signal_state": "warmup_fallback",
            "eligible_sleeves": [],
            "target_weights": {code: float(fallback_target[code]) for code in codes},
            "one_way_turnover": 1.0,
            "illustrative_cost_fraction_of_pretrade_proxy_value": cost_rate,
            "proxy_fill_status": "not_observed_market_price_proxy",
        }
    ]
    scheduled_effective_positions = final_month_positions(index)
    for position in range(2, len(index)):
        session = index[position]
        values = values * (opens.iloc[position] / closes.iloc[position - 1])
        if position in scheduled_effective_positions:
            decision_position = position - 1
            signal = signal_target(
                closes,
                daily,
                decision_position,
                score_horizons,
                volatility_observations,
                eligibility_threshold_excess,
            )
            pre_trade_value = float(values.sum())
            pre_trade_weights = values / pre_trade_value
            event: dict[str, Any] = {
                "event_type": "monthly_signal_and_target",
                "decision_session": index[decision_position].date().isoformat(),
                "effective_session": session.date().isoformat(),
                "information_through": index[decision_position].date().isoformat(),
                "timing": "decision after close; target change only at next common-session reported open",
                "pre_trade_weights": {code: float(pre_trade_weights[code]) for code in codes},
                **signal,
                "proxy_fill_status": "not_observed_market_price_proxy",
            }
            target_weights = signal["target_weights"]
            if target_weights is None:
                event["one_way_turnover"] = 0.0
                event["illustrative_cost_fraction_of_pretrade_proxy_value"] = 0.0
                event["proxy_action"] = "no_action_invalid_signal_input"
            else:
                target = pd.Series({code: float(target_weights[code]) for code in codes}, dtype=float)
                if abs(float(target.sum()) - 1.0) > EPSILON or (target < -EPSILON).any():
                    raise AssertionError(f"C34 {variant_id}: invalid target weights")
                turnover = float((pre_trade_weights - target).abs().sum() / 2.0)
                cost = pre_trade_value * turnover * cost_rate
                values = target * (pre_trade_value - cost)
                event["one_way_turnover"] = turnover
                event["illustrative_cost_fraction_of_pretrade_proxy_value"] = float(cost / pre_trade_value)
                event["proxy_action"] = "target_applied_at_effective_open"
            events.append(event)
        values = values * (closes.iloc[position] / opens.iloc[position])
        nav_rows.append((session, float(values.sum())))
        weights = values / float(values.sum())
        weight_rows.append((session, *(float(weights[code]) for code in codes)))
    nav = pd.Series({date: value for date, value in nav_rows}, dtype=float).sort_index()
    weights = pd.DataFrame(weight_rows, columns=["date", *codes]).set_index("date")
    if nav.empty or not np.isfinite(nav.to_numpy()).all() or (nav <= 0).any():
        raise ValueError(f"C34 {variant_id}: invalid proxy NAV")
    if any(event["decision_session"] >= event["effective_session"] for event in events):
        raise AssertionError(f"C34 {variant_id}: same-session or backward execution detected")
    years = complete_year_metrics(nav)
    rolling = rolling_five_year_metrics(nav)
    full_start = nav.index[0].date().isoformat()
    full_end = nav.index[-1].date().isoformat()
    windows = {
        "development": period_summary(nav, years, rolling, "2014-12-31", "2019-12-31", "development"),
        "holdout": period_summary(nav, years, rolling, "2020-01-01", "2025-12-31", "holdout"),
        "full_sample": period_summary(nav, years, rolling, full_start, full_end, "full_sample"),
    }
    elapsed_days = int((nav.index[-1] - nav.index[0]).days)
    all_complete = [row for row in years if row["complete_calendar_year"]]
    full_year_below = sum(not bool(row["at_or_above_5pct_limited_proxy_screen"]) for row in all_complete)
    full_rolling_below = int(rolling["below_5pct_count"])
    if not all_complete or rolling["window_count"] == 0:
        full_screen = "NOT_EVALUABLE_IN_LIMITED_PROXY"
    elif full_year_below == 0 and full_rolling_below == 0:
        full_screen = "NOT_REJECTED_BY_LIMITED_PRICE_PROXY_SCREEN_ONLY"
    else:
        full_screen = "REJECTED_BY_LIMITED_PRICE_PROXY_SCREEN"
    action_counts: dict[str, int] = {}
    active_counts: dict[str, int] = {"equity": 0, "bond": 0, "gold": 0, "fallback": 0}
    for event in events:
        state = str(event["signal_state"])
        action_counts[state] = action_counts.get(state, 0) + 1
        if state == "no_active_risk_sleeve_fallback" or state == "warmup_fallback":
            active_counts["fallback"] += 1
        for sleeve in event.get("eligible_sleeves", []):
            active_counts[str(sleeve)] += 1
    total_turnover = sum(float(event["one_way_turnover"]) for event in events)
    total_cost_fraction = sum(float(event["illustrative_cost_fraction_of_pretrade_proxy_value"]) for event in events)
    daily_changes = nav.pct_change().dropna()
    metrics = {
        "initial_decision_session": initial_decision.date().isoformat(),
        "initial_effective_session": initial_effective.date().isoformat(),
        "terminal_session": nav.index[-1].date().isoformat(),
        "proxy_nav_observations": int(len(nav)),
        "final_unitized_market_price_proxy_value": float(nav.iloc[-1]),
        "annualized_market_price_proxy_change_after_illustrative_cost": float(
            (nav.iloc[-1] / nav.iloc[0]) ** (365.25 / elapsed_days) - 1.0
        ),
        "annualized_market_price_proxy_volatility": float(daily_changes.std(ddof=1) * math.sqrt(252.0)),
        "maximum_drawdown_detail": drawdown_detail(nav),
        "worst_one_session_proxy_change": loss_window(nav, 1),
        "worst_twenty_session_proxy_change": loss_window(nav, 20),
        "monthly_signal_event_count_including_initial_entry": len(events),
        "signal_state_counts": action_counts,
        "eligible_sleeve_event_counts": active_counts,
        "aggregate_one_way_turnover_including_initial_entry": total_turnover,
        "illustrative_cost_arithmetic_sum_of_pretrade_proxy_value_fractions": total_cost_fraction,
        "complete_calendar_years": years,
        "complete_calendar_year_summary": {
            "count": len(all_complete),
            "at_or_above_5pct_count": len(all_complete) - full_year_below,
            "below_5pct_count": full_year_below,
        },
        "rolling_five_calendar_year": rolling,
        "full_limited_price_proxy_hurdle_screen": full_screen,
        "predeclared_windows": windows,
        "terminal_proxy_weights": {code: float(weights.iloc[-1][code]) for code in codes},
    }
    result = {
        "variant_id": variant_id,
        "settings": {
            "score_horizons_common_observations": list(score_horizons),
            "score_combination": "arithmetic mean",
            "eligibility": "risk_sleeve_score > fallback_score + threshold_excess, strictly",
            "eligibility_threshold_excess": eligibility_threshold_excess,
            "volatility_return_observations": volatility_observations,
            "volatility_return_type": "one-session simple market-price return; ddof=1",
            "active_weighting": "inverse realized volatility",
            "equity_target_split": {"510300": 0.5, "510880": 0.5},
            "none_active_target": {"511990": 1.0},
            "effective_timing": "following common session at reported open",
            "illustrative_one_way_bps": one_way_bps,
        },
        "metrics": metrics,
    }
    if include_events:
        result["events"] = events
    return result


def window_short_summary(period: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "annualized_market_price_proxy_change_after_illustrative_cost",
        "complete_calendar_year_count",
        "complete_calendar_year_below_5pct_count",
        "rolling_five_year_endpoint_count",
        "rolling_five_year_below_5pct_count",
        "limited_price_proxy_hurdle_screen",
        "status",
    )
    return {key: period[key] for key in keys if key in period}


def mutation_summary(variant: dict[str, Any]) -> dict[str, Any]:
    return {
        "variant_id": variant["variant_id"],
        "settings": variant["settings"],
        "full_sample": window_short_summary(variant["metrics"]["predeclared_windows"]["full_sample"]),
        "development": window_short_summary(variant["metrics"]["predeclared_windows"]["development"]),
        "holdout": window_short_summary(variant["metrics"]["predeclared_windows"]["holdout"]),
        "maximum_drawdown": variant["metrics"]["maximum_drawdown_detail"]["maximum_drawdown"],
        "aggregate_one_way_turnover_including_initial_entry": variant["metrics"]["aggregate_one_way_turnover_including_initial_entry"],
    }


def build_result() -> dict[str, Any]:
    protocol, codes = load_protocol()
    opens, closes, source_info = load_source(protocol, codes)
    base_rule = protocol["base_rule"]
    base = simulate_variant(
        opens,
        closes,
        tuple(int(value) for value in base_rule["score_horizons_common_observations"]),
        int(base_rule["realized_volatility"]["return_observations"]),
        0.0,
        float(protocol["illustrative_cost"]["one_way_bps"]),
        "base",
        include_events=True,
    )
    mutations: list[dict[str, Any]] = []
    for mutation in protocol["mutations"]:
        mutations.append(
            simulate_variant(
                opens,
                closes,
                tuple(int(value) for value in mutation["score_horizons_common_observations"]),
                int(mutation["volatility_return_observations"]),
                float(mutation["eligibility_threshold_excess"]),
                float(protocol["illustrative_cost"]["one_way_bps"]),
                str(mutation["id"]),
                include_events=False,
            )
        )
    base_metrics = base["metrics"]
    full_window = base_metrics["predeclared_windows"]["full_sample"]
    development = base_metrics["predeclared_windows"]["development"]
    holdout = base_metrics["predeclared_windows"]["holdout"]
    full_rolling = base_metrics["rolling_five_calendar_year"]
    drawdown = base_metrics["maximum_drawdown_detail"]
    scenario_results = [
        {
            "scenario": "Observed maximum drawdown in the limited dynamic market-price proxy",
            "assumption": "Base monthly dual-horizon score, strict fallback comparison, 60-return inverse-vol weighting, next-session reported-open proxy timing, and 20 bp illustrative turnover arithmetic.",
            "impact": drawdown,
            "boundary": "This is not an investor drawdown, execution loss, or bound on future loss.",
        },
        {
            "scenario": "Illustrative pre-rebalance 10 percent move in all active risk sleeves",
            "assumption": "Equity, bond, and gold sleeves all fall 10 percent before the next scheduled target event; fallback is unchanged. The active-set mix at the event is unknown in advance, so the result is a range across zero to full risk-sleeve exposure.",
            "impact": {
                "arithmetic_loss_range": "0 percent to -10 percent before friction, depending on the frozen signal's active target set",
                "meaning": "A one-period arithmetic sensitivity only; it is not a forecast or a loss bound.",
            },
            "boundary": "Correlation, gaps, price limits, halts, liquidity and ability to exit are not present in the input.",
        },
        {
            "scenario": "Limit-down, suspension, and no-fill stress",
            "assumption": "The retained daily rows do not contain product status, price-limit, order-book, depth, or execution data.",
            "impact": "UNAVAILABLE: inability to change target or exit, delayed implementation, and loss amplification cannot be quantified from this source.",
            "boundary": "A daily close or next-session open proxy must not be treated as a fill.",
        },
    ]
    result = {
        "schema_version": "d5pt_c34_dual_horizon_inverse_vol_etf_candidate.v1",
        "artifact_id": "D5PT-C34-DUAL-HORIZON-INVERSE-VOL-v1",
        "as_of": closes.index[-1].date().isoformat(),
        "artifact_class": "exploratory_retrospective_market_price_proxy",
        "research_only": True,
        "external_orders": False,
        "formal_decision_eligible": False,
        "portfolio_q": 0,
        "protocol": {
            "json_path": repo_path(PROTOCOL_JSON),
            "json_sha256": sha256_file(PROTOCOL_JSON),
            "markdown_path": repo_path(PROTOCOL_MD),
            "markdown_sha256": sha256_file(PROTOCOL_MD),
            "recorded_before_calculation": protocol["recorded_before_calculation"],
            "predeclared_no_winner_selection": True,
        },
        "integrity_disclosure": {
            "protocol_status": "pre_formal_recompute_not_true_preregistration",
            "formula_timing": "The C34 formula was formalized after prior exploratory public-price observation. The retained protocol predates this formal recomputation only; it is not a clean preregistration before the underlying observations.",
            "development_holdout_boundary": "The chronological 2020-01-01 through 2025-12-31 holdout is a robustness slice, not clean unseen out-of-sample validation. It does not convert the calculation into independent evidence.",
            "effect_on_disposition": "No proxy result may be used as independent proof, a return promise, or an external-action basis.",
        },
        "data_quality": {
            **source_info,
            "degradation": "Retrospective official daily market-price observations only; no point-in-time availability, adjustment/total-return, distributions, fund events, quote, liquidity, costs, execution, settlement, tax, account, or capacity evidence.",
        },
        "candidate_action_card": {
            "status": "research_candidate_not_admitted_not_a_live_action_card",
            "exact_universe": {
                "equity": {"codes": ["510300", "510880"], "within_sleeve_weight": [0.5, 0.5]},
                "bond": "511010",
                "gold": "518880",
                "fallback": "511990",
            },
            "score_and_eligibility": "For each final common monthly close, score each sleeve by the mean of 126- and 252-common-observation price returns; a risk sleeve is active only when its score is strictly greater than the fallback score.",
            "target_action": "Active risk sleeves receive inverse trailing-60-common-return-volatility weights, with equity split 50/50. No active sleeve means 100 percent fallback. A target can apply only at the following common-session reported open in the proxy; no external order is authorized.",
            "warmup": "100 percent fallback while required input observations are unavailable.",
            "forward_paper_order_protection": protocol["forward_paper_order_protection"],
            "no_action_conditions": protocol["no_action_conditions"],
            "prohibited": [
                "automatic ETF substitution",
                "same-session close execution",
                "assumed fill or synthetic close fill",
                "leverage, short sale, borrowing, futures, or options",
                "external order or account action",
            ],
        },
        "calculation_design": {
            "timing": protocol["timing"],
            "illustrative_cost": protocol["illustrative_cost"],
            "market_price_proxy_only": True,
            "not_modelled": [
                "total return, distributions, or fund events",
                "NAV, IOPV, premium/discount, bid/ask, depth, or impact",
                "actual fees, taxes, fills, settlement, lot rounding, or account rules",
                "halts, price limits, capacity, partial fills, or no fills",
            ],
        },
        "base_diagnostic": base,
        "predeclared_mutations": mutations,
        "mutation_summary_no_winner_selection": [mutation_summary(base), *[mutation_summary(item) for item in mutations]],
        "hurdle_assessment": {
            "research_hurdle": protocol["research_hurdle"],
            "base_development": summary_without_rows(development),
            "base_holdout": summary_without_rows(holdout),
            "base_full_sample": summary_without_rows(full_window),
            "strict_rolling_five_year_failure_count_full_sample": full_rolling["below_5pct_count"],
            "strict_rolling_five_year_endpoint_count_full_sample": full_rolling["window_count"],
            "formal_total_return_and_execution_hurdle_verdict": "NOT_ADJUDICABLE",
            "meaning": "A 5 percent outcome is not guaranteed. Any limited proxy success would remain insufficient for admission; any limited proxy failure is stated without changing the rule.",
        },
        "scenario_results": scenario_results,
        "risk_model": {
            "role": "quant-risk-modeler",
            "risk_model_status": "VETO",
            "conclusion": "The dynamic proxy has explicit signals, next-session timing, and a frozen sensitivity family, but missing total-return, liquidity, execution, account, risk-budget and forward-paper inputs prevent a bounded-loss or personally operable-strategy conclusion.",
            "exposure_findings": [
                "At an active signal, allocation can concentrate in a single bond or gold sleeve or distribute across three risk sleeves; the rule provides no independent correlation or concentration proof.",
                "The equity sleeve combines two domestic equity ETFs, so its 50/50 split is not evidence of low correlation or crisis protection.",
                "The fallback ETF is a money-market-tool exposure, not a cash, liquidity, or loss-free assertion.",
            ],
            "scenario_results": [
                "Historical proxy maximum drawdown and a signal-dependent -10 percent arithmetic stress are reported above; neither bounds a future loss.",
                "Limit-down, halt, depth, and no-fill stress are unavailable because the input has no relevant execution fields.",
            ],
            "model_limits": [
                "The SSE rows were captured retrospectively and do not establish point-in-time availability or adjustment basis.",
                "Market-price proxies do not establish investor total return, fees, taxes, bids, asks, fills, settlement, account access, or capacity.",
                "The frozen development/holdout split and finite mutations are descriptive controls, not proof of alpha, VaR, correlation, or future outcome.",
            ],
            "required_controls": [
                "Keep research_only and portfolio_q=0; do not use the proxy to send or support an external order.",
                "Acquire a rights-cleared point-in-time total-return, distribution, and fund-event ledger plus dated execution, cost, tax, settlement, status, and no-fill records.",
                "For any future paper record, fail closed to no_action unless current product, account, status, quote/depth, IOPV where applicable, lot, fee/tax, and settlement evidence are complete.",
                "Define user loss budget, concentration limits, liquidity needs, and a continuous forward-paper ledger before considering any operability review.",
            ],
            "confidence": 95,
            "degradation": "Retrospective official market-price input only; actual total-return and execution data are absent.",
        },
        "runtime_provenance": {
            "script_path": repo_path(Path(__file__).resolve()),
            "script_sha256": sha256_file(Path(__file__).resolve()),
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "pandas_version": pd.__version__,
            "numpy_version": np.__version__,
            "command": "PYTHONDONTWRITEBYTECODE=1 .venv/bin/python workspace/research/domestic-5pct-target-paper-strategy-20260815/tools/C34_run_dual_horizon_inverse_vol_etf_proxy.py --write",
        },
    }
    return result


def percent(value: float | None, places: int = 2) -> str:
    if value is None:
        return "—"
    return f"{value * 100:.{places}f}%"


def summary_value(summary: dict[str, Any], key: str, default: str = "—") -> Any:
    return summary.get(key, default)


def render_window_row(name: str, summary: dict[str, Any]) -> str:
    if summary.get("status") == "UNAVAILABLE":
        return f"| {name} | — | — | — | — | `UNAVAILABLE` |"
    return (
        f"| {name} | {percent(summary['annualized_market_price_proxy_change_after_illustrative_cost'])} | "
        f"{summary['complete_calendar_year_below_5pct_count']}/{summary['complete_calendar_year_count']} | "
        f"{summary['rolling_five_year_below_5pct_count']}/{summary['rolling_five_year_endpoint_count']} | "
        f"{summary['baseline_proxy_date']} → {summary['terminal_proxy_date']} | "
        f"`{summary['limited_price_proxy_hurdle_screen']}` |"
    )


def render_markdown(result: dict[str, Any]) -> str:
    base = result["base_diagnostic"]
    metrics = base["metrics"]
    windows = metrics["predeclared_windows"]
    rolling = metrics["rolling_five_calendar_year"]
    drawdown = metrics["maximum_drawdown_detail"]
    one_day = metrics["worst_one_session_proxy_change"]
    twenty = metrics["worst_twenty_session_proxy_change"]
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
        for row in metrics["complete_calendar_years"]
    )
    mutation_rows = "\n".join(
        "| {id} | {dev} | {hold} | {full} | {dd} |".format(
            id=row["variant_id"],
            dev=(
                f"{percent(row['development'].get('annualized_market_price_proxy_change_after_illustrative_cost'))}; "
                f"年 {summary_value(row['development'], 'complete_calendar_year_below_5pct_count')}/"
                f"{summary_value(row['development'], 'complete_calendar_year_count')}; "
                f"滚 {summary_value(row['development'], 'rolling_five_year_below_5pct_count')}/"
                f"{summary_value(row['development'], 'rolling_five_year_endpoint_count')}"
            ),
            hold=(
                f"{percent(row['holdout'].get('annualized_market_price_proxy_change_after_illustrative_cost'))}; "
                f"年 {summary_value(row['holdout'], 'complete_calendar_year_below_5pct_count')}/"
                f"{summary_value(row['holdout'], 'complete_calendar_year_count')}; "
                f"滚 {summary_value(row['holdout'], 'rolling_five_year_below_5pct_count')}/"
                f"{summary_value(row['holdout'], 'rolling_five_year_endpoint_count')}"
            ),
            full=(
                f"{percent(row['full_sample'].get('annualized_market_price_proxy_change_after_illustrative_cost'))}; "
                f"年 {summary_value(row['full_sample'], 'complete_calendar_year_below_5pct_count')}/"
                f"{summary_value(row['full_sample'], 'complete_calendar_year_count')}; "
                f"滚 {summary_value(row['full_sample'], 'rolling_five_year_below_5pct_count')}/"
                f"{summary_value(row['full_sample'], 'rolling_five_year_endpoint_count')}"
            ),
            dd=percent(row["maximum_drawdown"]),
        )
        for row in result["mutation_summary_no_winner_selection"]
    )
    source_rows = "\n".join(
        f"| `{row['code']}` | {row['response_rows']} | {row['first_trade_date']} | {row['last_trade_date']} | `{row['sha256']}` |"
        for row in result["data_quality"]["raw_responses"]
    )
    no_actions = "\n".join(f"- {value}" for value in result["candidate_action_card"]["no_action_conditions"])
    controls = "\n".join(f"- {value}" for value in result["risk_model"]["required_controls"])
    rolling_statement = (
        "没有完整滚动五年端点。"
        if rolling["window_count"] == 0
        else (
            f"全样本月末滚动五年端点 {rolling['window_count']} 个，其中 "
            f"{rolling['below_5pct_count']} 个低于 5%，"
            f"区间为 {percent(rolling['minimum_annualized_market_price_proxy_change_after_illustrative_cost'])} 至 "
            f"{percent(rolling['maximum_annualized_market_price_proxy_change_after_illustrative_cost'])}。"
        )
    )
    rolling_fail = rolling["below_5pct_count"] > 0
    hard_text = (
        f"**严格滚动五年 5% 代理筛查失败：** {rolling['below_5pct_count']}/{rolling['window_count']} 个全样本端点低于 5%。"
        if rolling_fail
        else "全样本滚动五年代理没有低于 5% 的端点；这仍不能构成总回报、可操作性或外部行动结论。"
    )
    return f"""# C34：双期限评分与逆波动 ETF 候选 — 价格代理诊断

- 工件 ID：`{result['artifact_id']}`
- 截止日：`{result['as_of']}`
- 角色：`quant-risk-modeler`
- 风险模型状态：`VETO`
- 当前处置：`research_only`、`portfolio_q=0`、不发送外部订单。
- 结论：C34 已把双期限评分、严格回退比较、逆波动权重和次交易日时序写成可复算候选；但它的历史输入仅为回溯日价代理，公式形成于既有探索性观察之后，且严格滚动五年筛查 {"出现失败" if rolling_fail else "未出现失败"}，不能作为稳定 5% 或实际行动依据。

## 1. 冻结前协议与精确动作卡

本次计算之前已经冻结协议：[c34_dual_horizon_inverse_vol_etf_protocol_20260815.md](c34_dual_horizon_inverse_vol_etf_protocol_20260815.md)，JSON 哈希为 `{result['protocol']['json_sha256']}`。它是与 C30 静态诊断和 R01 月度纸面规则相互独立的候选，绝不改写两者。

**完整性边界：** C34 公式是在先前公开价格的探索性观察之后才被形式化。上述“计算前冻结”只表示它先于本次正式复算被记录，状态为 `pre_formal_recompute_not_true_preregistration`，并非在底层观察之前的干净预注册。2020-01-01 至 2025-12-31 的时间顺序留出段仅为鲁棒性切片，**不是**干净、未见的样本外验证；它不能把任何正面代理数值升级为独立证据、收益承诺或外部行动依据。

| 袖套 | 代码 | 目标形成方式 |
|---|---|---|
| 权益 | `510300`、`510880` | 权益袖套获选后内部各占其袖套 50% |
| 国债 | `511010` | 获选后按逆波动权重进入 |
| 黄金 | `518880` | 获选后按逆波动权重进入 |
| 回退 | `511990` | 没有风险袖套获选或预热期时为 100% |

每月最后一个共同收盘日 `D` 后，对权益、国债、黄金和回退分别计算 126 与 252 个共同观察值的市场价变化，取均值为分数。风险袖套仅在分数**严格大于**回退分数时获选；相等即不获选。获选袖套按最近 60 个共同单期市场价变化的样本波动率倒数分配；权益份额再固定均分给两只股票 ETF。无任何获选袖套时，目标为 100% `511990`。

没有杠杆、空头、期货、期权、借入、相似 ETF 替换、主观覆盖、横截面排名或事后改参。预热期也固定为 100% 回退，直到 252 期分数与波动率输入完整。

## 2. 时序、成本与来源边界

决策只使用 `D` 收盘前的信息；最早代理变更在下一共同交易日 `E` 的开盘价。旧持有先承受 `D` 收盘至 `E` 开盘的变化，`E` 开盘才发生目标和说明性成本算术，新目标随后承受 `E` 开盘至收盘的变化。程序逐笔断言 `D < E`，禁止同日收盘执行与同一 K 线前视。

每次代理变化按单边换手扣 `20 bp`，首次回退入场亦包含。它只是说明性算术，不是手续费、税费、点差、冲击、基金费用、结算或成交。上交所输入被严格哈希核验，但为回溯获取且调整口径未说明；它**不是**总回报、净值回报、实际订单或个人可操作性证明。

| 代码 | 原始行数 | 首日 | 末日 | SHA-256 |
|---|---:|---|---|---|
{source_rows}

共同日价面板为 {result['data_quality']['common_panel']['first_common_session']} 至 {result['data_quality']['common_panel']['last_common_session']}，共 {result['data_quality']['common_panel']['observations']} 个日期。

## 3. 基准候选：开发、留出与全样本上下文

开发窗口固定为 2014-12-31 至 2019-12-31；留出窗口固定为 2020-01-01 至 2025-12-31。模型没有在开发结果后选择某一突变；留出结果也不是交易许可。

| 窗口 | 年化市场价代理变化 | 完整年度 <5% | 滚动五年 <5% | 代理基线 → 末端 | 有限筛查 |
|---|---:|---:|---:|---|---|
{render_window_row('Development', windows['development'])}
{render_window_row('Holdout', windows['holdout'])}
{render_window_row('Full sample', windows['full_sample'])}

{hard_text}

全样本期末单位值为 {metrics['final_unitized_market_price_proxy_value']:.4f}，年化市场价代理变化为 {percent(metrics['annualized_market_price_proxy_change_after_illustrative_cost'])}，最大回撤代理为 {percent(drawdown['maximum_drawdown'])}（{drawdown['peak_date']} 至 {drawdown['trough_date']}）。最差单期代理变化为 {percent(one_day['return'])}（{one_day['start']} 至 {one_day['end']}），最差 20 期代理变化为 {percent(twenty['return'])}（{twenty['start']} 至 {twenty['end']}）。共 {metrics['monthly_signal_event_count_including_initial_entry']} 个信号/入场记录，累计单边换手 {metrics['aggregate_one_way_turnover_including_initial_entry']:.4f}，说明性成本分数算术和为 {percent(metrics['illustrative_cost_arithmetic_sum_of_pretrade_proxy_value_fractions'])}。

{rolling_statement}

## 4. 全样本完整自然年

| 年份 | 首日 | 末日 | 完整 | 市场价代理变化 | ≥5%（仅有限筛查） |
|---:|---|---|:---:|---:|:---:|
{year_rows}

以上年度和滚动结果仅是未确认调整口径的价格代理。5% 是研究阈值，不是保证、年度下限、预测或适当性结论。

## 5. 预先声明的突变族（无选优）

下表完整显示基准、126-only、252-only、60×80% 的 48 期波动和 60×120% 的 72 期波动变体。每格的“年/滚”均为低于 5% 的计数，不允许按较高年化或较低回撤挑选任一变体。

| 变体 | 开发（年化；年/滚失败） | 留出（年化；年/滚失败） | 全样本（年化；年/滚失败） | 最大回撤代理 |
|---|---|---|---|---:|
{mutation_rows}

该敏感度族不估计 alpha、相关性、VaR、容量或未来结果，也不是独立样本外证明。

## 6. 场景、操作闸门与未界定风险

1. **历史最大回撤代理：** {percent(drawdown['maximum_drawdown'])}，不是投资者回撤或未来损失上限。
2. **全部活跃风险袖套下跌 10% 的算术压力：** 在下次调仓前的单期影响范围为 0% 至 -10%，取决于当期冻结信号是否仅在回退或配置了风险袖套；它不是预测或损失边界。
3. **跌停、停牌与未成交：** `UNAVAILABLE`。日线没有状态、价格限制、订单簿、深度或成交记录，不能量化无法调仓或退出时的影响。

未来纸面记录必须保留产品文件和公告、状态、账户/适当性、可用份额和资金、费率税费、结算、带时间戳报价与深度，以及适用的 IOPV。买入只在 `ask ≤ IOPV × 1.003`，卖出只在 `bid ≥ IOPV × 0.997` 时进入限价纸面流程。下列任一情形为 `no_action`，不得假设成交或替换标的：

{no_actions}

## 7. 量化风险闸门

**Role:** quant-risk-modeler  
**Risk Model Status:** VETO  
**Conclusion:** {result['risk_model']['conclusion']}  
**Confidence:** {result['risk_model']['confidence']} / 100  
**Degradation:** {result['risk_model']['degradation']}

**Exposure Findings:**

- 任一动态时点可能把目标集中到国债或黄金单一袖套；规则没有相关性、容量或集中度安全证明。
- 权益袖套中的两个 ETF 同属国内股票风险，50/50 并不证明低相关或危机保护。
- `511990` 是货币市场工具 ETF 暴露，不等同账户现金或损失消除机制。

**Required Controls:**

{controls}

**最终边界：** 本工件不承诺 5%，不授权账户动作、外部订单、申购、赎回或任何实际投资行动。
"""


def write_outputs(result: dict[str, Any]) -> None:
    OUTPUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(result), encoding="utf-8")


def verify_outputs(result: dict[str, Any]) -> None:
    if not OUTPUT_JSON.is_file() or not OUTPUT_MD.is_file():
        raise FileNotFoundError("C34 outputs are absent; run --write first")
    expected_json = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    expected_md = render_markdown(result)
    if OUTPUT_JSON.read_text(encoding="utf-8") != expected_json:
        raise AssertionError("C34 JSON differs from a fresh frozen-protocol recomputation")
    if OUTPUT_MD.read_text(encoding="utf-8") != expected_md:
        raise AssertionError("C34 Markdown differs from a fresh frozen-protocol recomputation")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--write", action="store_true", help="write C34 Markdown and JSON artifacts")
    action.add_argument("--verify", action="store_true", help="recompute and require byte-identical C34 artifacts")
    args = parser.parse_args()
    result = build_result()
    if args.verify:
        verify_outputs(result)
        print("PASS: C34 recomputes byte-identically from the frozen protocol and hash-checked SSE inputs.")
    else:
        write_outputs(result)
        print(f"WROTE: {repo_path(OUTPUT_MD)}")
        print(f"WROTE: {repo_path(OUTPUT_JSON)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

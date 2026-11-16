#!/usr/bin/env python3
"""Derive a C9 actual-contract route/snapshot record from frozen SHFE files.

This utility deliberately has no P&L calculation.  Its only selection output
is a dated illustration of the predeclared contract-selection rule.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
SOURCE_DIR = CASE_DIR / "sources" / "c9-official-shfe-commodity-contracts-20260815"
MANIFEST_PATH = SOURCE_DIR / "manifest.json"
OUTPUT_JSON = CASE_DIR / "analysis" / "c9_actual_contract_snapshot_20260815.json"
OUTPUT_MD = CASE_DIR / "analysis" / "c9_actual_contract_snapshot_20260815.md"
FAMILIES = ("CU", "AU", "RU")
CURRENT_DATE = "2026-08-14"
MIN_DAYS_TO_LAST_TRADE = 90
MAX_DAYS_TO_LAST_TRADE = 270


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _write(path: Path, content: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def _load_source_file(filename: str) -> tuple[dict[str, Any], bytes]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    matches = [item for item in manifest["files"] if Path(item["path"]).name == filename]
    if len(matches) != 1:
        raise ValueError(f"manifest lacks exactly one row for {filename}")
    entry = matches[0]
    path = REPO_ROOT / str(entry["path"])
    raw = path.read_bytes()
    if len(raw) != entry["bytes"] or _sha256(raw) != entry["sha256"]:
        raise ValueError(f"frozen source mismatch for {filename}")
    return entry, raw


def _family(row: dict[str, Any]) -> str:
    return str(row.get("PRODUCTGROUPID") or row.get("PRODUCTID") or "").strip().split("_")[0].upper()


def _as_int(value: Any) -> int:
    return int(float(value))


def _scheduled_last_trade(delivery_month: str) -> date:
    if len(delivery_month) != 4 or not delivery_month.isdigit():
        raise ValueError(f"unsupported delivery month {delivery_month!r}")
    return date(2000 + int(delivery_month[:2]), int(delivery_month[2:]), 15)


def _contract_code(family: str, delivery_month: str) -> str:
    return f"{family}{delivery_month}"


def _current_snapshot() -> dict[str, Any]:
    entry, raw = _load_source_file("shfe_actual_contract_daily_20260814.json")
    payload = json.loads(raw.decode("utf-8"))
    decision_date = datetime.strptime(CURRENT_DATE, "%Y-%m-%d").date()
    grouped: dict[str, list[dict[str, Any]]] = {family: [] for family in FAMILIES}
    for row in payload["o_curinstrument"]:
        if not isinstance(row, dict):
            continue
        family = _family(row)
        delivery_month = str(row.get("DELIVERYMONTH") or "").strip()
        if family not in grouped or delivery_month in {"", "小计", "合计"}:
            continue
        last_trade = _scheduled_last_trade(delivery_month)
        days = (last_trade - decision_date).days
        observation = {
            "contract": _contract_code(family, delivery_month),
            "delivery_month": delivery_month,
            "scheduled_last_trade_date": last_trade.isoformat(),
            "scheduled_days_to_last_trade": days,
            "settlement": float(row["SETTLEMENTPRICE"]),
            "close": float(row["CLOSEPRICE"]),
            "volume": _as_int(row["VOLUME"]),
            "open_interest": _as_int(row["OPENINTEREST"]),
            "eligible_for_90_to_270_day_selection": (
                MIN_DAYS_TO_LAST_TRADE <= days <= MAX_DAYS_TO_LAST_TRADE
                and float(row["SETTLEMENTPRICE"]) > 0
                and _as_int(row["VOLUME"]) > 0
                and _as_int(row["OPENINTEREST"]) > 0
            ),
        }
        grouped[family].append(observation)

    selected: list[dict[str, Any]] = []
    for family in FAMILIES:
        candidates = [row for row in grouped[family] if row["eligible_for_90_to_270_day_selection"]]
        if not candidates:
            selected.append({"family": family, "selected_contract": None, "reason": "no eligible actual contract"})
            continue
        candidates.sort(key=lambda row: (-int(row["open_interest"]), -int(row["volume"]), str(row["delivery_month"])))
        row = candidates[0]
        selected.append(
            {
                "family": family,
                "selected_contract": row["contract"],
                "selection_rank": 1,
                "settlement": row["settlement"],
                "volume": row["volume"],
                "open_interest": row["open_interest"],
                "scheduled_last_trade_date": row["scheduled_last_trade_date"],
                "scheduled_days_to_last_trade": row["scheduled_days_to_last_trade"],
                "selection_reason": "highest official EOD open interest; volume then earliest delivery month are deterministic tie-breakers",
            }
        )
    return {
        "source_file": entry["path"],
        "source_sha256": entry["sha256"],
        "decision_date": CURRENT_DATE,
        "rule": {
            "families": list(FAMILIES),
            "min_calendar_days_to_scheduled_last_trade": MIN_DAYS_TO_LAST_TRADE,
            "max_calendar_days_to_scheduled_last_trade": MAX_DAYS_TO_LAST_TRADE,
            "requires_positive_settlement_volume_and_open_interest": True,
            "ranking": ["open_interest_desc", "volume_desc", "delivery_month_asc"],
            "date_boundary": "The exchange may adjust a 15th-day last-trade date for holidays. This sample's selected 2026-12-15 and 2027-01-15 scheduled dates are weekday dates; any live use must obtain the exchange-adjusted calendar before applying the rule.",
        },
        "selected_contracts": selected,
        "all_candidate_rows": grouped,
        "interpretation": {
            "status": "DATED_SELECTION_ILLUSTRATION_ONLY",
            "signal_history_verified": False,
            "personal_access_verified": False,
            "order_or_position": "none",
            "return_or_backtest": "none",
            "boundary": "This record selects from one retrospective official EOD snapshot using actual listed contracts. It is not a live order, a recommendation, a complete historical roll ledger or a performance result.",
        },
    }


def _route_samples() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for day in ("20160104", "20180102", "20200102", "20220104", "20240102", "20260814"):
        entry, raw = _load_source_file(f"shfe_actual_contract_daily_{day}.json")
        payload = json.loads(raw.decode("utf-8"))
        by_family = {family: 0 for family in FAMILIES}
        observed_fields: set[str] = set()
        for row in payload["o_curinstrument"]:
            if not isinstance(row, dict):
                continue
            family = _family(row)
            delivery_month = str(row.get("DELIVERYMONTH") or "").strip()
            if family not in by_family or delivery_month in {"", "小计", "合计"}:
                continue
            by_family[family] += 1
            observed_fields.update(row.keys())
        essential = {"PRESETTLEMENTPRICE", "OPENPRICE", "HIGHESTPRICE", "LOWESTPRICE", "CLOSEPRICE", "SETTLEMENTPRICE", "VOLUME", "OPENINTEREST", "DELIVERYMONTH"}
        rows.append(
            {
                "trade_date": f"{day[:4]}-{day[4:6]}-{day[6:]}",
                "source_file": entry["path"],
                "source_sha256": entry["sha256"],
                "total_rows": len(payload["o_curinstrument"]),
                "actual_contract_rows": by_family,
                "all_essential_eod_fields_observed": essential.issubset(observed_fields),
                "observed_essential_fields": sorted(essential.intersection(observed_fields)),
                "turnover_field_observed": "TURNOVER" in observed_fields,
                "retrieval_basis": "retrospective_source_access_sample",
            }
        )
    return rows


def main() -> int:
    snapshot = _current_snapshot()
    route = _route_samples()
    result = {
        "schema_version": "c9_actual_contract_snapshot.v1",
        "artifact_class": "derived_research_evidence",
        "research_only": True,
        "not_a_backtest": True,
        "portfolio_q": 0,
        "actual_contract_source_route": {
            "status": "SIX_RETROSPECTIVE_SAMPLES_OBSERVED_NOT_REPLAY_READY",
            "samples": route,
            "supported": "The retained official daily files contain actual CU, AU and RU contract rows and the EOD fields required for a future actual-contract ledger.",
            "not_supported": [
                "A complete historical actual-contract archive or original-date availability.",
                "A point-in-time contract master, exchange calendar, delivery-state record, fee/margin/limit notices or broker parameters.",
                "Bid/ask, depth, fills, capacity, personal account access, cost, P&L, return, drawdown or a trading action."
            ],
        },
        "dated_selection_snapshot": snapshot,
    }
    _write(OUTPUT_JSON, json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    selected_rows = "\n".join(
        f"| {row['family']} | {row['selected_contract']} | {row.get('settlement', 'n/a')} | {row.get('volume', 'n/a')} | {row.get('open_interest', 'n/a')} | {row.get('scheduled_last_trade_date', 'n/a')} | {row.get('scheduled_days_to_last_trade', 'n/a')} |"
        for row in snapshot["selected_contracts"]
    )
    route_rows = "\n".join(
        f"| {row['trade_date']} | {row['total_rows']} | {row['actual_contract_rows']['CU']} | {row['actual_contract_rows']['AU']} | {row['actual_contract_rows']['RU']} | {'yes' if row['all_essential_eod_fields_observed'] else 'no'} | {'yes' if row['turnover_field_observed'] else 'no'} |"
        for row in route
    )
    _write(
        OUTPUT_MD,
        f"""# C9 Actual-Contract Source Route and Dated Selection Snapshot

- Status: **source route observed; not replay-ready**; `portfolio_q=0`.
- Source: six retrospectively captured first-party SHFE daily files, bound in `sources/c9-official-shfe-commodity-contracts-20260815/manifest.json`.
- Boundary: this is neither a continuous series nor a backtest, order, position, allocation or return result.

## Actual-contract route samples

| Trade date | Total rows | CU actual rows | AU actual rows | RU actual rows | Essential EOD fields observed | Turnover field observed |
|---|---:|---:|---:|---:|---|---|
{route_rows}

Every sample contains prior settlement, OHLC, settlement, volume, open interest and delivery month. Turnover appears in the later schema but not the 2016--2020 samples, which is a source-schema limitation rather than an inferred zero. The files were retrieved retrospectively and do not establish point-in-time availability, a complete contract lifecycle, effective risk parameters, costs, fills, account access or P&L.

## 2026-08-14 dated selection illustration

Fixed illustration rule: select only an actual contract with a positive settlement, volume and open interest, a scheduled expiry 90--270 calendar days away, then rank by official EOD open interest, volume and earliest delivery month. The source page permits holiday adjustments to the 15th-day last-trade date; the selected dates below are weekday dates and must still be exchange-calendar checked before any live application.

| Family | Selected actual contract | Settlement | Volume | Open interest | Scheduled last trade | Days |
|---|---|---:|---:|---:|---|---:|
{selected_rows}

No 65-session signal history, personal access, broker margin, quote, fill or trade is asserted. The selection is a reproducible observation only.
""",
    )
    print(f"wrote {OUTPUT_JSON} and {OUTPUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

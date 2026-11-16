#!/usr/bin/env python3
"""Build C12 research-only actual-contract, rulebook and feasibility artifacts.

The source batch is verified before it is read.  The output deliberately
contains no continuous-series return calculation, simulated fill, account
claim, order, position or allocation.
"""

from __future__ import annotations

import calendar
import csv
import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
SOURCE_DIR = CASE_DIR / "sources" / "c12-official-cash-futures-basis-20260815"
MANIFEST_PATH = SOURCE_DIR / "manifest.json"
ROUTE_JSON = CASE_DIR / "analysis" / "c12_cffex_actual_contract_route_20260815.json"
ROUTE_MD = CASE_DIR / "analysis" / "c12_cffex_actual_contract_route_20260815.md"
RULEBOOK_JSON = CASE_DIR / "analysis" / "c12_cash_futures_basis_rulebook_20260815.json"
RULEBOOK_MD = CASE_DIR / "analysis" / "c12_cash_futures_basis_rulebook_20260815.md"
FEASIBILITY_JSON = CASE_DIR / "analysis" / "c12_cash_futures_basis_feasibility_20260815.json"
FEASIBILITY_MD = CASE_DIR / "analysis" / "c12_cash_futures_basis_feasibility_20260815.md"

SAMPLE_DATES = (
    "20160104",
    "20180102",
    "20200102",
    "20220104",
    "20240102",
    "20260814",
)
CURRENT_DECISION_DATE = date(2026, 8, 14)
MIN_DAYS_TO_LAST_TRADE = 60
MAX_DAYS_TO_LAST_TRADE = 150


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _write(path: Path, text: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def _load_json(path: Path) -> Any:
    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key {key} in {path}")
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)


def _load_manifested_raw(filename: str) -> tuple[dict[str, Any], bytes]:
    manifest = _load_json(MANIFEST_PATH)
    matches = [
        item for item in manifest["files"] if Path(str(item["path"])).name == filename
    ]
    if len(matches) != 1:
        raise ValueError(f"manifest lacks one row for {filename}")
    entry = matches[0]
    path = REPO_ROOT / str(entry["path"])
    raw = path.read_bytes()
    if len(raw) != entry["bytes"] or _sha256(raw) != entry["sha256"]:
        raise ValueError(f"frozen source mismatch for {filename}")
    return entry, raw


def _family(code: str) -> str | None:
    if code.startswith("TF") and code[2:].isdigit():
        return "TF"
    if code.startswith("TS") and code[2:].isdigit():
        return "TS"
    if code.startswith("TL") and code[2:].isdigit():
        return "TL"
    if code.startswith("T") and code[1:].isdigit():
        return "T"
    return None


def _float(value: str) -> float | None:
    value = value.strip()
    if value in {"", "--", "null", "None"}:
        return None
    return float(value)


def _actual_rows(day: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    entry, raw = _load_manifested_raw(f"cffex_actual_contract_daily_{day}.csv")
    text = raw.decode("gb18030")
    parsed = list(csv.reader(text.splitlines()))
    if not parsed or "合约代码" not in parsed[0][0]:
        raise ValueError(f"CFFEX {day} header malformed")
    rows: list[dict[str, Any]] = []
    for source_row in parsed[1:]:
        if not source_row:
            continue
        code = source_row[0].strip().upper()
        family = _family(code)
        if family is None:
            continue
        if len(source_row) < 11:
            raise ValueError(f"CFFEX {day} actual contract has short row: {code}")
        rows.append(
            {
                "contract": code,
                "family": family,
                "open": _float(source_row[1]),
                "high": _float(source_row[2]),
                "low": _float(source_row[3]),
                "volume": _float(source_row[4]),
                "turnover": _float(source_row[5]),
                "open_interest": _float(source_row[6]),
                "open_interest_change": _float(source_row[7]),
                "close": _float(source_row[8]),
                "settlement": _float(source_row[9]),
                "previous_settlement": _float(source_row[10]),
            }
        )
    if not rows:
        raise ValueError(f"CFFEX {day} has no Treasury-futures rows")
    return entry, rows


def _last_trade_date(contract: str) -> date:
    digits = contract[2:] if contract.startswith(("TF", "TS", "TL")) else contract[1:]
    if len(digits) != 4 or not digits.isdigit():
        raise ValueError(f"unsupported actual contract code {contract}")
    year = 2000 + int(digits[:2])
    month = int(digits[2:])
    fridays = [
        week[calendar.FRIDAY]
        for week in calendar.monthcalendar(year, month)
        if week[calendar.FRIDAY] != 0
    ]
    return date(year, month, fridays[1])


def _leading(rows: list[dict[str, Any]], family: str) -> dict[str, Any] | None:
    candidates = [
        row
        for row in rows
        if row["family"] == family
        and row["settlement"] is not None
        and row["volume"] is not None
        and row["open_interest"] is not None
    ]
    if not candidates:
        return None
    candidates.sort(
        key=lambda row: (
            -float(row["open_interest"]),
            -float(row["volume"]),
            str(row["contract"]),
        )
    )
    return candidates[0]


def _route_artifact() -> dict[str, Any]:
    samples: list[dict[str, Any]] = []
    current_t_rows: list[dict[str, Any]] = []
    for day in SAMPLE_DATES:
        entry, rows = _actual_rows(day)
        per_family = {
            family: [row for row in rows if row["family"] == family]
            for family in ("T", "TF", "TS", "TL")
        }
        sample = {
            "trade_date": f"{day[:4]}-{day[4:6]}-{day[6:]}",
            "source_file": entry["path"],
            "source_sha256": entry["sha256"],
            "retrieval_basis": "retrospective_source_access_sample",
            "actual_contract_rows_by_family": {
                family: len(values) for family, values in per_family.items()
            },
            "source_columns_used": [
                "contract_code",
                "open",
                "high",
                "low",
                "volume",
                "turnover",
                "open_interest",
                "close",
                "settlement",
                "previous_settlement",
            ],
            "leading_t": _leading(rows, "T"),
            "leading_tf": _leading(rows, "TF"),
        }
        samples.append(sample)
        if day == "20260814":
            current_t_rows = per_family["T"]

    eligible: list[dict[str, Any]] = []
    for row in current_t_rows:
        last_trade = _last_trade_date(str(row["contract"]))
        days = (last_trade - CURRENT_DECISION_DATE).days
        item = {
            **row,
            "scheduled_last_trade_date": last_trade.isoformat(),
            "scheduled_days_to_last_trade": days,
            "eligible_for_dated_research_screen": (
                MIN_DAYS_TO_LAST_TRADE <= days <= MAX_DAYS_TO_LAST_TRADE
                and row["settlement"] is not None
                and float(row["settlement"]) > 0
                and row["volume"] is not None
                and float(row["volume"]) > 0
                and row["open_interest"] is not None
                and float(row["open_interest"]) > 0
            ),
        }
        eligible.append(item)
    candidates = [item for item in eligible if item["eligible_for_dated_research_screen"]]
    candidates.sort(
        key=lambda item: (
            -float(item["open_interest"]),
            -float(item["volume"]),
            str(item["contract"]),
        )
    )
    selected = candidates[0] if candidates else None

    return {
        "schema_version": "c12_cffex_actual_contract_route.v1",
        "artifact_class": "derived_research_evidence",
        "research_only": True,
        "not_a_backtest": True,
        "portfolio_q": 0,
        "actual_contract_source_route": {
            "status": "SIX_RETROSPECTIVE_SAMPLES_OBSERVED_NOT_REPLAY_READY",
            "source_batch": "sources/c12-official-cash-futures-basis-20260815/manifest.json",
            "samples": samples,
            "supported": "The frozen official CSV files retain actual listed CFFEX T and TF contract rows and daily EOD fields across six sample dates. They are not a continuous futures series.",
            "not_supported": [
                "A complete every-session, point-in-time actual-contract history for all listed and expired Treasury-futures contracts.",
                "A point-in-time delivery-bond list, conversion-factor history, coupon/accrual record, contract-status master, exchange calendar, margin/limit/fee notices or broker schedule.",
                "A cash-bond or ETF execution record, bid/ask, premium/discount, financing/repo result, custody-account approval, personal account result, order, fill, return or five-year replay.",
            ],
        },
        "dated_t_family_research_screen": {
            "decision_date": CURRENT_DECISION_DATE.isoformat(),
            "screen": {
                "family": "T",
                "minimum_calendar_days_to_scheduled_last_trade": MIN_DAYS_TO_LAST_TRADE,
                "maximum_calendar_days_to_scheduled_last_trade": MAX_DAYS_TO_LAST_TRADE,
                "requires_positive_settlement_volume_and_open_interest": True,
                "ranking": ["open_interest_desc", "volume_desc", "contract_code_asc"],
                "calendar_boundary": "The T rule states that the last trading day is the second Friday of the delivery month, with a holiday/abnormal-event adjustment. This output uses the unadjusted second-Friday schedule solely for a dated research screen; a live use would require the exchange-adjusted calendar.",
            },
            "all_actual_t_rows": eligible,
            "selected_actual_contract": selected,
            "interpretation": {
                "status": "DATED_ACTUAL_CONTRACT_OBSERVATION_ONLY",
                "personal_access_verified": False,
                "delivery_bond_verified": False,
                "cash_leg_quote_verified": False,
                "order_or_position": "none",
                "return_or_backtest": "none",
                "boundary": "A single 2026-08-14 selection under a fixed screen is not an instruction, fill, position, five-year replay or performance result.",
            },
        },
    }


def _rulebook(route: dict[str, Any]) -> dict[str, Any]:
    selected = route["dated_t_family_research_screen"]["selected_actual_contract"]
    return {
        "schema_version": "c12_cash_futures_basis_rulebook.v1",
        "artifact_class": "research_specification",
        "status": "RESEARCH_SPECIFICATION_NOT_ACTION_READY",
        "research_only": True,
        "portfolio_q": 0,
        "formal_decision_eligible": False,
        "orders_or_positions": "none",
        "target_requirement": {
            "hard_standard": "each full calendar-year net return >= 5% AND annualized net return for every completed rolling five-calendar-year window >= 5%",
            "evidence_status": "not measured; no guarantee; no complete actual-contract/cash-bond/cost/fill ledger",
            "calculation_boundary": "Any eventual test must use a unit-NAV ledger with actual contracts, dated cash-bond inputs and recorded costs. A continuous futures return proxy is prohibited.",
        },
        "candidate_route": {
            "name": "C12 domestic Treasury cash/futures basis study",
            "actual_futures_leg": {
                "exchange": "China Financial Futures Exchange",
                "family": "10-year Treasury bond futures (T)",
                "dated_source_observation": selected,
                "direction_for_long_basis_research": "buy one exact eligible cash Treasury bond and sell the selected actual T contract only after all no-action gates pass",
                "contractual_basis": "CFFEX educational material defines clean-price basis as cash clean price minus futures price times the conversion factor, and describes buy-cash/sell-futures as long-basis exposure.",
            },
            "cash_bond_delivery_route": {
                "required_instrument": "one currently CFFEX-eligible book-entry fixed-coupon Treasury bond from the selected actual T contract's official deliverable list",
                "required_custody": "an approved CCDC or CSDC Treasury custody account declared through the futures member before delivery-month controls apply",
                "delivery_link": "physical delivery only; the CFFEX delivery rules specify delivery invoice, conversion factor, accrued interest and custody-account procedures",
                "status": "NOT_VERIFIED_FOR_THIS_CASE",
            },
            "exchange_traded_etf_substitute": {
                "illustrative_product": "SSE 511260, an exchange-traded 10-year Treasury-bond fund",
                "source_fact": "Its exchange disclosure says it uses optimized sampling to track an index of Treasury-bond constituents.",
                "classification": "RELATIVE_VALUE_HEDGE_ONLY_NOT_DELIVERY_LINKED",
                "reason": "A fund share is not the exact book-entry Treasury bond specified for futures delivery. It therefore cannot be treated as a delivery-basis lock; it retains index-tracking, duration, basket, ETF price-versus-NAV, fund-fee and execution differences.",
            },
        },
        "fixed_mechanics": {
            "contract_screen": {
                "data_source": "frozen official CFFEX actual-contract daily CSV rows only",
                "eligible_contract": "actual T row with positive settlement, volume and open interest and 60--150 unadjusted calendar days to the second-Friday scheduled last-trade date",
                "ranking": ["open_interest_desc", "volume_desc", "contract_code_asc"],
                "delivery_firewall": "No new research action after the last-trade schedule enters the 60-calendar-day screen boundary. Delivery-month use requires a separately verified custody-account approval and exchange-adjusted calendar.",
                "continuous_series_policy": "prohibited for accounting, selection, return, roll or target validation",
            },
            "cash_bond_screen": {
                "required_fields": [
                    "official selected-contract deliverable-bond identifier",
                    "official conversion factor for that bond and delivery month",
                    "cash clean price, accrued interest, coupon schedule and actual settlement convention from a dated permitted source",
                    "custody location and transferability consistent with the delivery rule",
                    "observed executable cash-bond bid/ask or a predeclared no-fill treatment",
                ],
                "selection": "Evaluate every officially eligible bond on the same dated information set; do not infer a cheapest-to-deliver bond from maturity alone.",
                "missing_field_action": "NO_ACTION_AND_NOT_TESTABLE",
            },
            "basis_and_carry_accounting": {
                "clean_price_basis": "B_i,t = P_clean_i,t - F_t * CF_i",
                "net_basis_concept": "NB_i,t = B_i,t - H_i,t, where H is carry/having-cost accounting that must include coupon accrual, funding or repo, cash settlement, futures exchange and broker fees, custody/transfer, margin-cash financing, taxes if applicable, and separately observed execution costs.",
                "delivery_invoice_reference": "Delivery invoice must follow the dated CFFEX delivery-rule equation using delivery settlement, conversion factor, accrued interest, delivery quantity and contract face amount.",
                "daily_accounting": "Use actual contract settlement marks and separately recorded cash-bond/ETF marks. Daily futures variation and any margin-cash funding must be ledgered; neither may be assumed away.",
                "boundary": "These are frozen research accounting fields, not a realized return, fill or yield assertion.",
            },
            "paired_execution_policy": {
                "allowed_state": "no state is executable under the current case evidence",
                "future_test_requirement": "A prospective or licensed historical ledger must predeclare same-window paired-leg instructions, timestamp, quote source, partial-fill state, cancellation state, no-fill state, spread/impact treatment and reconciliation of cash, futures and margin cash flows.",
                "prohibited": [
                    "using daily settlement as an assumed two-leg fill",
                    "using a continuous futures series",
                    "inventing cash-bond, ETF or futures fills",
                    "backfilling a deliverable basket or conversion factor from hindsight",
                ],
            },
        },
        "no_action_gates": [
            {
                "id": "C12-G1",
                "gate": "actual-contract and lifecycle evidence",
                "pass_condition": "Complete hash-bound, point-in-time actual T contract history and contract master for every test session; all selected contracts and rolls are actual codes.",
                "current_state": "FAIL",
            },
            {
                "id": "C12-G2",
                "gate": "cash-bond/delivery-basket match",
                "pass_condition": "Dated official deliverable-bond list, conversion factors, accrued interest/coupon inputs, cash settlement data and custody/transfer state exist for each selected contract.",
                "current_state": "FAIL",
            },
            {
                "id": "C12-G3",
                "gate": "ETF substitute boundary",
                "pass_condition": "If ETF is used, it is independently labelled relative-value only and its basket, duration, NAV premium/discount, fees and execution differences are fully ledgered; it cannot receive delivery-basis treatment.",
                "current_state": "FAIL",
            },
            {
                "id": "C12-G4",
                "gate": "financing and repo evidence",
                "pass_condition": "Effective-session cash financing or repo, cash settlement and coupon-reinvestment treatment are source-bound for every ledger session.",
                "current_state": "FAIL",
            },
            {
                "id": "C12-G5",
                "gate": "margin and position-limit evidence",
                "pass_condition": "Effective-session exchange margin, price-limit, position-limit, delivery-month control and the broker's margin overlay are source-bound for every ledger session.",
                "current_state": "FAIL",
            },
            {
                "id": "C12-G6",
                "gate": "fee and transfer-cost evidence",
                "pass_condition": "Exchange fees, broker commissions, cash-bond/ETF costs, custody/transfer charges and taxes are source-bound for every ledger session.",
                "current_state": "FAIL",
            },
            {
                "id": "C12-G7",
                "gate": "personal route and delivery-account evidence",
                "pass_condition": "A licensed futures broker confirms the current trading-code route and the applicable custody-account/delivery process for the individual, without recording personal information in this case.",
                "current_state": "FAIL",
            },
            {
                "id": "C12-G8",
                "gate": "executable paired-leg evidence",
                "pass_condition": "Dated bid/ask, depth or a conservative no-fill convention plus actual permissible broker cost data allow a two-leg execution ledger without invented fills.",
                "current_state": "FAIL",
            },
            {
                "id": "C12-G9",
                "gate": "strict annual and rolling-five-year outcome test",
                "pass_condition": "A frozen unit-NAV ledger produces the complete population of full-calendar-year and rolling five-calendar-year windows after costs and independently recomputes the hard 5% standard.",
                "current_state": "FAIL",
            },
        ],
        "source_scope": {
            "primary_batch": "sources/c12-official-cash-futures-basis-20260815/manifest.json",
            "rule_sources": [
                "CFFEX current T product page",
                "CFFEX dated T contract and Treasury-futures delivery rules",
                "CFFEX trader-suitability measures",
                "CFFEX official basis-strategy education material",
                "SSE 2023 bond-investor suitability rule",
                "SSE 511260 annual report",
            ],
            "actual_contract_source_scope": "Six retrospectively captured official CFFEX daily CSV samples, 2016--2026, each carrying actual listed contracts. This is a route observation rather than a full historical replay dataset.",
        },
    }


def _feasibility(route: dict[str, Any], rulebook: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "c12_cash_futures_basis_feasibility.v1",
        "artifact_class": "research_feasibility_conclusion",
        "research_only": True,
        "portfolio_q": 0,
        "status": "NOT_FEASIBLE_FOR_STRICT_5PCT_OR_PERSONAL_EXECUTION",
        "formal_decision_eligible": False,
        "return_result": None,
        "backtest_run": False,
        "orders_or_positions": "none",
        "conclusion": {
            "strict_target": "NOT_FEASIBLE: the case cannot establish, and must not claim, that every full calendar year or the annualized net return of every completed rolling five-calendar-year window clears 5% after costs.",
            "personal_execution": "NOT_FEASIBLE under case evidence: exchange-level rules show a possible customer/delivery framework, but this case holds no individual trading-code, broker-route, custody-account, delivery-process, commission, margin or execution evidence.",
            "cash_bond_delivery_route": "NOT_FEASIBLE under case evidence: the actual delivery relationship requires the exact official deliverable bond, conversion factor, approved custody route, cash-bond pricing/carry and delivery process. Those dated inputs are not present for a reproducible ledger.",
            "etf_substitute": "NOT_FEASIBLE as a cash-and-carry lock: the disclosed ETF is a fund using optimized sampling, not a contract-deliverable bond. It may be studied only as an unvalidated relative-value hedge, not as a convergence guarantee.",
            "why_actual_contract_samples_do_not_close_the_gap": "The frozen CFFEX CSV files prove a currently reachable source route for actual contracts on six retrospective dates. They are neither complete point-in-time history nor executable two-leg evidence, so they cannot support a return test.",
        },
        "verified_mechanics": [
            {
                "topic": "actual CFFEX contract identity",
                "evidence": "Six official CSV samples contain actual T/TF rows; the dated 2026-08-14 T screen selects T2612 under the frozen 60--150-calendar-day research filter.",
                "scope": "source-route observation only",
            },
            {
                "topic": "basis, conversion factor and carry concept",
                "evidence": "CFFEX educational material defines clean-price basis as cash clean price less futures price times conversion factor, and net basis as basis less holding cost.",
                "scope": "mechanical definition only; no live basis or return has been calculated",
            },
            {
                "topic": "physical delivery and custody",
                "evidence": "CFFEX delivery rules specify physical delivery, a deliverable book-entry Treasury, conversion factor, accrued interest and custody-account review; an unapproved account faces delivery-month position controls.",
                "scope": "dated exchange rule; no customer account outcome is inferred",
            },
            {
                "topic": "dated margin and position-limit framework",
                "evidence": "The 2020-effective T rule states a 2% base minimum margin, 3% from settlement two trading days before delivery, and client single-side limits of 4,000 lots from listing and 1,200 lots from the trading day before the delivery month. The current CFFEX product page also displays a 2% base minimum margin.",
                "scope": "Dated/product-page exchange framing only; it is not a complete effective-session history or a broker-specific margin/limit result.",
            },
            {
                "topic": "exchange-listed cash bond access",
                "evidence": "The 2023 SSE rule says ordinary investors may trade listed Treasury bonds, while intermediaries must apply suitability and transaction controls.",
                "scope": "generic market-rule context only; no exact delivery bond, stock availability, settlement or custody match is established",
            },
            {
                "topic": "ETF distinction",
                "evidence": "SSE disclosure describes 511260 as an ETF using optimized sampling of index constituent Treasuries with a tracking objective.",
                "scope": "does not make an ETF share a delivery instrument or validate an ETF/futures return",
            },
        ],
        "blocking_requirements": [
            {
                "id": "C12-B1",
                "blocker": "complete actual-contract historical population",
                "missing": "Every-session T contract rows, listings, expiries, delivery state and exchange-adjusted calendar are not frozen point in time.",
                "impact": "No full-calendar-year or rolling-five-year selection, roll or return population can be computed.",
            },
            {
                "id": "C12-B2",
                "blocker": "cash-bond/delivery-basket history",
                "missing": "Dated official deliverable lists, conversion factors, cash clean/dirty prices, coupon/accrual, custody and transfer state for each candidate contract.",
                "impact": "No matched cash-and-carry ledger or CTD decision can be reproduced.",
            },
            {
                "id": "C12-B3",
                "blocker": "ETF/futures mapping",
                "missing": "A predeclared duration/convexity/basket/NAV-premium/fund-fee/execution mapping and proof it is not treated as deliverable.",
                "impact": "An ETF alternative cannot support a delivery-basis or hard-return claim.",
            },
            {
                "id": "C12-B4",
                "blocker": "financing and repo path",
                "missing": "Effective cash financing or repo, cash settlement, coupon reinvestment and funding-cash treatment across every session.",
                "impact": "Net carry is unknown; assuming a favorable fixed rate would be fabrication.",
            },
            {
                "id": "C12-B5",
                "blocker": "margin, price-limit and position-limit path",
                "missing": "Effective-session exchange risk parameters, delivery-month controls and broker margin overlays across every session.",
                "impact": "The dated base margin and limit rules cannot be projected into a five-year ledger.",
            },
            {
                "id": "C12-B6",
                "blocker": "fee, custody and transfer-cost path",
                "missing": "Effective exchange fees, broker commissions, cash-bond/ETF costs, custody/transfer charges and taxes for every ledger session.",
                "impact": "Net return is unknown; exchange-level base fees do not prove the individual total cost.",
            },
            {
                "id": "C12-B7",
                "blocker": "personal suitability and delivery route",
                "missing": "Individual trading-code result, broker route, risk match, current account terms and Treasury custody-account/delivery confirmation.",
                "impact": "Case evidence cannot authorize or call the route personally operable.",
            },
            {
                "id": "C12-B8",
                "blocker": "two-leg fills and liquidity",
                "missing": "Dated cash-bond/ETF and actual-futures bid/ask, depth, paired timing, partial-fill/no-fill and rejection handling.",
                "impact": "Daily settlements and reported volume cannot be converted into an executable paired transaction.",
            },
            {
                "id": "C12-B9",
                "blocker": "strict-target endpoint population and independent check",
                "missing": "A frozen unit-NAV ledger, complete annual and rolling-five-year endpoint list, and maker-checker recomputation.",
                "impact": "The hard 5% annual and rolling-five-year standard is untestable.",
            },
            {
                "id": "C12-B10",
                "blocker": "rule-version continuity",
                "missing": "Complete effective-date history of CFFEX delivery, margin, limit, fee and operational notices plus the broker's overlays.",
                "impact": "Dated base rules cannot be silently projected across a five-year outcome test.",
            },
        ],
        "no_action_statement": "No external order, account opening, broker contact, cash-bond/ETF purchase, futures sale, short sale, repo, delivery submission or allocation is authorized by this research artifact.",
        "next_research_gate": [
            "Acquire a licensed or authorized point-in-time dataset covering actual T contracts, lifecycle/calendar, delivery basket and conversion factors, eligible cash-bond pricing/accrual/coupon data, and a documented data right.",
            "Obtain dated broker documentation for commission, margin, cash-bond/ETF route, custody and delivery operations; do not store personal data in the case.",
            "Freeze the exact paired-leg/no-fill/cost/roll/marking rules before looking at a result, then independently recompute every eligible annual and rolling-five-year window.",
            "If any required field remains missing, retain NO_ACTION_AND_NOT_TESTABLE rather than substituting a continuous series, generic ETF return or invented fill.",
        ],
        "source_scope": rulebook["source_scope"],
    }


def _route_markdown(route: dict[str, Any]) -> str:
    samples = route["actual_contract_source_route"]["samples"]
    rows = "\n".join(
        "| {date} | {t_count} | {tf_count} | {lead_t} | {lead_tf} |".format(
            date=item["trade_date"],
            t_count=item["actual_contract_rows_by_family"]["T"],
            tf_count=item["actual_contract_rows_by_family"]["TF"],
            lead_t=(item["leading_t"] or {}).get("contract", "n/a"),
            lead_tf=(item["leading_tf"] or {}).get("contract", "n/a"),
        )
        for item in samples
    )
    screen = route["dated_t_family_research_screen"]
    selected = screen["selected_actual_contract"]
    all_rows = "\n".join(
        "| {contract} | {settlement} | {volume} | {oi} | {last_trade} | {days} | {eligible} |".format(
            contract=item["contract"],
            settlement=item["settlement"],
            volume=item["volume"],
            oi=item["open_interest"],
            last_trade=item["scheduled_last_trade_date"],
            days=item["scheduled_days_to_last_trade"],
            eligible="yes" if item["eligible_for_dated_research_screen"] else "no",
        )
        for item in screen["all_actual_t_rows"]
    )
    selected_text = "none" if selected is None else selected["contract"]
    return f"""# C12 中金所实际国债期货合约数据路由

- 状态：**已观察到六个事后抓取样本，不能用于回放**（`SIX_RETROSPECTIVE_SAMPLES_OBSERVED_NOT_REPLAY_READY`）；`portfolio_q=0`。
- 来源批次：`sources/c12-official-cash-futures-basis-20260815/manifest.json`。
- 边界：原始 CFFEX CSV 是具体挂牌合约行，不是连续主力序列；它只证明数据路由与字段样本，不是收益测试、成交、订单、持仓或个人权限结论。

## 实际合约样本

| 交易日 | T 行数 | TF 行数 | T 中持仓量最高的行 | TF 中持仓量最高的行 |
|---|---:|---:|---|---|
{rows}

六份文件均保留合约代码和官方日终字段，但都是在原交易日之后获取。它们不构成逐日、时点可得的全量档案，也不包含现券账本、可交割券历史、经纪成本、成交记录或五年检验总体。

## 2026-08-14 固定 T 合约研究筛选

冻结筛选规则只接受结算价、成交量和持仓量均为正，且按“未作节假日调整的到期月第二个星期五”计算尚余 60--150 个日历日的实际 T 合约；排序依次为持仓量、成交量和合约代码。其在该日观察到的结果为 **{selected_text}**。规则文本允许节假日或异常情况下调整最后交易日，因此该计算不能直接作为实盘操作参数。

| 实际 T 合约 | 结算价 | 成交量 | 持仓量 | 计划最后交易日 | 剩余日数 | 通过筛选 |
|---|---:|---:|---:|---|---:|---|
{all_rows}

本工件不声称已取得该合约当前可交割券清单、转换因子、托管账户审核、现券报价、双腿成交、费用或收益。
"""


def _rulebook_markdown(rulebook: dict[str, Any]) -> str:
    gate_labels = {
        "C12-G1": "实际合约与生命周期证据",
        "C12-G2": "现券与可交割券篮子匹配",
        "C12-G3": "ETF 替代品边界",
        "C12-G4": "融资与回购证据",
        "C12-G5": "保证金与持仓限额证据",
        "C12-G6": "费用与过户成本证据",
        "C12-G7": "个人通道与托管账户证据",
        "C12-G8": "双腿可成交证据",
        "C12-G9": "年度与滚动五年严格结果检验",
    }
    gates = "\n".join(
        "| {id} | {gate} | {state} |".format(
            id=item["id"],
            gate=gate_labels[item["id"]],
            state=item["current_state"],
        )
        for item in rulebook["no_action_gates"]
    )
    selected = rulebook["candidate_route"]["actual_futures_leg"]["dated_source_observation"]
    selected_code = "none" if selected is None else selected["contract"]
    return f"""# C12 国债现券／期货基差研究规则书

- 状态：**仅为研究规格，不能执行**（`RESEARCH_SPECIFICATION_NOT_ACTION_READY`）；`portfolio_q=0`。
- 硬门槛：每个完整日历年度经成本后的净回报率、以及每个完整滚动五个日历年度区间的年化净回报率，均须不低于 5%。当前未测量，也不存在保证。
- 实际期货观察：冻结的 2026-08-14 中金所文件中，按筛选规则得到 `{selected_code}`；这不是订单，也不是已选定的实盘交易。

## 独立候选机制

精确现券路径研究“做多基差”：只有在同一份时点数据同时具备合约专属可交割券清单、转换因子、现券净价／应计利息／票息、托管路径、全成本和双腿可成交证据时，才研究“买入一只可交割记账式附息国债、卖出一手实际 CFFEX T 合约”。官方基差定义为 `B = 现券净价 - 期货价格 × 转换因子`；净基差必须扣除经完整观察的持有成本与其他成本。

中金所国债期货采用实物交割。日期明确的交割细则要求可交割国债、转换因子、应计利息和通过审核的国债托管账户。因此，现券必须与期货合约的交割篮子逐券匹配，而不能只按“久期相近”替代。

## ETF 边界

上交所披露的 511260 是以优化抽样跟踪国债指数成份券的交易型基金。ETF 份额不是合约指定的那一只记账式国债。故“买 ETF、卖 T”的组合最多是相对价值对冲研究：仍有组合、久期、折溢价、费用和执行差异，不能被称为可交割基差锁定。

## 禁止行动门槛

| ID | 门槛 | 当前状态 |
|---|---|---|
{gates}

任一门槛未通过时，唯一有效状态是 `NO_ACTION_AND_NOT_TESTABLE`。连续期货序列、未匹配的 ETF 回报或以日结算价假设两腿成交，都不能替代真实双腿成交与完整成本核算。
"""


def _feasibility_markdown(feasibility: dict[str, Any]) -> str:
    mechanics_rows = (
        (
            "实际 CFFEX 合约身份",
            "六个官方 CSV 样本含实际 T／TF 合约行；冻结的 2026-08-14 T 筛选得到 T2612。",
            "只证明数据路由样本；不是回放结果。",
        ),
        (
            "基差、转换因子与持有成本概念",
            "中金所教育材料定义“现券净价－期货价格×转换因子”的净价基差，并将净基差定义为基差扣除持有成本。",
            "仅是机制定义；未计算实时基差或回报。",
        ),
        (
            "实物交割与托管",
            "中金所交割细则规定实物交割、可交割记账式国债、转换因子、应计利息和国债托管账户审核；未审核账户面临交割月持仓控制。",
            "是日期明确的交易所规则，不推断任何客户账户结果。",
        ),
        (
            "日期明确的保证金与持仓限额框架",
            "2020 年生效的 T 细则列示 2% 基准最低保证金、交割前两个交易日结算起 3%，以及客户单边限额为上市后 4,000 手、交割月前一个交易日起 1,200 手；当前产品页也显示 2% 基准最低保证金。",
            "不能替代逐日有效参数或经纪商附加保证金／限额。",
        ),
        (
            "交易所现券市场准入",
            "2023 年上交所规则列示普通投资者可交易上市国债，同时要求中介机构落实适当性与交易控制。",
            "仅是一般市场规则；没有证明某一交割券、库存、结算或托管匹配。",
        ),
        (
            "ETF 区别",
            "上交所披露显示 511260 是通过优化抽样跟踪国债指数成份券的 ETF。",
            "不能使 ETF 份额成为交割工具，也不能验证 ETF／期货回报。",
        ),
    )
    blocker_labels = {
        "C12-B1": (
            "全量实际合约历史总体",
            "无法计算完整日历年度或滚动五年期间的选择、换月和回报总体。",
        ),
        "C12-B2": (
            "现券／可交割券篮子历史",
            "无法复现匹配的现券持有－期货交割账本或 CTD 决策。",
        ),
        "C12-B3": (
            "ETF／期货映射",
            "ETF 替代路径不能支持交割基差或严格回报主张。",
        ),
        "C12-B4": (
            "融资与回购路径",
            "净持有成本未知；假设有利的固定利率将构成虚构。",
        ),
        "C12-B5": (
            "保证金、涨跌停与持仓限额路径",
            "日期明确的基准参数不能被外推为五年逐日账本。",
        ),
        "C12-B6": (
            "费用、托管和过户成本路径",
            "净回报未知；交易所基准费用不等同于个人总成本。",
        ),
        "C12-B7": (
            "个人适当性与交割通道",
            "案例证据不能授权或认定该路线可由个人执行。",
        ),
        "C12-B8": (
            "双腿成交与流动性",
            "日结算价与公布成交量不能转化为可执行的配对交易。",
        ),
        "C12-B9": (
            "严格目标端点总体与独立复核",
            "年度和滚动五年的硬性 5% 标准无法检验。",
        ),
        "C12-B10": (
            "规则版本连续性",
            "日期明确的基础规则不能被无证据地投射到完整五年测试。",
        ),
    }
    blockers = "\n".join(
        "| {id} | {blocker} | {impact} |".format(
            id=item["id"],
            blocker=blocker_labels[item["id"]][0],
            impact=blocker_labels[item["id"]][1],
        )
        for item in feasibility["blocking_requirements"]
    )
    mechanics = "\n".join(
        f"| {topic} | {evidence} | {scope} |"
        for topic, evidence, scope in mechanics_rows
    )
    next_research_steps = (
        "以持牌或获授权渠道获得时点可得的数据集：实际 T 合约、生命周期／日历、交割券篮子与转换因子、可交割现券价格／应计利息／票息，以及明确的数据使用权。",
        "取得日期明确的经纪商文件，覆盖佣金、保证金、现券／ETF 通道、托管与交割操作；案例中不保存个人信息。",
        "在阅读结果前冻结双腿下单、无成交、成本、换月和盯市规则，再由独立复核人重算全部合格年度与滚动五年窗口。",
        "任一必需字段继续缺失时，保持 `NO_ACTION_AND_NOT_TESTABLE`，不得以连续序列、泛化 ETF 回报或虚构成交替代。",
    )
    next_gates = "\n".join(
        f"{index}. {item}" for index, item in enumerate(next_research_steps, 1)
    )
    return f"""# C12 可行性结论：境内国债现券／期货基差

## 结论

**NOT_FEASIBLE_FOR_STRICT_5PCT_OR_PERSONAL_EXECUTION（严格 5% 门槛及个人执行均不可行）。** `portfolio_q=0`；没有回报结果、回测、订单、持仓、配置或个人适当性结论。这里的严格门槛指每个完整日历年度经成本后净回报率、及每个完整滚动五年区间的年化净回报率均不低于 5%。

本次证据冻结确认了中金所具体国债期货合约行，以及实物交割现券基差的规则机制；但没有证明完整五年结果、双腿可成交性、净成本或个人账户路径。因此，严格 5% 标准既未达成也无法验证，不能表述为收益下限或保证。

## 已核实内容及其边界

| 主题 | 证据 | 边界 |
|---|---|---|
{mechanics}

## 严格门槛与个人路径为何失败

| ID | 阻断项 | 后果 |
|---|---|---|
{blockers}

实际合约 CSV 路径刻意不替代连续序列。六份源文件是事后获取的日度快照，不是完整的时点可得“现券／期货／交割／成本／成交”记录。用两条腿的日结算价直接盯市会虚构双腿成交；ETF 也无法提供精确现券路径所必需的交割关联。

## 唯一允许的后续研究门槛

{next_gates}

本案例不授权外部订单、开户、联系经纪商、买卖现券／ETF、卖出期货、回购融资或提交交割。
"""


def main() -> int:
    route = _route_artifact()
    rulebook = _rulebook(route)
    feasibility = _feasibility(route, rulebook)
    _write(ROUTE_JSON, json.dumps(route, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    _write(ROUTE_MD, _route_markdown(route))
    _write(RULEBOOK_JSON, json.dumps(rulebook, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    _write(RULEBOOK_MD, _rulebook_markdown(rulebook))
    _write(FEASIBILITY_JSON, json.dumps(feasibility, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    _write(FEASIBILITY_MD, _feasibility_markdown(feasibility))
    print("wrote C12 actual-contract route, rulebook and feasibility artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

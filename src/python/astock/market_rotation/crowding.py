"""Source-labelled flow-persistence proxy for rotation crowding review."""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime
from typing import Any, Mapping, Sequence


def build_rotation_crowding_proxy(
    rotation: Mapping[str, Any],
    observations: Sequence[Mapping[str, Any]],
    *,
    lookback_observations: int = 5,
) -> dict[str, Any]:
    """Build a bounded flow-persistence proxy from externally sourced records.

    The result is explicitly not a holder-position or investor-crowding model.
    It measures repeated net-flow attention only, requires source-labelled
    observations for every covered board, and carries zero promotion weight.
    """
    if lookback_observations < 2:
        raise ValueError("crowding proxy requires at least two observations")
    rankings = rotation.get("rankings")
    if not isinstance(rankings, Mapping):
        raise ValueError("rotation packet requires rankings")
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    errors: list[dict[str, str]] = []
    for observation in observations:
        normalized = _normalize_observation(observation)
        if normalized is None:
            errors.append({"code": "invalid_flow_observation", "message": "Ignored flow observation missing required source, timestamp, subject, quality, or net flow."})
            continue
        grouped[(normalized["component"], normalized["name"])].append(normalized)
    records: list[dict[str, Any]] = []
    required_count = 0
    covered_count = 0
    for component, rows in rankings.items():
        if component not in {"industries", "concepts"} or not isinstance(rows, Sequence):
            continue
        singular = "industry" if component == "industries" else "concept"
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            name = str(row.get("name") or "").strip()
            if not name:
                continue
            required_count += 1
            history = sorted(grouped[(singular, name)], key=lambda item: item["observed_at"])[-lookback_observations:]
            if len(history) < lookback_observations:
                continue
            covered_count += 1
            net_flow_sum = sum(item["net_flow"] for item in history)
            positive_days = sum(item["net_flow"] > 0 for item in history)
            records.append(
                {
                    "subject_type": singular,
                    "name": name,
                    "source_refs": sorted({item["source"] for item in history}),
                    "observation_count": len(history),
                    "net_flow_sum": round(net_flow_sum, 8),
                    "positive_flow_ratio": round(positive_days / len(history), 6),
                    "turnover_attention_percentile": row.get("turnover_attention_percentile"),
                    "multi_horizon_return_pct": row.get("multi_horizon_return_pct"),
                }
            )
    for index, record in enumerate(sorted(records, key=lambda item: (item["net_flow_sum"], item["name"])), start=1):
        record["net_flow_percentile"] = round(index / len(records), 6) if records else None
    for record in records:
        turnover = _float_or_none(record.get("turnover_attention_percentile"))
        return_5d = _float_or_none(
            record.get("multi_horizon_return_pct", {}).get("5d")
            if isinstance(record.get("multi_horizon_return_pct"), Mapping)
            else None
        )
        record["flow_attention_risk"] = bool(
            record["net_flow_percentile"] is not None
            and record["net_flow_percentile"] >= 0.9
            and record["positive_flow_ratio"] >= 0.8
            and turnover is not None
            and turnover >= 0.9
            and return_5d is not None
            and return_5d > 0
        )
    coverage = covered_count / required_count if required_count else 0.0
    return {
        "schema_version": "market-rotation-crowding-proxy.v1",
        "status": "available" if required_count and coverage >= 0.98 else "partial",
        "lookback_observations": lookback_observations,
        "required_count": required_count,
        "covered_count": covered_count,
        "coverage_ratio": round(coverage, 6),
        "records": sorted(records, key=lambda item: (item["subject_type"], item["name"])),
        "decision_weight": 0,
        "limitations": [
            "This is repeated net-flow attention, not investor crowding or holder-position concentration.",
            "It may only add a risk-review flag; it cannot promote an observation to an investment candidate.",
            "Margin, ownership, derivative positioning, and constituent-level flow data remain separate required evidence for a crowding conclusion.",
        ],
        "errors": errors,
    }


def _normalize_observation(value: Mapping[str, Any]) -> dict[str, Any] | None:
    component = str(value.get("subject_type") or "").strip().lower()
    name = str(value.get("name") or "").strip()
    source = str(value.get("source") or "").strip()
    quality = str(value.get("quality") or "").strip().lower()
    if component not in {"industry", "concept"} or not name or not source or quality not in {"full", "realtime"}:
        return None
    try:
        observed = datetime.fromisoformat(str(value.get("observed_at") or "").replace("Z", "+00:00"))
        flow = float(value.get("net_flow"))
    except (TypeError, ValueError):
        return None
    if observed.tzinfo is None or not math.isfinite(flow):
        return None
    return {"component": component, "name": name, "source": source, "observed_at": observed, "net_flow": flow}


def _float_or_none(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None

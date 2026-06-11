"""Tests for data provenance records."""

import json
from datetime import datetime, timezone
from typing import cast

import pytest

from astock.data_provenance import (
    DataProvenance,
    ProvenanceIssue,
    QualityTier,
    combine_provenance,
    worst_quality_tier,
)

FIXED_TS = "2026-06-12T09:30:00+08:00"


def test_record_serializes_to_json_ready_dict() -> None:
    """DataProvenance should expose stable JSON-ready fields."""
    record = DataProvenance(
        source="akshare.stock_zh_a_spot_em",
        timestamp=FIXED_TS,
        quality_tier=QualityTier.REALTIME,
        latency_ms=42.4,
        fallback_path=["akshare", "cache", "akshare"],
        warnings=[
            ProvenanceIssue(
                message="Field volume was missing",
                code="missing_field",
                details={"field": "volume", "observed_at": datetime(2026, 6, 12)},
            )
        ],
    )

    payload = record.to_dict()

    assert payload["schema_version"] == "data_provenance.v1"
    assert payload["source"] == "akshare.stock_zh_a_spot_em"
    assert payload["timestamp"] == FIXED_TS
    assert payload["quality_tier"] == "realtime"
    assert payload["quality_rank"] == 100
    assert payload["latency_ms"] == 42
    assert payload["fallback_path"] == ["akshare", "cache"]
    warning_payloads = cast(list[dict[str, object]], payload["warnings"])
    assert warning_payloads[0]["code"] == "missing_field"
    assert payload["errors"] == []
    assert payload["ok"] is True

    json.dumps(payload, ensure_ascii=False)


def test_record_round_trip_from_dict_and_json() -> None:
    """Records should round-trip through dict and JSON forms."""
    data = {
        "source": "baostock.query_history_k_data_plus",
        "timestamp": "2026-06-12T01:30:00Z",
        "quality_tier": "delayed",
        "latency_ms": 130,
        "fallback_path": ["baostock", "daily_cache"],
        "warnings": ["Realtime quote unavailable"],
        "errors": [{"message": "Minute data missing", "code": "missing_minute"}],
    }

    record = DataProvenance.from_dict(data)
    restored = DataProvenance.from_json(record.to_json())

    assert restored.source == "baostock.query_history_k_data_plus"
    assert restored.timestamp == "2026-06-12T01:30:00+00:00"
    assert restored.quality_tier is QualityTier.DELAYED
    assert restored.fallback_path == ("baostock", "daily_cache")
    assert restored.warnings[0].message == "Realtime quote unavailable"
    assert restored.errors[0].code == "missing_minute"
    assert restored.ok is False


def test_copy_helpers_are_immutable() -> None:
    """Helper methods should return changed copies without mutating the source."""
    original = DataProvenance(
        source="cache.quote_snapshot",
        timestamp=datetime(2026, 6, 12, 9, 30, tzinfo=timezone.utc),
        quality_tier="cached",
    )

    changed = (
        original.with_fallback("akshare.realtime")
        .with_warning("Used cached quote", code="fallback_cache")
        .with_error("No live source available", code="live_source_unavailable")
        .with_quality(QualityTier.DEGRADED)
    )

    assert original.fallback_path == ()
    assert original.warnings == ()
    assert original.errors == ()
    assert original.quality_tier is QualityTier.CACHED
    assert changed.fallback_path == ("akshare.realtime",)
    assert changed.warnings[0].code == "fallback_cache"
    assert changed.errors[0].code == "live_source_unavailable"
    assert changed.quality_tier is QualityTier.DEGRADED
    assert changed.ok is False


def test_combine_provenance_uses_worst_quality_and_max_latency() -> None:
    """Derived records should preserve source lineage and issue context."""
    quote_record = DataProvenance(
        source="akshare.quote",
        timestamp=FIXED_TS,
        quality_tier="realtime",
        latency_ms=55,
        warnings=["Quote source used fallback columns"],
    )
    flow_record = DataProvenance(
        source="eastmoney.sector_flow",
        timestamp=FIXED_TS,
        quality_tier="cached",
        latency_ms=210,
        fallback_path=["eastmoney.snapshot"],
        errors=[{"message": "Intraday flow unavailable", "code": "flow_missing"}],
    )

    combined = combine_provenance(
        [quote_record, flow_record],
        source="market_packet",
        timestamp=FIXED_TS,
    )

    assert combined.quality_tier is QualityTier.CACHED
    assert combined.latency_ms == 210
    assert combined.fallback_path == (
        "akshare.quote",
        "eastmoney.sector_flow",
        "eastmoney.snapshot",
    )
    assert combined.warnings[0].message == "Quote source used fallback columns"
    assert combined.errors[0].code == "flow_missing"
    assert combined.ok is False


def test_quality_tier_helpers_validate_values() -> None:
    """Quality helpers should reject empty and unknown values."""
    assert (
        worst_quality_tier(["realtime", QualityTier.DEGRADED]) is QualityTier.DEGRADED
    )

    with pytest.raises(ValueError, match="Unknown quality tier"):
        QualityTier.parse("fast")

    with pytest.raises(ValueError, match="At least one quality"):
        worst_quality_tier([])


def test_invalid_record_inputs_raise_clear_errors() -> None:
    """Invalid required fields should fail before records reach agents."""
    with pytest.raises(ValueError, match="source must not be empty"):
        DataProvenance(source="", timestamp=FIXED_TS, quality_tier="realtime")

    with pytest.raises(ValueError, match="timestamp must be ISO-8601"):
        DataProvenance(
            source="akshare", timestamp="not-a-date", quality_tier="realtime"
        )

    with pytest.raises(ValueError, match="Latency must not be negative"):
        DataProvenance(
            source="akshare",
            timestamp=FIXED_TS,
            quality_tier="realtime",
            latency_ms=-1,
        )

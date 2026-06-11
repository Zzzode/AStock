from pathlib import Path
from typing import Any

import pytest

from astock import capabilities


class DummyDatabase:
    def __init__(self, path: str):
        self.path = path

    async def connect(self) -> None:
        return None

    async def close(self) -> None:
        return None


def test_capability_provenance_record_and_combine() -> None:
    quote = capabilities.create_data_provenance_record(
        source="akshare.quote",
        timestamp="2026-06-12T09:30:00+08:00",
        quality_tier="realtime",
        latency_ms=50,
    )
    flow = capabilities.create_data_provenance_record(
        source="eastmoney.flow",
        timestamp="2026-06-12T09:30:00+08:00",
        quality_tier="cached",
        warnings=["flow source delayed"],
    )

    combined = capabilities.combine_data_provenance_records(
        [quote, flow],
        source="team_packet",
        timestamp="2026-06-12T09:30:00+08:00",
    )

    assert quote["quality_tier"] == "realtime"
    assert combined["quality_tier"] == "cached"
    assert combined["fallback_path"] == ["akshare.quote", "eastmoney.flow"]
    assert combined["warnings"][0]["message"] == "flow source delayed"


def test_capability_market_event_packet_from_quote() -> None:
    packet = capabilities.build_market_event_packet(
        {
            "code": "000001",
            "name": "Ping An Bank",
            "price": 15.5,
            "prev_close": 15.0,
            "volume_ratio": 3.0,
            "main_net_inflow": 450_000_000,
            "timestamp": "2026-06-12T10:30:00+08:00",
            "data_quality": "full_realtime",
        },
        payload_type="quote",
        source="unit-test",
    )

    assert packet["success"] is True
    assert packet["event_count"] == 3
    event_types = {event["event_type"] for event in packet["events"]}
    assert event_types == {"price_move", "volume_spike", "fund_flow_move"}


@pytest.mark.asyncio  # type: ignore[untyped-decorator]
async def test_get_quote_attaches_provenance_and_market_events(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    class DummyQuoteService:
        def __init__(self, db: DummyDatabase):
            self.db = db

        async def get_realtime(self, code: str) -> dict[str, Any]:
            return {
                "code": code,
                "name": "Ping An Bank",
                "price": 15.5,
                "prev_close": 15.0,
                "volume_ratio": 3.0,
                "data_quality": "full_realtime",
                "timestamp": "2026-06-12T10:30:00+08:00",
            }

    monkeypatch.setattr(capabilities, "Database", DummyDatabase)
    monkeypatch.setattr(capabilities, "QuoteService", DummyQuoteService)

    quote = await capabilities.get_quote("000001", db_path=tmp_path / "stocks.db")

    assert quote["provenance"]["quality_tier"] == "realtime"
    assert quote["provenance"]["source"] == "astock.quote_service"
    assert {event["event_type"] for event in quote["market_events"]} == {
        "price_move",
        "volume_spike",
    }


@pytest.mark.asyncio  # type: ignore[untyped-decorator]
async def test_build_team_packet_attaches_foundation_context(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    class DummyTeamResult:
        pass

    class DummyTeamAnalysisService:
        def __init__(self, db: DummyDatabase):
            self.db = db

        async def analyze(
            self,
            code: str,
            *,
            question: str,
            days: int,
            user_id: str,
        ) -> DummyTeamResult:
            return DummyTeamResult()

        def to_dict(self, result: DummyTeamResult) -> dict[str, Any]:
            return {
                "code": "000001",
                "question": "track?",
                "summary": "Data packet ready, awaiting Agent team reasoning",
                "recommended_roles": ["core"],
                "data_quality": {
                    "quote": "full_realtime",
                    "analysis": {"daily": "daily_only", "quote": "full_realtime"},
                    "screen": {"data_quality": "daily_only"},
                },
                "warnings": [],
                "orchestration": {"strategy": "packet_only_agent_reasoning"},
                "packet": {
                    "quote": {
                        "code": "000001",
                        "name": "Ping An Bank",
                        "price": 15.5,
                        "prev_close": 15.0,
                        "volume_ratio": 3.0,
                        "data_quality": "full_realtime",
                        "timestamp": "2026-06-12T10:30:00+08:00",
                    },
                    "analysis": {
                        "code": "000001",
                        "name": "Ping An Bank",
                        "indicators": {"close": 15.5, "macd_hist": 0.2},
                        "signals": [{"type": "macd_cross_up", "bias": "bullish"}],
                        "quote": {
                            "code": "000001",
                            "price": 15.5,
                            "prev_close": 15.0,
                            "data_quality": "full_realtime",
                        },
                        "data_quality": {
                            "daily": "daily_only",
                            "quote": "full_realtime",
                        },
                        "analyzed_at": "2026-06-12T10:30:00+08:00",
                    },
                    "screen": {
                        "mode": "single_stock",
                        "data_quality": "daily_only",
                        "results": [
                            {
                                "code": "000001",
                                "name": "Ping An Bank",
                                "matched_factors": ["macd_golden_cross"],
                                "factor_checks": {
                                    "macd_golden_cross": {
                                        "matched": True,
                                        "type": "technical",
                                        "field": "macd_hist",
                                        "weight": 2.0,
                                        "value": 0.2,
                                    }
                                },
                                "screened_at": "2026-06-12T10:30:00+08:00",
                            }
                        ],
                    },
                },
                "analyzed_at": "2026-06-12T10:30:00+08:00",
                "error": None,
            }

    monkeypatch.setattr(capabilities, "Database", DummyDatabase)
    monkeypatch.setattr(capabilities, "TeamAnalysisService", DummyTeamAnalysisService)

    packet = await capabilities.build_team_packet(
        "000001",
        question="track?",
        db_path=tmp_path / "stocks.db",
    )

    assert packet["provenance"]["source"] == "astock.team_packet"
    assert packet["provenance"]["quality_tier"] == "delayed"
    assert packet["market_events"]
    assert packet["packet"]["quote"]["provenance"]["quality_tier"] == "realtime"
    assert packet["packet"]["screen"]["market_events"][0]["event_type"] == (
        "technical_signal"
    )


def test_capability_research_ledger_round_trip(tmp_path: Path) -> None:
    ledger_path = tmp_path / "research-ledger.json"
    created = capabilities.create_research_entry(
        title="AI hardware pullback watch",
        thesis="Track leaders after a volume-backed pullback.",
        targets=["300001"],
        catalysts=["sector volume expansion"],
        risks=["failed breakout"],
        monitoring_triggers=[
            {
                "name": "volume confirmation",
                "condition": "volume ratio stays above 2 for two sessions",
                "metric": "volume_ratio",
                "threshold": 2,
            }
        ],
        tags=["ai", "hardware"],
        ledger_path=ledger_path,
    )
    entry_id = created["entry"]["entry_id"]

    observed = capabilities.record_research_observation(
        entry_id,
        observation_type="trigger_check",
        note="Trigger weakened; move to monitoring.",
        evidence={"volume_ratio": 1.4},
        status_after="monitoring",
        ledger_path=ledger_path,
    )
    listed = capabilities.list_research_entries(
        status="monitoring",
        tag="ai",
        ledger_path=ledger_path,
    )

    assert observed["entry"]["status"] == "monitoring"
    assert listed["total"] == 1
    assert listed["entries"][0]["entry_id"] == entry_id

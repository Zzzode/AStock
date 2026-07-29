import json
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


def test_capability_market_event_store_round_trip(tmp_path: Path) -> None:
    store_path = tmp_path / "market-events.jsonl"
    packet = capabilities.build_market_event_packet(
        {
            "code": "000001",
            "name": "Ping An Bank",
            "price": 15.5,
            "prev_close": 15.0,
            "volume_ratio": 3.0,
            "timestamp": "2026-06-12T10:30:00+08:00",
        },
        payload_type="quote",
        source="unit-test",
    )
    events = packet["events"]

    first_write = capabilities.record_market_events(
        events,
        event_store_path=store_path,
    )
    second_write = capabilities.record_market_events(
        events,
        event_store_path=store_path,
    )
    listed = capabilities.list_market_events(
        subject_code="000001",
        event_store_path=store_path,
    )
    replay = capabilities.replay_market_subject_events(
        subject_code="000001",
        event_store_path=store_path,
    )
    aggregate = capabilities.aggregate_market_events(event_store_path=store_path)

    assert first_write["inserted"] == 2
    assert second_write["duplicate"] == 2
    assert listed["total"] == 2
    assert {event["event_type"] for event in replay["events"]} == {
        "price_move",
        "volume_spike",
    }
    assert aggregate["aggregate"]["event_type"] == {
        "price_move": 1,
        "volume_spike": 1,
    }


def test_capability_market_subject_mapping_round_trip(tmp_path: Path) -> None:
    market_map_path = tmp_path / "market-map.json"
    node = capabilities.create_industry_chain_node(
        chain="AI infrastructure",
        stage="Compute hardware",
        role="Server supplier",
        downstream=["Cloud capex"],
    )
    saved = capabilities.upsert_market_subject_mapping(
        {
            "code": "1",
            "name": "Ping An Bank",
            "industry": "Banking",
            "industry_code": "BK0477",
            "sectors": ["Finance"],
            "themes": ["High dividend"],
            "concepts": ["Retail banking"],
            "industry_chain": [node["node"]],
            "source_refs": ["manual_seed"],
        },
        market_map_path=market_map_path,
    )
    resolved = capabilities.resolve_market_subject_context(
        "SZ000001",
        market_map_path=market_map_path,
    )
    listed = capabilities.list_market_subject_mappings(
        theme="High dividend",
        market_map_path=market_map_path,
    )

    assert saved["mapping"]["code"] == "000001"
    assert resolved["found"] is True
    assert resolved["relationships"]["industry"]["name"] == "Banking"
    assert listed["total"] == 1
    assert listed["mappings"][0]["themes"] == ["High dividend"]


def test_capability_fund_flow_anomaly_packet() -> None:
    packet = capabilities.build_fund_flow_anomaly_packet(
        {
            "code": "000001",
            "name": "Ping An Bank",
            "industry": "Banking",
            "theme": "High dividend",
            "change_pct": -1.5,
            "net_flow": 220_000_000,
            "timestamp": "2026-06-12T10:30:00+08:00",
        },
        source="unit-test",
    )
    event_types = {event["event_type"] for event in packet["market_events"]}
    divergence = next(
        event
        for event in packet["market_events"]
        if event["context"]["anomaly_type"] == "flow_price_divergence"
    )

    assert packet["success"] is True
    assert "fund_flow_move" in event_types
    assert packet["snapshot"]["subject"]["type"] == "stock"
    assert divergence["direction"] == "mixed"
    assert divergence["subject"]["code"] == "000001"


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
async def test_get_quote_assigns_and_discloses_local_observation_time(
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
                "change_percent": 3.33,
                "data_quality": "full_realtime",
            }

    monkeypatch.setattr(capabilities, "Database", DummyDatabase)
    monkeypatch.setattr(capabilities, "QuoteService", DummyQuoteService)

    quote = await capabilities.get_quote("000001", db_path=tmp_path / "stocks.db")

    assert quote["observed_at"]
    assert not quote["market_events"][0]["observed_at"].startswith("1970-")
    assert quote["provenance"]["warnings"][0]["message"] == (
        "Provider timestamp unavailable; assigned local observation timestamp."
    )


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
                        "indicators": {"open": 15.0, "high": 15.8, "low": 14.9, "close": 15.5, "volume": 2_000_000},
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
                                "matched_factors": ["range_expansion"],
                                "factor_checks": {
                                    "range_expansion": {
                                        "matched": True,
                                        "type": "market_structure",
                                        "field": "intraday_range_pct",
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
    assert packet["packet"]["screen"]["market_events"][0]["event_type"] == "alert_trigger"


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


def test_quality_feedback_is_bound_to_an_existing_research_entry(tmp_path: Path) -> None:
    ledger_path = tmp_path / "research-ledger.json"
    created = capabilities.create_research_entry(
        title="Quality feedback linkage",
        thesis="A feedback report must remain attached to its underlying research entry.",
        targets=["000001"],
        ledger_path=ledger_path,
    )
    entry_id = created["entry"]["entry_id"]
    postmortem = capabilities.record_research_postmortem(
        entry_id,
        outcome="The monitored thesis concluded with a documented outcome.",
        expected="A structured review would establish whether the thesis held.",
        actual="The structured review produced the quality-assessment input.",
        error_analysis="The feedback must be linked to a persisted outcome review.",
        lessons=["Anchor quality feedback to postmortem evidence"],
        ledger_path=ledger_path,
    )
    anchor = f"postmortem:{postmortem['postmortem']['postmortem_id']}"

    report = capabilities.record_quality_feedback(
        entry_id=entry_id,
        agent_scores=[{"role": "risk-analyst", "correct_calls": 1, "total_calls": 1}],
        notes="Validated after a structured review.",
        evidence_refs=[anchor],
        store_path=tmp_path / "quality-feedback.json",
        ledger_path=ledger_path,
    )

    linked = capabilities.get_research_entry(entry_id, ledger_path=ledger_path)["entry"]
    assert report["entry_id"] == entry_id
    assert linked["observations"][-1]["observation_type"] == "quality_feedback"
    assert linked["observations"][-1]["evidence"]["quality_feedback"]["entry_id"] == entry_id
    assert linked["observations"][-1]["evidence"]["quality_feedback"]["evidence_refs"] == [anchor]


def test_quality_feedback_requires_evidence_references(tmp_path: Path) -> None:
    ledger_path = tmp_path / "research-ledger.json"
    created = capabilities.create_research_entry(
        title="Quality feedback evidence",
        thesis="Team scores require source-addressable review evidence.",
        targets=["000001"],
        ledger_path=ledger_path,
    )

    with pytest.raises(ValueError, match="evidence reference"):
        capabilities.record_quality_feedback(
            entry_id=created["entry"]["entry_id"],
            agent_scores=[{"role": "risk-analyst", "correct_calls": 1, "total_calls": 1}],
            store_path=tmp_path / "quality-feedback.json",
            ledger_path=ledger_path,
        )


def test_quality_feedback_requires_a_prior_review_or_postmortem_anchor(tmp_path: Path) -> None:
    ledger_path = tmp_path / "research-ledger.json"
    created = capabilities.create_research_entry(
        title="Unanchored quality feedback",
        thesis="A quality score must have a reviewable outcome.",
        targets=["000001"],
        ledger_path=ledger_path,
    )

    with pytest.raises(ValueError, match="prior persisted"):
        capabilities.record_quality_feedback(
            entry_id=created["entry"]["entry_id"],
            agent_scores=[{"role": "risk-analyst", "correct_calls": 1, "total_calls": 1}],
            evidence_refs=["review-packet:unlinked"],
            store_path=tmp_path / "quality-feedback.json",
            ledger_path=ledger_path,
        )


def test_capability_research_index_query_and_duplicates(tmp_path: Path) -> None:
    ledger_path = tmp_path / "research-ledger.json"
    created = capabilities.create_research_entry(
        title="Bank sector re-rating",
        thesis="Low valuation plus credit impulse recovery.",
        targets=["000001", "600000"],
        tags=["bank", "value"],
        catalysts=["credit data rebound"],
        ledger_path=ledger_path,
    )
    entry_id = created["entry"]["entry_id"]
    capabilities.record_research_observation(
        entry_id,
        observation_type="evidence_update",
        note="Credit impulse improved.",
        status_after="monitoring",
        ledger_path=ledger_path,
    )

    index = capabilities.get_research_ledger_index(ledger_path=ledger_path)
    queried = capabilities.query_research_entries(
        statuses=["monitoring"],
        targets=["000001"],
        tags=["bank"],
        text="credit impulse",
        ledger_path=ledger_path,
    )
    duplicates = capabilities.find_research_duplicate_candidates(
        targets=["600000"],
        title="Bank sector re-rating",
        tags=["bank"],
        ledger_path=ledger_path,
    )

    assert index["index"]["entry_count"] == 1
    assert index["index"]["status_counts"]["monitoring"] == 1
    assert queried["total"] == 1
    assert queried["entries"][0]["entry_id"] == entry_id
    assert duplicates["total"] == 1
    assert duplicates["candidates"][0]["overlap"]["targets"] == ["600000"]


def test_capability_research_postmortem_records_observation(tmp_path: Path) -> None:
    ledger_path = tmp_path / "research-ledger.json"
    created = capabilities.create_research_entry(
        title="AI hardware thesis",
        thesis="Track AI hardware after pullback.",
        targets=["300001"],
        ledger_path=ledger_path,
    )
    entry_id = created["entry"]["entry_id"]

    result = capabilities.record_research_postmortem(
        entry_id,
        outcome="Thesis invalidated after demand signal weakened.",
        root_cause="timing",
        expected="Demand recovery would appear before earnings.",
        actual="Demand recovery lagged and price broke support.",
        error_analysis="Timing assumption was early.",
        lessons=["Require demand confirmation before upgrade"],
        status_after="invalidated",
        reviewed_at="2026-06-12T15:30:00+08:00",
        ledger_path=ledger_path,
    )

    assert result["postmortem"]["root_cause"] == "timing"
    assert result["entry"]["status"] == "invalidated"
    assert result["entry"]["observations"][0]["observation_type"] == "postmortem"
    assert result["entry"]["observations"][0]["evidence"]["postmortem"]["lessons"] == [
        "Require demand confirmation before upgrade"
    ]


def test_capability_evidence_packet_and_review_updates_status(tmp_path: Path) -> None:
    ledger_path = tmp_path / "research-ledger.json"
    created = capabilities.create_research_entry(
        title="Bank sector re-rating",
        thesis="Low valuation plus improving credit impulse may support re-rating.",
        targets=["000001"],
        invalidation_conditions=["credit spread widens above 120bp"],
        ledger_path=ledger_path,
    )
    entry_id = created["entry"]["entry_id"]
    evidence_item = capabilities.create_evidence_item(
        title="Credit spread breach",
        stance="contradicts",
        notes="credit spread widens above 120bp after weak macro data",
        payload={"invalidation_triggered": True},
        collected_at="2026-06-12T10:30:00+08:00",
    )
    evidence_packet = capabilities.create_evidence_packet(
        title="Daily thesis review packet",
        targets=["000001"],
        items=[evidence_item["item"]],
        collected_at="2026-06-12T10:30:00+08:00",
    )

    review = capabilities.review_research_entry(
        entry_id,
        evidence_packets=[evidence_packet["packet"]],
        apply_suggested_status=True,
        ledger_path=ledger_path,
    )

    assert review["success"] is True
    assert review["review"]["classification"] == "invalidated"
    assert review["status_updated"] is True
    assert review["entry"]["status"] == "invalidated"
    assert evidence_packet["all_source_refs"] == []
    assert evidence_packet["packet"]["items"][0]["stance"] == "contradicts"


def test_capability_quality_checks(tmp_path: Path) -> None:
    left = tmp_path / ".agents" / "skills" / "team" / "skill.md"
    right = tmp_path / ".codex" / "skills" / "team" / "SKILL.md"
    left.parent.mkdir(parents=True)
    right.parent.mkdir(parents=True)
    left.write_text("same prompt\n", encoding="utf-8")
    right.write_text("same prompt\n", encoding="utf-8")

    health = capabilities.evaluate_data_source_health(
        [
            {"source": "akshare.quote", "quality_tier": "realtime"},
            {
                "source": "eastmoney.flow",
                "quality_tier": "unavailable",
                "errors": ["timeout"],
            },
        ]
    )
    drift = capabilities.check_system_prompt_drift(root_path=tmp_path)
    report = capabilities.evaluate_research_report_quality("""
        Evidence source and data quality are stated.
        Risk and downside are covered.
        Contrarian bear case is included.
        Monitoring trigger and invalidation are explicit.
        Source exhaustion log is complete.
        Full-chain full_chain_universe coverage gap is explicit.
        Model reproducibility is recorded in the valuation audit.
        Review findings and repair plan close the review lifecycle.
        Final sign-off includes publishability score.
        Evidence depth covers customer order ASP utilization evidence gap.
        Model depth separates base business and growth segment gross profit net profit EPS.
        Investment committee portfolio position risk budget expected return is explicit.
        """)
    case_dir = tmp_path / "research-case"
    (case_dir / "analysis").mkdir(parents=True)
    (case_dir / "data").mkdir()
    (case_dir / "research_brief.md").write_text("single-stock report", encoding="utf-8")
    (case_dir / "gate_manifest.md").write_text("gate", encoding="utf-8")
    (case_dir / "gate_manifest.json").write_text(
        json.dumps(
                {
                    "report_type": "single-stock",
                    "depth_gates": [
                        "evidence_depth",
                        "broker_consensus_depth",
                        "model_depth",
                        "valuation_depth",
                        "ic_readiness",
                ],
            }
        ),
        encoding="utf-8",
    )
    (case_dir / "artifact_contract.md").write_text("contract", encoding="utf-8")
    (case_dir / "artifact_contract.json").write_text(
        json.dumps(
            {
                "artifacts": [
                    {
                        "path": "analysis/valuation_audit.md",
                        "required_fields": ["model_reproducibility"],
                        "minimum_depth": "valuation audit fixture",
                        "blocking_conditions": ["missing reproducibility"],
                        "reviewer_cycle": "R1_model",
                        "verifier_check": "evaluate_research_case_quality",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (case_dir / "review_log.md").write_text(
        "Publishability Score: 50\nPublishability Score: 93",
        encoding="utf-8",
    )
    (case_dir / "final_signoff.md").write_text("signoff", encoding="utf-8")
    (case_dir / "final_signoff.json").write_text(
        json.dumps({"signoff_status": "PASS", "publishability_score": 93}),
        encoding="utf-8",
    )
    (case_dir / "source_exhaustion_log.md").write_text("done", encoding="utf-8")
    (case_dir / "source_exhaustion_log.json").write_text(
        json.dumps({"status": "complete"}),
        encoding="utf-8",
    )
    (case_dir / "data" / "source_registry.md").write_text("sources", encoding="utf-8")
    (case_dir / "data" / "source_registry.json").write_text(
        json.dumps({"sources": []}),
        encoding="utf-8",
    )
    (case_dir / "data" / "claim_audit.md").write_text("claims", encoding="utf-8")
    (case_dir / "data" / "claim_audit.json").write_text(
        json.dumps({"claims": []}),
        encoding="utf-8",
    )
    (case_dir / "analysis" / "valuation_audit.md").write_text(
        "Model Reproducibility: PASS",
        encoding="utf-8",
    )
    valuation_sections = [
        "Final Valuation Table",
        "Three-Tier Targets",
        "Relative / PEG / PSG Comparison",
        "Seasonality Calibration",
        "Next-Quarter Threshold",
        "Method and Assumption Bridge",
        "Market-Expectation Valuation Bridge",
        "Broker/Street Comparison",
        "Market-Implied Sentiment Anchor",
        "Growth Earnings Dependency",
        "Full-Chain Classification Dependency",
    ]
    (case_dir / "analysis" / "valuation_model.md").write_text(
        "\n\n".join(
            f"## {section}\ncurrent share market cap broker Street market-implied weight target upside"
            for section in valuation_sections
        ),
        encoding="utf-8",
    )
    (case_dir / "analysis" / "segment_valuation_model.md").write_text(
        "segment SOTP revenue net profit multiple sensitivity validation trigger",
        encoding="utf-8",
    )
    (case_dir / "analysis" / "secondary_market_analysis.md").write_text(
        "price volume turnover drawdown relative performance valuation crowding "
        "support resistance seat institutional northbound financing trading style "
        "hot-money fund attitude trend swing",
        encoding="utf-8",
    )
    (case_dir / "data" / "current_valuation_model_20260630.json").write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "ticker": "000001",
                        "company": "Fixture Bank",
                        "current_price": 10.0,
                        "price_date": "2026-06-30",
                        "shares_100mn": 100.0,
                        "market_cap_100mn_cny": 1000.0,
                        "revenue_2026e_100mn": 200.0,
                        "np_2026e_100mn": 20.0,
                        "eps_2026e": 0.2,
                        "method": "PE",
                        "bear": 8.0,
                        "base": 10.0,
                        "bull": 12.0,
                        "market_implied_anchor": 10.0,
                        "fundamental_weight": 0.7,
                        "market_weight": 0.1,
                        "broker_weight": 0.2,
                        "final_target": 11.0,
                        "upside": 0.1,
                        "action": "core review",
                        "evidence_quality": "A",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (case_dir / "data" / "broker_street_consensus_20260630.md").write_text(
        "complete broker street consensus",
        encoding="utf-8",
    )
    (case_dir / "data" / "broker_street_consensus_20260630.json").write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "ticker": "000001",
                        "broker": "Fixture Securities",
                        "report_date": "2026-06-30",
                        "rating": "Buy",
                        "target_price": 12.0,
                        "revenue_E": {"2026E": 200.0},
                        "net_profit_E": {"2026E": 20.0},
                        "EPS_E": {"2026E": 0.2},
                        "method": "PE",
                        "implied_upside": 0.2,
                        "source_quality": "original_pdf",
                        "source_path": "sources/broker-reports/2026-06-30/index.md",
                        "valuation_weight": 0.2,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (case_dir / "review_findings_R0_evidence.json").write_text(
        json.dumps({"findings": [{"severity": "A", "status": "closed"}]}),
        encoding="utf-8",
    )
    (case_dir / "repair_plan_R0_evidence.md").write_text("repair", encoding="utf-8")
    (case_dir / "repair_plan_R0_evidence.json").write_text(
        json.dumps({"status": "closed"}),
        encoding="utf-8",
    )
    case_quality = capabilities.evaluate_research_case_quality(case_dir)
    skill_eval = capabilities.evaluate_skill_boundary_cases(
        [
            {
                "name": "boundary",
                "response": "Python returns data packets; agents explain risks.",
                "required_terms": ["data packets"],
            }
        ]
    )

    assert health["health"]["overall_status"] == "failing"
    assert drift["drift"]["status"] == "ok"
    assert drift["drift"]["pair_count"] == 1
    assert report["quality"]["status"] in {"pass", "excellent"}
    assert case_quality["quality"]["publishable"] is True
    assert skill_eval["evaluation"]["passed_count"] == 1

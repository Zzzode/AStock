from datetime import datetime, timezone

from astock.research import (
    EvidenceItem,
    EvidencePacket,
    EvidenceStance,
    make_evidence_item_id,
    make_evidence_packet_id,
)

FIXED_TIME = datetime(2026, 6, 12, 9, 30, tzinfo=timezone.utc)


def test_evidence_item_roundtrip_normalizes_json_ready_fields() -> None:
    item = EvidenceItem(
        title="Q1 earnings beat",
        source_refs={"source": "exchange filing", "url": "https://example.test/q1"},
        collected_at=FIXED_TIME,
        data_quality={"quality_tier": "snapshot", "ok": True},
        provenance={
            "source": "exchange",
            "timestamp": FIXED_TIME,
            "quality_tier": "snapshot",
        },
        market_events={
            "id": "mevt_1",
            "event_type": "news_policy_event",
            "title": "Earnings beat",
        },
        notes=["Net profit exceeded consensus", "Net profit exceeded consensus"],
        tags=["earnings", "earnings", "bank"],
        stance=EvidenceStance.SUPPORTS,
        item_type="filing",
        payload={"net_profit_yoy": 18.5},
    )

    restored = EvidenceItem.from_json(item.to_json())

    assert restored.item_id == item.item_id
    assert restored.source_refs[0]["source"] == "exchange filing"
    assert restored.provenance[0]["timestamp"] == FIXED_TIME.isoformat()
    assert restored.market_events[0]["event_type"] == "news_policy_event"
    assert restored.notes == ("Net profit exceeded consensus",)
    assert restored.tags == ("earnings", "bank")
    assert restored.stance == EvidenceStance.SUPPORTS


def test_evidence_packet_roundtrip_and_aggregates_item_refs() -> None:
    item = EvidenceItem(
        title="Sector fund flow confirmation",
        source_refs={"source": "market_data", "dataset": "sector_flow"},
        collected_at=FIXED_TIME,
        market_events={"id": "mevt_flow", "event_type": "fund_flow_move"},
        stance="supports",
    )
    packet = EvidencePacket(
        title="Bank sector evidence packet",
        targets=["000001", "600000", "000001"],
        collected_at=FIXED_TIME,
        source_refs={"source": "manual_note"},
        provenance={"source": "combined", "quality_tier": "snapshot"},
        market_events={"id": "mevt_price", "event_type": "price_move"},
        notes="Cross-source confirmation",
        tags=["bank", "flow"],
        items=[item],
        metadata={"review_cycle": 1},
    )

    restored = EvidencePacket.from_dict(packet.to_dict())

    assert restored.packet_id == packet.packet_id
    assert restored.targets == ("000001", "600000")
    assert restored.items[0].item_id == item.item_id
    assert len(restored.all_source_refs) == 2
    assert {event["id"] for event in restored.all_market_events} == {
        "mevt_flow",
        "mevt_price",
    }


def test_evidence_ids_are_stable_for_same_identity() -> None:
    source_refs = ({"source": "akshare", "dataset": "quote"},)

    first_item = make_evidence_item_id(
        title="Quote snapshot",
        source_refs=source_refs,
        collected_at=FIXED_TIME,
        item_type="quote",
    )
    second_item = make_evidence_item_id(
        title="Quote snapshot",
        source_refs=source_refs,
        collected_at=FIXED_TIME,
        item_type="quote",
    )
    first_packet = make_evidence_packet_id(
        title="Daily review packet",
        targets=["600000", "000001"],
        collected_at=FIXED_TIME,
    )
    second_packet = make_evidence_packet_id(
        title="Daily review packet",
        targets=["000001", "600000"],
        collected_at=FIXED_TIME,
    )

    assert first_item == second_item
    assert first_item.startswith("evid_")
    assert first_packet == second_packet
    assert first_packet.startswith("epkt_")

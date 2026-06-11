from datetime import datetime, timezone

from astock.research import (
    EvidenceItem,
    EvidencePacket,
    EvidenceStance,
    ResearchEntry,
    ResearchObservation,
    ResearchStatus,
    ThesisReview,
    ThesisReviewClassification,
    review_thesis,
)

FIXED_TIME = datetime(2026, 6, 12, 10, 0, tzinfo=timezone.utc)


def _entry() -> ResearchEntry:
    return ResearchEntry(
        title="Bank sector re-rating",
        thesis="Low valuation and improving credit impulse support re-rating.",
        targets=["000001"],
        invalidation_conditions=["credit spread widens above 120bp"],
        created_at=FIXED_TIME,
        updated_at=FIXED_TIME,
    )


def test_review_strengthened_by_supporting_evidence() -> None:
    item = EvidenceItem(
        title="Credit impulse improves",
        collected_at=FIXED_TIME,
        notes="Credit data confirms the re-rating thesis.",
        stance=EvidenceStance.SUPPORTS,
    )
    packet = EvidencePacket(
        title="Daily evidence packet",
        collected_at=FIXED_TIME,
        items=[item],
    )

    review = review_thesis(
        _entry(),
        evidence_packets=[packet],
        reviewed_at=FIXED_TIME,
    )

    assert review.classification == ThesisReviewClassification.STRENGTHENED
    assert review.supporting_evidence_ids == [item.item_id]
    assert review.evidence_packet_ids == [packet.packet_id]
    assert review.suggested_status is None


def test_review_weakened_by_contradicting_evidence() -> None:
    item = EvidenceItem(
        title="NIM pressure worsens",
        collected_at=FIXED_TIME,
        notes="NIM pressure offsets valuation support.",
        stance="contradicts",
    )

    review = review_thesis(
        _entry(),
        evidence_items=[item],
        reviewed_at=FIXED_TIME,
    )

    assert review.classification == ThesisReviewClassification.WEAKENED
    assert review.contradicting_evidence_ids == [item.item_id]


def test_review_invalidated_by_condition_match() -> None:
    item = EvidenceItem(
        title="Credit spread breach",
        collected_at=FIXED_TIME,
        notes="credit spread widens above 120bp after weak macro data",
        stance="contradicts",
    )

    review = review_thesis(
        _entry(),
        evidence_items=[item],
        reviewed_at=FIXED_TIME,
    )

    assert review.classification == ThesisReviewClassification.INVALIDATED
    assert review.suggested_status == ResearchStatus.INVALIDATED
    assert review.matched_invalidation_conditions == [
        "credit spread widens above 120bp"
    ]


def test_review_invalidated_by_observation_status() -> None:
    entry = _entry()
    observation = ResearchObservation(
        observation_type="thesis_check",
        note="Manual review marked thesis invalidated.",
        observed_at=FIXED_TIME,
        evidence={"stance": "contradicts"},
        status_after=ResearchStatus.INVALIDATED,
    )

    review = review_thesis(
        entry,
        observations=[observation],
        reviewed_at=FIXED_TIME,
    )

    assert review.classification == ThesisReviewClassification.INVALIDATED
    assert review.observation_count == 1
    assert "observation_status_after" in review.matched_invalidation_conditions


def test_review_required_for_mixed_stance_or_degraded_provenance() -> None:
    mixed_item = EvidenceItem(
        title="Conflicting sector signals",
        collected_at=FIXED_TIME,
        stance=EvidenceStance.MIXED,
    )
    degraded_packet = EvidencePacket(
        title="Low quality evidence packet",
        collected_at=FIXED_TIME,
        provenance={
            "source": "quote_fallback",
            "timestamp": FIXED_TIME,
            "quality_tier": "degraded",
        },
        items=[mixed_item],
    )

    review = review_thesis(
        _entry(),
        evidence_packets=[degraded_packet],
        reviewed_at=FIXED_TIME,
    )

    assert review.classification == ThesisReviewClassification.REVIEW_REQUIRED
    assert mixed_item.item_id in review.review_required_evidence_ids
    assert degraded_packet.packet_id in review.review_required_evidence_ids


def test_review_roundtrip_keeps_classification_and_metadata() -> None:
    review = review_thesis(
        _entry(),
        reviewed_at=FIXED_TIME,
    )

    restored = ThesisReview.from_json(review.to_json())

    assert restored.classification == ThesisReviewClassification.UNCHANGED
    assert restored.reviewed_at == FIXED_TIME
    assert restored.metadata["target_count"] == 1

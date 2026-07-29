"""Native tests for immutable public market-observation archives."""

from datetime import datetime, timezone

from astock.market_data import (
    build_public_market_observation_packet,
    verify_frozen_market_archive,
)


def test_public_observation_freezes_exact_market_rotation_packet(tmp_path) -> None:
    packet = build_public_market_observation_packet(
        subject="market_rotation",
        observation={
            "observed_at": "2026-07-28T15:00:00+08:00",
            "data_quality": "snapshot",
            "rankings": {"industries": [{"name": "电力", "change_pct": 1.2}]},
        },
    )

    archive_path = packet.write_frozen_archive(tmp_path)
    manifest = packet.to_dict()["source_manifest"]

    assert manifest["data_class"] == "public_observation"
    assert manifest["source"] == "akshare_public"
    assert verify_frozen_market_archive(
        archive_path,
        expected_archive_id=packet.archive_id,
        expected_source="akshare_public",
    )["status"] == "pass"
    assert packet.write_frozen_archive(tmp_path) == archive_path


def test_public_observation_requires_timezone_aware_timestamp() -> None:
    packet = build_public_market_observation_packet(
        subject="market_rotation",
        observation={"rankings": {}},
        observed_at=datetime(2026, 7, 28, tzinfo=timezone.utc),
    )

    assert packet.to_dict()["source_manifest"]["as_of"].endswith("+00:00")

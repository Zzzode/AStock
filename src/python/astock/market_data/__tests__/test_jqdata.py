"""Tests for the optional, fail-closed JQData minute observation adapter."""

from datetime import datetime, timezone

import pandas as pd
import pytest

from astock.market_data import JQDataMinuteAdapter


class FakeJQDataClient:
    last_arguments: dict[str, object] | None = None

    def get_bars(self, security: str, **_: object) -> pd.DataFrame:
        assert security == "600460.XSHG"
        self.last_arguments = _
        return pd.DataFrame(
            {
                "date": pd.to_datetime([
                    "2026-07-03 09:30:00",
                    "2026-07-03 09:31:00",
                    "2026-07-03 13:00:00",
                ]),
                "open": [10.0, 10.1, 10.2],
                "high": [10.1, 10.2, 10.3],
                "low": [9.9, 10.0, 10.1],
                "close": [10.1, 10.2, 10.3],
                "volume": [1000, 1500, 1200],
                "money": [10_000, 15_150, 12_300],
            }
        )


def test_jqdata_adapter_builds_raw_source_frozen_minute_observation(tmp_path) -> None:
    client = FakeJQDataClient()
    packet = JQDataMinuteAdapter(
        client=client,
        data_owner="research-data-owner",
        now=lambda: datetime(2026, 7, 3, 8, tzinfo=timezone.utc),
    ).build_minute_observation_packet(
        ["600460.XSHG"],
        start_time="2026-07-03 09:30:00",
        end_time="2026-07-03 13:00:00",
    )

    frame = packet.market_data["600460.XSHG"]
    assert packet.price_basis == "raw"
    assert packet.source_manifest["domains"] == {"minute_bars": "jqdata"}
    assert frame["date"].dt.strftime("%H:%M").tolist() == ["09:30", "09:31", "13:00"]
    assert packet.to_dict()["limitations"]
    assert client.last_arguments is not None
    assert client.last_arguments["skip_paused"] is False
    archive_path = packet.write_frozen_archive(tmp_path)
    assert archive_path.name == packet.source_manifest["archive_id"].removeprefix("sha256:") + ".json"
    assert packet.write_frozen_archive(tmp_path) == archive_path


def test_jqdata_adapter_fails_closed_without_authorized_access() -> None:
    with pytest.raises(ValueError, match="JQDATA_USERNAME"):
        JQDataMinuteAdapter(username="", password="", data_owner="owner").build_minute_observation_packet(
            ["600460.XSHG"], start_time="2026-07-03 09:30:00", end_time="2026-07-03 09:31:00"
        )
    with pytest.raises(ValueError, match="ATTESTED_BY"):
        JQDataMinuteAdapter(client=FakeJQDataClient(), data_owner="").build_minute_observation_packet(
            ["600460.XSHG"], start_time="2026-07-03 09:30:00", end_time="2026-07-03 09:31:00"
        )


def test_jqdata_adapter_rejects_non_session_bars() -> None:
    class InvalidSessionClient(FakeJQDataClient):
        def get_bars(self, security: str, **kwargs: object) -> pd.DataFrame:
            frame = super().get_bars(security, **kwargs)
            frame.loc[0, "date"] = pd.Timestamp("2026-07-03 12:00:00")
            return frame

    with pytest.raises(ValueError, match="outside A-share continuous sessions"):
        JQDataMinuteAdapter(
            client=InvalidSessionClient(), data_owner="research-data-owner"
        ).build_minute_observation_packet(
            ["600460.XSHG"], start_time="2026-07-03 09:30:00", end_time="2026-07-03 13:00:00"
        )

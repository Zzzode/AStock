"""Tests for the optional, fail-closed Tushare daily replay adapter."""

from datetime import datetime, timezone

import pandas as pd
import pytest

from astock import capabilities
from astock.market_data import TushareProBacktestAdapter, verify_frozen_market_archive


class FakeTushareClient:
    def trade_cal(self, **_: object) -> pd.DataFrame:
        return pd.DataFrame({"cal_date": ["20260701", "20260702", "20260703"]})

    def daily(self, **_: object) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "trade_date": ["20260703", "20260702", "20260701"],
                "open": [10.0, 11.0, 10.0],
                "high": [10.0, 11.0, 10.2],
                "low": [10.0, 11.0, 9.9],
                "close": [10.0, 11.0, 10.1],
                "vol": [0, 100, 100],
            }
        )

    def stk_limit(self, **_: object) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "trade_date": ["20260701", "20260702", "20260703"],
                "up_limit": [11.0, 11.0, 12.1],
                "down_limit": [9.0, 9.0, 9.9],
            }
        )

    def suspend_d(self, **_: object) -> pd.DataFrame:
        return pd.DataFrame({"trade_date": ["20260703"], "suspend_type": ["S"]})

    def dividend(self, **_: object) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "pay_date": ["20260702"],
                "cash_div_tax": [0.2],
                "ex_date": ["20260703"],
                "stk_div": [0.1],
                "stk_bo_rate": [0.0],
                "stk_co_rate": [0.0],
            }
        )

    def stock_basic(self, **_: object) -> pd.DataFrame:
        return pd.DataFrame({"list_status": ["L"], "delist_date": [None]})


def test_tushare_adapter_builds_raw_source_frozen_replay_input(tmp_path) -> None:
    adapter = TushareProBacktestAdapter(
        client=FakeTushareClient(),
        data_owner="research-data-owner",
        now=lambda: datetime(2026, 7, 3, 8, tzinfo=timezone.utc),
    )

    packet = adapter.build_daily_replay_packet(
        ["600460.SH"], start_date="2026-07-01", end_date="2026-07-03"
    )

    frame = packet.market_data["600460.SH"]
    assert packet.price_basis == "raw"
    assert packet.source_manifest["archive_id"].startswith("sha256:")
    assert frame["execution_status"].tolist() == ["tradable", "limit_up_locked", "halted"]
    assert frame["volume"].tolist() == [10_000.0, 10_000.0, 0.0]
    assert packet.corporate_actions["600460.SH"][0]["cash_per_share"] == 0.2
    assert packet.corporate_actions["600460.SH"][1]["share_factor"] == 1.1
    assert packet.delisting_status["600460.SH"]["list_status"] == "L"
    assert packet.to_dict()["market_data"]["600460.SH"][0]["date"].startswith("2026-07-01")
    archive_path = packet.write_frozen_archive(tmp_path)
    assert archive_path.name == packet.source_manifest["archive_id"].removeprefix("sha256:") + ".json"
    assert packet.write_frozen_archive(tmp_path) == archive_path
    verified = verify_frozen_market_archive(
        archive_path,
        expected_archive_id=packet.source_manifest["archive_id"],
        expected_source="tushare_pro",
    )
    assert verified["status"] == "pass"
    assert capabilities.verify_frozen_market_data_archive(
        archive_path,
        expected_archive_id=packet.source_manifest["archive_id"],
        expected_source="tushare_pro",
    )["status"] == "pass"


def test_tushare_intraday_suspension_event_blocks_open_fill_when_volume_is_nonzero() -> None:
    class IntradaySuspensionClient(FakeTushareClient):
        def daily(self, **_: object) -> pd.DataFrame:
            frame = super().daily()
            frame.loc[frame["trade_date"] == "20260703", "vol"] = 100
            return frame

    packet = TushareProBacktestAdapter(
        client=IntradaySuspensionClient(), data_owner="research-data-owner"
    ).build_daily_replay_packet(["600460.SH"], start_date="2026-07-01", end_date="2026-07-03")

    assert packet.market_data["600460.SH"].iloc[-1]["execution_status"] == "unknown"


def test_tushare_adapter_builds_frozen_historical_listing_universe_snapshot(tmp_path) -> None:
    class UniverseClient(FakeTushareClient):
        def stock_basic(self, **kwargs: object) -> pd.DataFrame:
            status = kwargs.get("list_status")
            if status == "L":
                return pd.DataFrame(
                    {"ts_code": ["600460.SH"], "list_status": ["L"], "list_date": ["20000801"], "delist_date": [None]}
                )
            if status == "D":
                return pd.DataFrame(
                    {"ts_code": ["000001.SZ"], "list_status": ["D"], "list_date": ["19910403"], "delist_date": ["20260702"]}
                )
            if status == "P":
                return pd.DataFrame(
                    {"ts_code": ["300001.SZ"], "list_status": ["P"], "list_date": ["20260702"], "delist_date": [None]}
                )
            if status == "G":
                return pd.DataFrame(
                    {"ts_code": ["688999.SH"], "list_status": ["G"], "list_date": ["20260801"], "delist_date": [None]}
                )
            return super().stock_basic(**kwargs)

    snapshot = TushareProBacktestAdapter(
        client=UniverseClient(), data_owner="research-data-owner"
    ).build_listing_universe_snapshot(as_of_date="2026-07-01")

    assert snapshot.members == ["000001.SZ", "600460.SH"]
    assert snapshot.to_dict()["source_ref"] == "tushare_pro.stock_basic:20260701"
    assert snapshot.write_frozen_archive(tmp_path).name == snapshot.archive_id.removeprefix("sha256:") + ".json"


def test_adapter_fails_closed_without_authorized_access() -> None:
    with pytest.raises(ValueError, match="TUSHARE_TOKEN"):
        TushareProBacktestAdapter(token="", data_owner="owner").build_daily_replay_packet(
            ["600460.SH"], start_date="2026-07-01", end_date="2026-07-03"
        )
    with pytest.raises(ValueError, match="ATTESTED_BY"):
        TushareProBacktestAdapter(client=FakeTushareClient(), data_owner="").build_daily_replay_packet(
            ["600460.SH"], start_date="2026-07-01", end_date="2026-07-03"
        )


def test_universe_snapshot_capability_is_a_thin_adapter(monkeypatch) -> None:
    expected = {
        "as_of_date": "20260701",
        "source_ref": "tushare_pro.stock_basic:20260701",
        "archive_id": "sha256:universe",
        "members": ["600460.SH"],
    }

    class StubPacket:
        def to_dict(self) -> dict[str, object]:
            return expected

    class StubAdapter:
        def __init__(self, **_: object) -> None:
            pass

        def build_listing_universe_snapshot(self, *, as_of_date: str) -> StubPacket:
            assert as_of_date == "2026-07-01"
            return StubPacket()

    monkeypatch.setattr(capabilities, "TushareProBacktestAdapter", StubAdapter)
    monkeypatch.setattr(
        capabilities,
        "load_user_config",
        lambda user_id="default": {"market_data_mode": "licensed_eod"},
    )
    assert capabilities.build_tushare_listing_universe_snapshot(as_of_date="2026-07-01") == expected


def test_paid_market_data_capabilities_are_blocked_in_public_observation_mode(monkeypatch) -> None:
    monkeypatch.setattr(
        capabilities,
        "load_user_config",
        lambda user_id="default": {"market_data_mode": "public_observation"},
    )

    with pytest.raises(ValueError, match="Licensed market-data capability is disabled"):
        capabilities.build_tushare_daily_replay_input(
            ["600460.SH"], start_date="2026-07-01", end_date="2026-07-03"
        )
    with pytest.raises(ValueError, match="Licensed market-data capability is disabled"):
        capabilities.build_tushare_listing_universe_snapshot(as_of_date="2026-07-01")
    with pytest.raises(ValueError, match="Licensed market-data capability is disabled"):
        capabilities.build_jqdata_minute_observation_input(
            ["600460.XSHG"],
            start_time="2026-07-01 09:30:00",
            end_time="2026-07-01 09:31:00",
        )


def test_portfolio_capability_accepts_json_records_from_source_adapter(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv("TUSHARE_TOKEN", "licensed-test-token")
    packet = TushareProBacktestAdapter(
        client=FakeTushareClient(), data_owner="research-data-owner"
    ).build_daily_replay_packet(
        ["600460.SH"], start_date="2026-07-01", end_date="2026-07-03"
    )
    archive_path = packet.write_frozen_archive(tmp_path)
    payload = packet.to_dict()

    result = capabilities.run_portfolio_backtest(
        payload["market_data"],
        {"2026-07-01": {"600460.SH": 0.5}},
        universe_references={"2026-07-01": "tushare:universe:20260701"},
        trading_calendar=payload["trading_calendar"],
        universe_snapshots={
            "2026-07-01": {
                "as_of_date": "2026-07-01",
                "source_ref": "tushare:universe:20260701",
                "archive_id": "sha256:universe-20260701",
                "members": ["600460.SH"],
            }
        },
        coverage_manifest={
            "corporate_actions": "covered",
            "delistings": "covered",
            "price_limits": "covered",
            "halts": "covered",
        },
        source_manifest=payload["source_manifest"],
        source_archive_path=str(archive_path),
        price_basis=payload["price_basis"],
        corporate_actions=payload["corporate_actions"],
        delisting_status=payload["delisting_status"],
        max_participation_rate=0.1,
    )

    assert result["source_assurance"]["status"] == "pass"
    assert result["reproducibility_assurance"]["status"] == "pass"
    assert result["trades"] == []

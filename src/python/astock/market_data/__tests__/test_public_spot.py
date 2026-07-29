"""Contract tests for the bounded public A-share spot parser."""

import json
from urllib.parse import parse_qs, urlparse

import pytest

from astock.market_data.public_spot import (
    fetch_eastmoney_a_share_spot,
    fetch_sina_a_share_spot,
    parse_eastmoney_a_share_spot_payload,
    parse_sina_a_share_spot_rows,
)


def test_public_spot_parser_normalizes_the_existing_a_share_schema() -> None:
    frame = parse_eastmoney_a_share_spot_payload(
        {
            "data": {
                "diff": [
                    {
                        "f12": "600460",
                        "f14": "士兰微",
                        "f2": 31.25,
                        "f3": 2.5,
                        "f5": 100,
                        "f6": 300_000_000,
                        "f8": 3.1,
                        "f9": 55.0,
                        "f23": 4.2,
                    }
                ]
            }
        }
    )

    assert frame.to_dict("records") == [
        {
            "代码": "600460",
            "名称": "士兰微",
            "最新价": 31.25,
            "涨跌幅": 2.5,
            "成交量": 100,
            "成交额": 300_000_000,
            "换手率": 3.1,
            "市盈率-动态": 55.0,
            "市净率": 4.2,
        }
    ]


def test_public_spot_parser_rejects_an_empty_or_invalid_response() -> None:
    with pytest.raises(ValueError, match="no rows"):
        parse_eastmoney_a_share_spot_payload({"data": {"diff": []}})


def test_eastmoney_fetch_collects_every_declared_page_before_returning(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Response:
        def __init__(self, payload: dict) -> None:
            self._payload = payload

        def read(self) -> bytes:
            return json.dumps(self._payload).encode("utf-8")

        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

    def fake_urlopen(request, *, timeout: int) -> Response:
        page = int(parse_qs(urlparse(request.full_url).query)["pn"][0])
        start = (page - 1) * 100
        end = min(start + 100, 101)
        rows = [
            {"f12": f"{600000 + index:06d}", "f14": f"测试{index}", "f2": 10.0, "f3": 1.0}
            for index in range(start, end)
        ]
        return Response({"data": {"total": 101, "diff": rows}})

    monkeypatch.setattr("astock.market_data.public_spot.urlopen", fake_urlopen)

    frame = fetch_eastmoney_a_share_spot()

    assert len(frame) == 101
    assert frame.iloc[0]["代码"] == "600000"
    assert frame.iloc[-1]["代码"] == "600100"


def test_sina_fallback_parser_normalizes_one_bounded_response() -> None:
    frame = parse_sina_a_share_spot_rows(
        [
            {
                "symbol": "sh600460",
                "name": "士兰微",
                "trade": "31.25",
                "changepercent": "2.5",
                "volume": "100",
                "amount": "300000000",
                "turnoverratio": "3.1",
                "per": "55.0",
                "pb": "4.2",
            }
        ]
    )

    assert frame.to_dict("records") == [
        {
            "代码": "600460",
            "名称": "士兰微",
            "最新价": "31.25",
            "涨跌幅": "2.5",
            "成交量": "100",
            "成交额": "300000000",
            "换手率": "3.1",
            "市盈率-动态": "55.0",
            "市净率": "4.2",
        }
    ]


def test_sina_fetch_requires_every_counted_page_before_returning_a_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Response:
        def __init__(self, text: str) -> None:
            self.text = text

        def raise_for_status(self) -> None:
            return None

    def fake_get(url: str, *, params=None, timeout: int) -> Response:
        if "StockCount" in url:
            return Response("2")
        assert params is not None
        assert params["page"] == "1"
        assert params["num"] == "100"
        return Response(
            "[{symbol:'sh600460',name:'士兰微',trade:'31.25',changepercent:'2.5'},"
            "{symbol:'sz000001',name:'平安银行',trade:'10.0',changepercent:'1.0'}]"
        )

    monkeypatch.setattr("astock.market_data.public_spot.requests.get", fake_get)

    frame = fetch_sina_a_share_spot()

    assert frame["代码"].tolist() == ["600460", "000001"]

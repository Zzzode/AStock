"""Bounded public A-share spot adapter for observation-only desk workflows."""

from __future__ import annotations

import json
import math
import re
from collections.abc import Mapping
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd
import requests


EASTMONEY_A_SHARE_SPOT_SOURCE = "eastmoney.push2.a_share_spot"
EASTMONEY_A_SHARE_SPOT_HOSTS = (
    "17.push2.eastmoney.com",
    "79.push2.eastmoney.com",
    "push2.eastmoney.com",
)
_A_SHARE_FILTER = "m:0+t:6+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2"
_A_SHARE_FIELDS = "f2,f3,f5,f6,f8,f9,f12,f14,f23"
SINA_A_SHARE_SPOT_SOURCE = "sina.market_center.a_share_spot"


def fetch_eastmoney_a_share_spot() -> pd.DataFrame:
    """Fetch one bounded public A-share cross-section without progress output.

    The adapter deliberately returns a single raw public snapshot.  It makes
    no claim about point-in-time listing membership, trading availability, or
    formal decision-data eligibility.
    """
    last_error: Exception | None = None
    def fetch_page(page: int) -> tuple[list[Mapping[str, Any]], int]:
        nonlocal last_error
        query = urlencode(
            {
                "pn": str(page),
                "pz": "100",
                "po": "1",
                "np": "1",
                "ut": "bd1d9ddb04089700cf9c27f6f7426281",
                "fltt": "2",
                "invt": "2",
                "fid": "f3",
                "fs": _A_SHARE_FILTER,
                "fields": _A_SHARE_FIELDS,
            }
        )
        for host in EASTMONEY_A_SHARE_SPOT_HOSTS:
            request = Request(
                f"https://{host}/api/qt/clist/get?{query}",
                headers={"User-Agent": "Mozilla/5.0"},
            )
            try:
                with urlopen(request, timeout=4) as response:  # nosec B310 - fixed HTTPS hosts
                    payload = json.loads(response.read().decode("utf-8", errors="replace"))
                data = payload.get("data") if isinstance(payload, Mapping) else None
                rows = data.get("diff") if isinstance(data, Mapping) else None
                total = data.get("total") if isinstance(data, Mapping) else None
                if not isinstance(rows, list) or not rows:
                    raise ValueError(f"East Money A-share spot page {page} has no rows")
                if not isinstance(total, int) or total < len(rows):
                    raise ValueError("East Money A-share spot response has no valid total")
                return [row for row in rows if isinstance(row, Mapping)], total
            except Exception as error:
                last_error = error
        raise RuntimeError(f"All East Money A-share spot mirrors failed for page {page}") from last_error

    first_rows, expected_count = fetch_page(1)
    page_count = math.ceil(expected_count / 100)
    if page_count < 1 or page_count > 100:
        raise ValueError("East Money A-share spot page count is outside the bounded adapter limit")
    if page_count == 1:
        return _frame_from_eastmoney_a_share_rows(first_rows)
    with ThreadPoolExecutor(max_workers=4, thread_name_prefix="eastmoney-a-share") as executor:
        remaining = list(executor.map(fetch_page, range(2, page_count + 1)))
    rows = [*first_rows, *(row for page_rows, _total in remaining for row in page_rows)]
    if len(rows) < expected_count:
        raise ValueError(
            f"East Money A-share spot response is incomplete: expected {expected_count}, got {len(rows)}"
        )
    return _frame_from_eastmoney_a_share_rows(rows)


def parse_eastmoney_a_share_spot_payload(payload: Mapping[str, Any]) -> pd.DataFrame:
    """Normalize a public East Money response into the established spot schema."""
    data = payload.get("data")
    rows = data.get("diff") if isinstance(data, Mapping) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError("East Money A-share spot response has no rows")
    return _frame_from_eastmoney_a_share_rows(
        [row for row in rows if isinstance(row, Mapping)]
    )


def _frame_from_eastmoney_a_share_rows(rows: list[Mapping[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(
        [
            {
                "代码": str(row.get("f12") or ""),
                "名称": str(row.get("f14") or ""),
                "最新价": row.get("f2"),
                "涨跌幅": row.get("f3"),
                "成交量": row.get("f5"),
                "成交额": row.get("f6"),
                "换手率": row.get("f8"),
                "市盈率-动态": row.get("f9"),
                "市净率": row.get("f23"),
            }
            for row in rows
        ]
    )
    if frame.empty:
        raise ValueError("East Money A-share spot response has no usable rows")
    return frame


def fetch_sina_a_share_spot() -> pd.DataFrame:
    """Fetch a bounded full Sina cross-section without progress UI.

    The upstream endpoint caps a page despite larger ``num`` values.  We first
    obtain its declared count and then retrieve the required pages with bounded
    four-way concurrency and per-request timeouts.  A missing page fails the
    whole snapshot instead of silently presenting a partial universe as full.
    """
    from akshare.stock.cons import (
        zh_sina_a_stock_count_url,
        zh_sina_a_stock_payload,
        zh_sina_a_stock_url,
    )
    from akshare.utils import demjson

    count_response = requests.get(zh_sina_a_stock_count_url, timeout=8)
    count_response.raise_for_status()
    match = re.search(r"\d+", count_response.text)
    if match is None:
        raise ValueError("Sina A-share spot count response is invalid")
    expected_count = int(match.group())
    page_size = 100
    page_count = math.ceil(expected_count / page_size)
    if page_count < 1 or page_count > 100:
        raise ValueError("Sina A-share spot page count is outside the bounded adapter limit")

    def fetch_page(page: int) -> list[Any]:
        response = requests.get(
            zh_sina_a_stock_url,
            params={**zh_sina_a_stock_payload, "page": str(page), "num": str(page_size)},
            timeout=8,
        )
        response.raise_for_status()
        raw_rows = demjson.decode(response.text)
        if not isinstance(raw_rows, list) or not raw_rows:
            raise ValueError(f"Sina A-share spot page {page} has no rows")
        return raw_rows

    with ThreadPoolExecutor(max_workers=4, thread_name_prefix="sina-a-share") as executor:
        pages = list(executor.map(fetch_page, range(1, page_count + 1)))
    raw_rows = [row for page in pages for row in page]
    if len(raw_rows) < expected_count:
        raise ValueError(
            f"Sina A-share spot response is incomplete: expected {expected_count}, got {len(raw_rows)}"
        )
    return parse_sina_a_share_spot_rows(raw_rows)


def parse_sina_a_share_spot_rows(rows: list[Any]) -> pd.DataFrame:
    """Normalize a bounded Sina response to the established spot schema."""
    normalized: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        normalized.append(
            {
                "代码": _normalize_sina_code(row.get("symbol")),
                "名称": str(row.get("name") or ""),
                "最新价": row.get("trade"),
                "涨跌幅": row.get("changepercent"),
                "成交量": row.get("volume"),
                "成交额": row.get("amount"),
                "换手率": row.get("turnoverratio"),
                "市盈率-动态": row.get("per"),
                "市净率": row.get("pb"),
            }
        )
    frame = pd.DataFrame(normalized)
    if frame.empty:
        raise ValueError("Sina A-share spot response has no usable rows")
    return frame


def _normalize_sina_code(value: Any) -> str:
    code = str(value or "").strip()
    return code[2:] if len(code) == 8 and code[:2].lower() in {"sh", "sz"} else code

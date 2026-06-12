"""News and announcement ingestion pipeline.

Fetches structured corporate events (announcements, earnings forecasts,
dividends) and market news from akshare, normalizes into a canonical
event schema for agent consumption.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import StrEnum
from functools import partial
from typing import Any, Optional

import akshare as ak
import pandas as pd

from ..utils import get_logger

logger = get_logger("news_pipeline")

_executor: Optional[ThreadPoolExecutor] = None


def _get_executor() -> ThreadPoolExecutor:
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="news_")
    return _executor


class EventType(StrEnum):
    NEWS = "news"
    EARNINGS_FORECAST = "earnings_forecast"
    EARNINGS_EXPRESS = "earnings_express"
    DIVIDEND = "dividend"
    EQUITY_PLEDGE = "equity_pledge"
    ANNOUNCEMENT = "announcement"
    POLICY = "policy"


class EventSeverity(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class CorporateEvent:
    """Normalized corporate event/announcement."""

    event_type: EventType
    code: str
    title: str
    summary: str = ""
    published_at: Optional[datetime] = None
    severity: EventSeverity = EventSeverity.MEDIUM
    source: str = ""
    url: str = ""
    raw_data: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type.value,
            "code": self.code,
            "title": self.title,
            "summary": self.summary,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "severity": self.severity.value,
            "source": self.source,
            "url": self.url,
            "raw_data": self.raw_data,
            "tags": self.tags,
        }


class NewsPipeline:
    """Fetches and normalizes corporate events for a stock."""

    async def get_stock_news(
        self,
        code: str,
        *,
        limit: int = 20,
    ) -> list[CorporateEvent]:
        """Fetch recent news for a stock."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            _get_executor(),
            partial(self._fetch_news_sync, code, limit),
        )

    async def get_earnings_forecast(
        self,
        code: str,
        *,
        recent_quarters: int = 4,
    ) -> list[CorporateEvent]:
        """Fetch recent earnings forecasts (业绩预告)."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            _get_executor(),
            partial(self._fetch_earnings_forecast_sync, code, recent_quarters),
        )

    async def get_dividends(
        self,
        code: str,
    ) -> list[CorporateEvent]:
        """Fetch dividend history."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            _get_executor(),
            partial(self._fetch_dividends_sync, code),
        )

    async def get_all_events(
        self,
        code: str,
        *,
        days: int = 90,
        include_news: bool = True,
        include_earnings: bool = True,
        include_dividends: bool = True,
    ) -> dict[str, Any]:
        """Fetch all event types for a stock and return a unified packet."""
        tasks = []
        if include_news:
            tasks.append(("news", self.get_stock_news(code, limit=20)))
        if include_earnings:
            tasks.append(("earnings", self.get_earnings_forecast(code)))
        if include_dividends:
            tasks.append(("dividends", self.get_dividends(code)))

        results: dict[str, list[CorporateEvent]] = {}
        errors: list[str] = []

        for label, coro in tasks:
            try:
                results[label] = await coro
            except Exception as e:
                logger.warning(f"Failed to fetch {label} for {code}: {e}")
                results[label] = []
                errors.append(f"{label}: {e}")

        all_events = []
        for events in results.values():
            all_events.extend(events)

        cutoff = datetime.now() - timedelta(days=days)
        filtered = [
            e for e in all_events
            if e.published_at is None or e.published_at >= cutoff
        ]
        filtered.sort(
            key=lambda e: e.published_at or datetime.min,
            reverse=True,
        )

        return {
            "code": code,
            "event_count": len(filtered),
            "events": [e.to_dict() for e in filtered],
            "fetched_at": datetime.now().isoformat(),
            "errors": errors,
            "data_quality": "full" if not errors else "partial",
        }

    def _fetch_news_sync(self, code: str, limit: int) -> list[CorporateEvent]:
        try:
            df = ak.stock_news_em(symbol=code)
        except Exception as e:
            logger.warning(f"stock_news_em failed for {code}: {e}")
            return []

        if df is None or df.empty:
            return []

        events: list[CorporateEvent] = []
        for _, row in df.head(limit).iterrows():
            published = _parse_datetime(row.get("发布时间"))
            title = str(row.get("新闻标题", ""))
            content = str(row.get("新闻内容", ""))

            severity = _classify_news_severity(title, content)
            tags = _extract_news_tags(title, content)

            events.append(CorporateEvent(
                event_type=EventType.NEWS,
                code=code,
                title=title,
                summary=content[:300] if content else "",
                published_at=published,
                severity=severity,
                source=str(row.get("文章来源", "eastmoney")),
                url=str(row.get("新闻链接", "")),
                tags=tags,
            ))
        return events

    def _fetch_earnings_forecast_sync(
        self, code: str, recent_quarters: int
    ) -> list[CorporateEvent]:
        events: list[CorporateEvent] = []
        today = date.today()

        quarters_to_check = []
        for i in range(recent_quarters):
            q_date = today - timedelta(days=90 * i)
            year = q_date.year
            month = q_date.month
            if month <= 3:
                quarter_str = f"{year}0331"
            elif month <= 6:
                quarter_str = f"{year}0630"
            elif month <= 9:
                quarter_str = f"{year}0930"
            else:
                quarter_str = f"{year}1231"
            quarters_to_check.append(quarter_str)

        for quarter in set(quarters_to_check):
            try:
                df = ak.stock_yjyg_em(date=quarter)
            except Exception as e:
                logger.debug(f"stock_yjyg_em failed for {quarter}: {e}")
                continue

            if df is None or df.empty:
                continue

            code_col = "股票代码"
            if code_col not in df.columns:
                continue

            matched = df[df[code_col].astype(str).str.strip() == code]
            for _, row in matched.iterrows():
                published = _parse_datetime(row.get("公告日期"))
                forecast_type = str(row.get("预告类型", ""))
                change_desc = str(row.get("业绩变动", ""))

                severity = EventSeverity.HIGH
                tags = ["earnings_forecast", forecast_type]

                events.append(CorporateEvent(
                    event_type=EventType.EARNINGS_FORECAST,
                    code=code,
                    title=f"业绩预告({quarter[:4]}Q{_quarter_from_date(quarter)}): {forecast_type}",
                    summary=change_desc[:300],
                    published_at=published,
                    severity=severity,
                    source="eastmoney",
                    tags=tags,
                    raw_data={
                        "quarter": quarter,
                        "forecast_type": forecast_type,
                        "predicted_value": _safe_float(row.get("预测数值")),
                        "change_ratio": _safe_float(row.get("业绩变动幅度")),
                        "prev_year_value": _safe_float(row.get("上年同期值")),
                        "reason": str(row.get("业绩变动原因", "")),
                    },
                ))
        return events

    def _fetch_dividends_sync(self, code: str) -> list[CorporateEvent]:
        try:
            df = ak.stock_history_dividend_detail(
                symbol=code, indicator="分红"
            )
        except Exception as e:
            logger.warning(f"stock_history_dividend_detail failed for {code}: {e}")
            return []

        if df is None or df.empty:
            return []

        events: list[CorporateEvent] = []
        for _, row in df.head(10).iterrows():
            announce_date = _parse_datetime(row.get("公告日期"))
            ex_date = row.get("除权除息日")
            scheme = str(row.get("分红方案说明", row.get("方案", "")))

            events.append(CorporateEvent(
                event_type=EventType.DIVIDEND,
                code=code,
                title=f"分红: {scheme}",
                summary=scheme,
                published_at=announce_date,
                severity=EventSeverity.MEDIUM,
                source="cninfo",
                tags=["dividend"],
                raw_data={
                    "scheme": scheme,
                    "ex_dividend_date": str(ex_date) if ex_date else None,
                },
            ))
        return events


def _parse_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()
    try:
        text = str(value).strip()
        if len(text) == 10:
            return datetime.strptime(text, "%Y-%m-%d")
        return datetime.fromisoformat(text.replace(" ", "T"))
    except (ValueError, TypeError):
        return None


def _safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        f = float(value)
        return f if not pd.isna(f) else None
    except (ValueError, TypeError):
        return None


def _quarter_from_date(quarter_str: str) -> int:
    month = int(quarter_str[4:6])
    if month <= 3:
        return 1
    elif month <= 6:
        return 2
    elif month <= 9:
        return 3
    return 4


def _classify_news_severity(title: str, content: str) -> EventSeverity:
    high_keywords = [
        "重大", "停牌", "退市", "违规", "立案", "处罚", "暴跌", "暴涨",
        "收购", "并购", "重组", "增发", "配股", "减持", "增持",
        "业绩预增", "业绩预减", "业绩亏损",
    ]
    medium_keywords = [
        "分红", "股东", "董事", "高管", "机构调研", "回购",
        "解禁", "质押", "担保",
    ]
    combined = title + content
    for kw in high_keywords:
        if kw in combined:
            return EventSeverity.HIGH
    for kw in medium_keywords:
        if kw in combined:
            return EventSeverity.MEDIUM
    return EventSeverity.LOW


def _extract_news_tags(title: str, content: str) -> list[str]:
    tags: list[str] = []
    combined = title + content
    tag_keywords = {
        "dividend": ["分红", "派息"],
        "buyback": ["回购"],
        "insider": ["增持", "减持", "高管"],
        "restructure": ["重组", "收购", "并购"],
        "earnings": ["业绩", "净利润", "营收"],
        "risk": ["风险", "退市", "违规", "处罚", "立案"],
        "fundraise": ["增发", "配股", "定增"],
    }
    for tag, keywords in tag_keywords.items():
        if any(kw in combined for kw in keywords):
            tags.append(tag)
    return tags

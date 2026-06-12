"""Tests for news pipeline (unit tests with mocked data)."""

from datetime import datetime

from astock.news import (
    CorporateEvent,
    EventSeverity,
    EventType,
    _classify_news_severity,
    _extract_news_tags,
)


def test_classify_severity_high():
    assert _classify_news_severity("重大资产重组", "") == EventSeverity.HIGH
    assert _classify_news_severity("", "公司收购标的") == EventSeverity.HIGH


def test_classify_severity_medium():
    assert _classify_news_severity("分红公告", "") == EventSeverity.MEDIUM
    assert _classify_news_severity("", "股东回购") == EventSeverity.MEDIUM


def test_classify_severity_low():
    assert _classify_news_severity("普通新闻", "无关紧要的内容") == EventSeverity.LOW


def test_extract_tags():
    tags = _extract_news_tags("公司发布回购公告", "拟回购股份")
    assert "buyback" in tags

    tags = _extract_news_tags("业绩预增", "净利润增长50%")
    assert "earnings" in tags

    tags = _extract_news_tags("高管增持", "")
    assert "insider" in tags


def test_corporate_event_to_dict():
    event = CorporateEvent(
        event_type=EventType.NEWS,
        code="000001",
        title="Test news",
        summary="Summary",
        published_at=datetime(2024, 1, 15, 10, 30),
        severity=EventSeverity.HIGH,
        source="eastmoney",
        tags=["earnings"],
    )
    d = event.to_dict()
    assert d["event_type"] == "news"
    assert d["code"] == "000001"
    assert d["severity"] == "high"
    assert d["published_at"] == "2024-01-15T10:30:00"

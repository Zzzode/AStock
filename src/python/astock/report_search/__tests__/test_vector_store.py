"""Tests for report vector store."""

import pytest

from astock.report_search import ReportVectorStore


@pytest.fixture
def tmp_store(tmp_path):
    return ReportVectorStore(tmp_path / "vectors.json")


def test_index_and_search(tmp_store):
    text = "平安银行2024年年报分析。营业收入同比下降3.2%，净利润微增1.8%。资产质量持续改善。"
    tmp_store.index_document("report-001", text, metadata={"ticker": "000001"})

    results = tmp_store.search("平安银行 净利润")
    assert len(results) >= 1
    assert results[0].doc_id == "report-001"
    assert results[0].score > 0


def test_index_removes_old_chunks(tmp_store):
    tmp_store.index_document("doc1", "first version of the document")

    tmp_store.index_document("doc1", "second version completely rewritten")
    stats2 = tmp_store.get_stats()

    assert stats2["total_documents"] == 1


def test_remove_document(tmp_store):
    tmp_store.index_document("doc1", "some text here")
    tmp_store.index_document("doc2", "other text there")

    removed = tmp_store.remove_document("doc1")
    assert removed >= 1
    stats = tmp_store.get_stats()
    assert stats["total_documents"] == 1
    assert "doc2" in stats["documents"]


def test_search_empty_store(tmp_store):
    results = tmp_store.search("anything")
    assert results == []


def test_doc_filter(tmp_store):
    tmp_store.index_document("sector-bank-001", "银行业分析报告")
    tmp_store.index_document("sector-tech-001", "科技行业分析报告")

    results = tmp_store.search("分析报告", doc_filter="sector-bank")
    assert all(r.doc_id.startswith("sector-bank") for r in results)


def test_large_document_chunking(tmp_store):
    text = "这是一段测试文本。" * 200
    count = tmp_store.index_document("large-doc", text, chunk_size=100)
    assert count > 1


def test_stats(tmp_store):
    tmp_store.index_document("doc1", "hello world test")
    tmp_store.index_document("doc2", "another document here")
    stats = tmp_store.get_stats()
    assert stats["total_documents"] == 2
    assert stats["total_chunks"] >= 2
    assert stats["vocabulary_size"] > 0

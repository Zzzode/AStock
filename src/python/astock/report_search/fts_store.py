"""SQLite FTS5 backend for the report vector store.

Replaces JSON-based storage for large document sets (>500 chunks).
Uses SQLite full-text search for keyword matching and BM25 ranking,
which is much more efficient than TF-IDF cosine similarity for
large vocabularies.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from ..utils import get_logger

logger = get_logger("fts_store")


@dataclass
class FTSSearchResult:
    """A ranked FTS5 search result."""

    chunk_id: str
    doc_id: str
    text: str
    score: float
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "text": self.text,
            "score": round(self.score, 4),
            "metadata": self.metadata,
        }


class FTSReportStore:
    """SQLite FTS5-backed report store for scalable full-text search.

    Use this instead of ReportVectorStore when document count exceeds ~500.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path("data/report-fts.db")
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._init_tables()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "FTSReportStore":
        self.connect()
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _ensure_connected(self) -> sqlite3.Connection:
        if self._conn is None:
            self.connect()
        assert self._conn is not None
        return self._conn

    def _init_tables(self) -> None:
        conn = self._ensure_connected()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id TEXT PRIMARY KEY,
                doc_id TEXT NOT NULL,
                text TEXT NOT NULL,
                metadata TEXT NOT NULL DEFAULT '{}'
            );

            CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON chunks(doc_id);

            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                text,
                content='chunks',
                content_rowid='rowid',
                tokenize='trigram'
            );

            CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
                INSERT INTO chunks_fts(rowid, text) VALUES (new.rowid, new.text);
            END;

            CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
                INSERT INTO chunks_fts(chunks_fts, rowid, text) VALUES('delete', old.rowid, old.text);
            END;

            CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
                INSERT INTO chunks_fts(chunks_fts, rowid, text) VALUES('delete', old.rowid, old.text);
                INSERT INTO chunks_fts(rowid, text) VALUES (new.rowid, new.text);
            END;
        """)
        conn.commit()

    def index_document(
        self,
        doc_id: str,
        text: str,
        *,
        metadata: Optional[dict[str, Any]] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
    ) -> int:
        """Split document into chunks and store in FTS5."""
        conn = self._ensure_connected()

        conn.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))

        chunks = _split_text(text, chunk_size=chunk_size, overlap=chunk_overlap)
        meta_json = json.dumps(metadata or {}, ensure_ascii=False)

        for i, chunk_text in enumerate(chunks):
            chunk_id = _make_chunk_id(doc_id, i)
            conn.execute(
                "INSERT INTO chunks (chunk_id, doc_id, text, metadata) VALUES (?, ?, ?, ?)",
                (chunk_id, doc_id, chunk_text, meta_json),
            )

        conn.commit()
        return len(chunks)

    def remove_document(self, doc_id: str) -> int:
        """Remove all chunks for a document."""
        conn = self._ensure_connected()
        cursor = conn.execute(
            "SELECT COUNT(*) FROM chunks WHERE doc_id = ?", (doc_id,)
        )
        count = cursor.fetchone()[0]
        conn.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))
        conn.commit()
        return count

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        doc_filter: Optional[str] = None,
    ) -> list[FTSSearchResult]:
        """Full-text search with BM25 ranking.

        Args:
            query: Search query (supports FTS5 query syntax)
            top_k: Maximum results
            doc_filter: Optional doc_id prefix filter
        """
        conn = self._ensure_connected()

        fts_query = _normalize_query(query)
        if not fts_query:
            return []

        if doc_filter:
            sql = """
                SELECT c.chunk_id, c.doc_id, c.text, c.metadata,
                       rank AS score
                FROM chunks_fts
                JOIN chunks c ON chunks_fts.rowid = c.rowid
                WHERE chunks_fts MATCH ?
                  AND c.doc_id LIKE ?
                ORDER BY rank
                LIMIT ?
            """
            cursor = conn.execute(sql, (fts_query, f"{doc_filter}%", top_k))
        else:
            sql = """
                SELECT c.chunk_id, c.doc_id, c.text, c.metadata,
                       rank AS score
                FROM chunks_fts
                JOIN chunks c ON chunks_fts.rowid = c.rowid
                WHERE chunks_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """
            cursor = conn.execute(sql, (fts_query, top_k))

        results: list[FTSSearchResult] = []
        for row in cursor.fetchall():
            results.append(FTSSearchResult(
                chunk_id=row["chunk_id"],
                doc_id=row["doc_id"],
                text=row["text"],
                score=-float(row["score"]),  # FTS5 rank is negative (lower=better)
                metadata=json.loads(row["metadata"]),
            ))

        return results

    def get_stats(self) -> dict[str, Any]:
        """Return store statistics."""
        conn = self._ensure_connected()
        chunk_count = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        doc_count = conn.execute(
            "SELECT COUNT(DISTINCT doc_id) FROM chunks"
        ).fetchone()[0]
        return {
            "total_chunks": chunk_count,
            "total_documents": doc_count,
            "backend": "sqlite_fts5",
            "db_path": str(self.db_path),
        }


def _split_text(text: str, *, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0:
        overlap = 0
    if overlap >= chunk_size:
        overlap = max(0, chunk_size // 5)

    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start += chunk_size - overlap
    return chunks


def _make_chunk_id(doc_id: str, index: int) -> str:
    seed = f"{doc_id}:{index}"
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:10]
    return f"chunk-{digest}"


def _normalize_query(query: str) -> str:
    """Convert natural language query to FTS5 trigram query.

    Trigram tokenizer matches exact substrings of 3+ characters.
    We split tokens and try each individually with OR logic.
    """
    tokens = query.strip().split()
    if not tokens:
        return ""
    # Each token >= 3 chars can be searched individually
    valid = [t for t in tokens if len(t) >= 3]
    if not valid:
        # Concatenate short tokens
        combined = "".join(tokens)
        return combined if len(combined) >= 3 else ""
    if len(valid) == 1:
        return valid[0]
    # Multiple terms: use OR to find any match
    return " OR ".join(valid)

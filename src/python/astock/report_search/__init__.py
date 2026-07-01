"""Lightweight vector store for semantic search over research reports.

Uses TF-IDF + cosine similarity as a zero-dependency baseline.
The interface supports drop-in replacement with embedding APIs (OpenAI, etc.)
when an API key is configured.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class DocumentChunk:
    """One indexed chunk of a research report."""

    chunk_id: str
    doc_id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    vector: list[float] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "text": self.text,
            "metadata": self.metadata,
            "vector": self.vector,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DocumentChunk":
        return cls(
            chunk_id=str(data["chunk_id"]),
            doc_id=str(data["doc_id"]),
            text=str(data["text"]),
            metadata=dict(data.get("metadata", {})),
            vector=list(data.get("vector", [])),
        )


@dataclass
class SearchResult:
    """A ranked search result."""

    chunk_id: str
    doc_id: str
    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "text": self.text,
            "score": round(self.score, 4),
            "metadata": self.metadata,
        }


class ReportVectorStore:
    """JSON-backed vector store with pluggable embedding backend.

    Supports "tfidf" (default), "openai", or "local" backends.
    When using openai/local, vectors are dense fixed-dimension embeddings.
    """

    def __init__(
        self,
        store_path: Optional[Path] = None,
        embedding_backend: str = "tfidf",
        **embedding_kwargs: Any,
    ):
        self.store_path = store_path or Path("data/report-vectors.json")
        self._chunks: dict[str, DocumentChunk] = {}
        self._vocabulary: dict[str, int] = {}
        self._idf: dict[str, float] = {}
        self._loaded = False
        self._embedding_backend = embedding_backend
        self._embedding_provider = None
        if embedding_backend != "tfidf":
            from .embeddings import get_embedding_provider
            self._embedding_provider = get_embedding_provider(
                embedding_backend, **embedding_kwargs
            )

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self._load()
            self._loaded = True

    def _load(self) -> None:
        if not self.store_path.exists():
            self._chunks = {}
            return
        try:
            raw = json.loads(self.store_path.read_text(encoding="utf-8"))
            self._chunks = {
                item["chunk_id"]: DocumentChunk.from_dict(item)
                for item in raw.get("chunks", [])
            }
            self._vocabulary = raw.get("vocabulary", {})
            self._idf = raw.get("idf", {})
        except Exception:
            self._chunks = {}

    def _save(self) -> None:
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": "report-vectors.v1",
            "updated_at": time.time(),
            "chunk_count": len(self._chunks),
            "vocabulary_size": len(self._vocabulary),
            "chunks": [c.to_dict() for c in self._chunks.values()],
            "vocabulary": self._vocabulary,
            "idf": self._idf,
        }
        self.store_path.write_text(
            json.dumps(payload, ensure_ascii=False),
            encoding="utf-8",
        )

    def index_document(
        self,
        doc_id: str,
        text: str,
        *,
        metadata: Optional[dict[str, Any]] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
    ) -> int:
        """Split document into chunks and index them.

        Returns the number of chunks created.
        """
        self._ensure_loaded()

        self._chunks = {
            cid: c for cid, c in self._chunks.items() if c.doc_id != doc_id
        }

        chunks = _split_text(text, chunk_size=chunk_size, overlap=chunk_overlap)
        for i, chunk_text in enumerate(chunks):
            chunk_id = _make_chunk_id(doc_id, i)
            chunk = DocumentChunk(
                chunk_id=chunk_id,
                doc_id=doc_id,
                text=chunk_text,
                metadata=metadata or {},
            )
            self._chunks[chunk_id] = chunk

        self._rebuild_index()
        self._save()
        return len(chunks)

    def remove_document(self, doc_id: str) -> int:
        """Remove all chunks for a document. Returns removed count."""
        self._ensure_loaded()
        to_remove = [cid for cid, c in self._chunks.items() if c.doc_id == doc_id]
        for cid in to_remove:
            del self._chunks[cid]
        if to_remove:
            self._rebuild_index()
            self._save()
        return len(to_remove)

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        min_score: float = 0.01,
        doc_filter: Optional[str] = None,
    ) -> list[SearchResult]:
        """Semantic search over indexed chunks.

        Args:
            query: Natural language query
            top_k: Max results to return
            min_score: Minimum cosine similarity threshold
            doc_filter: Optional doc_id prefix filter
        """
        self._ensure_loaded()
        if not self._chunks or (not self._vocabulary and not self._embedding_provider):
            return []

        query_vector = self._vectorize(query)
        if not query_vector:
            return []

        results: list[SearchResult] = []
        for chunk in self._chunks.values():
            if doc_filter and not chunk.doc_id.startswith(doc_filter):
                continue
            if not chunk.vector:
                continue
            score = _cosine_similarity(query_vector, chunk.vector)
            if score >= min_score:
                results.append(SearchResult(
                    chunk_id=chunk.chunk_id,
                    doc_id=chunk.doc_id,
                    text=chunk.text,
                    score=score,
                    metadata=chunk.metadata,
                ))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def get_stats(self) -> dict[str, Any]:
        """Return store statistics."""
        self._ensure_loaded()
        doc_ids = set(c.doc_id for c in self._chunks.values())
        return {
            "total_chunks": len(self._chunks),
            "total_documents": len(doc_ids),
            "vocabulary_size": len(self._vocabulary),
            "embedding_backend": self._embedding_backend,
            "documents": sorted(doc_ids),
        }

    def reindex_all(self) -> int:
        """Re-vectorize all chunks with current embedding backend.

        Use after switching embedding_backend to rebuild vectors.
        Returns number of chunks re-indexed.
        """
        self._ensure_loaded()
        if not self._chunks:
            return 0
        self._rebuild_index()
        self._save()
        return len(self._chunks)

    def _rebuild_index(self) -> None:
        """Rebuild vocabulary, IDF, and all chunk vectors."""
        if self._embedding_provider:
            texts = [chunk.text for chunk in self._chunks.values()]
            if texts:
                vectors = self._embedding_provider.embed_batch(texts)
                for chunk, vector in zip(self._chunks.values(), vectors):
                    chunk.vector = vector
            return

        all_tokens: list[list[str]] = []
        for chunk in self._chunks.values():
            tokens = _tokenize(chunk.text)
            all_tokens.append(tokens)

        vocab: set[str] = set()
        for tokens in all_tokens:
            vocab.update(tokens)
        self._vocabulary = {token: idx for idx, token in enumerate(sorted(vocab))}

        n_docs = len(all_tokens)
        doc_freq: Counter[str] = Counter()
        for tokens in all_tokens:
            doc_freq.update(set(tokens))
        self._idf = {
            token: math.log((n_docs + 1) / (freq + 1)) + 1
            for token, freq in doc_freq.items()
        }

        for chunk, tokens in zip(self._chunks.values(), all_tokens):
            chunk.vector = self._tfidf_vector(tokens)

    def _vectorize(self, text: str) -> list[float]:
        """Convert text to vector using configured backend."""
        if self._embedding_provider:
            return self._embedding_provider.embed(text)
        tokens = _tokenize(text)
        return self._tfidf_vector(tokens)

    def _tfidf_vector(self, tokens: list[str]) -> list[float]:
        if not tokens or not self._vocabulary:
            return []
        tf = Counter(tokens)
        vector = [0.0] * len(self._vocabulary)
        for token, count in tf.items():
            idx = self._vocabulary.get(token)
            if idx is not None:
                idf = self._idf.get(token, 1.0)
                vector[idx] = (count / len(tokens)) * idf
        return vector


def _tokenize(text: str) -> list[str]:
    """Simple tokenizer: split on non-alphanumeric, lowercase, filter short tokens."""
    text = text.lower()
    tokens = re.findall(r"[\u4e00-\u9fff]+|[a-z0-9]+", text)
    cjk_chars: list[str] = []
    result: list[str] = []
    for token in tokens:
        if re.match(r"[\u4e00-\u9fff]", token):
            for ch in token:
                cjk_chars.append(ch)
            for i in range(len(token) - 1):
                result.append(token[i : i + 2])
        else:
            if len(token) >= 2:
                result.append(token)
    return result


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _split_text(
    text: str, *, chunk_size: int = 500, overlap: int = 100
) -> list[str]:
    """Split text into overlapping chunks by character count."""
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

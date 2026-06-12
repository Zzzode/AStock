"""Pluggable embedding backend for report vector store.

Supports:
- tfidf: Default, zero-dependency TF-IDF (existing behavior)
- openai: OpenAI text-embedding-3-small via API
- local: Sentence-transformers via local model (requires torch)
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any, Optional


class EmbeddingProvider(ABC):
    """Abstract embedding provider interface."""

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Embed a single text string into a vector."""
        ...

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts. Default: iterate over embed()."""
        ...

    @abstractmethod
    def dimension(self) -> int:
        """Return the embedding dimension."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name identifier."""
        ...


class TfidfProvider(EmbeddingProvider):
    """TF-IDF provider — delegates to ReportVectorStore's built-in logic.

    This is a marker class; the vector store handles TF-IDF internally.
    embed() is not used directly when this provider is active.
    """

    @property
    def name(self) -> str:
        return "tfidf"

    def dimension(self) -> int:
        return -1  # Dynamic, depends on vocabulary

    def embed(self, text: str) -> list[float]:
        raise NotImplementedError("TF-IDF uses internal vectorization")

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError("TF-IDF uses internal vectorization")


class OpenAIProvider(EmbeddingProvider):
    """OpenAI embedding provider using text-embedding-3-small."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "text-embedding-3-small",
        base_url: Optional[str] = None,
    ):
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self._model = model
        self._base_url = base_url
        self._dimension = 1536
        if not self._api_key:
            raise ValueError(
                "OpenAI API key required: set OPENAI_API_KEY env var or pass api_key"
            )

    @property
    def name(self) -> str:
        return "openai"

    def dimension(self) -> int:
        return self._dimension

    def embed(self, text: str) -> list[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        import httpx

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        url = (self._base_url or "https://api.openai.com/v1") + "/embeddings"
        payload = {"model": self._model, "input": texts}

        response = httpx.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()

        results = sorted(data["data"], key=lambda x: x["index"])
        return [item["embedding"] for item in results]


class LocalProvider(EmbeddingProvider):
    """Local sentence-transformers embedding provider."""

    def __init__(self, model_name: str = "shibing624/text2vec-base-chinese"):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers required: pip install sentence-transformers"
            )
        self._model = SentenceTransformer(model_name)
        self._dimension = self._model.get_sentence_embedding_dimension()

    @property
    def name(self) -> str:
        return "local"

    def dimension(self) -> int:
        return self._dimension

    def embed(self, text: str) -> list[float]:
        embedding = self._model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        embeddings = self._model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()


def get_embedding_provider(
    backend: str = "tfidf",
    **kwargs: Any,
) -> EmbeddingProvider:
    """Factory function for embedding providers.

    Args:
        backend: One of "tfidf", "openai", "local"
        **kwargs: Provider-specific arguments (api_key, model, etc.)
    """
    if backend == "tfidf":
        return TfidfProvider()
    elif backend == "openai":
        return OpenAIProvider(**kwargs)
    elif backend == "local":
        return LocalProvider(**kwargs)
    else:
        raise ValueError(f"Unknown embedding backend: {backend}")

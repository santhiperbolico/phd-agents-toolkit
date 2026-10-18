"""Embedding provider with configurable device for PhD indexing."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from claudia_docs.config import Settings
from claudia_docs.loaders.base import EmbeddingsProvider
from langchain_huggingface import HuggingFaceEmbeddings

from phd_docs.config import resolve_embedding_device


@dataclass
class PhdEmbeddingsProvider(EmbeddingsProvider):
    """HuggingFace embeddings provider with an explicit compute device."""

    settings: Settings
    _model: HuggingFaceEmbeddings | None = field(default=None, init=False, repr=False)

    def get_model(self) -> Any:
        """
        Return the embedding model, loading it lazily on first use.

        Returns
        -------
        HuggingFaceEmbeddings
            Model configured for the selected device.
        """
        if self._model is None:
            device = resolve_embedding_device()
            self._model = HuggingFaceEmbeddings(
                model_name=self.settings.embedding_model,
                model_kwargs={"device": device},
                encode_kwargs={
                    "prompt": self.settings.embedding_passage_prefix,
                    "normalize_embeddings": self.settings.embedding_normalize,
                },
                query_encode_kwargs={
                    "prompt": self.settings.embedding_query_prefix,
                    "normalize_embeddings": self.settings.embedding_normalize,
                },
            )
        return self._model

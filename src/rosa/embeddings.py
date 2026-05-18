#  Copyright (c) 2024. Jet Propulsion Laboratory. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.

"""Optional SentenceTransformer encoder for hybrid memory (vector channel)."""

from __future__ import annotations

import logging
import os
from typing import List, Optional

logger = logging.getLogger(__name__)


class EmbeddingEncoder:
    """Lazy-loads SentenceTransformer; returns L2-normalized vectors as float lists."""

    def __init__(self, model_name: Optional[str] = None):
        self._model_name = model_name or os.getenv(
            "ROSA_MEMORY_EMBED_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2",
        )
        self._model = None

    def _ensure_model(self):
        if self._model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as e:
            raise RuntimeError(
                "Vector memory requires sentence-transformers. "
                "Install: pip install 'jpl-rosa[memory]' or pip install sentence-transformers"
            ) from e
        self._model = SentenceTransformer(self._model_name)

    def encode(self, text: str) -> List[float]:
        self._ensure_model()
        v = self._model.encode(
            text or "",
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return [float(x) for x in v]

    def is_available(self) -> bool:
        try:
            import sentence_transformers  # noqa: F401
        except ImportError:
            return False
        return True


_encoder_singleton: Optional[EmbeddingEncoder] = None


def get_embedding_encoder() -> EmbeddingEncoder:
    global _encoder_singleton
    if _encoder_singleton is None:
        _encoder_singleton = EmbeddingEncoder()
    return _encoder_singleton


def embeddings_enabled() -> bool:
    return os.getenv("ROSA_MEMORY_EMBEDDINGS", "1").lower() in ("1", "true", "yes")

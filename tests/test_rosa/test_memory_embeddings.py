#  Copyright (c) 2024. Jet Propulsion Laboratory. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.

import os
import tempfile
import unittest

from src.rosa.embeddings import EmbeddingEncoder, embeddings_enabled
from src.rosa.memory_hybrid import hybrid_retrieve
from src.rosa.memory_store import append_memory


def _sentence_transformers_installed() -> bool:
    try:
        import sentence_transformers  # noqa: F401
        return True
    except ImportError:
        return False


def _clear_socks_proxy_env():
    """SOCKS in ALL_PROXY breaks httpx without socksio; pop for HF hub / ST tests."""
    saved = {}
    for key in ("ALL_PROXY", "all_proxy"):
        if key in os.environ:
            saved[key] = os.environ.pop(key)
    return saved


def _restore_proxy_env(saved: dict) -> None:
    for key, val in saved.items():
        if val is not None:
            os.environ[key] = val


class _ProxyCleanMixin:
    def setUp(self):
        self._proxy_saved = _clear_socks_proxy_env()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        _restore_proxy_env(self._proxy_saved)


class TestEmbeddingEncoder(_ProxyCleanMixin, unittest.TestCase):
    @unittest.skipUnless(_sentence_transformers_installed(), "sentence-transformers not installed")
    def test_encode_returns_vector_and_self_similar(self):
        enc = EmbeddingEncoder()
        self.assertTrue(enc.is_available())
        v = enc.encode("ROS2 navigation uses costmaps.")
        self.assertGreater(len(v), 10)
        w = enc.encode("ROS2 navigation uses costmaps.")
        dot = sum(a * b for a, b in zip(v, w))
        self.assertGreater(dot, 0.99)


class TestHybridWithLiveEncoder(_ProxyCleanMixin, unittest.TestCase):
    @unittest.skipUnless(_sentence_transformers_installed(), "sentence-transformers not installed")
    def test_hybrid_retrieve_uses_query_embedding(self):
        tmp = tempfile.TemporaryDirectory()
        try:
            path = os.path.join(tmp.name, "mem.jsonl")
            enc = EmbeddingEncoder()
            e1 = enc.encode("The turtlebot battery was low yesterday.")
            e2 = enc.encode("Weather is sunny at the beach.")
            append_memory(
                path,
                {
                    "type": "summary",
                    "content": "Q: status\nA: turtlebot battery low",
                    "embedding": e1,
                    "memory_kind": "natural",
                },
            )
            append_memory(
                path,
                {
                    "type": "summary",
                    "content": "Q: chat\nA: beach weather sunny",
                    "embedding": e2,
                    "memory_kind": "natural",
                },
            )
            qe = enc.encode("Is the robot battery okay?")
            hits = hybrid_retrieve(path, "Is the robot battery okay?", qe, top_k=2)
            self.assertGreaterEqual(len(hits), 1)
            self.assertIn("battery", hits[0]["content"].lower())
        finally:
            tmp.cleanup()


class TestEmbeddingsEnv(unittest.TestCase):
    def test_embeddings_enabled_default(self):
        self.assertTrue(embeddings_enabled())


if __name__ == "__main__":
    unittest.main()

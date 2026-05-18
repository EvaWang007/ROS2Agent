#  Copyright (c) 2024. Jet Propulsion Laboratory. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.

import os
import tempfile
import unittest

from src.rosa.memory_hybrid import enrich_memory_for_write, format_retrieved_for_prompt, hybrid_retrieve
from src.rosa.memory_meta import (
    extract_query_meta,
    extract_tags_from_text,
    infer_memory_kind,
    memory_is_expired,
    memory_passes_scope,
    metadata_match_score,
    query_has_engineering_symbols,
)
from src.rosa.memory_store import append_memory, load_memories, retrieve_memories, score_lexical


class TestMemoryMeta(unittest.TestCase):
    def test_query_has_engineering_symbols_slash(self):
        self.assertTrue(query_has_engineering_symbols("echo /cmd_vel"))

    def test_query_has_engineering_symbols_plain(self):
        self.assertFalse(query_has_engineering_symbols("hello world"))

    def test_extract_query_meta_symbols(self):
        m = extract_query_meta("Check /odom and /scan")
        self.assertIn("/odom", m["symbols"])
        self.assertIn("/scan", m["symbols"])

    def test_infer_memory_kind(self):
        self.assertEqual(infer_memory_kind("uses /map topic"), "symbolic")
        self.assertEqual(infer_memory_kind("robot feels slow"), "natural")

    def test_extract_tags_from_text(self):
        self.assertIn("/tf", extract_tags_from_text("static /tf tree"))

    def test_metadata_match_score_domain(self):
        qm = {"domain": "navigation", "symbols": []}
        mem = {"domain": "navigation", "tags": []}
        self.assertGreater(metadata_match_score(qm, mem), 0.0)

    def test_memory_passes_scope(self):
        self.assertTrue(memory_passes_scope({"scene_id": "a"}, "a", None))
        self.assertFalse(memory_passes_scope({"scene_id": "b"}, "a", None))

    def test_memory_is_expired_false_when_missing(self):
        self.assertFalse(memory_is_expired({}))


class TestMemoryStoreAndHybrid(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self._tmpdir.name, "m.jsonl")

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_score_lexical_overlap(self):
        s = score_lexical("hello world test", "hello there world")
        self.assertGreater(s, 0.0)

    def test_append_optional_fields_roundtrip(self):
        ok = append_memory(
            self.path,
            {
                "type": "fact",
                "content": "Uses /cmd_vel for motion.",
                "memory_kind": "symbolic",
                "domain": "navigation",
                "tags": ["/cmd_vel"],
            },
        )
        self.assertTrue(ok)
        rows = load_memories(self.path)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["tags"], ["/cmd_vel"])
        self.assertEqual(rows[0]["domain"], "navigation")

    def test_retrieve_memories_lexical(self):
        append_memory(self.path, {"type": "summary", "content": "Q: odom\nA: filtered topic"})
        hits = retrieve_memories(self.path, "odom filtered", top_k=3)
        self.assertTrue(len(hits) >= 1)

    def test_hybrid_retrieve_without_embeddings(self):
        append_memory(
            self.path,
            {
                "type": "fact",
                "content": "controller_server inactive caused no motion",
                "memory_kind": "natural",
            },
        )
        append_memory(
            self.path,
            {
                "type": "fact",
                "content": "/cmd_vel geometry twist",
                "memory_kind": "symbolic",
                "tags": ["/cmd_vel"],
            },
        )
        hits = hybrid_retrieve(self.path, "/cmd_vel publisher", None, top_k=5)
        self.assertTrue(len(hits) >= 1)
        self.assertIn("_score_final", hits[0])

    def test_hybrid_retrieve_with_vectors(self):
        def _norm(v):
            s = sum(x * x for x in v) ** 0.5
            return [x / s for x in v] if s else v

        v = _norm([0.1 * i for i in range(1, 385)])
        w = [x + 0.001 * (i % 7) for i, x in enumerate(v)]
        w = _norm(w)

        append_memory(
            self.path,
            {
                "type": "summary",
                "content": "alpha beta gamma semantic blob",
                "embedding": v,
                "memory_kind": "natural",
            },
        )
        append_memory(
            self.path,
            {
                "type": "summary",
                "content": "unrelated zzz qqq",
                "embedding": w,
                "memory_kind": "natural",
            },
        )
        hits = hybrid_retrieve(
            self.path,
            "tell me about semantic blob gamma",
            v,
            top_k=2,
        )
        self.assertGreaterEqual(len(hits), 1)
        self.assertIn("semantic", hits[0]["content"])

    def test_format_retrieved_for_prompt_empty(self):
        self.assertIn("No long-term", format_retrieved_for_prompt([]))

    def test_enrich_memory_for_write(self):
        row = enrich_memory_for_write(
            {"type": "summary", "content": "touch /scan"},
            domain="navigation",
            tags=["/scan"],
        )
        self.assertEqual(row["memory_kind"], "symbolic")
        self.assertEqual(row["domain"], "navigation")


if __name__ == "__main__":
    unittest.main()

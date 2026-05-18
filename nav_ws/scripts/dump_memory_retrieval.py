#!/usr/bin/env python3
"""Print hybrid memory retrieval hits for a query (no LLM). Run from repo or set PYTHONPATH to src."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# nav_ws/scripts -> repo root is parents[2]
_REPO = Path(__file__).resolve().parents[2]
_SRC = _REPO / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

_DEFAULT_REL = Path("nav_ws") / "nav_ws" / "logs" / "long_term_memory.jsonl"


def _default_path() -> str:
    env = os.environ.get("ROSA_MEMORY_PATH")
    if env:
        return env
    return str(_REPO / "nav_ws" / "nav_ws" / "logs" / "long_term_memory.jsonl")


def main() -> None:
    for k in ("ALL_PROXY", "all_proxy"):
        os.environ.pop(k, None)

    query = " ".join(sys.argv[1:]).strip()
    if not query:
        print("Usage: ROSA_MEMORY_PATH=/path/to/long_term_memory.jsonl dump_memory_retrieval.py <query>", file=sys.stderr)
        print("Example: dump_memory_retrieval.py 'ROSA-MEM-TEST-7F3'", file=sys.stderr)
        sys.exit(1)

    path = _default_path()
    if not os.path.isfile(path):
        print(f"No file at {path!r} (set ROSA_MEMORY_PATH)", file=sys.stderr)
        sys.exit(2)

    from rosa.embeddings import embeddings_enabled, get_embedding_encoder
    from rosa.memory_hybrid import hybrid_retrieve

    q_emb = None
    if embeddings_enabled():
        try:
            enc = get_embedding_encoder()
            if enc.is_available():
                q_emb = enc.encode(query)
        except Exception as e:
            print(f"(query embedding skipped: {e})", file=sys.stderr)

    hits = hybrid_retrieve(path, query, q_emb, top_k=int(os.getenv("ROSA_MEMORY_TOP_K", "5")))
    print(f"path={path}\nquery={query!r}\nhits={len(hits)}\n")
    for i, h in enumerate(hits, 1):
        content = (h.get("content") or "").replace("\n", " ")[:400]
        score = h.get("_score_final", "?")
        mk = h.get("memory_kind", "?")
        print(f"--- {i} score={score} kind={mk} ---\n{content}\n")


if __name__ == "__main__":
    main()

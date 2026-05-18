#  Copyright (c) 2024. Jet Propulsion Laboratory. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.

"""Hybrid long-term memory retrieval: lexical + optional vector + metadata fusion."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from .memory_meta import (
    extract_query_meta,
    infer_memory_kind,
    memory_is_expired,
    memory_passes_scope,
    metadata_match_score,
    query_has_engineering_symbols,
)
from .memory_store import load_memories, score_lexical


def _cosine_dense(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(dot / (na * nb))


def hybrid_retrieve(
    path: str,
    query: str,
    query_embedding: Optional[List[float]],
    *,
    top_k: int = 5,
    scene_id: Optional[str] = None,
    robot_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    memories = load_memories(path)
    qm = extract_query_meta(query)
    symbolic_mode = query_has_engineering_symbols(query)

    if symbolic_mode:
        alpha_lex = float(os.getenv("ROSA_MEMORY_LEX_WEIGHT_SYMBOLIC", "0.65"))
    else:
        alpha_lex = float(os.getenv("ROSA_MEMORY_LEX_WEIGHT_NATURAL", "0.35"))
    beta_vec = max(0.0, min(1.0, 1.0 - alpha_lex))
    meta_w = float(os.getenv("ROSA_MEMORY_META_WEIGHT", "0.10"))
    sym_boost = float(os.getenv("ROSA_MEMORY_SYMBOLIC_BOOST", "0.08"))

    q_emb_ok = bool(query_embedding)
    candidates: List[Dict[str, Any]] = []

    for m in memories:
        if memory_is_expired(m):
            continue
        if not memory_passes_scope(m, scene_id, robot_id):
            continue

        lex = score_lexical(query, m.get("content", ""))
        mem_emb = m.get("embedding")
        if q_emb_ok and isinstance(mem_emb, list) and len(mem_emb) > 0:
            cos = _cosine_dense(query_embedding, mem_emb)
            vec01 = (cos + 1.0) / 2.0
            a_lex, b_vec = alpha_lex, beta_vec
        else:
            vec01 = 0.0
            a_lex, b_vec = 1.0, 0.0

        meta = metadata_match_score(qm, m)
        boost = sym_boost if (symbolic_mode and m.get("memory_kind") == "symbolic") else 0.0

        final = a_lex * lex + b_vec * vec01 + meta_w * meta + boost
        if final <= 0.0:
            continue
        row = dict(m)
        row["_score_lex"] = lex
        row["_score_vec"] = vec01
        row["_score_meta"] = meta
        row["_score_final"] = final
        candidates.append(row)

    candidates.sort(key=lambda x: x["_score_final"], reverse=True)
    return candidates[:top_k]


def format_retrieved_for_prompt(hits: List[Dict[str, Any]], max_lines: int = 8) -> str:
    if not hits:
        return "(No long-term memories matched this query.)"
    lines: List[str] = []
    for i, h in enumerate(hits[:max_lines], start=1):
        score = h.get("_score_final", 0.0)
        kind = h.get("memory_kind") or "unknown"
        typ = h.get("type", "?")
        body = (h.get("content") or "").replace("\n", " ").strip()
        if len(body) > 220:
            body = body[:220] + "…"
        lines.append(f"[Memory#{i}][{score:.2f}][{kind}][{typ}] {body}")
    return "\n".join(lines)


def enrich_memory_for_write(
    base: Dict[str, Any],
    *,
    embedding: Optional[List[float]] = None,
    scene_id: Optional[str] = None,
    robot_id: Optional[str] = None,
    domain: Optional[str] = None,
    tags: Optional[List[str]] = None,
    memory_kind: Optional[str] = None,
) -> Dict[str, Any]:
    out = dict(base)
    content = out.get("content", "")
    out["memory_kind"] = memory_kind or infer_memory_kind(str(content))
    if embedding is not None:
        out["embedding"] = embedding
    if scene_id:
        out["scene_id"] = scene_id
    if robot_id:
        out["robot_id"] = robot_id
    if domain:
        out["domain"] = domain
    if tags is not None:
        out["tags"] = tags
    return out

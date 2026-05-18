#  Copyright (c) 2024. Jet Propulsion Laboratory. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.

"""JSONL long-term memory store with lexical scoring (hybrid vector layer is separate)."""

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Dict, List
from uuid import uuid4


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _norm(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def _score(query: str, content: str) -> float:
    q_tokens = set(_norm(query).split())
    c_tokens = set(_norm(content).split())
    if not q_tokens or not c_tokens:
        return 0.0
    inter = len(q_tokens & c_tokens)
    return inter / (len(q_tokens) ** 0.5)


def score_lexical(query: str, content: str) -> float:
    """Public alias for lexical overlap (used by hybrid retrieval)."""
    return _score(query, content)


def _line_hash(mem_type: str, content: str) -> str:
    raw = f"{mem_type}|{_norm(content)}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_memories(path: str) -> List[Dict]:
    if not os.path.exists(path):
        return []
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    return out


def append_memory(path: str, memory: Dict) -> bool:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    existing = load_memories(path)
    sig = _line_hash(memory["type"], memory["content"])
    for m in existing:
        if m.get("sig") == sig:
            return False

    row = {
        "memory_id": memory.get("memory_id", str(uuid4())),
        "user_id": memory.get("user_id", "default"),
        "type": memory["type"],
        "content": memory["content"],
        "source": memory.get("source", "inferred"),
        "confidence": float(memory.get("confidence", 0.7)),
        "created_at": memory.get("created_at", _now_iso()),
        "last_used_at": memory.get("last_used_at", _now_iso()),
        "sig": sig,
    }
    for opt in (
        "embedding",
        "memory_kind",
        "scene_id",
        "robot_id",
        "domain",
        "tags",
        "expires_at",
    ):
        if opt in memory and memory[opt] is not None:
            row[opt] = memory[opt]
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return True


def retrieve_memories(path: str, query: str, top_k: int = 3) -> List[Dict]:
    mems = load_memories(path)
    scored = []
    for m in mems:
        s = _score(query, m.get("content", ""))
        if s > 0:
            scored.append((s, m))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored[:top_k]]


def make_summary_memory(query: str, output: str) -> Dict:
    text = f"Q: {query}\nA: {output[:200]}"
    return {"type": "summary", "content": text, "source": "query"}


def make_fact_memories(query: str, output: str) -> List[Dict]:
    facts = []
    text = f"{query}\n{output}"
    for kw in ["/scan", "/odom", "/cmd_vel", "/map", "/tf"]:
        if kw in text:
            facts.append(
                {
                    "type": "fact",
                    "content": f"Environment uses ROS topic {kw}.",
                    "source": "inferred",
                    "confidence": 0.8,
                }
            )
    return facts

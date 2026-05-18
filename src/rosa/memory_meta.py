#  Copyright (c) 2024. Jet Propulsion Laboratory. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.

"""Metadata extraction and scope helpers for hybrid long-term memory."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Set

_SYMBOLIC_HINTS = ("node", "topic", "service", "tf", "yaml", "launch", "srv", "msg", "action")


def extract_query_meta(query: str) -> Dict[str, Any]:
    q = (query or "").lower()
    domain = None
    if any(k in q for k in ("nav", "路径", "规划", "navigation", "planner", "costmap")):
        domain = "navigation"
    elif any(k in q for k in ("odom", "cmd_vel", "velocity", "twist", "底盘")):
        domain = "navigation"
    symbols = re.findall(r"/[a-zA-Z0-9_][a-zA-Z0-9_/]*", query or "")
    return {"domain": domain, "symbols": symbols}


def query_has_engineering_symbols(query: str) -> bool:
    if "/" in (query or ""):
        return True
    ql = (query or "").lower()
    return any(k in ql for k in _SYMBOLIC_HINTS)


def infer_memory_kind(content: str) -> str:
    text = content or ""
    if re.search(r"/[a-zA-Z0-9_][a-zA-Z0-9_/]*", text):
        return "symbolic"
    low = text.lower()
    if any(k in low for k in _SYMBOLIC_HINTS + ("error", "traceback", "exception")):
        return "symbolic"
    return "natural"


def extract_tags_from_text(text: str) -> List[str]:
    return sorted(set(re.findall(r"/[a-zA-Z0-9_][a-zA-Z0-9_/]*", text or "")))


def metadata_match_score(query_meta: Dict[str, Any], memory: Dict[str, Any]) -> float:
    s = 0.0
    qd = query_meta.get("domain")
    if qd and memory.get("domain") == qd:
        s += 1.0
    q_symbols: Set[str] = set(query_meta.get("symbols") or [])
    m_tags: Set[str] = set(memory.get("tags") or [])
    if q_symbols and m_tags:
        hit = len(q_symbols & m_tags)
        s += min(1.0, hit / max(1, len(q_symbols)))
    return s / 2.0


def memory_passes_scope(
    memory: Dict[str, Any],
    scene_id: str | None,
    robot_id: str | None,
) -> bool:
    if scene_id and memory.get("scene_id") and memory["scene_id"] != scene_id:
        return False
    if robot_id and memory.get("robot_id") and memory["robot_id"] != robot_id:
        return False
    return True


def memory_is_expired(memory: Dict[str, Any]) -> bool:
    exp = memory.get("expires_at")
    if not exp:
        return False
    from datetime import datetime, timezone

    try:
        dt = datetime.fromisoformat(str(exp).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt < datetime.now(timezone.utc)
    except Exception:
        return False

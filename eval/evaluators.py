"""Minimal evaluators for ROSA bootstrap eval."""


def must_include_evaluator(outputs: dict, reference_outputs: dict) -> dict:
    pred = outputs.get("answer", "")
    must = reference_outputs.get("must_include", [])
    if not must:
        return {"key": "must_include", "score": 1.0}
    hit = sum(1 for token in must if token in pred)
    return {"key": "must_include", "score": hit / len(must)}


def forbidden_claims_evaluator(outputs: dict, reference_outputs: dict) -> dict:
    pred = (outputs.get("answer") or "").lower()
    forbidden = [s.lower() for s in reference_outputs.get("forbidden_claims", [])]
    bad = any(f in pred for f in forbidden)
    return {"key": "no_forbidden_claims", "score": 0.0 if bad else 1.0}


def keyword_correctness_evaluator(outputs: dict, reference_outputs: dict) -> dict:
    pred = (outputs.get("answer") or "").lower()
    score = 1.0 if ("cmd_vel" in pred and "controller_server" in pred) else 0.0
    return {"key": "keyword_correctness", "score": score}

"""Target function for LangSmith eval: invoke current ROSA agent."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from src.rosa.rosa import ROSA


def _build_agent() -> ROSA:
    llm = ChatOpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        temperature=0,
        streaming=False,
    )
    return ROSA(ros_version=2, llm=llm, streaming=False, verbose=False)


_AGENT = None


def target_fn(inputs: dict) -> dict:
    global _AGENT
    if _AGENT is None:
        load_dotenv()
        _AGENT = _build_agent()
    query = inputs["query"]
    answer = _AGENT.invoke(query)
    return {"answer": answer}

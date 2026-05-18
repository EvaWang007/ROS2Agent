#  Copyright (c) 2024. Jet Propulsion Laboratory. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#
#  https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import annotations

from typing import Any

from .prompts import RobotSystemPrompts

__all__ = ["ROSA", "RobotSystemPrompts", "ChatModel"]


def __getattr__(name: str) -> Any:
    """Lazy-import heavy agent stack so submodules (e.g. memory_*) can be tested without LangChain."""
    if name in ("ROSA", "ChatModel"):
        from . import rosa as _rosa_mod

        return getattr(_rosa_mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

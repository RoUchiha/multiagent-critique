"""Deterministic provider that plays scripted turns per agent.

Concurrent critics each pull from their own queue, so a full loop is reproducible
regardless of `asyncio` scheduling order. When an agent's queue is exhausted, the
last response repeats (so a loop can run more rounds than scripted without error).
"""

from __future__ import annotations


class MockProvider:
    def __init__(self, scripts: dict[str, list[str]] | None = None, default: str = "") -> None:
        # agent name -> ordered list of responses
        self.scripts = {k: list(v) for k, v in (scripts or {}).items()}
        self.default = default
        self.calls: list[tuple[str, str]] = []
        self._cursor: dict[str, int] = {}

    async def generate(self, prompt: str, agent: str | None = None) -> str:
        key = agent or "default"
        self.calls.append((key, prompt))
        queue = self.scripts.get(key)
        if not queue:
            return self.default
        i = self._cursor.get(key, 0)
        if i >= len(queue):
            return queue[-1]  # repeat last scripted turn
        self._cursor[key] = i + 1
        return queue[i]

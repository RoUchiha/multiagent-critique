"""Provider protocol. `agent` lets the MockProvider script per-agent turns so a
loop with concurrent critics stays deterministic; real providers ignore it."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Provider(Protocol):
    async def generate(self, prompt: str, agent: str | None = None) -> str: ...

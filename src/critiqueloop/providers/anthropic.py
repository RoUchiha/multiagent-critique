"""Anthropic provider — import-safe without the SDK or a key (lazy import)."""

from __future__ import annotations

import os


class AnthropicProvider:
    def __init__(self, model: str = "claude-sonnet-4-6", api_key: str | None = None) -> None:
        self.model = model
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")

    async def generate(self, prompt: str, agent: str | None = None) -> str:
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=self.api_key)
        resp = await client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in resp.content if b.type == "text")

"""OpenAI provider — import-safe without the SDK or a key (lazy import)."""

from __future__ import annotations

import os


class OpenAIProvider:
    def __init__(self, model: str = "gpt-4o", api_key: str | None = None) -> None:
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")

    async def generate(self, prompt: str, agent: str | None = None) -> str:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.api_key)
        resp = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content or ""

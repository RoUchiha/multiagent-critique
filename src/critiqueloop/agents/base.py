"""Base agent: a named role backed by a provider."""

from __future__ import annotations

from critiqueloop.providers.base import Provider


class Agent:
    def __init__(self, name: str, system_prompt: str, provider: Provider) -> None:
        self.name = name
        self.system_prompt = system_prompt
        self.provider = provider

    async def act(self, prompt: str) -> str:
        full = f"{self.system_prompt}\n\n{prompt}" if self.system_prompt else prompt
        return await self.provider.generate(full, agent=self.name)

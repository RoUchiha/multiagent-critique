"""Gate 2: scripted mock plays per-agent turns; real providers import-safe."""

from __future__ import annotations

import pytest

from critiqueloop.providers.mock import MockProvider


@pytest.mark.asyncio
async def test_scripted_per_agent_queues():
    p = MockProvider(scripts={"generator": ["v0", "v1"], "critic:x": ["c0"]})
    assert await p.generate("p", agent="generator") == "v0"
    assert await p.generate("p", agent="critic:x") == "c0"
    assert await p.generate("p", agent="generator") == "v1"
    # exhausted queue repeats last turn
    assert await p.generate("p", agent="generator") == "v1"
    assert await p.generate("p", agent="critic:x") == "c0"


@pytest.mark.asyncio
async def test_unknown_agent_returns_default():
    p = MockProvider(default="DEFAULT")
    assert await p.generate("p", agent="nobody") == "DEFAULT"


def test_real_providers_import_safe(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    from critiqueloop.providers.anthropic import AnthropicProvider
    from critiqueloop.providers.openai import OpenAIProvider

    assert AnthropicProvider().api_key is None
    assert OpenAIProvider().api_key is None

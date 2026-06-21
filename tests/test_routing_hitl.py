"""Gate 7: tag-based routing + human-in-the-loop approval gate."""

from __future__ import annotations

import pytest

from critiqueloop.config import default_config
from critiqueloop.hitl import ApprovalGate
from critiqueloop.loop import CritiqueLoop
from critiqueloop.providers.mock import MockProvider
from tests.conftest import cj

CRITICS = ("critic:accuracy", "critic:clarity", "critic:safety")


@pytest.mark.asyncio
async def test_routing_selects_specialist_only():
    scripts = {"generator": ["v0"], "critic:safety": [cj(0.95)]}
    provider = MockProvider(scripts)
    loop = CritiqueLoop(default_config(), provider)
    await loop.run("task", tags=["safety"])
    called_agents = {a for a, _ in provider.calls}
    assert "critic:safety" in called_agents
    assert "critic:accuracy" not in called_agents  # routed away
    assert "critic:clarity" not in called_agents


@pytest.mark.asyncio
async def test_hitl_reject_blocks_acceptance():
    scripts = {"generator": ["v0", "v1", "v2"]}
    for c in CRITICS:
        scripts[c] = [cj(0.95)]  # would pass on score alone
    gate = ApprovalGate(policy="auto_reject")
    loop = CritiqueLoop(default_config(), MockProvider(scripts), approval_gate=gate)
    result = await loop.run("task")
    assert gate.calls  # gate was consulted
    assert all(not r.accepted for r in result.rounds)  # human vetoed every accept


@pytest.mark.asyncio
async def test_hitl_approve_allows_acceptance():
    scripts = {"generator": ["v0"]}
    for c in CRITICS:
        scripts[c] = [cj(0.95)]
    gate = ApprovalGate(policy="auto_approve")
    loop = CritiqueLoop(default_config(), MockProvider(scripts), approval_gate=gate)
    result = await loop.run("task")
    assert result.rounds[0].accepted is True
    assert len(gate.calls) == 1

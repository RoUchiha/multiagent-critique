"""Gate 5: evaluator-optimizer controller stop conditions + trajectory."""

from __future__ import annotations

import pytest

from critiqueloop.config import default_config
from critiqueloop.loop import CritiqueLoop
from critiqueloop.providers.mock import MockProvider
from tests.conftest import cj

CRITICS = ("critic:accuracy", "critic:clarity", "critic:safety")


@pytest.mark.asyncio
async def test_v0_fails_v1_passes_stops_round_1():
    scripts = {"generator": ["v0", "v1"]}
    for c in CRITICS:
        scripts[c] = [cj(0.5, issues=["weak"]), cj(0.9)]
    loop = CritiqueLoop(default_config(), MockProvider(scripts))
    result = await loop.run("task")

    assert len(result.rounds) == 2
    assert result.rounds[0].accepted is False
    assert result.rounds[1].accepted is True
    assert result.trajectory == [pytest.approx(0.5), pytest.approx(0.9)]
    assert result.final_candidate == "v1"
    assert result.improved_over_baseline is True


@pytest.mark.asyncio
async def test_max_rounds_respected():
    cfg = default_config()
    cfg.max_rounds = 2
    scripts = {"generator": ["v0", "v1", "v2"]}
    for c in CRITICS:
        scripts[c] = [cj(0.3)]  # always low -> never accepts
    loop = CritiqueLoop(cfg, MockProvider(scripts))
    result = await loop.run("task")
    assert len(result.rounds) == 3  # rounds 0,1,2 then stop at max_rounds
    assert all(not r.accepted for r in result.rounds)


@pytest.mark.asyncio
async def test_accepts_immediately_when_v0_passes():
    scripts = {"generator": ["great v0"]}
    for c in CRITICS:
        scripts[c] = [cj(0.95)]
    loop = CritiqueLoop(default_config(), MockProvider(scripts))
    result = await loop.run("task")
    assert len(result.rounds) == 1 and result.rounds[0].accepted

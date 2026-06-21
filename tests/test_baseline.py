"""Gate 6: looped output beats single-shot baseline on a task set."""

from __future__ import annotations

import pytest

from critiqueloop.config import default_config
from critiqueloop.loop import CritiqueLoop
from critiqueloop.providers.heuristic import HeuristicProvider

TASKS = [
    "Explain what a database index is.",
    "Describe how HTTPS keeps traffic private.",
    "What is the difference between a process and a thread?",
]


@pytest.mark.asyncio
async def test_loop_beats_single_shot():
    loop = CritiqueLoop(default_config(), HeuristicProvider())
    stats = await loop.evaluate_set(TASKS)
    assert stats["loop_mean"] > stats["baseline_mean"]


@pytest.mark.asyncio
async def test_single_run_improves_and_flags():
    loop = CritiqueLoop(default_config(), HeuristicProvider())
    result = await loop.run(TASKS[0])
    assert result.improved_over_baseline is True
    assert result.final_score > (result.baseline_score or 0)

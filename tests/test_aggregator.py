"""Gate 4: parallel critics + deterministic aggregation."""

from __future__ import annotations

import asyncio

import pytest

from critiqueloop.agents.aggregator import Aggregator
from critiqueloop.agents.critic import Critic
from critiqueloop.models import Critique
from critiqueloop.providers.mock import MockProvider
from tests.conftest import cj


def test_consensus_mean_and_dedup():
    crits = [
        Critique(critic_id="a", score=0.6, issues=["too short", "no example"]),
        Critique(critic_id="b", score=0.8, issues=["no example"]),
        Critique(critic_id="c", score=1.0, issues=["typo"]),
    ]
    consensus = Aggregator().aggregate(crits)
    assert consensus.score == pytest.approx((0.6 + 0.8 + 1.0) / 3)
    # "no example" raised twice -> first; deterministic order
    assert consensus.issues[0] == "no example"
    assert set(consensus.issues) == {"no example", "too short", "typo"}


def test_empty_aggregate():
    assert Aggregator().aggregate([]).score == 0.0


@pytest.mark.asyncio
async def test_three_critics_concurrent_deterministic():
    p = MockProvider(scripts={
        "critic:accuracy": [cj(0.6, issues=["x"])],
        "critic:clarity": [cj(0.8, issues=["y"])],
        "critic:safety": [cj(0.7, issues=["x"])],
    })
    critics = [Critic(n, "", p) for n in ("critic:accuracy", "critic:clarity", "critic:safety")]
    results = await asyncio.gather(*(c.critique("t", "cand", "r") for c in critics))
    consensus = Aggregator().aggregate(list(results))
    assert consensus.score == pytest.approx((0.6 + 0.8 + 0.7) / 3)
    assert consensus.issues[0] == "x"  # raised by 2 critics

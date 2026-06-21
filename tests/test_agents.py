"""Gate 3: generator produces a candidate; critic parses structured output."""

from __future__ import annotations

import pytest

from critiqueloop.agents.critic import Critic, parse_critique
from critiqueloop.agents.generator import Generator
from critiqueloop.providers.mock import MockProvider
from tests.conftest import cj


@pytest.mark.asyncio
async def test_generator_candidate_and_revise():
    p = MockProvider(scripts={"generator": ["first", "revised"]})
    gen = Generator("generator", "", p)
    assert await gen.generate_candidate("task") == "first"
    from critiqueloop.models import Consensus

    revised = await gen.revise("task", "first", Consensus(score=0.5, issues=["x"]))
    assert revised == "revised"


@pytest.mark.asyncio
async def test_critic_parses_json():
    p = MockProvider(scripts={"critic:a": [cj(0.9, issues=["i1"], suggestions=["s1"])]})
    crit = Critic("critic:a", "", p)
    result = await crit.critique("task", "candidate", "rubric")
    assert result.score == 0.9
    assert result.issues == ["i1"] and result.suggestions == ["s1"]


def test_parse_critique_handles_malformed():
    bad = parse_critique("c", "not json at all")
    assert bad.score == 0.0 and bad.issues

    embedded = parse_critique("c", 'prose {"score": 0.7, "issues": ["e"]} more')
    assert embedded.score == 0.7 and embedded.issues == ["e"]

    clamped = parse_critique("c", '{"score": 5}')
    assert clamped.score == 1.0  # clamped to [0,1]

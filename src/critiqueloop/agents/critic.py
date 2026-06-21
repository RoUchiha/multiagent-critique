"""Critic: scores a candidate against the rubric and returns a structured Critique.

The critic asks for JSON and parses it defensively — a malformed model response
becomes a low-score critique flagging the parse failure, never a crash.
"""

from __future__ import annotations

import json
import re

from critiqueloop.agents.base import Agent
from critiqueloop.models import Critique

_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def parse_critique(critic_id: str, raw: str) -> Critique:
    """Extract a Critique from (possibly messy) model output."""
    match = _JSON_RE.search(raw or "")
    if not match:
        return Critique(critic_id=critic_id, score=0.0,
                        issues=["unparseable critic output"], suggestions=[])
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return Critique(critic_id=critic_id, score=0.0,
                        issues=["invalid JSON in critic output"], suggestions=[])

    score = data.get("score", 0.0)
    try:
        score = max(0.0, min(1.0, float(score)))
    except (TypeError, ValueError):
        score = 0.0

    def _as_list(v) -> list[str]:
        if isinstance(v, list):
            return [str(x) for x in v]
        return [str(v)] if v else []

    return Critique(
        critic_id=critic_id,
        score=score,
        issues=_as_list(data.get("issues")),
        suggestions=_as_list(data.get("suggestions")),
    )


class Critic(Agent):
    async def critique(self, task: str, candidate: str, rubric: str) -> Critique:
        prompt = (
            f"RUBRIC:\n{rubric}\n\nTASK: {task}\n\nCANDIDATE ANSWER:\n{candidate}\n\n"
            'Respond ONLY with JSON: {"score": <0-1>, "issues": [...], "suggestions": [...]}'
        )
        raw = await self.act(prompt)
        return parse_critique(self.name, raw)

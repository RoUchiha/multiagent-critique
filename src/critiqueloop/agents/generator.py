"""Generator: produces an initial candidate and revises against critique."""

from __future__ import annotations

from critiqueloop.agents.base import Agent
from critiqueloop.models import Consensus


class Generator(Agent):
    async def generate_candidate(self, task: str) -> str:
        return (await self.act(f"TASK: {task}\n\nWrite the best answer you can.")).strip()

    async def revise(self, task: str, candidate: str, consensus: Consensus) -> str:
        issues = "\n".join(f"- {i}" for i in consensus.issues) or "- (none)"
        suggestions = "\n".join(f"- {s}" for s in consensus.suggestions) or "- (none)"
        prompt = (
            f"TASK: {task}\n\nYOUR PREVIOUS ANSWER:\n{candidate}\n\n"
            f"REVIEWER ISSUES:\n{issues}\n\nSUGGESTIONS:\n{suggestions}\n\n"
            "Rewrite the answer to fully address every issue."
        )
        return (await self.act(prompt)).strip()

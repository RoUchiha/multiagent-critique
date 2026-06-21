"""The evaluator-optimizer controller.

generate -> (critique in parallel -> aggregate -> accept? -> revise) until the
consensus passes the bar or max_rounds is hit. Returns the best candidate, the
full round history, and the score trajectory.
"""

from __future__ import annotations

import asyncio

from loguru import logger

from critiqueloop.agents.aggregator import Aggregator
from critiqueloop.agents.critic import Critic
from critiqueloop.agents.generator import Generator
from critiqueloop.config import CritiqueConfig
from critiqueloop.hitl import ApprovalGate
from critiqueloop.memory import Transcript
from critiqueloop.models import RoundResult, RunResult
from critiqueloop.providers.base import Provider


class CritiqueLoop:
    def __init__(
        self,
        config: CritiqueConfig,
        provider: Provider,
        approval_gate: ApprovalGate | None = None,
    ) -> None:
        self.config = config
        self.provider = provider
        self.generator = Generator(config.generator.name, config.generator.system_prompt, provider)
        self.aggregator = Aggregator()
        self.approval_gate = approval_gate
        self.transcript = Transcript()

    def _critics(self, tags: list[str] | None) -> list[Critic]:
        """Tag-based routing: keep only critics whose tags intersect the task's.
        With no tags (or no matches) every critic runs."""
        all_critics = [Critic(c.name, c.system_prompt, self.provider) for c in self.config.critics]
        if not tags:
            return all_critics
        wanted = set(tags)
        selected = [
            crit for crit, cfg in zip(all_critics, self.config.critics, strict=True)
            if wanted & set(cfg.tags)
        ]
        return selected or all_critics

    async def run(self, task: str, tags: list[str] | None = None) -> RunResult:
        critics = self._critics(tags)
        self.transcript = Transcript()
        self.transcript.add("task", task)

        candidate = await self.generator.generate_candidate(task)
        self.transcript.add("generator:v0", candidate)

        rounds: list[RoundResult] = []
        for round_idx in range(self.config.max_rounds + 1):
            critiques = await asyncio.gather(
                *(c.critique(task, candidate, self.config.rubric) for c in critics)
            )
            consensus = self.aggregator.aggregate(list(critiques))
            accepted = consensus.score >= self.config.pass_threshold

            # HITL: a human can veto an otherwise-accepted answer.
            if accepted and self.approval_gate is not None:
                if not self.approval_gate.request(candidate, consensus.score):
                    logger.info("human rejected candidate at round {}", round_idx)
                    accepted = False

            self.transcript.add(
                f"consensus:r{round_idx}",
                f"score={consensus.score:.2f} accepted={accepted} issues={consensus.issues}",
            )
            rounds.append(
                RoundResult(
                    round_idx=round_idx,
                    candidate=candidate,
                    critiques=list(critiques),
                    consensus_score=consensus.score,
                    accepted=accepted,
                )
            )
            if accepted or round_idx == self.config.max_rounds:
                break

            candidate = await self.generator.revise(task, candidate, consensus)
            self.transcript.add(f"generator:v{round_idx + 1}", candidate)

        best = max(rounds, key=lambda r: r.consensus_score)
        baseline = rounds[0].consensus_score
        return RunResult(
            task=task,
            rounds=rounds,
            final_candidate=best.candidate,
            final_score=best.consensus_score,
            baseline_score=baseline,
            improved_over_baseline=best.consensus_score > baseline,
        )

    async def evaluate_set(self, tasks: list[str]) -> dict[str, float]:
        """Compare looped output vs single-shot baseline across a task set.
        Single-shot = the round-0 (v0) consensus; looped = best consensus."""
        loop_scores, baseline_scores = [], []
        for task in tasks:
            result = await self.run(task)
            loop_scores.append(result.final_score)
            baseline_scores.append(result.baseline_score or 0.0)
        n = len(tasks) or 1
        return {
            "loop_mean": sum(loop_scores) / n,
            "baseline_mean": sum(baseline_scores) / n,
        }

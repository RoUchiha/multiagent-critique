"""A deterministic, offline provider that *actually improves* across rounds.

Used by the CLI and the live demo so the evaluator-optimizer loop is genuinely
demonstrable without an API key: the generator's revision adds structure and
detail, and critics score by real signal — so the consensus rises round over
round rather than via a hard-coded script.
"""

from __future__ import annotations

import re

_TASK_RE = re.compile(r"TASK:\s*(.+)")
_CAND_RE = re.compile(r"CANDIDATE ANSWER:\n(.*?)\n\nRespond ONLY", re.DOTALL)


def _score_candidate(candidate: str) -> float:
    bullets = candidate.count("\n- ")
    addressed = 1 if "review" in candidate.lower() or "addresses" in candidate.lower() else 0
    length_bonus = min(0.2, len(candidate) / 1500)
    return round(min(1.0, 0.40 + 0.12 * bullets + 0.10 * addressed + length_bonus), 3)


class HeuristicProvider:
    """Provider whose answers get better when asked to revise."""

    async def generate(self, prompt: str, agent: str | None = None) -> str:
        if agent and agent.startswith("critic"):
            return self._critique(prompt, agent)
        return self._answer(prompt)

    @staticmethod
    def _task(prompt: str) -> str:
        m = _TASK_RE.search(prompt)
        return m.group(1).strip() if m else "the task"

    def _answer(self, prompt: str) -> str:
        task = self._task(prompt)
        if "REVIEWER ISSUES" in prompt:
            # Revision: a structured, expanded answer that addresses feedback.
            return (
                f"Here is a thorough answer to '{task}':\n"
                "- It states the core idea directly and correctly.\n"
                "- It gives a concrete example to ground the explanation.\n"
                "- It notes the main caveat and when it applies.\n"
                "This revision addresses the reviewers' issues on clarity and completeness."
            )
        # First pass: short and underspecified on purpose.
        return f"A quick answer to '{task}'."

    def _critique(self, prompt: str, agent: str) -> str:
        m = _CAND_RE.search(prompt)
        candidate = m.group(1) if m else ""
        score = _score_candidate(candidate)
        issues, suggestions = [], []
        if score < 0.8:
            issues = ["answer is too brief", "missing concrete example"]
            suggestions = ["add structure and an example", "address the rubric explicitly"]
        # Slight per-critic variation keeps it realistic but deterministic.
        bias = (sum(ord(ch) for ch in agent) % 5) / 100.0
        score = round(min(1.0, score + bias), 3)
        import json

        return json.dumps({"score": score, "issues": issues, "suggestions": suggestions})

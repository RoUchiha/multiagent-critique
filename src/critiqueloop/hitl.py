"""Human-in-the-loop approval gate. Auto in tests/CI; interactive at the CLI edge."""

from __future__ import annotations

from collections.abc import Callable


class ApprovalGate:
    """Invoked when the loop is about to accept a final answer.

    `policy` is "auto_approve" (default), "auto_reject", or a callable that
    receives (candidate, score) and returns a bool.
    """

    def __init__(self, policy: str | Callable[[str, float], bool] = "auto_approve") -> None:
        self.policy = policy
        self.calls: list[tuple[str, float]] = []

    def request(self, candidate: str, score: float) -> bool:
        self.calls.append((candidate, score))
        if callable(self.policy):
            return bool(self.policy(candidate, score))
        return self.policy != "auto_reject"

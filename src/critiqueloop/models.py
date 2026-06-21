"""Pydantic v2 models for the critique loop."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Message(BaseModel):
    """A transcript entry."""

    role: str  # e.g. "generator", "critic:style", "system"
    content: str


class Critique(BaseModel):
    """One critic's structured assessment of a candidate."""

    critic_id: str
    score: float = Field(ge=0.0, le=1.0)
    issues: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class Consensus(BaseModel):
    """Aggregator output across multiple critics."""

    score: float
    issues: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    critiques: list[Critique] = Field(default_factory=list)


class RoundResult(BaseModel):
    round_idx: int
    candidate: str
    critiques: list[Critique]
    consensus_score: float
    accepted: bool


class RunResult(BaseModel):
    task: str
    rounds: list[RoundResult]
    final_candidate: str
    final_score: float
    improved_over_baseline: bool = False
    baseline_score: float | None = None

    @property
    def trajectory(self) -> list[float]:
        return [r.consensus_score for r in self.rounds]

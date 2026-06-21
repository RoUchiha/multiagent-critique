"""Config: agent roster, rubric, and loop parameters (YAML -> Pydantic)."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    name: str
    system_prompt: str = ""
    tags: list[str] = Field(default_factory=list)  # for tag-based routing


class CritiqueConfig(BaseModel):
    generator: AgentConfig
    critics: list[AgentConfig]
    rubric: str
    max_rounds: int = 3
    pass_threshold: float = 0.8

    @classmethod
    def load(cls, path: str | Path) -> CritiqueConfig:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        return cls(**data)


def default_config() -> CritiqueConfig:
    return CritiqueConfig(
        generator=AgentConfig(name="generator", system_prompt="You write clear, correct answers."),
        critics=[
            AgentConfig(name="critic:accuracy", tags=["accuracy", "facts"],
                        system_prompt="You judge factual accuracy and completeness."),
            AgentConfig(name="critic:clarity", tags=["clarity", "style"],
                        system_prompt="You judge clarity, structure, and concision."),
            AgentConfig(name="critic:safety", tags=["safety"],
                        system_prompt="You judge safety and appropriateness."),
        ],
        rubric=(
            "Score 0-1. Reward correctness, completeness, and clarity. "
            "Penalize errors, vagueness, and omissions."
        ),
        max_rounds=3,
        pass_threshold=0.8,
    )

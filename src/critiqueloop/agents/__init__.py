"""Agents: generator, critic, aggregator."""

from critiqueloop.agents.aggregator import Aggregator
from critiqueloop.agents.critic import Critic
from critiqueloop.agents.generator import Generator

__all__ = ["Generator", "Critic", "Aggregator"]

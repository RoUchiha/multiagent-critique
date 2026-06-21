"""Transcript memory: an ordered record of everything that happened in a run."""

from __future__ import annotations

from critiqueloop.models import Message


class Transcript:
    def __init__(self) -> None:
        self.messages: list[Message] = []

    def add(self, role: str, content: str) -> None:
        self.messages.append(Message(role=role, content=content))

    def render(self) -> str:
        return "\n\n".join(f"[{m.role}]\n{m.content}" for m in self.messages)

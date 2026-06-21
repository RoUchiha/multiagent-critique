"""Shared fixtures and helpers for building scripted critic turns."""

from __future__ import annotations

import json

import pytest

from critiqueloop.config import default_config


def cj(score: float, issues=None, suggestions=None) -> str:
    """Build a critic JSON turn."""
    return json.dumps({"score": score, "issues": issues or [], "suggestions": suggestions or []})


@pytest.fixture
def config():
    return default_config()

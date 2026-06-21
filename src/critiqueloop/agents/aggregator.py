"""Aggregator: merges multiple critiques into one consensus.

Consensus score is the mean (conservative — every critic must be satisfied for a
high score). Issues/suggestions are de-duplicated and prioritized by how many
critics raised them, then by first appearance (deterministic).
"""

from __future__ import annotations

from collections import Counter

from critiqueloop.models import Consensus, Critique


def _merge_prioritized(lists: list[list[str]]) -> list[str]:
    counts: Counter[str] = Counter()
    first_seen: dict[str, int] = {}
    idx = 0
    for items in lists:
        for item in items:
            key = item.strip()
            if not key:
                continue
            counts[key] += 1
            if key not in first_seen:
                first_seen[key] = idx
                idx += 1
    # Sort by frequency desc, then first-seen asc for determinism.
    return sorted(counts, key=lambda k: (-counts[k], first_seen[k]))


class Aggregator:
    def aggregate(self, critiques: list[Critique]) -> Consensus:
        if not critiques:
            return Consensus(score=0.0)
        mean = sum(c.score for c in critiques) / len(critiques)
        return Consensus(
            score=mean,
            issues=_merge_prioritized([c.issues for c in critiques]),
            suggestions=_merge_prioritized([c.suggestions for c in critiques]),
            critiques=list(critiques),
        )

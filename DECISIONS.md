# DECISIONS

Assumptions and deviations made during autonomous execution, dated.

## 2026-06-20

- **Two provider mocks, by intent.** A **scripted MockProvider** (per-agent response
  queues) keeps tests deterministic even with concurrent critics. A separate
  **HeuristicProvider** powers the CLI/demo: critics score by real signal (structure,
  length, addressing feedback) and revisions genuinely improve, so the loop is
  demonstrable offline without scripted theater.
- **Consensus = mean of critic scores.** Chosen over min/median so one harsh critic
  doesn't permanently block, but every critic still pulls weight. Configurable later.
- **Best-of-rounds is returned**, not necessarily the last round — protects against a
  revision that scores worse than a prior candidate.
- **`improved_over_baseline`** compares the best consensus against the round-0 (v0)
  consensus, i.e. the single-shot baseline. No separate generation needed since the
  deterministic provider yields the same v0.
- **Routing** is tag-based: a task's tags select critics whose tags intersect; with no
  tags (or no match) all critics run. Kept simple per the spec's "optional".
- **HITL** gate is invoked only when the loop is about to *accept* — a human can veto a
  passing answer. Auto-approve in tests/CI; interactive at the CLI edge.

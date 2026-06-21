# critiqueloop — Multi-Agent Evaluator-Optimizer Loop

**🔁 [Live demo on Hugging Face Spaces](https://huggingface.co/spaces/rosingh/ai-ml-portfolio-demos)** — enter a task and watch the consensus score climb round over round.

A generator proposes an answer, **multiple critics review it in parallel against a
rubric**, an aggregator merges their feedback into a consensus, and the generator
**revises** — looping until quality passes a bar or `max_rounds` is hit. Output
quality measurably improves over a single-shot baseline.

Implements the **Evaluator-Optimizer** pattern, plus **parallelization** (concurrent
critics), **tag-based routing** (send a task to specialist critics), and an optional
**human-in-the-loop** approval gate.

## How it works

```
generate v0
 └─ critics score v0 in parallel ─ aggregate ─ pass? ─ no ─ revise → v1 ─ ...
                                                  └─ yes ─ (optional human approval) ─ done
```

- **Consensus = mean of critic scores** — every critic must be satisfied for a high
  score (conservative by design).
- **Issues/suggestions** are de-duplicated and prioritized by how many critics raised
  them (deterministic ordering).
- Returns the **best candidate**, the **full round history**, and the **score
  trajectory**.

## Quickstart

```bash
python -m venv .venv && .venv/Scripts/activate     # Windows
pip install -e ".[dev]"

# Run the loop (offline heuristic provider — no API key)
critiqueloop run --task "Explain what a database index is." --transcript

# Compare loop vs single-shot over a task set
critiqueloop report --task-file tasks.yaml
```

The CLI/demo use a deterministic **heuristic provider** whose revisions genuinely
improve, so the loop is demonstrable offline. Swap in `AnthropicProvider` /
`OpenAIProvider` for real models.

## Tests

```bash
pytest                 # all gates, offline
pytest --cov=critiqueloop
```

Tests use a **scripted MockProvider** (per-agent queues) so a loop with concurrent
critics is fully deterministic regardless of scheduling order.

## Live demo

`app.py` is a Gradio demo: enter a task, watch each round's consensus score climb and
read the final answer. Deployable to Hugging Face Spaces.

## Layout

```
src/critiqueloop/
  config.py        # agent roster, rubric, max_rounds, pass_threshold
  models.py        # Message, Critique, Consensus, RoundResult, RunResult
  providers/       # base, anthropic, openai (import-safe), mock (scripted), heuristic
  agents/          # generator, critic (parses JSON critique), aggregator
  loop.py          # evaluator-optimizer controller (+ routing, baseline eval)
  hitl.py          # ApprovalGate (auto in tests, interactive at CLI)
  memory.py        # transcript
  cli.py           # run / report
```

## Cost note

Critique loops increase token spend: each round is `1 generation + N critic calls`.
A 2-round, 3-critic run is ~7 model calls vs 1 for single-shot. The trade is spend
for quality — worth it for high-stakes outputs, wasteful for trivial ones (route
accordingly). See [DECISIONS.md](DECISIONS.md).

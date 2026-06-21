"""Gradio live demo for critiqueloop.

Enter a task; watch the generator + critics iterate, the consensus score climb
round over round, and read the final answer. Offline heuristic provider — no keys.
Deployable to Hugging Face Spaces.
"""

from __future__ import annotations

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import gradio as gr  # noqa: E402
import pandas as pd  # noqa: E402

from critiqueloop.config import default_config  # noqa: E402
from critiqueloop.loop import CritiqueLoop  # noqa: E402
from critiqueloop.providers.heuristic import HeuristicProvider  # noqa: E402

CONFIG = default_config()


def run_loop(task: str):
    if not task.strip():
        return "Enter a task.", pd.DataFrame(), ""
    loop = CritiqueLoop(CONFIG, HeuristicProvider())
    result = asyncio.run(loop.run(task))

    rows = [
        {"round": r.round_idx, "consensus": round(r.consensus_score, 2),
         "accepted": "✅" if r.accepted else "—"}
        for r in result.rounds
    ]
    improved = "🟢 yes" if result.improved_over_baseline else "no"
    summary = (
        f"### Result\n"
        f"- **Rounds:** {len(result.rounds)}\n"
        f"- **Single-shot (v0) score:** {result.baseline_score:.2f}\n"
        f"- **Final score:** {result.final_score:.2f}\n"
        f"- **Improved over single-shot:** {improved}\n\n"
        f"**Final answer:**\n\n{result.final_candidate}"
    )
    return summary, pd.DataFrame(rows), loop.transcript.render()


with gr.Blocks(title="Multi-Agent Critique Loop", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        "# 🔁 Multi-Agent Critique Loop\n"
        "A generator writes an answer, **3 critics review it in parallel** against a "
        "rubric, and the generator **revises** — looping until the consensus passes the "
        "bar. Watch the score climb round over round.\n\n"
        "_Offline demo: a deterministic heuristic provider whose revisions genuinely "
        "improve — no API key._"
    )
    with gr.Row():
        task = gr.Textbox(label="Task", placeholder="Explain what a database index is.", scale=4)
        btn = gr.Button("Run loop", variant="primary", scale=1)
    gr.Examples(
        ["Explain what a database index is.",
         "Describe how HTTPS keeps traffic private.",
         "What is the difference between a process and a thread?"],
        inputs=task,
    )
    summary = gr.Markdown()
    rounds = gr.Dataframe(label="Score trajectory")
    with gr.Accordion("Full transcript", open=False):
        transcript = gr.Textbox(label="", lines=16)
    btn.click(run_loop, task, [summary, rounds, transcript])
    task.submit(run_loop, task, [summary, rounds, transcript])


if __name__ == "__main__":
    demo.launch()

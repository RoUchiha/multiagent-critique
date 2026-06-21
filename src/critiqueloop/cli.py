"""Typer CLI: run a critique loop and print the transcript + final answer."""

from __future__ import annotations

import asyncio
import os
import sys

import typer
import yaml
from loguru import logger
from rich.console import Console
from rich.table import Table

from critiqueloop.config import CritiqueConfig, default_config
from critiqueloop.loop import CritiqueLoop
from critiqueloop.providers.heuristic import HeuristicProvider

app = typer.Typer(add_completion=False, help="Multi-agent evaluator-optimizer critique loop.")
console = Console()


@app.callback()
def _configure() -> None:
    logger.remove()
    logger.add(sys.stderr, level=os.environ.get("CRITIQUELOOP_LOG_LEVEL", "WARNING"))


def _loop(config_path: str | None) -> CritiqueLoop:
    config = CritiqueConfig.load(config_path) if config_path else default_config()
    return CritiqueLoop(config, HeuristicProvider())


def _print_result(result) -> None:
    table = Table(title="Critique-Loop Trajectory", header_style="bold cyan")
    table.add_column("Round", justify="right")
    table.add_column("Consensus", justify="right")
    table.add_column("Accepted")
    for r in result.rounds:
        table.add_row(str(r.round_idx), f"{r.consensus_score:.2f}",
                      "[green]yes[/green]" if r.accepted else "no")
    console.print(table)
    console.print(f"[bold]Improved over single-shot:[/bold] {result.improved_over_baseline} "
                  f"({result.baseline_score:.2f} -> {result.final_score:.2f})")
    console.print("\n[bold]Final answer:[/bold]")
    console.print(result.final_candidate)


@app.command()
def run(
    task: str = typer.Option(..., "--task"),
    config: str = typer.Option(None, "--config"),
    show_transcript: bool = typer.Option(False, "--transcript"),
) -> None:
    """Run the loop on a single task."""
    loop = _loop(config)
    result = asyncio.run(loop.run(task))
    _print_result(result)
    if show_transcript:
        console.print("\n[bold]Transcript:[/bold]")
        console.print(loop.transcript.render())


@app.command()
def report(
    task_file: str = typer.Option(..., "--task-file", help="YAML list of tasks"),
    config: str = typer.Option(None, "--config"),
) -> None:
    """Run a task set and report loop vs single-shot baseline means."""
    import pathlib

    tasks = yaml.safe_load(pathlib.Path(task_file).read_text(encoding="utf-8"))
    loop = _loop(config)
    stats = asyncio.run(loop.evaluate_set(list(tasks)))
    console.print(f"[bold]Loop mean:[/bold] {stats['loop_mean']:.3f}")
    console.print(f"[bold]Single-shot baseline mean:[/bold] {stats['baseline_mean']:.3f}")
    lift = stats["loop_mean"] - stats["baseline_mean"]
    console.print(f"[bold green]Quality lift:[/bold green] +{lift:.3f}")


if __name__ == "__main__":
    app()

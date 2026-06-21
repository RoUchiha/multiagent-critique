"""CLI smoke tests (run / report) via Typer CliRunner, offline heuristic provider."""

from __future__ import annotations

from typer.testing import CliRunner

from critiqueloop.cli import app

runner = CliRunner()


def test_run_prints_trajectory():
    result = runner.invoke(app, ["run", "--task", "Explain database indexes.", "--transcript"])
    assert result.exit_code == 0
    assert "Trajectory" in result.stdout
    assert "Final answer" in result.stdout


def test_report_over_task_file(tmp_path):
    f = tmp_path / "tasks.yaml"
    f.write_text("- Explain indexes.\n- Explain HTTPS.\n", encoding="utf-8")
    result = runner.invoke(app, ["report", "--task-file", str(f)])
    assert result.exit_code == 0
    assert "Quality lift" in result.stdout

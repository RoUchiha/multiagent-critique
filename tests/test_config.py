"""Gate 1: config loads roster + rubric."""

from __future__ import annotations

from critiqueloop.config import CritiqueConfig, default_config


def test_default_config():
    c = default_config()
    assert c.generator.name == "generator"
    assert len(c.critics) == 3
    assert 0 < c.pass_threshold <= 1


def test_load_yaml(tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text(
        """
generator: {name: gen, system_prompt: write}
critics:
  - {name: "critic:a", tags: [accuracy]}
  - {name: "critic:b", tags: [style]}
rubric: "score it"
max_rounds: 2
pass_threshold: 0.75
""",
        encoding="utf-8",
    )
    c = CritiqueConfig.load(p)
    assert c.max_rounds == 2
    assert c.critics[0].tags == ["accuracy"]

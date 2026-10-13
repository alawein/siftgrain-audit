import sys

from eval_audit.cli import main


def test_rich_is_opt_in_and_missing_extra_is_controlled(monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "rich.console", None)
    assert main(["examples/manifest.json", "examples/results.jsonl", "--rich"]) == 2
    assert "optional cli extra" in capsys.readouterr().err

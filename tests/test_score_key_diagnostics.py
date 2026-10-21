"""Scorer errors help users recover without choosing or exposing score values."""

import json

import pytest
from test_audit import manifest

from eval_audit.adapters import convert
from eval_audit.cli import main
from eval_audit.contract import InputError


def source_file(tmp_path, scores):
    source = tmp_path / "source.json"
    source.write_text(
        json.dumps(
            {
                "samples": [
                    {
                        "id": "a",
                        "scores": scores,
                        "metadata": {"private": "do-not-echo-source-values"},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return source


def test_wrong_scorer_lists_names_without_selecting_one(tmp_path):
    source = source_file(tmp_path, {"accuracy": {"value": 0}, "toxicity": {"value": 0.25}})
    with pytest.raises(InputError) as error:
        convert("inspect", manifest(), source, "acc")
    message = str(error.value)
    assert "missing score key at record 1" in message
    assert "--score-key" in message and '"accuracy"' in message and '"toxicity"' in message
    assert "do-not-echo-source-values" not in message
    assert "0.25" not in message
    assert convert("inspect", manifest(), source, "accuracy")[0]["score"] == 0


def test_single_available_scorer_still_requires_explicit_choice(tmp_path):
    source = source_file(tmp_path, {"accuracy": {"value": 1}})
    with pytest.raises(InputError, match='available.*"accuracy"'):
        convert("inspect", manifest(), source, "missing")


def test_hint_escapes_terminal_controls(tmp_path):
    name = "metric\x1b[2J\n\u202e"
    source = source_file(tmp_path, {name: {"value": 0}})
    with pytest.raises(InputError) as error:
        convert("inspect", manifest(), source, "missing")
    message = str(error.value)
    assert json.dumps(name) in message
    assert "\x1b" not in message and "\n" not in message and "\u202e" not in message
    assert convert("inspect", manifest(), source, name)[0]["score"] == 0


def test_hint_limits_names_and_length(tmp_path):
    scores = {f"metric{i:02d}": {"value": 0} for i in range(12)}
    scores["x" * 10000] = {"value": 1}
    source = source_file(tmp_path, scores)
    with pytest.raises(InputError) as error:
        convert("inspect", manifest(), source, "missing")
    message = str(error.value)
    assert all(json.dumps(f"metric{i:02d}") in message for i in range(5))
    assert '"metric05"' not in message
    assert "8 additional" in message and "inspect source" in message
    assert len(message) < 700


def test_all_oversized_names_are_omitted_without_echoing_truncated_choices(tmp_path):
    source = source_file(tmp_path, {"x" * 10000: {"value": 0}})
    with pytest.raises(InputError) as error:
        convert("inspect", manifest(), source, "missing")
    message = str(error.value)
    assert "1 additional" in message and "inspect source" in message
    assert "xxxxxxxxxx" not in message
    assert len(message) < 700


@pytest.mark.parametrize("scores", [None, {}])
def test_absent_scores_remain_unscored(tmp_path, scores):
    rows = convert("inspect", manifest(), source_file(tmp_path, scores), "metric")
    assert rows[0]["status"] == "unscored" and rows[0]["score"] is None


def test_mismatch_keeps_all_outputs_and_retry_uses_explicit_key(tmp_path, capsys):
    source = source_file(tmp_path, {"accuracy": {"value": 0}})
    population = tmp_path / "manifest.json"
    population.write_text(json.dumps(manifest()), encoding="utf-8")
    output, report, html = (
        tmp_path / name for name in ["rows.jsonl", "report.json", "report.html"]
    )
    for path in [output, report, html]:
        path.write_bytes(b"keep existing output")
    args = [
        "convert",
        "inspect",
        str(source),
        "--manifest",
        str(population),
        "--score-key",
        "missing",
        "--output",
        str(output),
        "--json",
        str(report),
        "--html",
        str(html),
        "--force",
    ]
    before = {path: path.read_bytes() for path in [source, population, output, report, html]}
    assert main(args) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and "available" in captured.err and '"accuracy"' in captured.err
    assert before == {path: path.read_bytes() for path in before}
    args[args.index("--score-key") + 1] = "accuracy"
    assert main(args) == 0
    assert json.loads(report.read_bytes())["counts"]["score_present"] == 1
    assert json.loads(output.read_bytes())["score"] == 0

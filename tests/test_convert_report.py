"""One-command reports must match the established two-command workflow."""

import json
import os

import pytest

from eval_audit.cli import main


def inputs(tmp_path, *, complete=False):
    manifest = tmp_path / "manifest.json"
    source = tmp_path / "source.json"
    manifest.write_text(
        json.dumps({"schema_version": 1, "run_id": "synthetic", "expected_ids": ["0:0", "1:0"]}),
        encoding="utf-8",
    )
    rows = [{"testIdx": 0, "promptIdx": 0, "score": 0}]
    if complete:
        rows.append({"testIdx": 1, "promptIdx": 0, "score": 1})
    source.write_text(json.dumps({"results": rows}), encoding="utf-8")
    return manifest, source


def command(manifest, source, output):
    return [
        "convert",
        "promptfoo",
        str(source),
        "--manifest",
        str(manifest),
        "--output",
        str(output),
    ]


@pytest.mark.parametrize("complete, expected_exit", [(False, 1), (True, 0)])
def test_conversion_report_matches_separate_audit(tmp_path, capsys, complete, expected_exit):
    manifest, source = inputs(tmp_path, complete=complete)
    output = tmp_path / "results.jsonl"
    combined = tmp_path / "combined.html"
    separate = tmp_path / "separate.html"
    before = (manifest.read_bytes(), source.read_bytes())
    assert main(command(manifest, source, output) + ["--html", str(combined)]) == expected_exit
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "missing" in captured.err.lower()
    assert main([str(manifest), str(output), "--html", str(separate)]) == expected_exit
    assert combined.read_bytes() == separate.read_bytes()
    assert json.loads(output.read_text().splitlines()[0])["score"] == 0
    assert before == (manifest.read_bytes(), source.read_bytes())


@pytest.mark.parametrize("alias", ["manifest", "source", "output", "score_map"])
def test_report_alias_rejected_before_any_output_write(tmp_path, capsys, alias):
    manifest, source = inputs(tmp_path)
    output = tmp_path / "results.jsonl"
    score_map = tmp_path / "map.json"
    score_map.write_text("{}", encoding="utf-8")
    output.write_bytes(b"keep existing output")
    paths = {"manifest": manifest, "source": source, "output": output, "score_map": score_map}
    before = {name: path.read_bytes() for name, path in paths.items()}
    args = command(manifest, source, output) + [
        "--html",
        str(paths[alias]),
        "--score-map",
        str(score_map),
        "--force",
    ]
    assert main(args) == 2
    assert "output" in capsys.readouterr().err
    assert before == {name: path.read_bytes() for name, path in paths.items()}


def test_report_hardlink_to_source_is_rejected(tmp_path, capsys):
    manifest, source = inputs(tmp_path)
    output = tmp_path / "results.jsonl"
    report = tmp_path / "report.html"
    os.link(source, report)
    before = source.read_bytes()
    assert main(command(manifest, source, output) + ["--html", str(report), "--force"]) == 2
    assert "output cannot replace input" in capsys.readouterr().err
    assert not output.exists()
    assert source.read_bytes() == report.read_bytes() == before


def test_existing_report_preserves_both_outputs_without_force(tmp_path, capsys):
    manifest, source = inputs(tmp_path)
    output = tmp_path / "results.jsonl"
    report = tmp_path / "report.html"
    report.write_bytes(b"keep existing report")
    assert main(command(manifest, source, output) + ["--html", str(report)]) == 2
    assert "output exists" in capsys.readouterr().err
    assert not output.exists()
    assert report.read_bytes() == b"keep existing report"


def test_unexpected_record_needs_attention_despite_complete_expected_scores(tmp_path, capsys):
    manifest, source = inputs(tmp_path, complete=True)
    native = json.loads(source.read_text(encoding="utf-8"))
    native["results"].append({"testIdx": 9, "promptIdx": 0, "score": 1})
    source.write_text(json.dumps(native), encoding="utf-8")
    output = tmp_path / "results.jsonl"
    report = tmp_path / "report.html"
    assert main(command(manifest, source, output) + ["--html", str(report)]) == 1
    capsys.readouterr()
    assert main([str(manifest), str(output)]) == 1
    actual = json.loads(capsys.readouterr().out)
    assert actual["counts"]["scored"] == actual["counts"]["expected"] == 2
    assert actual["unexpected_ids"] == ["9:0"]
    assert report.exists()


def test_bad_source_preserves_existing_outputs_with_force(tmp_path, capsys):
    manifest, source = inputs(tmp_path)
    output = tmp_path / "results.jsonl"
    report = tmp_path / "report.html"
    source.write_bytes(b"{malformed")
    output.write_bytes(b"keep rows")
    report.write_bytes(b"keep report")
    assert main(command(manifest, source, output) + ["--html", str(report), "--force"]) == 2
    assert capsys.readouterr().err
    assert output.read_bytes() == b"keep rows"
    assert report.read_bytes() == b"keep report"


@pytest.mark.parametrize("format_name", ["inspect", "lm-evaluation-harness", "promptfoo"])
def test_native_reports_preserve_partial_error_scores_and_missing_cases(
    tmp_path, capsys, format_name
):
    manifest = tmp_path / "manifest.json"
    source = tmp_path / "source.json"
    output = tmp_path / "results.jsonl"
    report = tmp_path / "report.html"
    identifiers = [f"{i}:0" if format_name == "promptfoo" else str(i) for i in range(4)]
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "run_id": "synthetic",
                "expected_ids": identifiers,
            }
        ),
        encoding="utf-8",
    )
    if format_name == "inspect":
        samples = [
            {"id": "0", "scores": {"metric": {"value": 0}}},
            {"id": "1", "scores": {"metric": {"value": 0.4}}, "error": "synthetic"},
            {"id": "2"},
        ]
        source.write_text(json.dumps({"samples": samples}), encoding="utf-8")
    elif format_name == "lm-evaluation-harness":
        source.write_text(
            "\n".join(
                json.dumps(row)
                for row in [
                    {"doc_id": 0, "metric": 0},
                    {"doc_id": 1, "metric": 0.4, "error": "synthetic"},
                    {"doc_id": 2},
                ]
            ),
            encoding="utf-8",
        )
    else:
        source.write_text(
            json.dumps(
                {
                    "results": [
                        {"testIdx": 0, "promptIdx": 0, "score": 0},
                        {"testIdx": 1, "promptIdx": 0, "score": 0.4, "error": "synthetic"},
                        {"testIdx": 2, "promptIdx": 0, "score": None},
                    ]
                }
            ),
            encoding="utf-8",
        )
    args = [
        "convert",
        format_name,
        str(source),
        "--manifest",
        str(manifest),
        "--output",
        str(output),
        "--html",
        str(report),
    ]
    if format_name != "promptfoo":
        args += ["--score-key", "metric"]
    assert main(args) == 1
    assert "missing 1; errored 1; unscored 1" in capsys.readouterr().err
    assert main([str(manifest), str(output)]) == 1
    actual = json.loads(capsys.readouterr().out)
    assert actual["counts"] == {
        "expected": 4,
        "scored": 1,
        "errored": 1,
        "unscored": 1,
        "missing": 1,
        "score_present": 2,
    }
    assert actual["missing_ids"] == [identifiers[3]]
    assert report.is_file()

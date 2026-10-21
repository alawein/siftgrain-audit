"""Native JSON reports use the existing audit contract and output safeguards."""

import json
import os

import pytest
from test_convert_report import command, inputs

from eval_audit.cli import main


@pytest.mark.parametrize("complete", [False, True])
@pytest.mark.parametrize("with_html", [False, True])
def test_json_report_matches_separate_audit(tmp_path, capsys, complete, with_html):
    manifest, source = inputs(tmp_path, complete=complete)
    output = tmp_path / "rows.jsonl"
    report = tmp_path / "report.json"
    html = tmp_path / "report.html"
    separate = tmp_path / "separate.json"
    separate_html = tmp_path / "separate.html"
    before = manifest.read_bytes(), source.read_bytes()
    args = command(manifest, source, output) + ["--json", str(report)]
    if with_html:
        args += ["--html", str(html)]
    expected_exit = 0 if complete else 1
    assert main(args) == expected_exit
    captured = capsys.readouterr()
    assert captured.out == ""
    assert f"exit {expected_exit}" in captured.err
    assert html.exists() == with_html
    assert (
        main(
            [
                str(manifest),
                str(output),
                "--json",
                str(separate),
                "--html",
                str(separate_html),
            ]
        )
        == expected_exit
    )
    assert report.read_bytes() == separate.read_bytes()
    if with_html:
        assert html.read_bytes() == separate_html.read_bytes()
    assert json.loads(report.read_bytes())["counts"]["score_present"] >= 1
    assert before == (manifest.read_bytes(), source.read_bytes())


@pytest.mark.parametrize("alias", ["manifest", "source", "rows", "html", "score_map"])
def test_json_report_aliases_preserve_every_file(tmp_path, capsys, alias):
    manifest, source = inputs(tmp_path)
    output = tmp_path / "rows.jsonl"
    html = tmp_path / "report.html"
    score_map = tmp_path / "map.json"
    output.write_bytes(b"keep rows")
    html.write_bytes(b"keep html")
    score_map.write_bytes(b"{}")
    paths = {
        "manifest": manifest,
        "source": source,
        "rows": output,
        "html": html,
        "score_map": score_map,
    }
    before = {name: path.read_bytes() for name, path in paths.items()}
    assert (
        main(
            command(manifest, source, output)
            + [
                "--html",
                str(html),
                "--json",
                str(paths[alias]),
                "--score-map",
                str(score_map),
                "--force",
            ]
        )
        == 2
    )
    assert "output" in capsys.readouterr().err
    assert before == {name: path.read_bytes() for name, path in paths.items()}


def test_json_report_hardlink_cannot_replace_source(tmp_path, capsys):
    manifest, source = inputs(tmp_path)
    output = tmp_path / "rows.jsonl"
    report = tmp_path / "report.json"
    os.link(source, report)
    before = source.read_bytes()
    assert main(command(manifest, source, output) + ["--json", str(report), "--force"]) == 2
    assert "output cannot replace input" in capsys.readouterr().err
    assert not output.exists()
    assert source.read_bytes() == report.read_bytes() == before


@pytest.mark.parametrize("force", [False, True])
def test_existing_json_report_requires_force(tmp_path, capsys, force):
    manifest, source = inputs(tmp_path)
    output = tmp_path / "rows.jsonl"
    report = tmp_path / "report.json"
    report.write_bytes(b"keep report")
    args = command(manifest, source, output) + ["--json", str(report)]
    if force:
        args += ["--force"]
    assert main(args) == (1 if force else 2)
    captured = capsys.readouterr()
    if force:
        assert json.loads(report.read_bytes())["exit_code"] == 1
        assert output.exists()
    else:
        assert "output exists" in captured.err
        assert report.read_bytes() == b"keep report"
        assert not output.exists()


def test_malformed_source_preserves_all_three_outputs(tmp_path, capsys):
    manifest, source = inputs(tmp_path)
    output = tmp_path / "rows.jsonl"
    report = tmp_path / "report.json"
    html = tmp_path / "report.html"
    source.write_bytes(b"{malformed")
    for path in [output, report, html]:
        path.write_bytes(b"keep output")
    assert (
        main(
            command(manifest, source, output)
            + [
                "--json",
                str(report),
                "--html",
                str(html),
                "--force",
            ]
        )
        == 2
    )
    assert capsys.readouterr().err
    assert all(path.read_bytes() == b"keep output" for path in [output, report, html])

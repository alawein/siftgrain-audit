import base64
import hashlib
import json
import runpy
import tomllib
from html.parser import HTMLParser
from pathlib import Path

import pytest
from test_audit import manifest as make_manifest
from test_audit import row as make_row

from eval_audit.cli import __version__, main
from eval_audit.contract import InputError, load_inputs, validate
from eval_audit.core import audit
from eval_audit.report import render_html


def test_distribution_metadata_preserves_module_and_cli():
    project = tomllib.loads(
        (Path(__file__).parents[1] / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    assert project["name"] == "alawein-eval-audit"
    assert project["version"] == "0.3.1"
    assert project["scripts"] == {"eval-audit": "eval_audit.cli:main"}
    assert project["dependencies"] == []


def test_help_documents_invocations_and_exit_codes(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "examples/manifest.json" in out
    assert "exit" in out.lower()
    assert "contract" in out.lower()


def test_status_score_reason_errors_carry_row_index():
    with pytest.raises(InputError) as excinfo:
        validate(make_manifest(), [make_row("unknown")])
    assert "record 1" in str(excinfo.value)
    with pytest.raises(InputError) as excinfo:
        validate(make_manifest(), [make_row("scored", None)])
    assert "record 1" in str(excinfo.value)
    with pytest.raises(InputError) as excinfo:
        validate(make_manifest(), [make_row("unscored", 1)])
    assert "record 1" in str(excinfo.value)


def test_crlf_records_parse():
    import tempfile
    from pathlib import Path

    from eval_audit.contract import load_inputs

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        manifest_path = root / "manifest.json"
        records_path = root / "records.jsonl"
        manifest_path.write_text(json.dumps(make_manifest()), encoding="utf-8")
        records_path.write_bytes((json.dumps(make_row()) + "\r\n").encode())
        _, rows, _ = load_inputs(manifest_path, records_path)
        assert rows[0]["status"] == "scored"


def test_cli_missing_inputs_and_output_dir(tmp_path):
    missing_manifest = tmp_path / "no-manifest.json"
    missing_records = tmp_path / "no-records.jsonl"
    assert main([str(missing_manifest), str(missing_records)]) == 2
    manifest_path = tmp_path / "manifest.json"
    records_path = tmp_path / "records.jsonl"
    manifest_path.write_text(json.dumps(make_manifest()), encoding="utf-8")
    records_path.write_text(json.dumps(make_row()) + "\n", encoding="utf-8")
    target = tmp_path / "no-such-dir" / "out.json"
    assert main([str(manifest_path), str(records_path), "--json", str(target)]) == 2
    assert not target.exists()


def test_report_explains_counts_and_exit_code():
    report = audit(make_manifest(["a", "b"]), [make_row()])
    page = render_html(report)
    assert "How to read" in page
    assert "missing" in page.lower()
    assert "coverage" in page.lower()
    assert "exit" in page.lower()
    assert "<script>" not in page


def test_report_escapes_imported_text():
    report = audit(make_manifest(["a", "<script>"]), [make_row(identifier="a")])
    page = render_html(report)
    assert "<script>" not in page
    assert "&lt;script&gt;" in page


def test_version_flag_prints_carried_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    out = capsys.readouterr().out.strip()
    assert out == f"eval-audit {__version__}"
    assert __version__[0].isdigit()


def test_reason_and_score_errors_carry_row_two():
    overflow = make_row()
    overflow.update({"id": "b", "reason": "x" * 4001})
    with pytest.raises(InputError) as excinfo:
        validate(make_manifest(), [make_row(), overflow])
    assert "record 2" in str(excinfo.value)
    nonfinite = make_row()
    nonfinite.update({"id": "b", "score": float("nan")})
    with pytest.raises(InputError) as excinfo:
        validate(make_manifest(), [make_row(), nonfinite])
    assert "record 2" in str(excinfo.value)


def test_duplicate_record_error_names_row():
    duplicate = {"id": "b", "status": "scored", "score": 1, "reason": ""}
    with pytest.raises(InputError) as excinfo:
        validate(make_manifest(["a", "b"]), [make_row(), duplicate, dict(duplicate)])
    assert "record 3" in str(excinfo.value)


def test_report_escapes_unexpected_and_errored_lists():
    report = audit(
        make_manifest(["a", "<b>err</b>"]),
        [
            make_row(),
            make_row("errored", 0.5, identifier="<b>err</b>"),
            make_row("unscored", None, identifier="<script>"),
        ],
    )
    page = render_html(report)
    assert "<script>" not in page
    assert "&lt;b&gt;err" in page
    assert "&lt;script&gt;" in page


def test_generic_report_does_not_claim_an_executed_example():
    manifest = make_manifest() | {"run_id": "local-real-run"}
    page = render_html(audit(manifest, [make_row()]))
    assert "static executed example" not in page.lower()
    assert "synthetic" not in page.lower()


def test_report_shows_score_availability_over_declared_population():
    report = audit(
        make_manifest(["a", "b", "c", "d"]),
        [make_row(score=0), make_row("errored", 0.25, identifier="b")],
    )
    page = render_html(report)
    assert "50%" in page
    assert "2 of 4 expected IDs" in page
    assert "task quality" in page.lower()


def test_near_complete_score_coverage_does_not_display_complete():
    manifest = make_manifest([str(index) for index in range(201)])
    rows = [make_row(identifier=str(index)) for index in range(200)]
    page = render_html(audit(manifest, rows))
    assert "99.5%" in page
    assert "200 of 201 expected IDs" in page
    assert ">100%<" not in page


class _ReportPage(HTMLParser):
    def __init__(self):
        super().__init__()
        self.articles = []
        self.links = []
        self.downloads = {}
        self._article = None

    def handle_starttag(self, tag, attrs):
        if tag == "article":
            self._article = []
        if tag == "a":
            attributes = dict(attrs)
            self.links.append(attributes.get("href"))
            if attributes.get("download"):
                self.downloads[attributes["download"]] = attributes.get("href")

    def handle_endtag(self, tag):
        if tag == "article" and self._article is not None:
            self.articles.append(" ".join(self._article))
            self._article = None

    def handle_data(self, data):
        if self._article is not None:
            self._article.append(data)


def test_report_case_evidence_keeps_zero_error_score_and_missing_distinct():
    manifest = make_manifest(["zero", "partial", "empty", "absent"])
    rows = [
        make_row(score=0, identifier="zero"),
        make_row("errored", 0.25, identifier="partial"),
        make_row("unscored", None, identifier="empty"),
    ]
    page = render_html(audit(manifest, rows), manifest=manifest, records=rows)
    parsed = _ReportPage()
    parsed.feed(page)
    assert len(parsed.articles) == 4
    zero, partial, empty, absent = parsed.articles
    assert "zero" in zero and "scored" in zero and "Score: 0" in zero
    assert "partial" in partial and "errored" in partial and "Score: 0.25" in partial
    assert "empty" in empty and "unscored" in empty and "No numeric score" in empty
    assert "absent" in absent and "missing" in absent and "No result record" in absent


def test_report_escapes_case_reason_source_and_provenance():
    imported = '<script>alert("case")</script><img src=x onerror="alert(1)"> &'
    manifest = make_manifest([imported])
    rows = [make_row(identifier=imported) | {"reason": imported}]
    report = audit(manifest, rows) | {"provenance": imported}
    page = render_html(
        report,
        manifest=manifest,
        records=rows,
        example={"title": imported, "source_text": imported, "source_sha256": imported},
    )
    assert "<script>" not in page
    assert "<img" not in page
    assert "&lt;script&gt;" in page
    assert "Source SHA-256" in page


def test_report_downloads_do_not_render_executable_urls():
    page = render_html(
        audit(make_manifest(), [make_row()]),
        example={"downloads": {"Unsafe": "javascript:alert(1)"}},
    )
    parsed = _ReportPage()
    parsed.feed(page)
    assert "javascript:alert(1)" not in parsed.links


@pytest.mark.parametrize(
    "filename,payload,mime",
    [
        ("report.json", b'{"score":0}\n', "application/json"),
        ("results.jsonl", b'{"id":"a"}\r\n', "application/x-ndjson"),
        ("source.txt", "Refund & receipt: \u2713\n".encode(), "text/plain"),
        ("bytes.bin", b"\x00\xff\r\n", "application/octet-stream"),
    ],
)
def test_report_embeds_exact_download_bytes_and_skips_unsafe_names(filename, payload, mime):
    page = render_html(
        audit(make_manifest(), [make_row()]),
        example={
            "downloads": {"Artifact": filename, "Unsafe": "../source.txt"},
            "download_files": {filename: payload, "../source.txt": b"unsafe"},
        },
    )
    parsed = _ReportPage()
    parsed.feed(page)
    assert set(parsed.downloads) == {filename}
    prefix, encoded = parsed.downloads[filename].split(",", 1)
    assert prefix == f"data:{mime};base64"
    assert base64.b64decode(encoded, validate=True) == payload
    assert "../source.txt" not in parsed.links


def test_demo_build_preserves_original_and_adds_downloadable_acceptance_evidence(
    tmp_path, monkeypatch
):
    repository = Path(__file__).resolve().parents[1]
    fixtures = tmp_path / "examples"
    fixtures.mkdir()
    names = (
        "manifest.json",
        "results.jsonl",
        "acceptance-manifest.json",
        "acceptance-results.jsonl",
        "acceptance-source.txt",
    )
    for name in names:
        (fixtures / name).write_bytes((repository / "examples" / name).read_bytes())
    monkeypatch.chdir(tmp_path)
    runpy.run_path(str(repository / "scripts" / "build_demo.py"), run_name="__main__")

    site = tmp_path / "site"
    assert (site / "acceptance.html").is_file()
    original_manifest, original_rows, original_hashes = load_inputs(
        fixtures / "manifest.json", fixtures / "results.jsonl"
    )
    assert json.loads((site / "report.json").read_text(encoding="utf-8")) == (
        audit(original_manifest, original_rows)
        | {"inputs": original_hashes, "provenance": "Synthetic, AI-assisted, non-client"}
    )
    acceptance = json.loads((site / "acceptance-report.json").read_text(encoding="utf-8"))
    assert set(acceptance) == {
        "schema_version",
        "run_id",
        "counts",
        "score_present_coverage",
        "missing_ids",
        "unexpected_ids",
        "errored_with_score_ids",
        "exit_code",
        "inputs",
        "provenance",
    }
    assert acceptance["counts"] == {
        "expected": 4,
        "scored": 1,
        "errored": 1,
        "unscored": 1,
        "missing": 1,
        "score_present": 2,
    }
    assert acceptance["score_present_coverage"] == 0.5
    assert acceptance["exit_code"] == 1
    assert acceptance["missing_ids"] == ["refund-baseline"]
    assert acceptance["errored_with_score_ids"] == ["refund-contradicted"]
    for name in names[2:]:
        assert (site / name).read_bytes() == (fixtures / name).read_bytes()
    assert acceptance["inputs"] == {
        "manifest_sha256": hashlib.sha256((site / names[2]).read_bytes()).hexdigest(),
        "records_sha256": hashlib.sha256((site / names[3]).read_bytes()).hexdigest(),
    }
    page = (site / "acceptance.html").read_text(encoding="utf-8")
    parsed = _ReportPage()
    parsed.feed(page)
    assert len(parsed.articles) == 4
    partial = next(article for article in parsed.articles if "refund-contradicted" in article)
    assert "errored" in partial and "Score: 0.9" in partial
    assert set(parsed.downloads) == {"acceptance-report.json", *names[2:]}
    for name, destination in parsed.downloads.items():
        prefix, encoded = destination.split(",", 1)
        assert prefix.startswith("data:") and prefix.endswith(";base64")
        assert base64.b64decode(encoded, validate=True) == (site / name).read_bytes()
    assert hashlib.sha256((site / names[4]).read_bytes()).hexdigest() in page
    assert "Synthetic, AI-assisted, non-client" in page
    assert "50%" in page
    assert "2 of 4 expected IDs" in page
    assert "acceptance.html" in (site / "index.html").read_text(encoding="utf-8")

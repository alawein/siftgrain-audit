import json
import os

import pytest

from siftgrain_audit.cli import main
from siftgrain_audit.contract import InputError, load_inputs, validate
from siftgrain_audit.core import audit
from siftgrain_audit.report import render_html


def manifest(ids=None):
    return {"schema_version": 1, "run_id": "synthetic", "expected_ids": ids or ["a"]}


def row(status="scored", score=1, identifier="a"):
    return {"id": identifier, "status": status, "score": score, "reason": ""}


@pytest.mark.parametrize(
    "rows, counts, exit_code",
    [
        ([row()], (1, 0, 0, 0, 1), 0),
        ([], (0, 0, 0, 1, 0), 1),
        ([row(score=0)], (1, 0, 0, 0, 1), 0),
        ([row("errored", None)], (0, 1, 0, 0, 0), 1),
        ([row("errored", 0.5)], (0, 1, 0, 0, 1), 1),
        ([row("unscored", None)], (0, 0, 1, 0, 0), 1),
    ],
)
def test_status_matrix(rows, counts, exit_code):
    result = audit(manifest(), rows)
    assert (
        tuple(
            result["counts"][k]
            for k in ["scored", "errored", "unscored", "missing", "score_present"]
        )
        == counts
    )
    assert result["exit_code"] == exit_code
    assert not {"accuracy", "mean"} & result.keys()


def test_missing_partial_unexpected_and_order():
    rows = [row(score=0), row("errored", 0.5, "b"), row(identifier="extra")]
    result = audit(manifest(["a", "b", "c"]), rows)
    assert result["missing_ids"] == ["c"]
    assert result["unexpected_ids"] == ["extra"]
    assert result["errored_with_score_ids"] == ["b"]
    assert result["counts"]["score_present"] == 2
    assert result["score_present_coverage"] == 2 / 3
    assert audit(manifest(["c", "a", "b"]), list(reversed(rows))) == result


@pytest.mark.parametrize("score", [True, float("nan"), float("inf"), "1", []])
def test_bad_score(score):
    with pytest.raises(InputError):
        validate(manifest(), [row(score=score)])


@pytest.mark.parametrize(
    "rows",
    [
        [row(), row()],
        [row("unscored", 1)],
        [row("scored", None)],
        [row("unknown")],
        [row() | {"extra": 1}],
        [row() | {"reason": "x" * 4001}],
    ],
)
def test_bad_rows(rows):
    with pytest.raises(InputError):
        audit(manifest(), rows)


@pytest.mark.parametrize(
    "change",
    [
        {"expected_ids": []},
        {"expected_ids": ["a", "a"]},
        {"schema_version": True},
        {"run_id": ""},
        {"expected_ids": ["x" * 201]},
    ],
)
def test_bad_manifest(change):
    with pytest.raises(InputError):
        audit(manifest() | change, [])


def files(tmp_path, raw=None):
    m, r = tmp_path / "manifest.json", tmp_path / "records.jsonl"
    m.write_text(json.dumps(manifest()), encoding="utf-8")
    r.write_bytes(raw if raw is not None else (json.dumps(row()) + "\n").encode())
    return m, r


@pytest.mark.parametrize(
    "raw",
    [
        b"\xef\xbb\xbf{}",
        b"\xff",
        b"\n",
        b"{}\n\n",
        b'{"id":"a","id":"b"}',
        b'{"score":NaN}',
        b"x" * (5 * 1024 * 1024 + 1),
    ],
    ids=["bom", "utf8", "blank", "interior-blank", "duplicate-key", "nan", "oversize"],
)
def test_bad_bytes(tmp_path, raw):
    m, r = files(tmp_path, raw)
    with pytest.raises(InputError):
        load_inputs(m, r)
    output = tmp_path / "report.json"
    assert main([str(m), str(r), "--json", str(output)]) == 2
    assert not output.exists()


def test_unicode_and_big_integer(tmp_path):
    raw = (
        json.dumps(row(score=10**399) | {"reason": "Arabic عربي\u2028emoji 😀"}, ensure_ascii=False)
        + "\n"
    ).encode()
    m, r = files(tmp_path, raw)
    assert load_inputs(m, r)[1][0]["score"] == 10**399


def test_limits():
    ids = [str(i) for i in range(10000)]
    assert audit(manifest(ids), [row(identifier=i) for i in ids])["exit_code"] == 0
    with pytest.raises(InputError):
        audit(manifest(ids + ["overflow"]), [])


def test_output_identity_and_preservation(tmp_path):
    m, r = files(tmp_path)
    output = tmp_path / "report.json"
    output.write_text("KEEP")
    assert main([str(m), str(r), "--json", str(output)]) == 2
    assert output.read_text() == "KEEP"
    before = m.read_bytes()
    alias = tmp_path / "alias.json"
    os.link(m, alias)
    assert main([str(m), str(r), "--json", str(alias), "--force"]) == 2
    assert m.read_bytes() == before
    alias2 = tmp_path / "alias2.json"
    os.link(output, alias2)
    assert main([str(m), str(r), "--json", str(output), "--html", str(alias2), "--force"]) == 2
    assert output.read_text() == "KEEP"
    assert main([str(m), str(r), "--json", str(output), "--force"]) == 0
    assert json.loads(output.read_text())["counts"]["scored"] == 1


def test_html_text_is_escaped():
    assert "<script>" not in render_html({"run_id": "<script>alert(1)</script>"})
    assert "&lt;script&gt;" in render_html({"run_id": "<script>"})

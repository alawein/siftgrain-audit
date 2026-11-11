import json
import zipfile

import pytest
from test_audit import manifest

from siftgrain_audit.adapters import convert
from siftgrain_audit.cli import main
from siftgrain_audit.contract import InputError, load_inputs


def write(tmp_path, value):
    source = tmp_path / "source.json"
    source.write_text(json.dumps(value), encoding="utf-8")
    return source


def test_inspect_epochs_error_and_partial_score(tmp_path):
    samples = [
        {"id": "a", "epoch": 1, "scores": {"metric": {"value": 0}}},
        {
            "id": "a",
            "epoch": 2,
            "error": {"message": "failed"},
            "scores": {"metric": {"value": 0.5}},
        },
    ]
    population = manifest() | {"schema_version": 2, "trials_per_id": 2}
    source = write(tmp_path, {"samples": samples, "eval": {"dataset": {"samples": 999}}})
    rows = convert("inspect", population, source, "metric")
    assert [(r["trial"], r["status"], r["score"]) for r in rows] == [
        (1, "scored", 0),
        (2, "errored", 0.5),
    ]
    archive = tmp_path / "log.eval"
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr("header.json", "{}")
        for index, sample in enumerate(samples):
            stream.writestr(f"samples/{index}.json", json.dumps(sample))
    assert convert("inspect", population, archive, "metric") == rows


def test_lm_harness_jsonl_metric_and_missing_score(tmp_path):
    source = tmp_path / "samples.jsonl"
    source.write_text('{"doc_id":0,"acc,none":0}\n{"doc_id":1}\n', encoding="utf-8")
    rows = convert("lm-evaluation-harness", manifest(["0", "1"]), source, "acc,none")
    assert rows == [
        {"id": "0", "status": "scored", "score": 0, "reason": ""},
        {"id": "1", "status": "unscored", "score": None, "reason": ""},
    ]


def test_promptfoo_test_prompt_pair_is_explicit_id(tmp_path):
    source = write(
        tmp_path,
        {
            "results": {
                "results": [
                    {"testIdx": 0, "promptIdx": 1, "success": False, "score": 0},
                    {"testIdx": 1, "promptIdx": 1, "error": "provider failed", "score": 0.2},
                ]
            }
        },
    )
    rows = convert("promptfoo", manifest(["0:1", "1:1"]), source)
    assert rows[0]["status"] == "scored"
    assert rows[1]["status"] == "errored"
    assert rows[1]["score"] == 0.2


@pytest.mark.parametrize("bad", [True, float("nan"), float("inf"), "C", {"metric": 1}])
def test_inspect_rejects_unsupported_score_without_silent_drop(tmp_path, bad):
    source = write(tmp_path, {"samples": [{"id": "a", "scores": {"metric": {"value": bad}}}]})
    with pytest.raises(InputError, match="record 1|source: nonfinite"):
        convert("inspect", manifest(), source, "metric")


def test_inspect_missing_requested_key_errors(tmp_path):
    source = write(tmp_path, {"samples": [{"id": "a", "scores": {"other": {"value": 1}}}]})
    with pytest.raises(InputError, match="score key"):
        convert("inspect", manifest(), source, "metric")


def test_inspect_declared_dropped_fields_do_not_change_score_mapping(tmp_path):
    sample = {"id": "a", "scores": {"metric": {"value": 0}}}
    source = write(tmp_path, {"samples": [sample]})
    before = convert("inspect", manifest(), source, "metric")
    source = write(
        tmp_path,
        {
            "samples": [
                sample
                | {
                    "messages": [{"content": "not a score"}],
                    "target": "not evidence",
                    "metadata": {"accuracy": 1},
                    "events": [],
                    "output": {"choices": []},
                }
            ],
            "results": {"accuracy": 1},
        },
    )
    assert convert("inspect", manifest(), source, "metric") == before


def test_conversion_cli_preserves_source_and_explicit_population(tmp_path):
    source = write(tmp_path, {"samples": [{"id": "a", "scores": {"metric": {"value": 1}}}]})
    population = tmp_path / "manifest.json"
    population.write_text(json.dumps(manifest(["a", "missing"])), encoding="utf-8")
    out = tmp_path / "canonical.jsonl"
    assert (
        main(
            [
                "convert",
                "inspect",
                str(source),
                "--manifest",
                str(population),
                "--score-key",
                "metric",
                "--output",
                str(out),
            ]
        )
        == 0
    )
    assert len(out.read_text().splitlines()) == 1
    before = source.read_bytes()
    assert (
        main(
            [
                "convert",
                "inspect",
                str(source),
                "--manifest",
                str(population),
                "--score-key",
                "metric",
                "--output",
                str(source),
                "--force",
            ]
        )
        == 2
    )
    assert source.read_bytes() == before


def test_duplicate_zip_sample_names_rejected(tmp_path):
    source = tmp_path / "log.eval"
    with zipfile.ZipFile(source, "w") as stream:
        stream.writestr("samples/a.json", '{"id":"a"}')
        with pytest.warns(UserWarning):
            stream.writestr("samples/a.json", '{"id":"b"}')
    with pytest.raises(InputError, match="duplicate"):
        convert("inspect", manifest(), source, "metric")


def test_explicit_categorical_mapping_is_required(tmp_path):
    source = write(tmp_path, {"samples": [{"id": "a", "scores": {"metric": {"value": "C"}}}]})
    with pytest.raises(InputError):
        convert("inspect", manifest(), source, "metric")
    assert convert("inspect", manifest(), source, "metric", {"C": 1})[0]["score"] == 1
    with pytest.raises(InputError, match="record 1"):
        convert("inspect", manifest(), source, "metric", {"I": 0})
    with pytest.raises(InputError):
        convert("inspect", manifest(), source, "metric", {"C": True})


@pytest.mark.parametrize("scores", [[], False, 0, ""])
def test_falsy_malformed_scores_not_coerced_to_unscored(tmp_path, scores):
    source = write(tmp_path, {"samples": [{"id": "a", "scores": scores}]})
    with pytest.raises(InputError, match="record 1"):
        convert("inspect", manifest(), source, "metric")


def test_encrypted_archive_is_controlled_invalid_input(tmp_path, monkeypatch):
    source = tmp_path / "encrypted.eval"
    source.write_bytes(b"placeholder")
    member = zipfile.ZipInfo("samples/a.json")
    member.flag_bits = 1

    class EncryptedArchive:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def infolist(self):
            return [member]

        def read(self, *args):
            raise RuntimeError("password required")

    monkeypatch.setattr(zipfile, "ZipFile", lambda *args: EncryptedArchive())
    with pytest.raises(InputError, match="encrypted"):
        convert("inspect", manifest(), source, "metric")


def test_promptfoo_documented_v3_outputs_envelope(tmp_path):
    source = write(
        tmp_path,
        {
            "version": 3,
            "results": {
                "outputs": [{"testIdx": 0, "promptIdx": 0, "score": 0, "pass": False}],
                "stats": {},
            },
        },
    )
    assert convert("promptfoo", manifest(["0:0"]), source) == [
        {"id": "0:0", "status": "scored", "score": 0, "reason": ""}
    ]


def test_promptfoo_ambiguous_envelopes_fail(tmp_path):
    source = write(tmp_path, {"results": {"results": [], "outputs": []}})
    with pytest.raises(InputError, match="ambiguous"):
        convert("promptfoo", manifest(), source)


def test_unicode_conversion_output_is_loadable_under_byte_limit(tmp_path):
    source = tmp_path / "unicode.json"
    samples = [{"id": index, "error": "漢" * 4000} for index in range(300)]
    source.write_text(json.dumps({"samples": samples}, ensure_ascii=False), encoding="utf-8")
    population = tmp_path / "manifest.json"
    population.write_text(
        json.dumps(manifest([str(index) for index in range(300)])), encoding="utf-8"
    )
    output = tmp_path / "converted.jsonl"
    assert source.stat().st_size < 5 * 1024 * 1024
    assert (
        main(
            [
                "convert",
                "inspect",
                str(source),
                "--manifest",
                str(population),
                "--score-key",
                "metric",
                "--output",
                str(output),
            ]
        )
        == 0
    )
    assert len(load_inputs(population, output)[1]) == 300


def test_conversion_byte_expansion_fails_before_staging(tmp_path):
    samples = [{"id": index, "error": "r" * 490} for index in range(10000)]
    source = write(tmp_path, {"samples": samples})
    assert source.stat().st_size < 5 * 1024 * 1024
    population = tmp_path / "manifest.json"
    population.write_text(
        json.dumps(manifest([str(index) for index in range(10000)])), encoding="utf-8"
    )
    output = tmp_path / "converted.jsonl"
    output.write_text("KEEP", encoding="utf-8")
    assert (
        main(
            [
                "convert",
                "inspect",
                str(source),
                "--manifest",
                str(population),
                "--score-key",
                "metric",
                "--output",
                str(output),
                "--force",
            ]
        )
        == 2
    )
    assert output.read_text() == "KEEP"


@pytest.mark.parametrize("compression, offset", [(zipfile.ZIP_DEFLATED, 0), (zipfile.ZIP_LZMA, 4)])
def test_corrupt_compressed_archive_returns_exit_two_preserving_output(
    tmp_path, compression, offset
):
    source = tmp_path / "broken.eval"
    filename = "samples/a.json"
    with zipfile.ZipFile(source, "w", compression=compression) as stream:
        stream.writestr(filename, '{"id":"a","scores":{"metric":{"value":1}}}')
    damaged = bytearray(source.read_bytes())
    damaged[30 + len(filename) + offset] = 0xFF  # Invalid DEFLATE type or LZMA properties.
    source.write_bytes(damaged)
    population = tmp_path / "manifest.json"
    population.write_text(json.dumps(manifest()), encoding="utf-8")
    output = tmp_path / "converted.jsonl"
    output.write_text("KEEP", encoding="utf-8")
    assert (
        main(
            [
                "convert",
                "inspect",
                str(source),
                "--manifest",
                str(population),
                "--score-key",
                "metric",
                "--output",
                str(output),
                "--force",
            ]
        )
        == 2
    )
    assert output.read_text() == "KEEP"

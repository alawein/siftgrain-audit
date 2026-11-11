import json
import subprocess
import sys
from pathlib import Path


def test_consumer_gate_rejects_silent_shrinkage(tmp_path):
    manifest = tmp_path / "manifest.json"
    records = tmp_path / "records.jsonl"
    manifest.write_text(
        json.dumps({"schema_version": 1, "run_id": "ci", "expected_ids": ["a", "b"]}),
        encoding="utf-8",
    )
    records.write_text(
        json.dumps({"id": "a", "status": "scored", "score": 1, "reason": ""}) + "\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).parents[1] / "scripts/coverage_gate.py"),
            str(manifest),
            str(records),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert json.loads(result.stdout)["counts"]["expected"] == 2


def test_consumer_manifest_path_cannot_be_interpreted_as_help(tmp_path):
    (tmp_path / "--help").write_text(
        json.dumps({"schema_version": 1, "run_id": "ci", "expected_ids": ["a", "b"]}),
        encoding="utf-8",
    )
    records = tmp_path / "records.jsonl"
    records.write_text(
        json.dumps({"id": "a", "status": "scored", "score": 1, "reason": ""}) + "\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).parents[1] / "scripts/coverage_gate.py"),
            "--help",
            str(records),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert json.loads(result.stdout)["counts"]["missing"] == 1

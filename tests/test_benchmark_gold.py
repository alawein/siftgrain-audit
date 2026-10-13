import json
import runpy
from pathlib import Path

import pytest


def test_benchmark_fails_when_detector_misses_seeded_fault():
    namespace = runpy.run_path(str(Path(__file__).parents[1] / "benchmarks/run.py"))
    gold = {"should_flag": True, "invalid": False, "missing": [{"id": "a", "trial": 1}]}
    with pytest.raises(AssertionError, match="flag"):
        namespace["check_gold"]("seeded-drop", False, {"missing_trials": []}, None, gold)


def test_benchmark_fails_on_corrupted_answer_key_or_silent_invalid_acceptance():
    namespace = runpy.run_path(str(Path(__file__).parents[1] / "benchmarks/run.py"))
    gold = {"should_flag": True, "invalid": False, "missing": [{"id": "a", "trial": 1}]}
    with pytest.raises(AssertionError, match="missing"):
        namespace["check_gold"]("wrong-key", True, {"missing_trials": []}, None, gold)
    with pytest.raises(AssertionError, match="rejection"):
        namespace["check_gold"]("nan", True, {"missing_trials": []}, None, gold | {"invalid": True})


def test_benchmark_json_uses_lf_on_every_platform(tmp_path):
    namespace = runpy.run_path(str(Path(__file__).parents[1] / "benchmarks/run.py"))
    target = tmp_path / "data.json"
    namespace["write_json"](target, {"x": 1})
    assert b"\r" not in target.read_bytes()


def test_download_checksums_use_portable_paths_and_match_bytes():
    import hashlib

    root = Path(__file__).parents[1] / "benchmarks/dataset-v1"
    checksums = json.loads((root / "checksums.json").read_text())
    assert not any("\\" in name for name in checksums)
    assert all(
        hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
        for name, digest in checksums.items()
    )

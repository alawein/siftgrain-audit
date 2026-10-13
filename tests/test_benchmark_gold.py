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

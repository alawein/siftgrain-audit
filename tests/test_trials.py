import pytest
from test_audit import manifest, row

from siftgrain_audit.contract import InputError
from siftgrain_audit.core import audit


def test_trials_missing_and_mixed_partition():
    population = manifest(["a", "b"]) | {"schema_version": 2, "trials_per_id": 2}
    result = audit(population, [row() | {"trial": 1}, row("errored", 0, "a") | {"trial": 2}])
    assert result["schema_version"] == 2
    assert result["counts"] == dict(
        expected=2, scored=0, errored=1, unscored=0, missing=1, score_present=1
    )
    assert result["trial_counts"] == dict(
        expected=4,
        delivered=2,
        scored=1,
        errored=1,
        unscored=0,
        missing=2,
        score_present=2,
        unexpected=0,
        duplicate=0,
    )
    assert result["complete_ids"] == ["a"]
    assert result["missing_trials"] == [{"id": "b", "trial": 1}, {"id": "b", "trial": 2}]
    assert result["pass_k_denominators"]["1"] == dict(expected_ids=2, all_k_trials_scored=1)
    assert result["pass_k_denominators"]["2"] == dict(expected_ids=2, all_k_trials_scored=0)


def test_per_id_trials_unexpected_and_order():
    population = manifest(["a", "b"]) | {"trials_per_id": {"a": 2, "b": 1}}
    rows = [row() | {"trial": 2}, row(), row(identifier="b"), row() | {"trial": 3}]
    result = audit(population, rows)
    assert result == audit(population | {"expected_ids": ["b", "a"]}, list(reversed(rows)))
    assert result["unexpected_trials"] == [{"id": "a", "trial": 3}]
    assert result["trial_counts"]["expected"] == 3
    assert result["trial_counts"]["unexpected"] == 1
    assert result["complete_ids"] == ["a", "b"]
    assert result["exit_code"] == 1


@pytest.mark.parametrize("trials", [True, 0, -1, 1.5, {"a": True}, {}, {"a": 10001}])
def test_invalid_trial_plans(trials):
    with pytest.raises(InputError):
        audit(manifest() | {"trials_per_id": trials}, [])


@pytest.mark.parametrize("trial", [True, 0, -1, 1.5, "1"])
def test_invalid_trial_numbers_have_row(trial):
    with pytest.raises(InputError, match="record 1"):
        audit(manifest() | {"trials_per_id": 2}, [row() | {"trial": trial}])


def test_duplicate_trial_is_not_duplicate_id():
    with pytest.raises(InputError, match="record 2"):
        audit(manifest() | {"trials_per_id": 2}, [row(), row() | {"trial": 1}])


def test_legacy_duplicate_diagnostic_is_byte_compatible():
    with pytest.raises(InputError) as error:
        audit(manifest(), [row(), row()])
    assert str(error.value) == "duplicate record ID at record 2: a"


def test_schema_two_defaults_to_one_trial():
    result = audit(manifest() | {"schema_version": 2}, [row()])
    assert result["trial_counts"]["expected"] == 1
    assert result["exit_code"] == 0


def test_missing_precedes_error_and_unscored():
    result = audit(
        manifest() | {"trials_per_id": 3}, [row("errored", 1), row("unscored", None) | {"trial": 2}]
    )
    assert result["counts"]["missing"] == 1
    assert result["trial_counts"]["errored"] == 1
    assert result["trial_counts"]["unscored"] == 1
    assert result["counts"]["score_present"] == 0


@pytest.mark.parametrize("score", [True, False, float("nan"), float("inf"), -float("inf")])
def test_numeric_edges_row_two(score):
    with pytest.raises(InputError, match="record 2"):
        audit(manifest(["a", "b"]), [row(), row(score=score, identifier="b")])

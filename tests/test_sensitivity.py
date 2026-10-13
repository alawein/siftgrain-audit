import pytest

from eval_audit import sensitivity


def test_sensitivity_keeps_error_policy_and_missing_denominator_explicit():
    manifest = {"schema_version": 2, "run_id": "r", "expected_ids": ["a", "b", "c"]}
    rows = [
        {"id": "a", "status": "scored", "score": 0, "reason": ""},
        {"id": "b", "status": "errored", "score": 0.75, "reason": "timeout"},
        {"id": "extra", "status": "scored", "score": 99, "reason": ""},
    ]
    view = sensitivity.score_sensitivity(manifest, rows)
    assert view["policies"]["expected_zero_fill"] == {"denominator": 3, "sum": "3/4", "mean": "1/4"}
    assert view["policies"]["score_available"]["mean"] == "3/8"
    assert view["policies"]["scored_only"]["mean"] == "0"
    assert "pass_k_denominators" not in view


def test_sensitivity_undefined_mean_and_invalid_score():
    manifest = {"schema_version": 1, "run_id": "r", "expected_ids": ["a"]}
    assert sensitivity.score_sensitivity(manifest, [])["policies"]["scored_only"]["mean"] is None
    with pytest.raises(ValueError):
        sensitivity.score_sensitivity(
            manifest, [{"id": "a", "status": "scored", "score": True, "reason": ""}]
        )

import json

import pytest

from eval_audit.adapters import convert


@pytest.mark.parametrize(
    "adapter,document",
    [
        (
            "helm",
            [
                {
                    "instance_id": "a",
                    "train_trial_index": 0,
                    "stats": [{"name": {"name": "exact_match"}, "mean": 0.0}],
                }
            ],
        ),
        ("open-llm-leaderboard", [{"doc_id": "a", "exact_match": 0.0}]),
    ],
)
def test_detail_adapters_preserve_zero_and_explicit_population(tmp_path, adapter, document):
    source = tmp_path / "details.json"
    source.write_text(json.dumps(document), encoding="utf-8")
    manifest = {"schema_version": 2, "run_id": "run", "expected_ids": ["a", "b"]}
    assert convert(adapter, manifest, source, "exact_match") == [
        {"id": "a", "trial": 1, "status": "scored", "score": 0.0, "reason": ""}
    ]


@pytest.mark.parametrize(
    "adapter,document",
    [
        (
            "helm",
            [
                {
                    "instance_id": "a",
                    "stats": [
                        {"name": {"name": "x"}, "mean": 1},
                        {"name": {"name": "x"}, "mean": 0},
                    ],
                }
            ],
        ),
        ("open-llm-leaderboard", [{"doc_id": "a", "x": True}]),
    ],
)
def test_detail_adapters_reject_ambiguous_or_boolean_scores(tmp_path, adapter, document):
    source = tmp_path / "details.json"
    source.write_text(json.dumps(document), encoding="utf-8")
    manifest = {"schema_version": 2, "run_id": "run", "expected_ids": ["a"]}
    with pytest.raises(ValueError, match="record 1"):
        convert(adapter, manifest, source, "x")


def test_helm_does_not_silently_mix_perturbed_instances(tmp_path):
    source = tmp_path / "stats.json"
    source.write_text(
        json.dumps([{"instance_id": "a", "perturbation": {"name": "noise"}, "stats": []}]),
        encoding="utf-8",
    )
    manifest = {"schema_version": 2, "run_id": "run", "expected_ids": ["a"]}
    with pytest.raises(ValueError, match="perturbation.*record 1"):
        convert("helm", manifest, source, "x")

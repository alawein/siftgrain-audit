"""Offline audit of a pinned ten-sample Inspect archive; never executes a model."""

import argparse
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path

from siftgrain_audit.adapters import convert
from siftgrain_audit.core import audit

SOURCE_SHA256 = "6631813cb3cc25908d760d36677925a0e5753d06602c7d97385a4f448bafd9a1"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        parser.error("source checksum differs from the pinned public archive")
    with zipfile.ZipFile(args.source) as archive:
        header = json.loads(archive.read("header.json"))
        samples = [
            json.loads(archive.read(name))
            for name in archive.namelist()
            if name.startswith("samples/") and name.endswith(".json")
        ]
    assert header["eval"]["dataset"]["sample_ids"] == list(range(1, 11))
    assert header["eval"]["config"]["limit"] == 10
    assert header["results"]["total_samples"] == 10
    manifest = {
        "schema_version": 2,
        "run_id": "inspect-popularity-2025-02-11",
        "expected_ids": [str(i) for i in range(1, 11)],
        "trials_per_id": 1,
    }
    rows = convert("inspect", manifest, args.source, "match", {"C": 1, "I": 0})
    report = audit(manifest, rows)
    with tempfile.TemporaryDirectory() as directory:
        permuted = Path(directory) / "permuted.json"
        permuted.write_text(json.dumps({"samples": list(reversed(samples))}), encoding="utf-8")
        repeated = convert("inspect", manifest, permuted, "match", {"C": 1, "I": 0})
        assert report == audit(manifest, repeated)
        assert hashlib.sha256(permuted.read_bytes()).hexdigest() != SOURCE_SHA256
    assert report == audit(manifest, rows)
    counts = report["trial_counts"]
    result = {
        "source_sha256": SOURCE_SHA256,
        "source_bytes": len(raw),
        "selected_ids": manifest["expected_ids"],
        "dataset_size_before_limit": header["eval"]["dataset"]["samples"],
        "audit": report,
        "explicit_planned_denominator": 10,
        "delivered_denominator": counts["delivered"],
        "score_available_denominator": counts["score_present"],
        "planned_minus_delivered": 10 - counts["delivered"],
        "planned_minus_score_available": 10 - counts["score_present"],
        "upstream_headline_denominator": None,
        "upstream_headline_reason": "Archived results.scores is empty; no headline is asserted.",
        "score_mapping": {"key": "match", "categorical": {"C": 1, "I": 0}},
        "permutation_and_repeat_equal": True,
        "limitations": [
            "Selected ten-sample example; not representative failure-rate evidence.",
            "All score dictionaries are empty; scores are not reconstructed from model output.",
            "Upstream model execution and scorer execution are not repeated.",
            "No pass@k or pass^k rates are computed; readiness k=1 only.",
        ],
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("PASS: pinned offline ten-sample archive; repeat and permutation counts identical")


if __name__ == "__main__":
    main()

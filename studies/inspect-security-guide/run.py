"""Offline re-audit of an upstream recorded Inspect run; never runs its scorer."""

import argparse
import hashlib
import json
from pathlib import Path

from siftgrain_audit.adapters import convert
from siftgrain_audit.core import audit

SOURCE_SHA256 = "44f6203d88252de0c33f76c948ad7c537b412cff628c704e9a5449ffba9d5a34"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        parser.error("source checksum differs from the pinned public log")
    log = json.loads(raw)
    # Explicit selected IDs from the header, not IDs inferred from delivered rows.
    manifest = {
        "schema_version": 1,
        "run_id": "inspect-security-guide-2025-05-12",
        "expected_ids": ["1", "2", "3"],
    }
    assert log["eval"]["dataset"]["sample_ids"] == [1, 2, 3]
    assert log["eval"]["config"]["limit"] == 3
    rows = convert("inspect", manifest, args.source, "model_graded_fact", {"C": 1})
    report = audit(manifest, rows)
    assert report == audit(manifest, list(reversed(rows)))
    result = {
        "source_sha256": SOURCE_SHA256,
        "run_selected_ids": manifest["expected_ids"],
        "dataset_size_before_limit": log["eval"]["dataset"]["samples"],
        "audit": report,
        "headline_accuracy_recorded_by_upstream": 1.0,
        "headline_denominator": 3,
        "explicit_expected_denominator": report["counts"]["expected"],
        "denominator_shift": report["counts"]["expected"] - 3,
        "score_map": {"C": 1},
        "limitations": [
            "Three-record pilot of a real archived example evaluation, not a population study.",
            "The model and model-graded scorer were run by upstream; neither is rerun here.",
            "Coverage and byte integrity do not establish correctness of the scores.",
            "The dataset size of 16 is not the selected run denominator.",
        ],
    }
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    print("PASS: offline public-log audit; see output for counts")


if __name__ == "__main__":
    main()

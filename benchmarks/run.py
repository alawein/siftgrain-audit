"""Pinned public-log fault benchmark. Fetch is explicit and outside the product core."""

import argparse
import copy
import hashlib
import json
import platform
import random
import statistics
import sys
import tempfile
import time
import tracemalloc
import urllib.request
import zipfile
from pathlib import Path

from eval_audit.adapters import convert
from eval_audit.core import audit

ROOT = Path(__file__).resolve().parent
URL = (
    "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_ai/"
    "4acfd207ecca8e1c3b754a147c191f2f0f21ba71/tests/analysis/test_logs/"
    "2025-05-12T20-28-26-04-00_security-guide.json"
)
SHA = "44f6203d88252de0c33f76c948ad7c537b412cff628c704e9a5449ffba9d5a34"
FAULTS = ("drop", "duplicate", "error", "nan", "shuffled_epochs", "partial_retries")


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )


def metrics(actual: list[bool], predicted: list[bool]) -> dict:
    tp = sum(a and p for a, p in zip(actual, predicted, strict=True))
    fp = sum(not a and p for a, p in zip(actual, predicted, strict=True))
    fn = sum(a and not p for a, p in zip(actual, predicted, strict=True))
    tn = sum(not a and not p for a, p in zip(actual, predicted, strict=True))
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": tp / (tp + fp) if tp + fp else None,
        "recall": tp / (tp + fn) if tp + fn else None,
    }


def build_cases(document: dict) -> list[tuple[str, dict, dict, dict]]:
    # Population is independently declared by the archived run's selected header.
    selected = document["eval"]["dataset"]["sample_ids"]
    if selected != [1, 2, 3]:
        raise ValueError("selected header differs from pinned three-ID plan")
    cases = []
    for split, offset in (("dev", 1000), ("test", 2000)):
        for seed in range(offset, offset + 20):
            rng = random.Random(seed)
            base = []
            for sample in document["samples"]:
                for epoch in (1, 2):
                    value = copy.deepcopy(sample)
                    value["epoch"] = epoch
                    base.append(value)
            manifest = {
                "schema_version": 2,
                "run_id": f"fault-{seed}",
                "expected_ids": ["1", "2", "3"],
                "trials_per_id": 2,
            }
            for fault in ("clean",) + FAULTS:
                samples = copy.deepcopy(base)
                chosen = rng.randrange(len(samples))
                missing = []
                if fault == "drop":
                    removed = samples.pop(chosen)
                    missing = [{"id": str(removed["id"]), "trial": removed["epoch"]}]
                elif fault == "duplicate":
                    samples.append(copy.deepcopy(samples[chosen]))
                elif fault == "error":
                    samples[chosen]["error"] = {"message": "seeded execution error"}
                elif fault == "nan":
                    samples[chosen]["scores"]["model_graded_fact"]["value"] = float("nan")
                elif fault == "partial_retries":
                    missing = [{"id": str(s["id"]), "trial": 2} for s in samples if s["epoch"] == 2]
                    samples = [s for s in samples if s["epoch"] == 1]
                rng.shuffle(samples)
                gold = {
                    "fault": fault,
                    "should_flag": fault not in ("clean", "shuffled_epochs"),
                    "invalid": fault in ("duplicate", "nan"),
                    "expected_trials": 6,
                    "missing": sorted(missing, key=lambda row: (row["id"], row["trial"])),
                }
                # Export mapped fields only; original model responses are not needed.
                narrow = [
                    {key: s[key] for key in ("id", "epoch", "scores", "error") if key in s}
                    for s in samples
                ]
                for row in narrow:
                    row["scores"] = {
                        key: {"value": value.get("value")}
                        for key, value in row.get("scores", {}).items()
                    }
                cases.append((f"{split}-{seed}-{fault}", manifest, {"samples": narrow}, gold))
    return cases


def evaluate(manifest: dict, source: Path) -> tuple[bool, dict | None, str | None]:
    try:
        rows = convert("inspect", manifest, source, "model_graded_fact", {"C": 1, "I": 0})
        report = audit(manifest, rows)
        return bool(report["exit_code"]), report, None
    except ValueError as exc:
        return True, None, "duplicate" if "duplicate" in str(exc) else "invalid"


def check_gold(
    name: str, flagged: bool, report: dict | None, rejection: str | None, gold: dict
) -> None:
    if flagged != gold["should_flag"]:
        raise AssertionError(f"wrong flag: {name}")
    if bool(rejection) != gold["invalid"]:
        raise AssertionError(f"wrong rejection: {name}")
    if report and report["missing_trials"] != gold["missing"]:
        raise AssertionError(f"wrong missing set: {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="download the pinned public log once")
    parser.add_argument(
        "--source", type=Path, default=ROOT.parent / "studies/data/security-guide.json"
    )
    args = parser.parse_args()
    if args.fetch and not args.source.exists():
        args.source.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(URL, timeout=30) as response:
            raw = response.read(5 * 1024 * 1024 + 1)
        if hashlib.sha256(raw).hexdigest() != SHA:
            raise ValueError("download checksum mismatch")
        args.source.write_bytes(raw)
    raw = args.source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("source checksum mismatch")
    document = json.loads(raw)
    cases = build_cases(document)
    data = ROOT / "dataset-v1"
    data.mkdir(exist_ok=True)
    results, keys = [], {"dev": [], "test": []}
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / "source.json"
        for name, manifest, sample_log, gold in cases:
            encoded = json.dumps(sample_log, sort_keys=True) + "\n"
            source.write_text(encoded, encoding="utf-8", newline="\n")
            start = time.perf_counter()
            flagged, report, rejection = evaluate(manifest, source)
            elapsed = time.perf_counter() - start
            source.write_text(
                json.dumps({"samples": list(reversed(sample_log["samples"]))}), encoding="utf-8"
            )
            repeated = evaluate(manifest, source)
            invariant = (flagged, report, rejection) == repeated
            check_gold(name, flagged, report, rejection, gold)
            # Naive baseline: accept any delivered numeric score, use scored rows as N.
            naive_n = sum(
                isinstance(
                    s.get("scores", {}).get("model_graded_fact", {}).get("value"), (int, float)
                )
                or s.get("scores", {}).get("model_graded_fact", {}).get("value") in ("C", "I")
                for s in sample_log["samples"]
            )
            results.append(
                {
                    "case": name,
                    "fault": gold["fault"],
                    "actual": gold["should_flag"],
                    "flagged": flagged,
                    "rejected": rejection,
                    "expected_denominator_error": report["trial_counts"]["expected"] - 6
                    if report
                    else None,
                    "naive_flagged": naive_n == 0,
                    "naive_denominator_error": naive_n - 6,
                    "order_deterministic": invariant,
                    "seconds": elapsed,
                }
            )
            split = name.split("-")[0]
            split_dir = data / split
            split_dir.mkdir(exist_ok=True)
            write_json(split_dir / f"{name}-manifest.json", manifest)
            (split_dir / f"{name}-inspect.json").write_text(encoded, encoding="utf-8", newline="\n")
            keys[split].append({"case": name, **gold})
    for split, key in keys.items():
        write_json(data / f"{split}-answers.json", key)
    by_fault = {}
    for fault in FAULTS:
        subset = [r for r in results if r["fault"] in (fault, "clean")]
        by_fault[fault] = {
            "census": metrics([r["actual"] for r in subset], [r["flagged"] for r in subset]),
            "naive": metrics([r["actual"] for r in subset], [r["naive_flagged"] for r in subset]),
        }
    manifest = {
        "schema_version": 2,
        "run_id": "stress",
        "expected_ids": [str(i) for i in range(10000)],
    }
    tracemalloc.start()
    stress_start = time.perf_counter()
    audit(manifest, [])
    stress_seconds = time.perf_counter() - stress_start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    summary = {
        "schema_version": 1,
        "source_sha256": SHA,
        "source_url": URL,
        "access_date": "2026-10-13",
        "run_date": "2025-05-12",
        "license": "MIT",
        "source_commit": "4acfd207ecca8e1c3b754a147c191f2f0f21ba71",
        "cases": len(results),
        "metrics": by_fault,
        "all_order_deterministic": all(r["order_deterministic"] for r in results),
        "max_absolute_expected_denominator_error": max(
            abs(r["expected_denominator_error"])
            for r in results
            if r["expected_denominator_error"] is not None
        ),
        "invalid_cases_rejected": sum(r["rejected"] is not None for r in results),
        "performance": {
            "python": sys.version,
            "platform": platform.platform(),
            "median_case_ms": statistics.median(r["seconds"] for r in results) * 1000,
            "stress_10000_missing_seconds": stress_seconds,
            "tracemalloc_peak_bytes": peak,
        },
        "native_inspect_baseline": "Executed separately: native-inspect-results.json (0.3.279)",
        "native_lm_eval_baseline": "not run; source is Inspect, not lm-eval",
        "llm_baseline": "omitted; no model calls",
        "human_labels": "none",
        "limitations": [
            "Three actual archived selected samples; not representative.",
            "Epoch 2 and all injected faults are synthetic transformations.",
            "Binary run-level precision/recall, not record localization metrics.",
            "No statistical CI: deterministic exhaustively enumerated seeded suite.",
        ],
    }
    write_json(ROOT / "results.json", summary)
    write_json(ROOT / "case-results.json", results)
    checksums = {
        str(p.relative_to(data)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(data.rglob("*.json"))
        if p.name != "checksums.json"
    }
    write_json(data / "checksums.json", checksums)
    with zipfile.ZipFile(ROOT / "dataset-v1.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        paths = list(data.rglob("*.json")) + [
            ROOT / name
            for name in (
                "UPSTREAM-LICENSE.txt",
                "DATASET_CARD.md",
                "datasheet.md",
                "dataset.schema.json",
            )
        ]
        for path in sorted(paths):
            info = zipfile.ZipInfo(
                str(path.relative_to(ROOT)).replace("\\", "/"), date_time=(2026, 10, 13, 0, 0, 0)
            )
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
    print(f"PASS: {len(results)} seeded public-log cases; results in benchmarks/results.json")
    if (
        not summary["all_order_deterministic"]
        or summary["max_absolute_expected_denominator_error"] != 0
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

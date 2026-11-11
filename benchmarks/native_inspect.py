"""Optional actual Inspect parser/accuracy baseline; never evaluates a model."""

import copy
import hashlib
import json
import math
import sys
import tempfile
from pathlib import Path

from run import SHA, build_cases, metrics


def main() -> None:
    import inspect_ai
    from inspect_ai.log import read_eval_log
    from inspect_ai.scorer import SampleScore, accuracy

    source = Path(sys.argv[1])
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("source checksum mismatch")
    original = json.loads(raw)
    originals = {s["id"]: s for s in original["samples"]}
    results = []
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "native.json"
        for name, _, narrow, gold in build_cases(original):
            document = copy.deepcopy(original)
            samples = []
            for row in narrow["samples"]:
                full = copy.deepcopy(originals[row["id"]])
                full.update(row)
                if row.get("error") is not None:
                    full["error"] = {
                        "message": row["error"]["message"],
                        "traceback": "Seeded benchmark error",
                        "type": "RuntimeError",
                    }
                samples.append(full)
            document["samples"] = samples
            document["eval"]["config"]["epochs"] = 2
            path.write_text(json.dumps(document), encoding="utf-8", newline="\n")
            try:
                log = read_eval_log(str(path))
                scores = [
                    SampleScore(score=s.scores["model_graded_fact"], sample_id=s.id)
                    for s in log.samples or []
                    if s.scores and "model_graded_fact" in s.scores
                ]
                score = accuracy()(scores)
                flagged = any(s.error is not None for s in log.samples or [])
                result = {
                    "case": name,
                    "fault": gold["fault"],
                    "actual": gold["should_flag"],
                    "flagged": flagged,
                    "parser_rejected": False,
                    "metric_input_denominator": len(scores),
                    "denominator_error": len(scores) - 6,
                    "accuracy": score if math.isfinite(score) else "nonfinite",
                }
            except (ValueError, TypeError) as exc:
                result = {
                    "case": name,
                    "fault": gold["fault"],
                    "actual": gold["should_flag"],
                    "flagged": True,
                    "parser_rejected": True,
                    "reason": type(exc).__name__,
                    "metric_input_denominator": None,
                    "denominator_error": None,
                }
            results.append(result)
    by_fault = {}
    for fault in {r["fault"] for r in results} - {"clean"}:
        subset = [r for r in results if r["fault"] in (fault, "clean")]
        by_fault[fault] = metrics([r["actual"] for r in subset], [r["flagged"] for r in subset])
    output = {
        "framework": "inspect-ai",
        "version": inspect_ai.__version__,
        "source_sha256": SHA,
        "access_date": "2026-10-13",
        "cases": len(results),
        "definition": "Actual read_eval_log parser and accuracy metric; flags parse rejection "
        "or recorded execution errors. Metric gets delivered scores only. No eval/scorer calls.",
        "limitations": [
            "Not Inspect's full aggregation pipeline or on_missing policy.",
            "Does not claim a framework defect or comparative model accuracy.",
        ],
        "metrics": by_fault,
        "results": results,
    }
    Path(__file__).with_name("native-inspect-results.json").write_text(
        json.dumps(output, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(f"PASS: actual Inspect {inspect_ai.__version__} baseline over {len(results)} fault cases")


if __name__ == "__main__":
    main()

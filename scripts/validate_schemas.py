"""Development-only validation of published schemas and example bytes."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from eval_audit.adapters import convert
from eval_audit.contract import load_inputs
from eval_audit.core import audit
from eval_audit.sensitivity import score_sensitivity


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    validators = {}
    for name in ("manifest", "result-record", "report"):
        schema = json.loads((root / "schema" / f"{name}.v1.json").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        validators[name] = Draft202012Validator(schema)
    for directory in (root / "examples", root / "examples" / "trials"):
        manifest, rows, hashes = load_inputs(
            directory / "manifest.json", directory / "results.jsonl"
        )
        validators["manifest"].validate(manifest)
        for row in rows:
            validators["result-record"].validate(row)
        validators["report"].validate(audit(manifest, rows) | {"inputs": hashes})
        validators["report"].validate(json.loads((directory / "report.json").read_text()))
    report_schema = validators["report"].schema
    counts_schema = report_schema["properties"]["counts"] | {"$defs": report_schema["$defs"]}
    expected = json.loads((root / "examples" / "expected.json").read_text())
    Draft202012Validator(counts_schema).validate(expected["counts"])
    Draft202012Validator(report_schema["properties"]["exit_code"]).validate(expected["exit_code"])
    for name, filename, identifier, score_key in (
        ("inspect", "inspect.json", "a", "metric"),
        ("lm-evaluation-harness", "lm-harness.jsonl", "0", "acc,none"),
        ("promptfoo", "promptfoo.json", "0:0", None),
        ("promptfoo", "promptfoo-v3.json", "0:0", None),
    ):
        population = {
            "schema_version": 1,
            "run_id": "synthetic-adapter",
            "expected_ids": [identifier],
        }
        validators["manifest"].validate(population)
        records = convert(name, population, root / "examples" / "adapters" / filename, score_key)
        for record in records:
            validators["result-record"].validate(record)
        validators["report"].validate(audit(population, records))
    print("PASS: Draft 2020-12 schemas; all canonical examples and four adapter fixtures")
    sensitivity = json.loads((root / "schema/score-sensitivity.v1.json").read_text())
    Draft202012Validator.check_schema(sensitivity)
    Draft202012Validator(sensitivity).validate(score_sensitivity(population, records))
    benchmark = json.loads((root / "benchmarks/dataset.schema.json").read_text())
    Draft202012Validator.check_schema(benchmark)
    for split in ("dev", "test"):
        Draft202012Validator(benchmark).validate(
            json.loads((root / f"benchmarks/dataset-v1/{split}-answers.json").read_text())
        )


if __name__ == "__main__":
    main()

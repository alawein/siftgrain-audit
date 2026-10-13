"""Opt-in descriptive score policies, separate from completeness and pass@k."""

from fractions import Fraction

from eval_audit.contract import trial_plan, validate


def score_sensitivity(manifest: dict, records: list[dict]) -> dict:
    validate(manifest, records)
    plan = trial_plan(manifest)
    present = [
        row for row in records if row["id"] in plan and row.get("trial", 1) <= plan[row["id"]]
    ]
    available = [row for row in present if row["score"] is not None]
    scored = [row for row in present if row["status"] == "scored"]

    def policy(rows: list[dict], denominator: int) -> dict:
        total = sum((Fraction(str(row["score"])) for row in rows), Fraction())
        return {
            "denominator": denominator,
            "sum": str(total),
            "mean": str(total / denominator) if denominator else None,
        }

    return {
        "schema_version": 1,
        "run_id": manifest["run_id"],
        "unit": "expected trial",
        "meaning": "Descriptive arithmetic only; no success threshold or pass@k/pass^k rate.",
        "number_format": "Exact rational strings from the supplied decimal scores.",
        "policies": {
            "expected_zero_fill": policy(available, sum(plan.values())),
            "score_available": policy(available, len(available)),
            "scored_only": policy(scored, len(scored)),
        },
        "errored_score_rule": "Included in zero-fill and availability; excluded from scored-only.",
    }

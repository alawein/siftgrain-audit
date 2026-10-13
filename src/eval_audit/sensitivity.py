"""Opt-in descriptive score policies, separate from completeness and pass@k."""

from decimal import Decimal
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
        total = sum(
            (
                Fraction(row["score"]) if type(row["score"]) is int else Fraction(str(row["score"]))
                for row in rows
            ),
            Fraction(),
        )

        def rational(value: Fraction) -> str:
            # Arithmetic may add a digit beyond the JSON parser's per-number bound.
            # Decimal(int) is exact and avoids changing the process-wide int limit.
            numerator = format(Decimal(value.numerator), "f")
            if value.denominator == 1:
                return numerator
            return numerator + "/" + format(Decimal(value.denominator), "f")

        return {
            "denominator": denominator,
            "sum": rational(total),
            "mean": rational(total / denominator) if denominator else None,
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

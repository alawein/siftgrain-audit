from siftgrain_audit.contract import trial_mode, trial_plan, validate


def audit(manifest: dict, records: list[dict]) -> dict:
    validate(manifest, records)
    if trial_mode(manifest):
        return audit_trials(manifest, records)
    expected = set(manifest["expected_ids"])
    indexed = {row["id"]: row for row in records}
    present = [indexed[key] for key in sorted(expected & indexed.keys())]
    missing = sorted(expected - indexed.keys())
    unexpected = sorted(indexed.keys() - expected)
    counts = {"expected": len(expected)}
    counts.update(
        {
            status: sum(row["status"] == status for row in present)
            for status in ("scored", "errored", "unscored")
        }
    )
    counts["missing"] = len(missing)
    counts["score_present"] = sum(row["score"] is not None for row in present)
    return {
        "schema_version": 1,
        "run_id": manifest["run_id"],
        "counts": counts,
        "score_present_coverage": counts["score_present"] / len(expected),
        "missing_ids": missing,
        "unexpected_ids": unexpected,
        "errored_with_score_ids": sorted(
            row["id"] for row in present if row["status"] == "errored" and row["score"] is not None
        ),
        "exit_code": int(bool(missing or unexpected or counts["errored"] or counts["unscored"])),
    }


def audit_trials(manifest: dict, records: list[dict]) -> dict:
    plan = trial_plan(manifest)
    expected = {(key, trial) for key, count in plan.items() for trial in range(1, count + 1)}
    indexed = {(row["id"], row.get("trial", 1)): row for row in records}
    present = {key: indexed[key] for key in sorted(expected & indexed.keys())}
    missing = sorted(expected - indexed.keys())
    unexpected = sorted(indexed.keys() - expected)
    trial_counts = {"expected": len(expected), "delivered": len(present)}
    trial_counts.update(
        {
            status: sum(row["status"] == status for row in present.values())
            for status in ("scored", "errored", "unscored")
        }
    )
    trial_counts.update(
        missing=len(missing),
        unexpected=len(unexpected),
        duplicate=0,
        score_present=sum(row["score"] is not None for row in present.values()),
    )
    counts = dict(expected=len(plan), scored=0, errored=0, unscored=0, missing=0, score_present=0)
    complete = []
    for key, total in sorted(plan.items()):
        rows = [present.get((key, trial)) for trial in range(1, total + 1)]
        if any(row is None for row in rows):
            status = "missing"
        else:
            complete.append(key)
            statuses = {row["status"] for row in rows if row is not None}
            status = (
                "errored"
                if "errored" in statuses
                else ("unscored" if "unscored" in statuses else "scored")
            )
        counts[status] += 1
        counts["score_present"] += int(
            all(row is not None and row["score"] is not None for row in rows)
        )
    denominators = {}
    scored_prefix = {}
    for key, total in plan.items():
        prefix = 0
        for trial in range(1, total + 1):
            if present.get((key, trial), {}).get("status") != "scored":
                break
            prefix += 1
        scored_prefix[key] = prefix
    for k in range(1, max(plan.values()) + 1):
        eligible = [key for key, total in plan.items() if total >= k]
        denominators[str(k)] = {
            "expected_ids": len(eligible),
            "all_k_trials_scored": sum(scored_prefix[key] >= k for key in eligible),
        }

    def pairs(keys):
        return [{"id": key, "trial": trial} for key, trial in keys]

    return {
        "schema_version": 2,
        "run_id": manifest["run_id"],
        "counts": counts,
        "score_present_coverage": counts["score_present"] / len(plan),
        "trial_counts": trial_counts,
        "trial_score_present_coverage": trial_counts["score_present"] / len(expected),
        "missing_ids": sorted({key for key, trial in missing}),
        "unexpected_ids": sorted({key for key, trial in unexpected}),
        "missing_trials": pairs(missing),
        "unexpected_trials": pairs(unexpected),
        "complete_ids": complete,
        "errored_with_score_ids": sorted(
            {
                row["id"]
                for row in present.values()
                if row["status"] == "errored" and row["score"] is not None
            }
        ),
        "errored_with_score_trials": pairs(
            [
                key
                for key, row in present.items()
                if row["status"] == "errored" and row["score"] is not None
            ]
        ),
        "pass_k_denominators": denominators,
        "exit_code": int(
            bool(missing or unexpected or trial_counts["errored"] or trial_counts["unscored"])
        ),
    }

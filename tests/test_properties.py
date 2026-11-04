from hypothesis import given, settings
from hypothesis import strategies as st

from siftgrain_audit.core import audit


@st.composite
def packets(draw):
    size = draw(st.integers(1, 12))
    plan = {str(index): draw(st.integers(1, 6)) for index in range(size)}
    manifest = {
        "schema_version": 2,
        "run_id": "property",
        "expected_ids": list(plan),
        "trials_per_id": plan,
    }
    rows = []
    for key, total in plan.items():
        for trial in range(1, total + 1):
            status = draw(st.sampled_from(["missing", "scored", "errored", "unscored"]))
            if status != "missing":
                score = (
                    draw(st.one_of(st.none(), st.integers(-100, 100)))
                    if status == "errored"
                    else (None if status == "unscored" else draw(st.integers(-100, 100)))
                )
                rows.append(
                    {"id": key, "trial": trial, "status": status, "score": score, "reason": ""}
                )
    return manifest, rows


@given(packets())
@settings(max_examples=100, derandomize=True)
def test_partition_and_determinism(packet):
    manifest, rows = packet
    report = audit(manifest, rows)
    for counts in (report["counts"], report["trial_counts"]):
        assert (
            sum(counts[s] for s in ("scored", "errored", "unscored", "missing"))
            == counts["expected"]
        )
        assert counts["scored"] <= counts["score_present"] <= counts["expected"]
    assert report == audit(
        manifest | {"expected_ids": list(reversed(manifest["expected_ids"]))}, list(reversed(rows))
    )
    for k, denominator in report["pass_k_denominators"].items():
        indexed = {(r["id"], r["trial"]): r for r in rows}
        eligible = [key for key, total in manifest["trials_per_id"].items() if total >= int(k)]
        assert denominator["all_k_trials_scored"] == sum(
            all(
                indexed.get((key, trial), {}).get("status") == "scored"
                for trial in range(1, int(k) + 1)
            )
            for key in eligible
        )


@given(
    st.lists(st.sampled_from(["missing", "scored", "errored", "unscored"]), min_size=1, max_size=30)
)
@settings(max_examples=100, derandomize=True)
def test_legacy_partition(statuses):
    manifest = {
        "schema_version": 1,
        "run_id": "legacy-property",
        "expected_ids": [str(i) for i in range(len(statuses))],
    }
    rows = [
        {"id": str(i), "status": status, "score": 0 if status == "scored" else None, "reason": ""}
        for i, status in enumerate(statuses)
        if status != "missing"
    ]
    counts = audit(manifest, rows)["counts"]
    assert (
        sum(counts[s] for s in ("scored", "errored", "unscored", "missing")) == counts["expected"]
    )

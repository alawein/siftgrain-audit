# Public-log completeness benchmark v1

Task: flag incomplete or invalid logs against an independently declared selected
population and preserve trial denominators under reordering. The source is the
MIT-licensed Inspect security-guide log at commit
`4acfd207ecca8e1c3b754a147c191f2f0f21ba71`, run May 12, 2025. Its header selects
IDs 1, 2, 3 from 16 entries; the other 13 are outside this run, never missing.
Source URL and SHA-256 are in results.json and run.py. Access: October 13, 2026.
Log publication/revision date beyond the recorded run date: unknown.

`make bench` fetches exact pinned bytes if absent, verifies SHA-256, then runs
offline fault injection. Without make: `uv run python benchmarks/run.py --fetch`.
After initial fetch, omit --fetch for strictly offline reproduction.

The benchmark keeps the three actual scored samples. A second epoch is a
synthetic clone, not another model trial. Seeded transformations inject drop,
duplicate, errored-with-score, lexical NaN, shuffled epochs and partial retries.
Forty seeds are split into dev (1000-1019) and test (2000-2019). Each contributes
seven cases: clean plus six transformations. Shuffling is a negative control,
not a defect. Each case includes a manifest and mapped Inspect log, with
answer keys stored separately by split. Invalid NaN files deliberately fail JSON
syntax; they must never be silently sanitized. No human labels are claimed.

Metrics are binary **run-level** confusion counts, precision/recall per injected
fault compared with clean controls, expected-denominator error on valid runs,
and exact report/rejection-category equality under reversal. Rejection leaves
denominator error undefined, rather than claiming a successful audit. The naive
baseline accepts a log if any numeric/categorical score arrived and uses the
delivered score count as its denominator. It is deliberately simple and does
not represent Inspect or lm-eval. Native baseline execution is recorded separately.
No LLM baseline or model/scorer execution is performed.

`dataset-v1.zip` is a deterministic downloadable archive, with dev/test inputs,
separate answer keys and SHA-256 checksums. Derived mapped log fields retain
upstream MIT attribution; original messages/responses are unnecessary and omitted.
`DATASET_CARD.md`, `datasheet.md`, `croissant.json` and `dataset.schema.json`
describe provenance and fields. No Hugging Face upload has been performed.

Timing uses perf_counter; tracemalloc records Python allocations for a synthetic
10,000-missing-trial stress case. These measurements are host-specific, not an
independent hardware benchmark. No population confidence interval is appropriate
for this fixed deterministic suite. Three source samples cannot estimate real
harness defect prevalence or comparative framework performance.

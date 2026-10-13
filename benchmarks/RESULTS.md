# Benchmark results, October 13, 2026

Executed 280 seeded transformations on three actual pinned Inspect samples.
Cloned epoch 2 and all corruptions are synthetic. Dev/test split fault seeds,
not source instances; this is regression coverage, not a representative study.

| Fault | Census TP/FP/FN/TN | Precision | Recall | Native parser/metric TP/FP/FN/TN |
| --- | --- | --- | --- | --- |
| drop | 40/0/0/40 | 1.0 | 1.0 | 0/0/40/40 |
| duplicate | 40/0/0/40 | 1.0 | 1.0 | 0/0/40/40 |
| error | 40/0/0/40 | 1.0 | 1.0 | 40/0/0/40 |
| nan | 40/0/0/40 | 1.0 | 1.0 | 0/0/40/40 |
| partial_retries | 40/0/0/40 | 1.0 | 1.0 | 0/0/40/40 |
| shuffled_epochs | 0/0/0/80 | None | None | 0/0/0/80 |

Null precision/recall means no positive predictions/labels, not a perfect score.
The shuffled-epochs cases are negative controls. Zero false flags occurred on
clean controls. Eighty invalid duplicate/NaN cases were rejected; denominator
error is undefined for rejected input. Among valid reports the maximum absolute
expected-denominator error was 0.
All 280 reports/rejection categories were invariant under reversal.
The naive delivered-score baseline missed every injected fault; its definition
and signed denominator errors are in case-results.json. It is not a harness.

Actual Inspect 0.3.279 read_eval_log and accuracy were run in an isolated
Python 3.11 environment. That baseline flags parse rejection/recorded errors and
passes only delivered scores to accuracy. It is not native full aggregation or
on_missing handling, so these results do not establish a framework defect.
No model/scorer/network calls occur during baseline execution. No native lm-eval
baseline was run because this source is Inspect, not lm-eval. No LLM baseline
or human experiment was performed.

Observed host timing: median conversion+audit 7.353 ms;
synthetic 10,000-missing-trial audit 1.1706 s;
tracemalloc peak 3769834 bytes. Platform and Python
are recorded in results.json. These host-specific timings are descriptive.
No CI for a fixed exhaustively run seeded suite; three original IDs do not
support independent population inference.

Reproduction: `make bench` (or `uv run python benchmarks/run.py --fetch`).
Native reproduction after optional installation: `python benchmarks/native_inspect.py studies/data/security-guide.json`
using an environment with this repo and inspect-ai==0.3.279 installed.

[Download versioned inputs and separate keys](dataset-v1.zip). Two successive
runs produced identical ZIP SHA-256 `f2b86970a3a3c7bf1349a300239379816c510e42c4c45213f587d23741650a66`.
The raw third-party log remains ignored; the downloadable suite keeps mapped
score values and retains upstream MIT attribution in UPSTREAM-LICENSE.txt.

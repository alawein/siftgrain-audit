# Evaluation completeness research

Access date for this scan: October 13, 2026, America/Los_Angeles. Cutoff is the
same date. Undated living documentation has unknown publication/revision dates;
no future release is used. These sources support format and positioning choices,
not evidence of product adoption or novel research.

| Primary source | Publication / revision / release date | What was verified |
| --- | --- | --- |
| [Inspect error handling](https://inspect.aisi.org.uk/handling-errors.html) | unknown / unknown / not applicable | Error recording and score-on-error are explicit harness policies; an error retaining a score must remain an error. |
| [Inspect metrics](https://inspect.aisi.org.uk/metrics.html) | unknown / unknown / not applicable | Native missing-score handling matters; availability is separate from score aggregation. |
| [Inspect log documentation](https://inspect.aisi.org.uk/eval-logs.html) | unknown / unknown / not applicable | Per-sample scores and epochs are useful offline adapter inputs. |
| [Inspect issue 5659](https://github.com/UKGovernmentBEIS/inspect_ai/issues/5659) | October 2, 2026 / unknown / not applicable | Reported retry sample-selection changes under sample_shuffle=False; a report, not a reproduced general defect here. |
| [Kirgis, Kapoor, Rabanser et al.](https://arxiv.org/abs/2605.08545) | May 8, 2026 / v1 May 8, 2026 / not applicable | Log analysis complements final outcomes. Coverage is one mechanical check, not a substitute for trace analysis. |
| [lm-evaluation-harness evaluator](https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/evaluator.py) | unknown / unknown / not applicable | Per-sample outputs retain document IDs and literal metric keys; aggregate-only metrics do not supply an expected population. |
| [HELM PerInstanceStats](https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/metrics/metric.py) and [Stat](https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/metrics/statistic.py) | unknown / unknown / not applicable | Instance ID, zero-based training trial index, named statistic and mean; scenario context and perturbations need explicit boundaries. |
| [promptfoo output formats](https://www.promptfoo.dev/docs/configuration/outputs/) | unknown / unknown / not applicable | Exported per-test/provider rows are distinct from aggregate assertion tables. |
| [Open LLM details collection](https://huggingface.co/collections/open-llm-leaderboard/details) | unknown / varied dataset revisions / not applicable | Details repositories exist; some are gated. Exported local JSON is supported without claiming unrestricted dataset download access. |
| [OpenAI Evals](https://github.com/openai/evals) | unknown / unknown / not applicable | An evaluation framework and registry rather than independent completeness gold. Not executed as a benchmark baseline. |
| [tau-bench](https://arxiv.org/abs/2406.12045) | June 2024 / see version history / not applicable | Repeated trials motivate pass^k eligibility counts, without inferring task success from a numeric score. |
| [Pinned real Inspect log](https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_ai/4acfd207ecca8e1c3b754a147c191f2f0f21ba71/tests/analysis/test_logs/2025-05-12T20-28-26-04-00_security-guide.json) | recorded run May 12, 2025 / commit 4acfd207ecca8e1c3b754a147c191f2f0f21ba71 / unknown | Three selected scored samples, selected IDs declared in the header, actual SHA-256 verified. |
| [inspect-ai 0.3.279 metadata](https://pypi.org/pypi/inspect-ai/0.3.279/json) | October 13, 2026 at 00:07:35 UTC upload / same / 0.3.279 | Actual optional native parser/accuracy baseline installed and executed; no model or scorer calls. |

## How similar tools are evaluated

Harnesses score benchmark tasks and aggregate per-sample metrics under their
own missing/error policies. Inspect exposes native log structures and metric
controls; lm-eval emits task-specific per-sample details; HELM retains named
statistics tied to instances and training trials; promptfoo evaluates assertions
against test/provider combinations. Open LLM details reuse harness outputs and
dataset-specific metrics. A generic independent denominator cannot be inferred
from whichever rows happened to survive.

Census therefore evaluates a narrower task: reconcile supplied planned IDs and
trial counts with delivered records. Ground truth is an explicit plan plus
seeded corruption, not an LLM judgment. The benchmark uses actual archived
Inspect scores, controlled faults, an executed naive baseline and an executed
native Inspect parser/metric baseline with its own limits. It reports confusion
counts, denominator error and deterministic ordering, not model accuracy.
No native lm-eval model run, OpenAI Evals run or human study was performed.

The September 1 to October 13 scan found the concrete October 2 retry report
and the October 13 native package release; other living docs have unknown dates.
This is a bounded primary-source scan, not a complete census of 2026 tools.
Hugging Face details access is dataset-dependent. No papers, date ranges, user
counts, benchmark outcomes or licensing permissions are inferred from a search hit.

## Product choices

Primary user: an evaluation engineer inspecting partial batches or retry exports.
Job: see whether every expected trial has usable recorded evidence before
interpreting aggregate scores. Integrations: strict CLI, five local adapters,
composite GitHub Action, pre-commit hook and self-contained HTML report.
Scope: counts and supplied-score policy arithmetic, no pass@k/pass^k rates,
model calls, remote fetches or correctness inference in the core.

Naming search evidence is in docs/name-checks.json. Siftgrain was selected after
Spanward software collisions; Census is a descriptive product suffix. Limited
registry and trademark-style web search is not legal clearance. Historical
changes affecting style, naming, CI and security are in docs/recent-history.json
and docs/shared-history.md with their observed coverage limits.

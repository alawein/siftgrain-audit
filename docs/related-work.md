# Scope and related work

This tool checks availability against an explicit expected population. It does
not replace evaluation harnesses, compute model performance or validate the
population's provenance. It is independent of similarly named tools.

[tau-bench, original June 17, 2024 submission](https://arxiv.org/abs/2406.12045v1)
motivates repeated trials and pass^k reliability. Siftgrain Audit can expose absent
trials and eligibility counts; it does not implement tau-bench state checking
or compute pass^k. [Kirgis et al., May 8, 2026](https://arxiv.org/abs/2605.08545v1)
argue that evaluation credibility needs analysis of logs beyond final outcomes.
Coverage is one mechanical part of such analysis, not a substitute for it.

Inspect already supplies [error controls](https://inspect.aisi.org.uk/handling-errors.html),
[evaluation-set management](https://inspect.aisi.org.uk/eval-sets.html), and
[missing-score metric policies](https://inspect.aisi.org.uk/metrics.html).
Its native diagnostics remain useful; a supplied manifest is the external
population contract here. [Inspect issue 5659](https://github.com/UKGovernmentBEIS/inspect_ai/issues/5659)
reports retry sample-selection changes. It is a reported issue, not proof that
every retry changes the population or a confirmed defect in this tool.

The first implementation [PR #1 checks](https://github.com/alawein/siftgrain-audit/pull/1/checks)
show 30 successful Actions results and a pending CodeRabbit status in root's
October 8 readback. Pending automated review is distinct from a failing product
test. Historical checks do not establish current branch correctness.

Synthetic exercises demonstrate contracts and workflows only. Any public-log
pilot is a separately scoped observational study, not adoption, benchmark
superiority or a general estimate of denominator errors.

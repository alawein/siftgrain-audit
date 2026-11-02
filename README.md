# Eval Audit

Eval Audit is an offline Python command line tool for people who run
evaluations and need to know which expected results are missing before they
read the scores.

The package is `alawein-eval-audit`; the command is `eval-audit`.

![Evaluation coverage](assets/label-purpose.svg)
![Python](assets/label-stack.svg)
![Offline CLI](assets/label-runtime.svg)

Declare the expected IDs and supply JSONL results. Eval Audit separates scored,
errored, unscored, missing, and unexpected records, including errored records
that retain a score.

## Install and run

Python 3.11+. No runtime dependencies. Clone the repository, then:

```sh
uv sync --frozen
uv run eval-audit examples/manifest.json examples/results.jsonl
```

JSON prints to stdout by default, so a first run writes nothing to the repo. Add
`--html report.html` or `--json report.json` for files; reruns over an existing
path need `--force`. `eval-audit --help` shows the manifest and JSONL shapes, the
standard invocations, and exit-code meanings.

The synthetic example exits **1**: four expected IDs, one scored, one errored,
one unscored and one missing. Score-present coverage is 0.25. Exit 0 means a
complete scored population; exit 2 means invalid input or an I/O failure.

## Agent Acceptance demo

Agent Acceptance is a working demo title for synthetic refund case 1042. Audit
the supplied evaluation rows with the same offline engine:

```sh
uv run eval-audit examples/acceptance-manifest.json examples/acceptance-results.jsonl
uv run python scripts/build_demo.py
```

Open `site/acceptance.html` locally. The original example remains at
`site/index.html`, with links between both pages. The refund example declares four
expected IDs: one scored with **0**, one errored retaining **0.9**, one unscored,
and one missing. Two of four IDs have a numeric score, so score-present coverage
is **0.5 (50%)** and the exit code is **1**. Zero is present; an errored record
retaining a number stays errored.

This is score availability, not refund correctness or task quality. The auditor
does not decide whether the supplied refund claim is correct, the completion
observation is fresh, or the agent caused a change. The source text provides
context for the synthetic fixtures.

The page shows expected-record cards, reasons, provenance, and input hashes. It
links to `acceptance-report.json` and byte-for-byte copies of the manifest,
results, and source text. Report hashes cover the manifest and results; a separate
displayed source SHA-256 covers the source bytes. Hashes show consistency, not
authenticity. The report JSON contract remains unchanged.

## Capabilities and limits

Deterministic JSON, readable HTML, input SHA-256 hashes, sorted missing/unexpected
IDs, and errored records retaining a score. The population is supplied, never
guessed. Zero is a present score. Unexpected records do not inflate counts.

No accuracy, quality, means or rankings. It cannot verify the supplied population
or whether a partial score is usable. Native framework diagnostics remain useful.

For repeated trials, add `"trials_per_id": 5` to the manifest, or an exact ID-to-count
mapping, and `"trial": 1` to each record. Trial numbers start at 1. Counts include
both ID and trial partitions; IDs are complete only when every planned trial is
delivered. Readiness denominators for pass@k and pass^k require all first k trials
to have `status: scored`. They are counts, never success rates. An errored record
with a numeric score contributes to score availability, but remains errored and
does not qualify for these readiness counts.

Convert local Inspect `.eval`/`.json`, lm-evaluation-harness per-sample JSONL or
promptfoo JSON with an explicit population:

```sh
uv run eval-audit convert inspect log.json --manifest manifest.json --score-key metric --output results.jsonl
uv run eval-audit manifest.json results.jsonl
```

For a report in one command, add `--html report.html` to conversion:

```sh
uv run eval-audit convert inspect log.json --manifest manifest.json --score-key metric --output results.jsonl --html report.html
```

Open `report.html` locally. The converted rows remain in `results.jsonl` for
inspection or reuse. Use `--json report.json` instead of, or alongside, `--html`
to save the audit's machine-readable report in the same command.
With either report option, exit 0 means complete scored coverage,
1 means missing, unexpected, errored or unscored records need attention, and
2 means invalid input or an I/O failure. Without either report option, conversion still exits 0 on successful
conversion, which does not establish coverage. Expected IDs always come from
your manifest, never from the results being checked.

[Adapter mappings and discarded fields](docs/adapters.md) explain supported shapes,
categorical score maps and limitations. [Versioned JSON Schemas](schema/manifest.v1.json)
describe the portable formats. Schema-1 inputs without trials keep their v0.2.0
output shape exactly; schema 2 enables trials and defaults to one trial per ID.

Troubleshooting: status, score, and reason errors name the JSONL row (for example
`invalid status at record 2`); open that line before editing the file. The HTML
report's how-to-read section explains missing, unexpected, errored with score,
unscored, score-present coverage, and exit codes. [Input contract](docs/contract.md),
[test evidence](docs/evaluation.md), [usefulness exercise](docs/usefulness.md),
[provenance](docs/provenance.md).
[Related work](docs/related-work.md) puts these checks in context; [the public-log pilot](studies/inspect-security-guide/README.md) is a
small recorded-run exercise with its stated limits. The [ten-sample archive study](studies/harness-coverage/README.md) checks its selected population and unscored records.

## Related work and how this differs

[Inspect error handling](https://inspect.aisi.org.uk/handling-errors.html) and
[missing-score metric policies](https://inspect.aisi.org.uk/metrics.html) already
provide native controls. Eval Audit independently compares delivered rows with
a caller-supplied expected population. [Retry issue 5659](https://github.com/UKGovernmentBEIS/inspect_ai/issues/5659)
is a report about sample selection, not proof of a general harness defect.

[tau-bench](https://arxiv.org/abs/2406.12045v1) motivates repeated trials and
pass^k reliability; this tool reports readiness counts without computing success
rates or task-state correctness. [Kirgis et al.](https://arxiv.org/abs/2605.08545v1)
argue for analysis beyond final outcomes. Coverage checks are one mechanical
part of that work, with no claim of research novelty or comparative superiority.

## Develop

`just check` runs Ruff, pytest, type checks, schemas and wheel/sdist builds.
`uv run python scripts/build_demo.py` creates both static executed examples locally.
CLI does not fetch data or call a model. HTML escapes imported text. Existing
outputs require `--force`; outputs cannot alias inputs. Each output is staged in
its destination directory and installed atomically. Writes are not a multi-file
transaction: one complete file can be installed before another fails. A staging
or installation failure preserves that file's previous bytes. This does not
provide race-proof input identity checks or a power-loss durability guarantee.

This is [alawein/siftgrain-audit](https://github.com/alawein/siftgrain-audit), an
offline coverage auditor. It is unrelated to similarly named statistical or
human-grading tools. Releases are tagged v0.1.0 through v0.3.1.

Code is MIT ([LICENSE](LICENSE)). The synthetic example fixtures are CC0
([examples/LICENSE](examples/LICENSE)).

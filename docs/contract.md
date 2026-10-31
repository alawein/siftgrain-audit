# Input contract, schema 1 and 2

Manifest required fields: schema_version (integer 1 or 2), run_id (nonblank string <= 200),
expected_ids (1..10,000 unique nonblank strings <= 200 each). JSONL record fields
exactly: id (unique nonblank string <= 200), status (scored|errored|unscored), score
(finite number or null), reason (string <= 4,000, possibly empty). Booleans are not
numbers. Scored requires a number; unscored requires null; errored permits either.

Each file: UTF-8 without BOM, <= 5 MiB. Records <= 10,000. Empty results are valid,
blank rows invalid. LF separates rows; final LF optional. CRLF works as JSON
whitespace. U+2028 is content. Duplicate JSON keys and unknown fields fail.

`eval-audit MANIFEST RECORDS [--json PATH] [--html PATH] [--force]` prints JSON
unless --json is supplied. Hashes cover exact input bytes. Expected IDs define
counts. Score coverage includes scored and errored records with a number. Missing
and unscored records stay separate. Output parents must exist; resolved aliases
and existing hard links are rejected. No race-proof filesystem transaction.

Optional `trials_per_id` enables trial mode on schema 1; schema 2 enables trial
mode even when that field is absent (default 1). This field is either a positive
integer or an exact expected-ID mapping of positive integers. Trial numbers and
counts are <=10,000; sum of expected trials <=10,000. A trial record can include
`trial`, default 1. Its identity is `(id, trial)`, and both must be unique together.
An out-of-plan positive trial is unexpected, including for an expected ID.
Legacy schema-1 input without this field forbids `trial` and duplicate IDs as
before. Unknown manifest/row fields still fail. Schema-1 reports are unchanged;
trial reports use schema_version 2. v0.2.0 inputs and report exports still load.

Both count partitions satisfy scored + errored + unscored + missing = expected.
Trial counts categorize each expected trial. ID counts classify an ID as missing
if any trial is missing, otherwise errored if any is errored, otherwise unscored
if any is unscored, otherwise scored. `complete_ids` requires all trials present,
regardless of score/status. `trial_counts.delivered` excludes unexpected trials.
Duplicate identities are invalid input (exit 2), never silently retained/dropped.
Valid trial reports carry `trial_counts.duplicate: 0`; a duplicate prevents report
generation and its diagnostic names the repeated pair and source record number.

Trial `score_present` counts every expected non-null finite score, including zero
and errored-with-score. ID `score_present` requires all its planned trials to
have numbers. Each coverage divides the corresponding availability count by
its supplied expected count. An errored-with-score trial is still an error,
even when its score contributes to availability; it never becomes scored.

`pass_k_denominators[k]` describes both pass@k and pass^k readiness. `expected_ids`
counts IDs planning at least k trials; `all_k_trials_scored` counts those IDs whose
trials 1 through k all explicitly have scored status. Errors retaining scores
are excluded. These are eligibility counts only. There are no pass rates,
success judgments, combinatorial estimates or row-order selection. The caller
must define a scoring success rule and decide whether its supplied trial plan
is appropriate before interpreting any performance metric elsewhere.

All numeric input scores reject NaN, positive/negative infinity, overflow such
as `1e999`, and booleans with row-numbered errors. Arbitrarily large JSON integers
within Python's JSON digit bound remain valid. `NaN`/`Infinity` lexical constants
are invalid JSON and are rejected by the parser, also labeled by JSONL row.

Outputs stage bytes in a same-directory temporary file and atomically install
each file with `os.replace` under --force or exclusive hard-link creation
otherwise. Failed staging/installation leaves that output's previous bytes
untouched. Several outputs are not one transaction. Existing alias protections
remain, but no race-proof identity or crash durability is promised.

[JSON Schemas](../schema/manifest.v1.json) use Draft 2020-12; the filename's v1 is
the published schema-document revision, and schema_version is the packet shape.
Versioned schemas accept legacy and extended records. Manifest/record relationship
constraints (exact trial-map keys, total trial limits, legacy trial prohibition,
duplicate trial identity and numeric finiteness) are enforced by runtime validation
in addition to JSON Schema. No schema is fetched by runtime.

## Current release state, October 8, 2026

The v0.3.0 [merged PR](https://github.com/alawein/eval-audit/pull/15), immutable
`v0.3.0` tag, and [GitHub Release](https://github.com/alawein/eval-audit/releases/tag/v0.3.0)
are published. The historical PyPI run link now returns 404, so the recorded
invalid-publisher result cannot be independently verified here. The authenticated
form separately rejected the
original name. Maintenance alawein-eval-audit 0.3.1 is not yet published and its
pending-publisher acceptance remains blocked on owner-entered password confirmation.
See [release readiness](../RELEASE_READY.md) for the actual states and retry rules.
Historical preparation and checks below retain their original dates and scope.

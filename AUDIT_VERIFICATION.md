# Audit verification

## Current baseline verification, October 13, 2026

Prechange baseline: clean main `7fe0b7b05369ed3778d72775c3f2f913604ef96f`.
Fresh baseline pytest: **170 passed in 8.49 seconds**, no skips. All file:line
references in this table bind that baseline, before this redesign's edits.

| Prior hypothesis | Finding now | Baseline evidence |
| --- | --- | --- |
| Repeated trials absent | Refuted; superseded by v0.3.0 | src/eval_audit/core.py:35 and contract.py:56, trial plans and pair identity |
| No adapter support | Partially confirmed | adapters.py:82 supports Inspect, lm-eval and promptfoo; HELM/Open LLM missing |
| NaN/infinity/bool silently accepted | Refuted | contract.py:114-126 exact numeric types, finite floats and row-number diagnostics; parse rejects lexical constants |
| Errored-score numerator undefined | Refuted | core.py:21,54,71 availability includes numeric error scores; core.py:74 excludes errors from all-k-scored readiness; docs/contract.md explicit |
| Nonatomic writes | Refuted | output.py:26 stages same-directory bytes and atomically installs per file; multiple outputs are not a transaction |
| Python floor too high | Refuted | pyproject.toml:10 requires Python >=3.11; CI matrix covers 3.11-3.13 |
| Schemas absent | Refuted | schema/manifest.v1.json, result-record.v1.json, report.v1.json are Draft 2020-12; tests/test_schemas.py |
| Only synthetic empirical evidence | Partially confirmed | studies/inspect-security-guide and harness-coverage contain actual tiny pinned public-log studies; no seeded fault benchmark existed |
| Animated trial viewer and sensitivity absent | Confirmed | report.py:75 renders static counts/cards; cli.py:90 has no separate score-policy output |
| Generic name collision | Confirmed as positioning risk | Existing README disambiguates eval-audit; dated docs/name-checks.json records proposed-family searches |
| First PR has one check not passing | Partially confirmed, pending status | Fresh API for PR1 head e4f955490ba2508135b14851e0a1b918238d2ea1 returned 30 success check-runs, zero nonpassing; legacy CodeRabbit commit status remains pending since October 4. This is not a failed required build. |

Current remote history and settings observations: docs/recent-history.json.
Main uses an active ruleset, not legacy branch-protection API; a 404 on the latter
is not proof of unprotected main. No settings or Dependabot controls changed.
Current changes add regression tests for strict adapters, policy separation,
viewer states, consumer exit failure and benchmark gold failure. Historical
verification below remains bound to its own explicitly named revisions.

## Phase 0, October 8, 2026

Source: `compass_artifact_wf-8f32e147-9bf3-5208-ba05-acfbbd390eae_text_markdown.md`,
full supplied audit read locally. Baseline HEAD: `06b6d1eebe01455b08277a2caace54aa2417af28`.
Branch: `feat/v0.3.0-hardening`; clean before work.

`uv sync --frozen` succeeded. Python used by baseline: 3.13.9; system Python:
3.14.7; Node: 22.23.2. pytest: **46 passed**, no skips, failures or deselections.
Ruff check passed; Ruff format: 21 files already formatted. Wheel and sdist built.
Lock SHA-256: `c2a1c04338dfb918b3562e2a82ac6d60d047cdfa4d9a025c30b8c85298117117`.
Runtime dependency list is empty; development lock contains pytest and Ruff.

| Audit assertion | Finding at baseline | Evidence |
| --- | --- | --- |
| Offline runtime not verifiable | Confirmed offline statically | `core.py:1`, `contract.py:1-4`, `cli.py:1-7`: only stdlib/local imports; no network, model, subprocess or executor calls anywhere in runtime |
| Explicit denominator unclear | Confirmed correct | `core.py:11,24`: supplied expected-ID count is denominator; unexpected IDs excluded by expected intersection at line 8 |
| Error scores' numerator unclear | Refuted as code defect; documentation partially clear | `core.py:19,27-28`: every expected non-null score counts, including errored records; separate list preserved; contract states this explicitly |
| NaN/infinity/booleans unknown | Refuted as code defect | `contract.py:78-81`: bool rejected by exact type checks; nonfinite float rejected; JSON constants rejected at lines 37-38; numeric overflow `1e999` rejected after parsing; errors include row |
| Repeated trials unsupported | Confirmed | `contract.py:70-73` requires exact legacy fields and unique ID |
| No native adapters | Confirmed | Only canonical JSON/JSONL reader in `contract.py:91`; CLI exposes no conversion |
| Python floor 3.13 unnecessarily restrictive | Confirmed floor; no inspected runtime syntax needs 3.13 | `pyproject.toml` requires >=3.13; lowering and actual matrix tests planned |
| Writes may truncate existing output | Confirmed | `cli.py:64-68` writes target directly |
| No schemas/property tests | Confirmed | No schema directory or Hypothesis dev dependency/tests |
| Historical counts disagree | Confirmed baseline count; history treated separately | 46 collected and passed at specified baseline; historical PR/check evidence owned by root |
| Synthetic-only empirical evidence | Confirmed baseline | examples and usefulness docs synthetic; public study owned by root |
| Name collisions | Partially confirmed | README lacks disambiguation; externally verified registry/name evidence owned by root |
| Registry/security/first-PR checks | Partially confirmed; remote facts checked below | Root owns checks, settings and release-readiness documentation |

No source changes were made before these checks. Review claims about other two
repositories are outside this checkout; their assigned agents own verification.

## v0.3.0 local verification

The final suite collects **109 tests** (baseline 46), all passing on Python
**3.11.13, 3.12.10 and 3.13.9**. Two Hypothesis properties each exercise 100
deterministic generated cases. Ruff check/format, mypy and Pyright pass. Draft
2020-12 schema definitions, all canonical examples, expected count/exit fixture
and four converted native adapter fixtures validate. Both wheel and
sdist build through `uv build` and `python -m build`; Twine metadata checks pass.
Both artifacts install in isolated environments and pass the synthetic CLI smoke.
`uv sync --frozen` succeeds after lowering the floor. Runtime dependencies remain
empty. Final lock SHA-256:
`752b4947bd88982d98b56a7a837186aa013d1537439646d58cb259f4808f1de8`.

| Addressed finding | Current code evidence |
| --- | --- |
| Offline core and adapters | `core.py:1`, `contract.py:1-5`, `cli.py:1-16`, `adapters.py:3-6`, `output.py:3-5`: stdlib/local imports; inspected runtime has no network/model/subprocess/executor calls |
| Explicit denominators and legacy compatibility | `core.py:26,97,99`: supplied ID/trial populations; committed legacy JSON unchanged and full snapshot test passes |
| Errored numeric availability | `core.py:21,54,71`: availability counts numeric error scores; `core.py:74-90` separately excludes errors from all-k-scored readiness |
| Numeric and duplicate validation | `contract.py:114,122`: exact pair duplicate and finite exact numeric types, row-numbered; parser rejects nonfinite lexical constants at line 37; legacy duplicate diagnostic preserved exactly |
| Repeated trials | `contract.py:56-75`, `core.py:35-126`: explicit plans, expected/delivered/duplicate/unexpected counts, missing pairs, mixed statuses and readiness counts |
| Adapters | `adapters.py`: narrow explicit mappings; synthetic tests and caller-selected categorical mappings; docs/adapters.md lists discarded fields and limits |
| Output preservation | `output.py:26-48`: same-directory staging and atomic installation; injected stage-write/replace/link race failures preserve target bytes |
| Shared helper consistency | Both output.py files have SHA-256 `97a0787863525f5fc814e838f557940a226e7c3a31ea6f0b80fd31d038006c31`; SHARED_CODE.md names the three mirrored functions |

Remaining scope boundaries: scores/populations are supplied evidence, no rates or
accuracy inferred. Several file outputs are not one transaction. Archive retries,
arbitrary score objects and aggregate-only reports intentionally fail rather than
being silently normalized. Root owns remote checks/security/release readiness and
the separate three-record public Inspect pilot; its result is not adoption.

Fresh committed clone `0b58f10` passed its complete 93-test suite, frozen sync,
Ruff checks, both type checkers, schemas, wheel/sdist builds and Twine metadata.
Final review then added regression checks for malformed falsy Inspect scores,
unsupported archives and the mirrored deterministic JSON renderer. These checks
and expanded fixture schema validation are included in the subsequent fix commit;
Fresh committed clone `f5668dc` then passed 105 tests and the same checks.
Independent review reproduced UTF-8 expansion beyond the canonical input cap
and uncaught corrupt DEFLATE/LZMA decoders. All four regression cases failed
before fixes, and pass with UTF-8 JSONL, byte-cap validation before staging,
and controlled decoder failures. Fresh clone of final source commit
`b41a51b381423af6f0df94344b60537d06e9d658` passed all **109 tests**, frozen sync,
Ruff check/format, mypy, Pyright, every example schema validation, wheel/sdist
builds and Twine metadata validation. Its Git status remained clean. The final
source wheel and sdist separately installed and passed their isolated CLI smoke.

## Shared hardening and publication gates

| Recommendation | Status | Evidence or remaining scope |
| --- | --- | --- |
| Pinned Actions | Done | Every `uses:` in `.github/workflows` has a full commit SHA; local actionlint checks passed. |
| Dependency auditing | Done | CI reports audits with `continue-on-error`; it does not silently assert a clean audit. |
| Release workflows | Prepared, blocked by owner gates | `release.yml` fires only on tags, uses trusted publishing/provenance and checks version plus main ancestry. No tag or publication was executed. |
| Security settings | Prepared, blocked by owner gate | Exact settings paths and version-update configuration are in `SECURITY_SETTINGS.md`. No settings changed. |
| Pages | Prepared, blocked by owner gate | Existing Pages workflow is manual-only. Merge no longer deploys automatically. |
| README/changelog/contract | Done | Version 0.3.0 and candid scope documented; primary related-work sources opened and checked before citation. |
| Merge/tag/release/publish | Prepared, blocked by owner gates | `RELEASE_READY.md` includes commands and registry setup, and `RELEASE_NOTES.md` is ready for the release gate. |
| Final independent review | Done | Independent review found two eval adapter defects; both reproduced, regression-tested and independently rechecked after fixes. No remaining review findings. |
| Final clean-clone verification | Done | Fresh installs, full suites, lint/types, schemas and artifacts passed; exact coordinator evidence below. |
| Push and one draft PR | Done | [Draft PR #15](https://github.com/alawein/eval-audit/pull/15) opened on the authorized branch; no merge/main/tag/deploy/settings change. |

### Study status

Done, narrow pilot: `studies/inspect-security-guide` converts a pinned public MIT
Inspect log containing three archived scored samples. Actual missing, errored
and unscored counts are each zero; the supplied-subset denominator stays 3 of 3.
The 16-item underlying dataset is not substituted for the explicitly limited
three-sample run. The archived source is excluded from Git; download and SHA-256
are documented. This is not an estimate for larger evaluation populations.
The PyPI project lookup returned 404 on October 8, 2026; availability was checked,
not reserved. Disambiguation is included in the README.

### Historical checks and registry readback

First release PR #1 had 30 successful Actions checks; the remaining CodeRabbit
StatusContext was PENDING, not a failed Actions job. No failing build was inferred
from 30/31. [Historical checks](https://github.com/alawein/eval-audit/pull/1/checks).
The public PyPI project endpoint returned 404 for `eval-audit` on October 8, 2026;
that lookup does not reserve a name. Hosted Dependabot security updates and
alerts are disabled according to read-only API readback, detailed in
SECURITY_SETTINGS.md. Their re-enablement remains gated.

### Coordinator final verification

Coordinator clean clone at 8f6e67f with fresh copied Python 3.13.9 environment:
frozen install, 109 tests, Ruff check/format, mypy, Pyright, every canonical and
four adapter fixtures' schemas, python -m build and Twine checks passed.
The public-log study reproduced committed results without tracked changes.
pip-audit --local reported no known vulnerabilities in installed dependencies;
the unpublished eval-audit package itself was explicitly skipped.

All repository workflows pass local actionlint, and Markdown lint passes.
Remote main remained at the Phase 0 commit before branch publication.
Independent review findings were resolved and rechecked. No merging, tagging,
registry publication, release creation, deployment or settings mutation occurred.

Hosted initial link check failed on the two references to the authenticated
maintainer settings page, each returning 404 to anonymous lychee. Only the exact
settings URL is excluded in .lycheeignore; public citations remain checked.
The remote checks are rerun after this documented correction.

## Current release state, October 8, 2026

The v0.3.0 [merged PR](https://github.com/alawein/eval-audit/pull/15), immutable
`v0.3.0` tag, and [GitHub Release](https://github.com/alawein/eval-audit/releases/tag/v0.3.0)
are published. [PyPI run](https://github.com/alawein/eval-audit/actions/runs/37799361873)
failed with invalid-publisher; the authenticated form separately rejected the
original name. Maintenance alawein-eval-audit 0.3.1 is not yet published and its
pending-publisher acceptance remains blocked on owner-entered password confirmation.
See [release readiness](RELEASE_READY.md) for the actual states and retry rules.
Historical preparation and checks below retain their original dates and scope.

## Native review follow-up, October 8, 2026

Coordinator-reported native MAIOS job `e007ee02-144e-4615-86c7-fdb7efe7daa9`
reviewed head `454e9100f9cb28cd0ead9ad34b2d20172c2effc1`: four completed parts,
28 included files, with partial interaction coverage. This is not a complete
whole-branch review or a clean-review claim. Independent review remains separate.

Three model hypotheses were refuted by the actual contract and executed checks:

- The README wheel filename is correct: `README.md:16` uses normalized
  `alawein_eval_audit-0.3.1-py3-none-any.whl`, matching the actual wheel built by
  Hatchling and successfully installed in the isolated release smoke check.
- Distribution and import names intentionally differ: `pyproject.toml:6` names
  `alawein-eval-audit`, `pyproject.toml:15` retains the `eval-audit` entry point,
  and `pyproject.toml:33` packages `src/eval_audit`. Fresh installation imported
  `eval_audit` from the empty environment, then ran CLI help and the example.
- Owner approval is present: `AGENTS.md:30` records the exact named follow-up and
  `AGENTS.md:36` states no renewed per-step authorization is required. The entire
  Dependabot family remains explicitly excluded. A model cannot reinstate a gate
  contradicted by the owner's recorded words.

No implementation change was made for these refuted hypotheses. The independent
checksum-sidecar defect was repaired in `734bd24` and `b6f264c`, with exact LF
inventory validation and missing/modified/creator regression tests. Final source
head `b6f264cc4a72cff2beb67a47db9b5e0eb5f9619e` passed 140 tests on Python
3.11.13, 3.12.10 and 3.13.9, including the clean-clone fresh-environment run.
The current review note is a documentation-only follow-up to that checked head.

## Independent review repair, October 8, 2026

Independent exact-head review of `29fe353` found two release integration defects:
the publishing action's `.publish.attestation` sidecars polluted canonical dist,
and successful public notes would still say PyPI publication was pending. It also
identified the bounded partial-upload recovery limitation. The repair preserves
strict canonical inventory, stages only missing packages separately, verifies
present registry bytes/publisher proof before resuming, requires complete verified
postflight, and generates factual public notes only after independent verification.

New regressions model the pinned action's real sidecar filenames and workflow
packages-dir setting, completed partial uploads, foreign publishers, canonical
directory preservation, nested staging rejection, and successful/failed note
generation ordering. Runtime, adapters, study inputs/results and schemas are
unchanged. Actual new-version publication and live provenance remain pending.

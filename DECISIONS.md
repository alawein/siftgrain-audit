# v0.3.0 decisions

- Legacy schema-1 input without `trials_per_id` returns the identical schema-1
  report and still rejects duplicate IDs. Extended input accepts schema 1 or 2;
  schema 2 enables trial mode with default one trial. Extended reports use 2.
- Trials are one-based positive integers. `trials_per_id` is a positive integer
  or an exact expected-ID mapping. Total planned trials and delivered rows are
  capped at 10,000. In trial mode absent row trial means trial 1.
- ID status precedence is missing, errored, unscored, scored. Thus mixed trial
  statuses have exactly one ID category and the partition invariant holds.
  Complete means all expected trials delivered, independent of scoring.
- For each k, eligible IDs must plan at least k trials. Pass@k and pass^k
  denominator readiness counts IDs with trials 1..k all in scored status.
  They have the same readiness denominator; no correctness or success rates
  are computed. Errored-with-score contributes to availability only.
- Adapters require an explicit caller manifest and named score key for Inspect
  and lm-evaluation-harness. Framework fields are never used to infer expected
  population. Conversion validates every source row and canonical output.
- Atomic output guarantees apply per file. Several outputs are not one
  transaction. Existing aliases and hard links are rejected before staging.
- Order invariance applies to audit counts and report bodies. CLI input hashes
  bind exact file bytes, so reordering JSONL bytes correctly changes the input
  digest even when the audit body is identical. Source bytes are never normalized
  solely to equalize hashes.

## Dated v0.3.0 release coordination decisions

Hosted link checks returned 404 only for the repository's maintainer-only security
settings URL. Keep its exact click path, exclude only that anchored URL from
anonymous lychee probes, and continue checking all public research/document links.
Read-only API checks separately established the disabled alerts/update settings.
No setting or credential was changed to make the check pass.

Pages deployment is manual-only so approving a merge does not also approve
hosting. A release tag starts trusted package publication, so the tag requires
both tag and registry publication authorization. npm first-publication bootstrap,
if needed, is a separate owner-approved publication using existing access; this
run does not create secrets or bypass registry setup.

## PyPI first-publication finding (2026-10-08)

The unauthenticated project JSON endpoint returned 404 for `eval-audit`, but this
did not prove that PyPI would accept the name. The authenticated pending-publisher
form rejected it with "This project name is too similar to an existing project."
The planned distribution name is therefore blocked even though no package exists
at that exact JSON endpoint. No package was published under another name.

Historical proposal: `alawein-eval-audit` as the distribution-name alternative, subject to
PyPI's name checks and explicit owner selection. Keep the GitHub repository,
`eval_audit` import package, and `eval-audit` command unchanged. A renamed
distribution needs updated metadata, lockfile, docs, and a release version/tag
decision before publication; do not silently reinterpret the approved v0.3.0 tag.

## Authorized maintenance closeout (2026-10-08)

The owner's follow-up authorizes the reversible default `alawein-eval-audit`
distribution and maintenance version 0.3.1, preserving the repository, import,
CLI and schema/report contracts. Authenticated pending-publisher acceptance is
still unverified: the coordinator encountered an expired sensitive-action
password confirmation and prepared the owner-entry handoff. HTTP 404 is not an
acceptance check. If rejected, use the authorized `alawein-evaluation-audit`
alternative only after recording the actual form result. No new credential is
created as a workaround.

v0.3.0 [PR 15](https://github.com/alawein/eval-audit/pull/15) merged at
`b3d116f66840387013848781daa66f3968c9a5d6`; its immutable tag and
[GitHub Release](https://github.com/alawein/eval-audit/releases/tag/v0.3.0) are
published. [Publishing run](https://github.com/alawein/eval-audit/actions/runs/37799361873)
failed with PyPI `invalid-publisher`: no publisher matched the valid token's
claims. This is distinct from the separately observed name rejection. v0.3.1
publication is not yet attempted. Preserve old tags, feature branches and assets.

The release pipeline has separate build, publish and release-upload jobs. Locked
Hatchling 1.32.4 and pypi-attestations 0.0.30 are development tools only. A retained
canonical artifact is uploaded before registry authentication; retry failed jobs
from that run instead of rebuilding or blindly re-uploading an existing version.
Every present registry file requires exact downloaded hashes and publisher
provenance. A complete verified inventory skips publishing; a verified subset
stages only the missing canonical files. Complete inventory remains mandatory
after publication and before GitHub release creation. Existing differing release assets fail closed.
Checksums live outside dist. Build verification binds repository, workflow,
source commit, tag and hosted runner; registry publish provenance is verified
with PyPI's client. These workflow checks are implemented, not yet executed for
a new published maintenance release.

The larger real Inspect archive has ten explicitly selected trials, all delivered
and all unscored. It is a useful expanded example, not representative benchmark
failure-rate evidence. No scores, errors or headline metric were manufactured.
The original pilot remains intact. Both packages retain duplicated output helpers
and mirrored synthetic vectors rather than introducing a shared dependency.

Dependabot's entire family remains excluded. Existing report-only pip-audit,
full-SHA actions, protected reviews, OIDC and artifact verification provide the
non-Dependabot controls within this scope.

## Bounded release integration repair (2026-10-08)

Independent exact-head review of `29fe353` reproduced the pinned publishing action's
wheel/sdist `.publish.attestation` sidecars in dist. Strict postflight inventory
then rejected an otherwise successful publication. The publisher now receives a
fresh separate staging directory with copied missing files; canonical artifacts
are unchanged. Staging under canonical dist is rejected as well. Strict inventory
was preserved, rather than accepting arbitrary extra distribution files.

The same review found that the previous automatic public release body reused local
preparation text saying PyPI publication was pending. Public notes are now generated
after independently verified complete registry files/provenance, naming factual
package/version, source/tag, hashes and the committed changelog. Local readiness
documents continue to state the actual pending acceptance/publication state.

Partial-upload recovery verifies every existing file's name, digest, downloaded
bytes and exact publisher identity before staging only missing files. A foreign
publisher, changed file, extra/duplicate entry, unavailable proof or failed request
stops the attempt. No blind skip-existing switch is used. Offline synthetic
publisher integration tests reproduce the actual sidecar paths and partial upload
transitions; these do not simulate OIDC or establish actual live publication.

## Bounded registry propagation retry (2026-10-08)

The coordinator observed outcome-check release run 37824835131 upload successfully
before immediate version metadata verification reported incomplete inventory.
Later retained-byte and provenance reconciliation confirmed the complete release.
Complete postflight verification now permits five metadata attempts with delays
2, 5, 10 and 20 seconds (37 seconds accumulated sleep, plus verification time).
Only absent version metadata or missing canonical files can retry. Every visible
file is reverified on each attempt; duplicate/extra inventory, checksum mismatch,
artifact download failure and missing/foreign provenance fail immediately.
Preflight missing-only staging remains immediate. No runtime or study behavior
changes, and no assertion of eval-audit live publication follows from these tests.

## Existing release note reconciliation (2026-10-08)

The coordinator created the factual GitHub-only v0.3.1 release after canonical
run 37828182517 failed PyPI authentication with invalid-publisher. A subsequent
successful authenticated recovery must replace that pending registry statement.
The release helper now updates notes for an existing release only after every
existing asset and complete upload readback match canonical bytes. Conflicting
existing assets or corrupt readback stop before editing notes. Tags, version,
core behavior and artifacts remain unchanged; live registry setup remains pending
owner-entered sensitive-action password confirmation and name acceptance.

## Census redesign, October 13, 2026

This is architectural work spanning import boundaries, a viewer and a benchmark.
The user's original brief supplies the purpose and explicitly requests autonomous
execution; its no-pause instruction overrides optional design approval ceremonies.
Implementation plan stays in chat; this file records decisions, not a new tracker.

- Preserve the validated coverage engine and schema-1 output. Existing hardening
  findings are superseded rather than reimplemented. Keep Python 3.11 and stdlib.
- Add HELM original-instance stats and Open LLM exported JSON adapters as narrow
  explicit formats. Reject ambiguous metric/perturbation shapes; never infer N.
- Separate score sensitivity from audit JSON and pass readiness. Report exact
  rational sums/means under named policies; errors retain their original status.
- Keep Siftgrain Census as product branding while retaining repo/package/CLI names.
  Siftgrain replaces rejected Spanward; limited searches are not legal clearance.
- Vendor the single frozen unpublished suite token package byte-for-byte. Use
  data-theme and data-vibe attributes; do not create another shared registry.
- Embed trusted viewer assets, escape all imported evidence, block connect-src,
  guard every storage call, and apply stored appearance before first paint.
- Use an opt-in WebGL2 background in an OffscreenCanvas worker. Initial static
  rendering avoids startup shader stalls; missing-cell state settling stays
  lightweight. Unsupported workers/contexts, reduced motion and hidden pages keep
  evidence usable. No WebGPU dependency is justified for this effect.
- Put trial controls immediately after coverage. Detailed cards, source and hashes
  remain inside a labeled disclosure; no supplied evidence is lost on mobile.
- Benchmark actual pinned three-sample Inspect scores with explicitly synthetic
  cloned epochs and faults. Dev/test are disjoint fault seeds sharing source IDs.
  Report exact controlled counts without binomial CIs or human labels. Native
  Inspect parser/accuracy is an executed baseline, not its whole evaluation policy.
- A core/gold mismatch fails the benchmark command. Naive baseline performance is
  descriptive. Default product remains network-free; fetch is an explicit dev tool.
- Preserve prior tags/branches and all unrelated work. Draft PR plus coordinator
  review precede any eligible merge. Identity changes and external dataset uploads
  remain prepared steps with exact commands, not executed outcomes.

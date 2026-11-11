# Release readiness

## Current state, October 8, 2026

v0.3.0 [PR 15](https://github.com/alawein/eval-audit/pull/15) merged at
`b3d116f66840387013848781daa66f3968c9a5d6`. The immutable `v0.3.0` tag and
[GitHub Release](https://github.com/alawein/eval-audit/releases/tag/v0.3.0) exist.
The historical Registry run link now returns 404, so the recorded
`invalid-publisher` result cannot be independently verified here. It recorded no publisher matching the
valid token claims. Separately, its authenticated pending-publisher form rejected
`eval-audit` as too similar to an existing project. Its JSON 404 was not name
acceptance. Local v0.3.0 GitHub assets retain their documented CI-attestation
limitation; preserve their bytes and tag.

The owner authorized the remaining closeout, including registry setup, publication,
merge, tags, release, Pages and non-Dependabot controls. No repeated approval is
needed for that named scope. Preserve feature branches and avoid `--delete-branch`,
`--admin`, force pushes or rewritten tags. Dependabot's entire family is excluded.

Maintenance distribution `alawein-eval-audit` version 0.3.1 merged at
`af0eacba86add5311e901467352619fe01e53135`. Its immutable `v0.3.1` tag and
[GitHub Release](https://github.com/alawein/eval-audit/releases/tag/v0.3.1) exist.
The historical Canonical release run link now returns 404. It recorded
retained canonical artifacts but registry authentication failing with
`invalid-publisher`, which cannot be independently verified here. The public GitHub-only release records that actual state.
The historical Pages run link now returns 404. It recorded
success at the merged revision, which cannot be independently verified here. The merged test suite passed 157 cases.
Repository `eval-audit`, module `eval_audit` and command `eval-audit` are unchanged.
Pending-publisher acceptance and publication have not completed: the authenticated
PyPI session needs owner-entered sensitive-action password confirmation. This is
an access blocker, not a new approval gate. Do not put credentials in logs or use
tokens as a workaround. If the form rejects the default, record its exact cause
before trying the authorized `alawein-evaluation-audit` alternative.

## Maintenance delivery

Register the accepted project's [pending publisher](https://pypi.org/manage/account/publishing/):
GitHub owner `alawein`, repository `eval-audit`, workflow `release.yml`, environment
`pypi`. The existing immutable `v0.3.1` tag retains the merged revision; never alter it
or `v0.3.0`. After publisher acceptance, reconcile retained canonical bytes and
exact provenance through the coordinator-owned recovery path.

The tag-only release workflow builds once with the locked backend, verifies exact
wheel/sdist metadata and SHA-256, attests them, then retains
`canonical-distributions` for 30 days before registry authentication. SHA256SUMS
and inventory.json are outside dist, so neither can be sent to PyPI as a package.
Publishing copies only verified missing files into a fresh `publish-dist/` staging
directory. The pinned PyPA action writes `.publish.attestation` sidecars there;
they never enter canonical dist or retained release assets. GitHub Release upload
consumes the exact retained canonical files.
Only release-upload has contents:write. Existing mismatching GitHub assets fail.

For a failed publishing run, rerun failed jobs using its retained canonical
artifact. Preflight downloads every existing file to verify its exact hash and
publisher provenance. A complete matching version skips publication. A matching
verified subset resumes by staging only missing files; present files are never
re-uploaded. Different bytes, extra filenames, duplicate entries or foreign/missing
publisher provenance fail closed. Postflight requires the complete exact inventory
and re-verifies every file before any release creation. HTTP 403, other API failures and uncertain effects are not
absence. Reconcile at the destination before any retry. A success must not be
retried blindly. If the canonical artifact expires, stop and prepare a new version
instead of reconstructing old bytes.

After success, the workflow downloads the PyPI distributions and verifies hashes,
GitHub build provenance with exact repository/workflow/source commit/tag and hosted
runner constraints, and PyPI publish provenance. It uploads the identical built
files and checksums, then downloads every GitHub asset to verify bytes. A new
release is complete only after these actual remote checks pass. See
[GitHub verification flags](https://cli.github.com/manual/gh_attestation_verify)
and [PyPI provenance verification](https://docs.pypi.org/attestations/consuming-attestations/).

The public release body is generated only after the release-upload job independently
re-verifies complete registry bytes and publisher provenance. It names the verified
distribution/version, source commit, tag and SHA-256 values, and links the committed
changelog. Local preparation notes are not used as the public publication status.

Update v0.3.0's release description to point to the new distribution after actual
success, retaining the old tag/assets. The manual Pages workflow remains authorized;
verify its run and public page before claiming deployment. Follow
[non-Dependabot security controls](SECURITY_SETTINGS.md).

## Dated prepublication history

Earlier v0.3.0 preparation permitted a draft PR only, and separated merge, tag,
registry, release, Pages and settings gates. Those were the permissions at that
time; the owner's October 8 follow-up superseded them. The original Phase 0 and
prepublication test results remain in [AUDIT_VERIFICATION.md](AUDIT_VERIFICATION.md).
No historical test run is represented as a maintenance validation run.

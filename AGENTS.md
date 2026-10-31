# Eval audit

Strict, offline evaluation coverage auditor. Read README.md and docs/contract.md
before behavior changes. Python 3.11+, stdlib runtime; uv manages the dev lock.

- Work on a feature branch; preserve unrelated changes.
- Write meaningful contract and negative tests before changing behavior.
- Use `just check` for product lint, tests and build. No workspace audit required.
- Runtime never calls a network, model, subprocess or agent executor.
- Scores are availability evidence, never accuracy or an inferred denominator.
- Escape imported text in HTML; reject malformed input without dropping records.
- Preserve input/output identity checks, including existing hard links.
- Examples are synthetic, AI-assisted, non-client, CC0 data. No adoption claim.
- Do not edit the lock manually or expose secrets. Inference spending follows canonical policy; other spending requires owner authorization.

Owner authorized publication mode (c), October 4, 2026: bootstrap, first-release
feature and release PRs to main, public MIT repo, GitHub Release v0.1.0 and Pages
synthetic report. Push, check, review and merge within that scope. This scoped
permission supersedes the starter's owner-only merge rule. GitHub-only package
distribution and Pages are approved tool-class exceptions. New scope requires
the owner's instructions. Never bypass a hook or weaken protection to merge.

The owner selected chat option (b) on October 8, 2026: complete the reviewed
v0.3.0 release delivery for alawein/claim-review, alawein/eval-audit and
alawein/outcome-check, targeting main. This explicitly authorizes merging the
existing hardening PRs, registry trusted-publisher configuration, v0.3.0 tags,
npm/PyPI publication and GitHub Releases. It is the plain-language equivalent
of profile execution mode (c) for this named scope, not profile mode (b).

Owner follow-up on October 8, 2026: "I authorize all, except Dependabot
which takes time and is spamming PRs and stuff which I hate." This supersedes
previous gates for the remaining recommendations in these three repositories:
review repair, compatible code/documentation improvements, distribution naming,
registry setup/publication, necessary credential setup, release delivery, Pages,
and non-Dependabot security configuration. Record actual execution separately
from the requested plan. No renewed per-step authorization is required.

Exclude the entire Dependabot family: do not enable or modify its alerts,
security updates, version-update configuration, or PR automation. Use existing
report-only dependency audits instead. Credentials remain owner-entered and
managed through the established secret owner; never print or commit them.
Preserve existing release tags and feature branches. No force pushes, unrelated
remote changes, new repositories, or kohyr copies are part of this closeout.

## Current release state, October 8, 2026

The v0.3.0 [merged PR](https://github.com/alawein/eval-audit/pull/15), immutable
`v0.3.0` tag, and [GitHub Release](https://github.com/alawein/eval-audit/releases/tag/v0.3.0)
are published. [PyPI run](https://github.com/alawein/eval-audit/actions/runs/37799361873)
failed with invalid-publisher; the authenticated form separately rejected the
original name. Maintenance alawein-eval-audit 0.3.1 is not yet published and its
pending-publisher acceptance remains blocked on owner-entered password confirmation.
See [release readiness](RELEASE_READY.md) for the actual states and retry rules.
Historical preparation and checks below retain their original dates and scope.

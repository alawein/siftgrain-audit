# Security controls

## Current scope, October 8, 2026

The owner explicitly excludes the entire Dependabot family, including alerts,
security updates, version-update configuration and PR automation. No instruction
here asks to enable it. Preserve `.github/dependabot.yml` if present unchanged.

Existing CI uses report-only `pip-audit --local`, full-SHA action pins, restricted
workflow permissions, protected review/checks, and OIDC publication. The maintenance
release pipeline adds retained exact artifacts, SHA-256 comparisons and build/
publish attestation verification. A clean dependency audit does not establish
that software is secure. Default runtime dependencies remain empty.

Supported non-Dependabot settings include dependency graph, secret scanning and
push protection where available, branch protection/review/checks, and least-privilege
Actions permissions. Actual settings readback belongs to the coordinator; local
configuration is not proof that a hosted control is enabled. Maintainers can open
<https://github.com/alawein/eval-audit/settings/security_analysis>; anonymous link
checks retain the narrowly scoped settings-page exception.

Coordinator live GitHub readback on October 8 verified secret scanning and push
protection enabled, with Dependabot alerts and security updates disabled. No
non-Dependabot settings change was needed. This is attributed coordinator evidence,
separate from this worker's local tests.

The trusted publisher requires the accepted PyPI distribution, owner `alawein`,
repository `eval-audit`, workflow `release.yml`, and environment `pypi`. See
[release readiness](RELEASE_READY.md). Credentials remain owner-entered through
the managed-secret flow. Do not create or rotate a token as a workaround.

## Dated settings evidence

Read-only API checks before v0.3.0 publication on October 8 found disabled
vulnerability alerts and security updates, with automated fixes reporting
`enabled: false, paused: false`. No settings were changed in that preparation.
The old proposal to enable those controls is retired by the owner's explicit
exclusion. These observations are historical, not a claim about later settings.

## October 13 readback and optional restoration

Fresh repository API: secret scanning and push protection enabled; Dependabot
security updates disabled. Active main-protection ruleset requires signed,
linear-history squash PRs and markdown-lint, link-check, actionlint, pr-title,
python-ci. Legacy branch-protection endpoint returns 404 because this repository
uses rulesets. No setting was changed. Report-only npm audit is now included
for development browser tooling; pip-audit remains report-only.

Only after a future explicit owner instruction: repository Settings > Advanced
Security (or Code security and analysis) > Dependabot alerts > Enable; then
Dependabot security updates > Enable. Version-update PRs separately require
Settings > Advanced Security > Dependabot version updates > Configure and a
reviewed .github/dependabot.yml. These are restoration paths, not actions taken
or authorized by this document. The current entire-family exclusion remains.

# Requirement coverage

Scope: Census portions of the October 13 three-tool brief. Cite and State are
owned by their separate controllers. Done means the concrete implementation or
observed run named here, not a claim that the entire broad brief is complete.

| Requirement | Status | Evidence / boundary |
| --- | --- | --- |
| Current MAIOS policy, personal style, repo contract, continuation and task row | done | MAIOS_CONTEXT.md, verified origin/master pins; no MAIOS writes |
| Recent commits, PRs, releases and settings-visible changes | partial | docs/recent-history.json and shared-history.json/md inventory accessible branches and observations; inaccessible/deleted historical state cannot be reconstructed |
| Verify old audit with baseline counts and file:line | done | AUDIT_VERIFICATION.md, 170 prechange tests; superseded findings refuted explicitly |
| Primary-source market/evaluation scan, dates and cutoff | partial | RESEARCH.md bounded official-source scan; living-doc dates unknown; not exhaustive market coverage |
| Job, primary user and integrations | done | BRAND.md and RESEARCH.md |
| Family/product naming and cross-registry collision checks | done | docs/name-checks.json, Siftgrain Census, rejected Spanward; limited search, no trademark/domain clearance |
| Original logo, wordmark, palette, type and voice | done | brand SVGs, BRAND.md, frozen canonical token package |
| Shared design-token package | done | private unpublished design-tokens v1.0.0 vendored from claim-review; runtime CSS byte equality enforced |
| Four switchable vibes and remembered choices | done | viewer.js/css, guarded storage, data-theme/data-vibe; all eight appearance/vibe combinations axe-tested |
| Dark default and accessible light | done | before-paint guarded preference application, canonical AA token tests, browser axe |
| WebGL2 hero, local assets and static fallback | done | opt-in OffscreenCanvas worker effect, static grid fallback, no runtime CDN; WebGPU intentionally omitted |
| Transform/opacity/filter-only state animation and reduced motion | done | missing-cell settling, CSS reduced-motion override, pause/hidden/offscreen handling |
| WCAG 2.2 AA, keyboard, labels and focus | partial | zero axe violations in tested matrix, keyboard/focus checks and mobile screenshots; automated tools do not establish exhaustive manual WCAG conformance |
| 60 fps, INP <200 ms, file LCP <2.5 s and gzip CI budget | partial | PERF.md actual file/localhost lab measurements and enforced budgets; field INP and midrange-laptop certification unavailable; headless WebKit cadence below 60 fps in sampled window |
| Playwright Chromium/Firefox/WebKit, axe and Lighthouse CI | done | nine browser tests, all eight theme combinations per engine; actual LHCI runs and CI job |
| GIF/MP4 per vibe | done | actual captured brand/demos/*.mp4, reproducible Playwright+ffmpeg script |
| Deterministic offline explicit-input stdlib core | done | unchanged core/contract/output helpers; default runtime dependencies empty |
| v0.2.x compatibility and versioned Draft 2020-12 schemas | done | unchanged legacy snapshot path; MIGRATION.md and new separate sensitivity schema |
| Repeated trials, per-ID/per-trial and pass@k/pass^k denominator counts only | done | existing validated engine preserved; tests/test_trials.py; no success rates introduced |
| Row-numbered NaN/infinity/bool rejection | done | existing strict contract preserved, new adapters validated through it |
| Explicit errored-scored numerator policy | done | availability includes errors with scores; readiness/scored-only excludes them; separate sensitivity policies |
| Atomic output writes and Python 3.11 | done | unchanged shared helper, safety vectors and 3.11 CI matrix |
| Inspect/lm-eval/HELM/promptfoo/Open LLM convert adapters | partial | five strict local export adapters; HELM per-instance arrays and Open LLM exported JSON only, no arbitrary raw runs/Parquet or network download |
| GitHub Action and pre-commit denominator gate | done | action.yml, .pre-commit-hooks.yaml; subprocess negative tests prove shrinkage exit 1, including a manifest named --help |
| Separate score-sensitivity view | done | exact-rational three-policy HTML/optional JSON; no change to pass readiness or core audit JSON |
| Self-contained waffle, trial strips and table filter | done | every planned trial stays in N; escaped imported text; filters never change N |
| Optional rich CLI only | done | cli extra and --rich stderr summary; default JSON unchanged |
| Shared output/JSON safety behavior and tests | done | output.py preserved; shared vectors and render_json tests remain passing |
| Full-SHA Actions and report-only audits | done | CI pins; pip-audit reports zero, npm reports 17 development-tool vulnerabilities; Dependabot unchanged |
| SECURITY_SETTINGS restoration paths | done | exact optional click paths; entire-family exclusion remains active |
| Real public data, provenance/license/checksum/fetch and downloadable archive | done | pinned MIT Inspect source, minimal mapped values, dataset-v1.zip includes attribution and metadata; external source bytes ignored |
| Fault injection, P/R, denominator error and determinism | done | 280 fixed transformations; exact confusion counts, gold failure gate and reversal invariants; tiny source and synthetic epochs disclosed |
| Native Inspect/lm-eval and naive baselines | partial | actual Inspect parser/accuracy plus naive executed; full Inspect aggregation and native lm-eval not run; no model calls |
| Dev/test, separate keys, datasheet/Croissant/HF card/schema/checksums | partial | fault-seed split with separate public keys and metadata; source IDs overlap; actual mlcroissant1.1.1 parses two RecordSets and coordinator extracted 140 rows per split; not uploaded |
| One-command bench, performance/memory, honest uncertainty | done | make bench; fixed-suite counts and host timing/allocation measurements; no inappropriate population CIs |
| Human protocol and no fabricated labels/LLM baseline | done | datasheet protocol only; none collected; LLM baseline explicitly omitted |
| Clean-clone fresh environment full validation | partial | fresh local environment checks execute on the source; automatic approval review rejected PR-plus-clone command, so no clean-clone claim |
| Draft PR, independent review, final-head checks and eligible landing | partial | source checkpoint pushed and independent coordinator review completed on the first candidate, final corrections supplied; automatic approval review blocked draft PR creation; no merge |
| Repository rename/transfer, shared package publication, HF upload | gated | MIGRATION.md and PUBLICATION.md prepared commands; no identity or upload action executed |

Limits remain part of the product: supplied scores and populations are evidence,
hashes bind bytes rather than truth, and absence of records is never silently
treated as a smaller expected population. No client work or adoption is claimed.

# Viewer performance

Budget: self-contained acceptance report <= **32 KiB gzip**. Current observed
report: **9,414 gzip bytes**. CI builds the report, checks this budget and exact
runtime-token identity, runs three real browsers/axe, and runs Lighthouse CI.
No runtime CDN/library/font fetch is required. The Python core stays stdlib.

| Engine | file LCP ms | Max trusted lab interaction ms | Synthetic two-frame max ms | Frame median / p95 ms |
| --- | --- | --- | --- | --- |
| chromium | 164 | 56 | 34.9 | 16.5 / 18.0 |
| firefox | 313 | 24 | 13.0 | 6.0 / 7.0 |
| webkit | 942 | 144 | 74.0 | 26.0 / 33.0 |

Data: docs/browser-performance.json. The observer records trusted Event Timing
entries from twelve actual Playwright clicks. The lab candidate is the maximum
reported interaction duration in this small session, not field INP. Entries
below the browser's 16 ms threshold may be absent; missing entries are undefined,
never zero. The separate synthetic filter-to-two-frame measurement is not INP.

Frame cadence is sampled for 60 frames after filter dispatches, with the background
paused after an even number of clicks. It is not a per-interaction GPU benchmark
or certification of a midrange laptop. Chromium's median is near 60 fps; sampled
headless WebKit cadence was slower. No universal 60 fps claim is made. Field INP
is unavailable without real-user data; no telemetry is added.

Lighthouse CI uses localhost because Lighthouse does not audit file:// URLs.
The actual three-run result is docs/lighthouse-results.json: LCP 769-827 ms,
TBT 0-150.5 ms, accessibility 1.0. Worst-run LCP <=2500 ms and TBT <=200 ms are
enforced, along with accessibility 1.0. TBT is a diagnostic, not INP. Individual
file:// LCP values above are independently measured through Playwright.

Initial WebGL setup caused startup main-thread stalls in an earlier measured
implementation. The effect now uses an opt-in OffscreenCanvas worker; static
content and meaningful missing-cell settling are immediately available. Reduced
motion disables nonessential motion; hidden/offscreen pauses work. Unsupported
worker/WebGL contexts and context loss retain the static grid. No WebGPU branch
is needed. CSS animates only transform and opacity; colors/layout swap instantly.

`npm run perf` creates isolated retained Lighthouse storage so ports/runs do not
mix. `npm run test:browser` writes full measurements to ignored .verification.
The CI job is viewer-validation. Actual MP4s in brand/demos are Playwright captures
converted locally with ffmpeg, not generated imagery or fabricated human sessions.
Reproduce with `node scripts/record_demo.mjs` after building the static demo.

Report-only dependency audit: zero known Python findings on the locked default
development environment; npm reports 17 development-tool findings (11 high,
4 moderate, 2 low), including Lighthouse CI's transitive dependencies. These
packages are never embedded in the portable report or required by the Python
runtime. No forced major upgrade or Dependabot change is performed.

A subsequent final cold mobile-simulator session recorded TBT 271.5/0/0 ms,
exceeding the unchanged worst-run 200 ms TBT assertion. LCP and accessibility
passed. This occurred while other tool browser work was active; contention is
a hypothesis, not a proven cause. docs/lighthouse-contention.json preserves it.
The single rerun with this suite's other GPU checks idle passed the same original
mobile profile and bounds: LCP 769-827 ms, TBT 0/150.5/0 ms, and accessibility
1.0 in all three runs. Both observations are retained; this comparison supports
contention as a possible cause without proving all host activity was absent.
No number is reinterpreted as field INP.

# Siftgrain Census

For evaluation engineers reviewing incomplete runs, Siftgrain Census compares
supplied per-sample logs with an explicit population before anyone interprets
scores. It shows what arrived, what failed, and which planned trials are missing.
Use it locally, in CI, in pre-commit, or as a portable offline HTML artifact.

Voice: **Count the run before reading the score.**

The family names Siftgrain Cite, Census and State describe separate evidence
tasks. `docs/name-checks.json` records exact GitHub, npm, PyPI and Hugging Face
checks and rejected alternatives. Trademark-style web queries found dictionary
uses of Siftgrain and no obvious software brand among returned results. This is
a limited dated search, not trademark clearance or a domain availability claim.
Spanward was rejected because existing software businesses use that name.

`brand/logo.svg` is original geometry: four planned cells with one outlined gap,
inside a stepped census frame. `brand/wordmark.svg` combines the mark with a
plain wordmark. MIT code/artwork; no third-party marks or personal artwork copied.

The shared `design-tokens/` package is private and unpublished; claim-review is
its canonical source. Palette: deep violet background, warm paper text, amber
accent, mint focus and scored state, pink error state. Exact values and AA
contrast tests live in tokens.json and tokens.test.mjs, not a second palette.
Body: system UI. Display: Georgia when useful. Dense data: local system monospace.
No remote fonts, CDN scripts, analytics or runtime network requests.

Dark is the default. Light is explicit. Cartoon uses spring settling and sticker
shadows; Calm soft settling; Pixel stepped settling; Lab compact linear settling.
Missing cells settle below the grid but remain counted and labeled. Motion can
pause, stops while hidden/offscreen, and is disabled by reduced-motion preference.
WebGL2 adds a subtle local evidence grid; unsupported/lost contexts keep static
evidence usable. No WebGPU implementation is needed for this small effect.

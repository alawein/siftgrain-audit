# Migration and identity

Siftgrain Audit is the product title and the GitHub repository is
`alawein/siftgrain-audit`. Python distribution `alawein-eval-audit`, module
`eval_audit`, and command `eval-audit` remain compatible. Existing tags and
feature branches are retained. The family also includes Siftgrain Cite and
Siftgrain State; limited collision searches are not legal clearance.

v0.2.x schema-1 manifests and rows load directly through the existing legacy
validation path. Their audit JSON stays byte-for-byte compatible with committed
snapshots. No lossy rewrite is necessary. To enable repeated trials, add
`trials_per_id` or use schema_version 2 and explicit trial identities starting
at 1. Reports use schema_version 2 for trial populations.

The new HTML renderer embeds trusted local code and styles, full planned-trial
evidence, theme controls and a separate score-sensitivity table. Audit JSON
does not gain score averages or pass rates. Optional `--sensitivity policy.json`
exports descriptive arithmetic separately, including its denominator and
errored-score rule. Fractions preserve exact supplied decimals and huge integers.

HELM conversion accepts a local per-instance statistics array, one original
scenario/run/metric export at a time. Open LLM conversion accepts an exported
details JSON array with doc_id and a literal metric key. Neither downloads
datasets or reads Parquet. Unsupported shapes fail; population is always supplied.

The GitHub repository has been renamed to `alawein/siftgrain-audit`. Keep the
Python distribution and command names as compatibility entrypoints. No kohyr
transfer is proposed without explicit destination consent.

# Functional evidence

The v0.2.0 baseline at `06b6d1e` collected and passed 46 tests on Python 3.13.9.
The v0.3.0 suite adds repeated-trial and adapter cases, schema checks, atomic
output failure injection and 200 deterministic Hypothesis-generated packets.
Six status cases pin complete, missing, scored-zero, errored-null, errored-partial
and unscored-null outcomes. Other cases cover unexpected IDs, order invariance,
invalid numbers, duplicate keys/IDs, unknown fields, empty populations, limits,
UTF-8/BOM, U+2028, large integers, 10,000 IDs, hard-link preservation, HTML escaping
and CLI help. New tests cover --help content, row-index errors, the how-to-read legend,
escaping of missing-ID lists, CRLF records, and missing input/output-dir negatives.

One oversized test initially failed in pytest setup: its default case ID exceeded
Windows path limits. Short explicit IDs repaired the harness. No product mismatch
remained. Tests do not establish semantic evaluation quality. Actual released
artifact and hosting checks are recorded in release notes after execution.

Property tests check ID and trial partitions, availability bounds, explicit
all-k-scored readiness and independence from manifest/record order. Negatives
cover malformed trial plans/numbers, duplicate pairs, categorical mapping,
nonfinite/bool scores, unsupported score shapes and ambiguous ZIP members.
Atomic tests inject stage-write, forced-install and exclusive-create failures,
checking old bytes and stage cleanup. Published schemas validate both legacy
and extended example packets and reject malformed records/version extensions.

Verification counts come from `just check`. Tests establish the supplied
data contract, not the truth or representativeness of the source population.

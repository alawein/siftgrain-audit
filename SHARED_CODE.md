# Shared local output helpers

`src/siftgrain_audit/output.py` intentionally duplicates the stdlib helpers in
`alawein/outcome-check`, `src/outcome_check/output.py`: `same_location`,
`validate_outputs`, and `atomic_write`. Keep these three functions identical.
`src/siftgrain_audit/report.py:render_json` also duplicates the JSON renderer in
`src/outcome_check/report.py`. Both sort keys, indent by two spaces, reject NaN,
use ASCII-safe JSON strings and append one final newline. HTML renderers are
tool-specific and escape imported text. Keep the JSON function identical too.
The v0.3.0 changes were synchronized between both maintainers and tested in both
repositories. No shared runtime package or runtime dependency is introduced.

The output safety contract is per-file atomic installation: same-directory
temporary file, full write/flush/fsync, `os.replace` when forced, `os.link` for
exclusive creation otherwise, then stage cleanup. Validation rejects resolved
aliases and existing hard links before staging. This is not a multi-output
transaction, race-proof input validation, or a power-loss durability guarantee.

Both packages now mirror tests/test_shared_vectors.py: force and no-force writes,
hard-link input aliases, competing creation, unsupported link/replace, staging
failure, second-output failure, sorted finite JSON with trailing LF, and escaped
HTML text. These preserve per-file atomicity and fail-closed unsupported behavior.

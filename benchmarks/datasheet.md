# Datasheet

Purpose: regression and adapter verification, not model ranking. Unit: one
supplied six-trial plan plus transformed Inspect sample rows. Source population:
three real archived selected samples. Collection: pinned public upstream log,
MIT license, fixed checksum. No new model calls, human labels, personal-data
collection or manual adjudication. Model text is omitted from redistribution.

Composition: 280 cases in disjoint seed sets; 140 dev and 140 test. Each split
has 20 cases for each transformation and 20 clean controls. Both splits reuse
the same three underlying source samples and are not independent population
samples. A cloned second epoch is a synthetic stress device. Gold is the
specified transformation/plan, not correctness of original answers.

Preprocessing: keep id, epoch, scores, error; clone epoch; apply one seeded
mutation and shuffle. Unexpected fields aren't used to infer population.
NaN fault files are intentionally invalid JSON. Maintenance: version future
changes instead of silently rewriting the corpus. Git history binds releases.
Human-study protocol: recruit informed reviewers, assign blinded case sets,
record time and error definitions in advance, preserve self-reported identities,
report denominators and agreement with uncertainty. No study has been run.

# Prepared external steps

The implementation branch and draft PR are inside the authorized redesign scope.
Independent coordinator review must bind the final head before eligible merge.
No new tag, package release, identity change, dataset upload or transfer has been
executed by this redesign. Old tags and feature branches are retained.

Repo rename requires named identity approval. Prepared command:
`gh repo rename siftgrain-census --repo alawein/eval-audit`.
Migration/redirect checks and registry-owner update are in MIGRATION.md.
No kohyr transfer is prepared because a destination was not authorized.

Dataset upload requires named upload/repository approval and an existing accepted
authenticated destination. Prepared command after authorization:
`hf upload alawein/siftgrain-census-faults benchmarks --repo-type dataset`.
Review included files first; native scripts/results and the tiny-data caveats must
travel with the dataset card. No credentials are created or entered by the agent.

The old package identity remains. A new release needs a selected unused version,
version/lock/changelog update, full release checks and explicit scoped release
authorization. No concrete release number is invented here. The existing workflow
is then dispatched by a reviewed signed tag using its trusted publisher; never
overwrite a historical tag or publish current modified bytes as the old release.

Shared tokens are private and unpublished. No `npm publish` is planned. Pages
publication, if separately authorized for the reviewed source, uses
`gh workflow run pages.yml --repo alawein/eval-audit --ref main` after landing and
fresh source verification. This document is preparation, not deployment evidence.

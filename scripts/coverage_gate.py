"""CLI entry for composite Actions and pre-commit; no inferred population."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eval_audit.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())

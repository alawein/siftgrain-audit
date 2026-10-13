"""Enforce portable report gzip budget, offline references and token identity."""

import gzip
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    page = (ROOT / "site/acceptance.html").read_bytes()
    compressed = len(gzip.compress(page, mtime=0))
    if compressed > 32768:
        raise SystemExit(f"report gzip budget exceeded: {compressed} > 32768")
    if (ROOT / "src/eval_audit/tokens.css").read_bytes() != (
        ROOT / "design-tokens/tokens.css"
    ).read_bytes():
        raise SystemExit("runtime token projection differs from vendored owner")
    if b"<script src=" in page or b'<link rel="stylesheet"' in page:
        raise SystemExit("report requires external assets")
    print(f"PASS: self-contained report {compressed} gzip bytes <= 32768; token bytes match")


if __name__ == "__main__":
    main()

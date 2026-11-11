import hashlib
from pathlib import Path

from siftgrain_audit.contract import load_inputs
from siftgrain_audit.core import audit
from siftgrain_audit.report import render_html, render_json


def main() -> None:
    manifest, rows, hashes = load_inputs(
        Path("examples/manifest.json"), Path("examples/results.jsonl")
    )
    report = audit(manifest, rows) | {
        "inputs": hashes,
        "provenance": "Synthetic, non-client",
    }
    target = Path("site")
    target.mkdir(exist_ok=True)
    original_page = render_html(
        report,
        example={
            "synthetic": True,
            "description": (
                "Original synthetic coverage example, executed with the offline audit engine. "
                "CC0 fixtures; no client work or adoption claim."
            ),
            "links": {"Agent Acceptance refund demo": "acceptance.html"},
            "downloads": {
                "Original report JSON": "report.json",
                "Expected-ID manifest": "manifest.json",
                "Result rows": "results.jsonl",
            },
            "download_files": {
                "report.json": render_json(report).encode(),
                "manifest.json": Path("examples/manifest.json").read_bytes(),
                "results.jsonl": Path("examples/results.jsonl").read_bytes(),
            },
        },
    )
    (target / "index.html").write_text(original_page, encoding="utf-8")
    (target / "report.json").write_text(render_json(report), encoding="utf-8")

    manifest, rows, hashes = load_inputs(
        Path("examples/acceptance-manifest.json"), Path("examples/acceptance-results.jsonl")
    )
    report = audit(manifest, rows) | {
        "inputs": hashes,
        "provenance": "Synthetic, non-client",
    }
    source = Path("examples/acceptance-source.txt").read_bytes()
    report_bytes = render_json(report).encode("utf-8")
    download_files = {
        "acceptance-report.json": report_bytes,
        "acceptance-manifest.json": Path("examples/acceptance-manifest.json").read_bytes(),
        "acceptance-results.jsonl": Path("examples/acceptance-results.jsonl").read_bytes(),
        "acceptance-source.txt": source,
    }
    acceptance_page = render_html(
        report,
        manifest=manifest,
        records=rows,
        example={
            "synthetic": True,
            "title": "Agent Acceptance",
            "description": (
                "Synthetic refund case 1042. This static example was executed with the "
                "offline audit engine. Scores show availability, not task quality. "
                "CC0 fixtures; no client work or adoption claim."
            ),
            "source_text": source.decode("utf-8"),
            "source_sha256": hashlib.sha256(source).hexdigest(),
            "links": {"Original coverage example": "index.html"},
            "downloads": {
                "Report JSON": "acceptance-report.json",
                "Expected-ID manifest": "acceptance-manifest.json",
                "Result records": "acceptance-results.jsonl",
                "Supplied source": "acceptance-source.txt",
            },
            "download_files": download_files,
        },
    )
    (target / "acceptance.html").write_text(acceptance_page, encoding="utf-8")
    for name, payload in download_files.items():
        (target / name).write_bytes(payload)


if __name__ == "__main__":
    main()

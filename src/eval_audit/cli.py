import argparse
import hashlib
import json
import lzma
import sys
import zipfile
import zlib
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _package_version
from pathlib import Path
from typing import Any

from eval_audit.adapters import bounded_read, convert
from eval_audit.contract import InputError, decode, load_inputs, parse
from eval_audit.core import audit
from eval_audit.output import atomic_write, validate_outputs
from eval_audit.report import render_html, render_json

try:
    __version__ = _package_version("alawein-eval-audit")
except PackageNotFoundError:
    __version__ = "0.3.1"


def convert_main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Convert local per-sample logs; population supplied."
    )
    parser.add_argument("format", choices=["inspect", "lm-evaluation-harness", "promptfoo"])
    parser.add_argument("source", type=Path)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--score-key")
    parser.add_argument(
        "--score-map", type=Path, help="explicit categorical-to-numeric JSON object"
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--html",
        type=Path,
        help="also audit converted records and write an HTML report; exit 1 if work remains",
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        raw_manifest = bounded_read(args.manifest)
        manifest = parse(decode(raw_manifest, "manifest"), "manifest")
        score_map = None
        inputs = [args.source, args.manifest]
        if args.score_map is not None:
            score_map = parse(decode(bounded_read(args.score_map), "score map"), "score map")
            if type(score_map) is not dict:
                raise InputError("score map must be an object")
            inputs.append(args.score_map)
        rows = convert(args.format, manifest, args.source, args.score_key, score_map)
        outputs = [args.output] + ([args.html] if args.html is not None else [])
        validate_outputs(outputs, inputs, args.force)
        content = "".join(
            json.dumps(row, sort_keys=True, allow_nan=False, ensure_ascii=False) + "\n"
            for row in rows
        )
        if len(content.encode("utf-8")) > 5 * 1024 * 1024:
            raise InputError("converted records exceed 5 MiB")
        report: dict[str, Any] | None = None
        html = None
        if args.html is not None:
            report = audit(manifest, rows) | {
                "inputs": {
                    "manifest_sha256": hashlib.sha256(raw_manifest).hexdigest(),
                    "records_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                }
            }
            html = render_html(report)
        atomic_write(args.output, content, args.force)
        if args.html is not None and report is not None and html is not None:
            atomic_write(args.html, html, args.force)
            counts = report["counts"]
            print(
                f"eval-audit: expected {counts['expected']}; missing {counts['missing']}; "
                f"errored {counts['errored']}; unscored {counts['unscored']}; "
                f"exit {report['exit_code']}",
                file=sys.stderr,
            )
            return int(report["exit_code"])
        return 0
    except (
        ValueError,
        OSError,
        zipfile.BadZipFile,
        zlib.error,
        lzma.LZMAError,
        OverflowError,
        RecursionError,
    ) as exc:
        print(f"eval-audit: {exc}", file=sys.stderr)
        return 2


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "convert":
        return convert_main(argv[1:])
    parser = argparse.ArgumentParser(
        description="Audit evaluation result coverage.",
        epilog=(
            "manifest shape: schema_version 1 with run_id and expected_ids; "
            "records are JSONL rows with id, status, score, reason; "
            "see docs/contract.md. "
            "convert inspect|lm-evaluation-harness|promptfoo SOURCE --manifest PATH --output PATH. "
            "example: eval-audit examples/manifest.json examples/results.jsonl. "
            "exit 0 complete scored population; exit 1 work remains; "
            "exit 2 invalid input or I/O."
        ),
    )
    parser.add_argument("manifest", type=Path, help="manifest JSON file")
    parser.add_argument("records", type=Path, help="records JSONL file")
    parser.add_argument("--json", type=Path, help="write the JSON report to PATH")
    parser.add_argument("--html", type=Path, help="write the HTML report to PATH")
    parser.add_argument("--force", action="store_true", help="overwrite existing output files")
    parser.add_argument("--version", action="version", version=f"eval-audit {__version__}")
    args = parser.parse_args(argv)
    try:
        manifest, records, hashes = load_inputs(args.manifest, args.records)
        report: dict[str, Any] = audit(manifest, records) | {"inputs": hashes}
        targets = [(args.json, render_json(report)), (args.html, render_html(report))]
        outputs = [path for path, content in targets if path is not None]
        inputs = [args.manifest, args.records]
        validate_outputs(outputs, inputs, args.force)
        for path, content in targets:
            if path is not None:
                atomic_write(path, content, args.force)
        if args.json is None:
            sys.stdout.write(render_json(report))
        return int(report["exit_code"])
    except (InputError, ValueError, OSError, OverflowError, RecursionError) as exc:
        print(f"eval-audit: {exc}", file=sys.stderr)
        return 2

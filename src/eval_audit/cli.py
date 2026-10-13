import argparse
import json
import lzma
import sys
import zipfile
import zlib
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _package_version
from pathlib import Path
from typing import Any

from eval_audit.adapters import FORMATS, bounded_read, convert
from eval_audit.contract import InputError, decode, load_inputs, parse
from eval_audit.core import audit
from eval_audit.output import atomic_write, validate_outputs
from eval_audit.report import render_html, render_json
from eval_audit.sensitivity import score_sensitivity

try:
    __version__ = _package_version("alawein-eval-audit")
except PackageNotFoundError:
    __version__ = "0.3.1"


def convert_main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Convert local per-sample logs; population supplied."
    )
    parser.add_argument("format", choices=FORMATS)
    parser.add_argument("source", type=Path)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--score-key")
    parser.add_argument(
        "--score-map", type=Path, help="explicit categorical-to-numeric JSON object"
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        manifest = parse(decode(bounded_read(args.manifest), "manifest"), "manifest")
        score_map = None
        inputs = [args.source, args.manifest]
        if args.score_map is not None:
            score_map = parse(decode(bounded_read(args.score_map), "score map"), "score map")
            if type(score_map) is not dict:
                raise InputError("score map must be an object")
            inputs.append(args.score_map)
        rows = convert(args.format, manifest, args.source, args.score_key, score_map)
        validate_outputs([args.output], inputs, args.force)
        content = "".join(
            json.dumps(row, sort_keys=True, allow_nan=False, ensure_ascii=False) + "\n"
            for row in rows
        )
        if len(content.encode("utf-8")) > 5 * 1024 * 1024:
            raise InputError("converted records exceed 5 MiB")
        atomic_write(args.output, content, args.force)
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
    parser.add_argument("--sensitivity", type=Path, help="separate descriptive score-policy JSON")
    parser.add_argument("--rich", action="store_true", help="optional cli extra summary on stderr")
    parser.add_argument("--force", action="store_true", help="overwrite existing output files")
    parser.add_argument("--version", action="version", version=f"eval-audit {__version__}")
    args = parser.parse_args(argv)
    try:
        manifest, records, hashes = load_inputs(args.manifest, args.records)
        report: dict[str, Any] = audit(manifest, records) | {"inputs": hashes}
        if args.rich:
            try:
                from rich.console import Console
            except ImportError as exc:
                raise InputError("--rich requires the optional cli extra") from exc
            Console(stderr=True).print(
                f"Expected: {report['counts']['expected']} | "
                f"Score present: {report['counts']['score_present']} | Exit: {report['exit_code']}"
            )
        targets = [
            (args.json, render_json(report)),
            (args.html, render_html(report, manifest=manifest, records=records)),
        ]
        if args.sensitivity is not None:
            targets.append((args.sensitivity, render_json(score_sensitivity(manifest, records))))
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

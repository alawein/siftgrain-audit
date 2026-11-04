import hashlib
import json
import math
from pathlib import Path
from typing import Any


class InputError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InputError(message)


def text(value: object, limit: int, label: str, nonempty: bool = True) -> None:
    require(
        isinstance(value, str) and len(value) <= limit and (not nonempty or bool(value.strip())),
        f"invalid {label}",
    )


def fields(value: object, keys: set[str], label: str) -> None:
    require(type(value) is dict and set(value) == keys, f"invalid fields: {label}")


def unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def invalid_constant(value: str) -> None:
    raise InputError(f"nonfinite JSON number: {value}")


def decode(raw: bytes, label: str) -> str:
    require(len(raw) <= 5 * 1024 * 1024, f"{label} exceeds 5 MiB")
    require(not raw.startswith(b"\xef\xbb\xbf"), f"{label}: BOM forbidden")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InputError(f"{label}: invalid UTF-8") from exc


def parse(value: str, label: str) -> Any:
    try:
        return json.loads(value, object_pairs_hook=unique_pairs, parse_constant=invalid_constant)
    except (json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise InputError(f"{label}: {exc}") from exc


def trial_mode(manifest: dict) -> bool:
    return manifest.get("schema_version") == 2 or "trials_per_id" in manifest


def trial_plan(manifest: dict) -> dict[str, int]:
    trials = manifest.get("trials_per_id", 1)
    if type(trials) is int:
        require(0 < trials <= 10000, "invalid trials_per_id")
        plan = dict.fromkeys(manifest["expected_ids"], trials)
    else:
        require(type(trials) is dict, "invalid trials_per_id")
        require(set(trials) == set(manifest["expected_ids"]), "trial map must match expected IDs")
        require(
            all(type(v) is int and 0 < v <= 10000 for v in trials.values()), "invalid trials_per_id"
        )
        plan = dict(trials)
    require(sum(plan.values()) <= 10000, "expected trial count exceeds 10000")
    return plan


def validate(manifest: dict, records: list[dict]) -> None:
    keys = {"schema_version", "run_id", "expected_ids"}
    require(
        type(manifest) is dict
        and keys <= set(manifest)
        and set(manifest) <= keys | {"trials_per_id"},
        "invalid fields: manifest",
    )
    require(
        type(manifest["schema_version"]) is int and manifest["schema_version"] in (1, 2),
        "schema_version must be 1 or 2",
    )
    text(manifest["run_id"], 200, "run_id")
    expected = manifest["expected_ids"]
    require(type(expected) is list and 0 < len(expected) <= 10000, "invalid population")
    for identifier in expected:
        text(identifier, 200, "expected ID")
    require(len(set(expected)) == len(expected), "duplicate expected ID")
    trial_plan(manifest)
    require(type(records) is list and len(records) <= 10000, "invalid record count")
    seen = set()
    for index, row in enumerate(records, 1):
        row_keys = {"id", "status", "score", "reason"}
        if trial_mode(manifest):
            require(
                type(row) is dict and row_keys <= set(row) and set(row) <= row_keys | {"trial"},
                f"invalid fields: record {index}",
            )
            require(
                type(row.get("trial", 1)) is int and 0 < row.get("trial", 1) <= 10000,
                f"invalid trial at record {index}",
            )
        else:
            fields(row, row_keys, f"record {index}")
        text(row["id"], 200, f"ID at record {index}")
        key = (row["id"], row.get("trial", 1))
        label = "trial" if trial_mode(manifest) else "ID"
        identity = key if trial_mode(manifest) else row["id"]
        require(key not in seen, f"duplicate record {label} at record {index}: {identity}")
        seen.add(key)
        require(
            row["status"] in ("scored", "errored", "unscored"), f"invalid status at record {index}"
        )
        text(row["reason"], 4000, f"reason at record {index}", nonempty=False)
        score = row["score"]
        require(
            score is None or type(score) is int or (type(score) is float and math.isfinite(score)),
            f"score must be finite or null at record {index}",
        )
        require(
            row["status"] != "scored" or score is not None, f"scored needs score at record {index}"
        )
        require(
            row["status"] != "unscored" or score is None, f"unscored needs null at record {index}"
        )


def load_inputs(manifest_path: Path, records_path: Path) -> tuple[dict, list[dict], dict]:
    def bounded_read(path: Path) -> bytes:
        with path.open("rb") as stream:
            raw = stream.read(5 * 1024 * 1024 + 1)
        require(len(raw) <= 5 * 1024 * 1024, f"{path.name}: exceeds 5 MiB")
        return raw

    raw_manifest = bounded_read(manifest_path)
    raw_records = bounded_read(records_path)
    manifest = parse(decode(raw_manifest, "manifest"), "manifest")
    decoded = decode(raw_records, "records")
    lines = decoded.split("\n") if decoded else []
    if decoded.endswith("\n"):
        lines.pop()
    require(len(lines) <= 10000, "record count exceeds 10000")
    rows = []
    for index, line in enumerate(lines, 1):
        require(bool(line.strip()), f"blank JSONL row {index}")
        rows.append(parse(line, f"record {index}"))
    validate(manifest, rows)
    hashes = {
        "manifest_sha256": hashlib.sha256(raw_manifest).hexdigest(),
        "records_sha256": hashlib.sha256(raw_records).hexdigest(),
    }
    return manifest, rows, hashes

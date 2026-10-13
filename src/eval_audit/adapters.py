"""Narrow, offline mappings of local per-sample framework logs."""

import zipfile
from pathlib import Path

from eval_audit.contract import decode, parse, require, trial_mode, validate

FORMATS = ("inspect", "lm-evaluation-harness", "promptfoo", "helm", "open-llm-leaderboard")


def bounded_read(path: Path) -> bytes:
    with path.open("rb") as stream:
        raw = stream.read(5 * 1024 * 1024 + 1)
    require(len(raw) <= 5 * 1024 * 1024, "source exceeds 5 MiB")
    return raw


def source_rows(format_name: str, source: Path) -> list:
    if format_name == "inspect" and source.suffix == ".eval":
        require(source.stat().st_size <= 5 * 1024 * 1024, "source exceeds 5 MiB")
        with zipfile.ZipFile(source) as archive:
            members = archive.infolist()
            require(
                not any(member.flag_bits & 1 for member in members),
                "encrypted archive members are unsupported",
            )
            require(
                all(
                    member.compress_type
                    in (
                        zipfile.ZIP_STORED,
                        zipfile.ZIP_DEFLATED,
                        zipfile.ZIP_BZIP2,
                        zipfile.ZIP_LZMA,
                    )
                    for member in members
                ),
                "unsupported archive compression",
            )
            require(len(members) <= 20000, "too many archive members")
            require(
                len({member.filename for member in members}) == len(members),
                "duplicate archive member",
            )
            require(
                sum(member.file_size for member in members) <= 5 * 1024 * 1024,
                "expanded archive exceeds 5 MiB",
            )
            return [
                parse(decode(archive.read(member), member.filename), member.filename)
                for member in sorted(members, key=lambda member: member.filename)
                if member.filename.startswith("samples/") and member.filename.endswith(".json")
            ]
    raw = decode(bounded_read(source), "source")
    if format_name == "lm-evaluation-harness":
        lines = raw.split("\n") if raw else []
        if raw.endswith("\n"):
            lines.pop()
        return [parse(line, f"record {index}") for index, line in enumerate(lines, 1)]
    document = parse(raw, "source")
    if format_name in ("helm", "open-llm-leaderboard"):
        require(type(document) is list, "source must be a per-instance JSON array")
        return document
    require(type(document) is dict, "source must be an object")
    if format_name == "inspect":
        rows = document.get("samples")
    else:
        rows = document.get("results")
        if type(rows) is dict:
            require(
                not ("results" in rows and "outputs" in rows),
                "ambiguous promptfoo results/outputs envelopes",
            )
            rows = rows.get("outputs") if "outputs" in rows else rows.get("results")
    if not isinstance(rows, list):
        raise ValueError("source must contain per-sample rows")
    return rows


def convert(
    format_name: str,
    manifest: dict,
    source: Path,
    score_key: str | None = None,
    score_map: dict[str, int | float] | None = None,
) -> list[dict]:
    require(format_name in FORMATS, "unsupported adapter")
    validate(manifest, [])
    require(format_name == "promptfoo" or bool(score_key), "--score-key is required")
    source_records = source_rows(format_name, source)
    require(len(source_records) <= 10000, "record count exceeds 10000")
    rows = []
    for index, sample in enumerate(source_records, 1):
        label = f"record {index}"
        require(type(sample) is dict, f"invalid source {label}")
        error = sample.get("error")
        require(error is None or type(error) in (str, dict), f"invalid error at {label}")
        reason = error.get("message", "") if type(error) is dict else error or ""
        if format_name == "inspect":
            identifier = sample.get("id")
            trial = sample.get("epoch", 1)
            scores = sample.get("scores")
            scores = {} if scores is None else scores
            require(type(scores) is dict, f"invalid scores at {label}")
            require(not scores or score_key in scores, f"missing score key at {label}")
            entry = scores.get(score_key, {})
            require(type(entry) is dict, f"invalid score at {label}")
            score = entry.get("value")
        elif format_name in ("lm-evaluation-harness", "open-llm-leaderboard"):
            identifier, trial, score = sample.get("doc_id"), 1, sample.get(score_key)
        elif format_name == "helm":
            require(
                sample.get("perturbation") is None,
                f"unsupported perturbation at {label}; export original instances separately",
            )
            identifier = sample.get("instance_id")
            trial_index = sample.get("train_trial_index", 0)
            require(type(trial_index) is int and trial_index >= 0, f"invalid trial at {label}")
            trial = trial_index + 1
            stats = sample.get("stats")
            require(type(stats) is list, f"invalid stats at {label}")
            require(
                all(type(stat) is dict and type(stat.get("name")) is dict for stat in stats),
                f"invalid statistic at {label}",
            )
            selected = [stat for stat in stats if stat["name"].get("name") == score_key]
            require(len(selected) <= 1, f"ambiguous score key at {label}")
            require(not stats or bool(selected), f"missing score key at {label}")
            score = selected[0].get("mean") if selected else None
        else:
            test, prompt = sample.get("testIdx"), sample.get("promptIdx")
            require(
                type(test) is int and test >= 0 and type(prompt) is int and prompt >= 0,
                f"invalid testIdx/promptIdx at {label}",
            )
            identifier, trial, score = (
                f"{test}:{prompt}",
                sample.get("trial", 1),
                sample.get("score"),
            )
        if type(score) is str and score_map is not None:
            require(score in score_map, f"unmapped categorical score at {label}")
            score = score_map[score]
        require(type(identifier) in (str, int), f"invalid source ID at {label}")
        require(type(trial) is int and 0 < trial <= 10000, f"invalid trial at {label}")
        require(trial_mode(manifest) or trial == 1, f"trial manifest required at {label}")
        row = {
            "id": str(identifier),
            "status": "errored"
            if error is not None
            else ("scored" if score is not None else "unscored"),
            "score": score,
            "reason": reason,
        }
        if trial_mode(manifest):
            row["trial"] = trial
        rows.append(row)
    validate(manifest, rows)
    return sorted(rows, key=lambda row: (row["id"], row.get("trial", 1)))

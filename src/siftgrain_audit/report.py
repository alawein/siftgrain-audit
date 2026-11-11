import base64
import html
import json

from siftgrain_audit.viewer import enhance


def render_json(report: dict) -> str:
    return json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n"


def _id_list(title: str, values: object) -> str:
    if not isinstance(values, list) or not values:
        return ""
    items = "".join(f"<li>{html.escape(str(v))}</li>" for v in values)
    return f"<h3>{html.escape(title)}</h3><ul>{items}</ul>"


def _links(values: object, *, download: bool = False, files: object = None) -> str:
    if not isinstance(values, dict):
        return ""
    links = []
    for label, destination in values.items():
        # Demo artifacts are sibling files, never executable or external URLs.
        if not isinstance(destination, str) or not destination:
            continue
        if any(character in destination for character in (":", "/", "\\", "?", "#")):
            continue
        href = destination
        attribute = " download" if download else ""
        payload = files.get(destination) if isinstance(files, dict) else None
        if download and isinstance(payload, bytes):
            mime = {
                "json": "application/json",
                "jsonl": "application/x-ndjson",
                "txt": "text/plain",
            }.get(destination.rpartition(".")[2].lower(), "application/octet-stream")
            href = f"data:{mime};base64," + base64.b64encode(payload).decode("ascii")
            attribute = f' download="{html.escape(destination, quote=True)}"'
        links.append(
            f'<li><a href="{html.escape(href, quote=True)}"{attribute}>'
            f"{html.escape(str(label))}</a></li>"
        )
    return '<ul class="links">' + "".join(links) + "</ul>" if links else ""


def _case_cards(report: dict, manifest: dict | None, records: list[dict] | None) -> str:
    if manifest is None or records is None:
        return ""
    trial_mode = report.get("schema_version") == 2
    indexed = {(row["id"], row.get("trial", 1)): row for row in records}
    identities: list[tuple[str, int]] = []
    for identifier in manifest["expected_ids"]:
        plan = manifest.get("trials_per_id", 1) if trial_mode else 1
        total = plan.get(identifier, 1) if isinstance(plan, dict) else plan
        identities.extend((identifier, trial) for trial in range(1, total + 1))
    cases = []
    for identifier, trial in identities:
        row = indexed.get((identifier, trial))
        if row is None:
            status, score, reason = "missing", "No result record", "No JSONL row was supplied."
        else:
            status = row["status"]
            score = "No numeric score" if row["score"] is None else f"Score: {row['score']}"
            reason = row["reason"]
        trial_label = f" / Trial {trial}" if trial_mode else ""
        cases.append(
            '<article class="case"><p class="eyebrow">EXPECTED ID</p>'
            f"<h3>{html.escape(identifier)}{trial_label}</h3>"
            f'<p><span class="status">{html.escape(status)}</span> '
            f'<strong class="score">{html.escape(score)}</strong></p>'
            f"<p>{html.escape(reason)}</p></article>"
        )
    return (
        "<section><h2>Expected records</h2><p>These IDs come from the declared population. "
        "A scored row establishes score availability, not accepted task success.</p>"
        '<div class="cases">' + "".join(cases) + "</div></section>"
    )


def _render_html(
    report: dict,
    *,
    manifest: dict | None = None,
    records: list[dict] | None = None,
    example: dict | None = None,
) -> str:
    example = dict(example or {})
    files = dict(example.get("download_files", {}))
    files.setdefault("report.json", render_json(report).encode("utf-8"))
    example["download_files"] = files
    example.setdefault("downloads", {"Download report JSON": "report.json"})
    content = html.escape(render_json(report))
    title = html.escape(str(example.get("title", "Siftgrain audit")))
    description = html.escape(
        str(example.get("description", "Coverage of supplied records, not model accuracy."))
    )
    counts = report.get("counts", {})
    complete = report.get("exit_code") == 0
    result = "All expected IDs are scored." if complete else "Coverage needs attention."
    action_counts = report.get("trial_counts", counts)
    trial_mode = report.get("schema_version") == 2
    actions = []
    for key, instruction in (
        ("missing", "Find missing trials" if trial_mode else "Find missing rows"),
        ("errored", "Resolve errored trials" if trial_mode else "Resolve evaluation errors"),
        ("unscored", "Score unscored trials" if trial_mode else "Score unscored rows"),
    ):
        if action_counts.get(key, 0):
            actions.append(f"{instruction} ({action_counts[key]})")
    unexpected = len(report.get("unexpected_trials", report.get("unexpected_ids", [])))
    if unexpected:
        actions.append(f"Review unexpected records ({unexpected})")
    next_action = (
        "; ".join(actions) + "."
        if actions
        else "Inspect scores in your evaluation tool; availability does not establish quality."
    )
    first_use = (
        '<section aria-label="Result and next action">'
        "<h2>Are expected evaluation results present?</h2>"
        f"<p><strong>{result}</strong> {next_action}</p>"
        "<p>Invalid input produces exit 2 and no coverage verdict; "
        "fix the reported row or file first.</p>"
        "<h3>Check your own inputs</h3><p>Declare expected IDs independently of the results, "
        "then run locally:</p><pre>uv run siftgrain-audit manifest.json results.jsonl "
        "--html report.html --json report.json</pre></section>"
    )
    label = "Synthetic example" if example.get("synthetic") else "Supplied-input report"
    cards = "".join(
        f'<div class="card"><strong>{html.escape(str(v))}</strong>'
        f"<span>{html.escape(k.replace('_', ' '))}</span></div>"
        for k, v in counts.items()
    )
    coverage = ""
    if report.get("score_present_coverage") is not None:
        percentage = f"{report['score_present_coverage'] * 100:.2f}".rstrip("0").rstrip(".")
        percentage = html.escape(percentage + "%")
        numerator = html.escape(str(counts.get("score_present", "")))
        denominator = html.escape(str(counts.get("expected", "")))
        exit_code = html.escape(str(report.get("exit_code", "")))
        coverage = (
            '<section class="coverage" aria-label="Score availability">'
            f"<div><strong>{percentage}</strong><span>score-present coverage</span></div>"
            f"<p>{numerator} of {denominator} expected IDs have a numeric score. "
            "Availability evidence, not task quality.</p>"
            f'<span class="exit">Exit {exit_code}</span></section>'
        )
    source = ""
    if example.get("source_text") is not None:
        source = (
            "<section><h2>Supplied source</h2><p>Context for the example; the auditor "
            "counts supplied evaluation records and does not judge these claims.</p><pre>"
            + html.escape(str(example["source_text"]))
            + '</pre><p>Source SHA-256</p><code class="hash">'
            + html.escape(str(example.get("source_sha256", "")))
            + "</code><p>This separate digest covers the downloaded source bytes.</p></section>"
        )
    provenance = ""
    if report.get("provenance") is not None:
        provenance = "<p><strong>Provenance:</strong> " + html.escape(str(report["provenance"]))
        provenance += "</p>"
    hashes = "".join(
        f"<dt>{html.escape(key.replace('_', ' '))}</dt>"
        f'<dd><code class="hash">{html.escape(str(value))}</code></dd>'
        for key, value in report.get("inputs", {}).items()
    )
    downloads = _links(example.get("downloads"), download=True, files=example.get("download_files"))
    evidence = (
        "<section><h2>Provenance and files</h2>"
        + provenance
        + (f'<dl class="hashes">{hashes}</dl>' if hashes else "")
        + "<p>Input SHA-256 hashes cover the exact manifest and results bytes. "
        "Hashes bind bytes, not authenticity.</p>" + downloads + "</section>"
    )
    how_to = (
        "<section><h2>How to read this report</h2>"
        "<ul>"
        "<li>Missing lists expected IDs with no record; Unexpected lists records "
        "outside the expected population and never inflates counts.</li>"
        "<li>Errored records failed during evaluation; a retained partial score "
        "does not change their error status. Those IDs are listed separately.</li>"
        "<li>Unscored records have no numeric score. Score-present coverage counts "
        "scored plus errored-with-score over the expected population size: "
        "availability, not accuracy or task quality. Zero is a present score.</li>"
        "<li>Exit codes: 0 means a complete scored population; 1 means missing, "
        "unexpected, errored, or unscored work remains; 2 means invalid input or "
        "I/O. This report: "
        f"{html.escape(str(report.get('exit_code', '')))}.</li>"
        "</ul>"
        + _id_list("Missing IDs", report.get("missing_ids"))
        + _id_list("Unexpected IDs", report.get("unexpected_ids"))
        + _id_list("Errored with score", report.get("errored_with_score_ids"))
        + "</section>"
    )
    if report.get("schema_version") == 2:
        how_to += (
            "<h2>Trial coverage</h2><p>ID status precedence is missing, errored, unscored, "
            "scored. Complete IDs have all planned trials delivered. Trial availability "
            "includes errored-with-score; ID availability needs a number on every trial. "
            "Pass@k and pass^k readiness counts require all first k trials explicitly "
            "scored. These counts are not success rates.</p>"
            + _id_list("Missing trials", report.get("missing_trials"))
            + _id_list("Unexpected trials", report.get("unexpected_trials"))
            + _id_list("Complete IDs", report.get("complete_ids"))
        )
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="description" content="Coverage of supplied evaluation records: '
        'scored, errored, unscored, missing and unexpected, with input hashes.">'
        '<meta name="theme-color" content="#101c1b">'
        f"<title>{title} | Siftgrain Audit coverage report</title><style>"
        ":root{color-scheme:dark}"
        "body{--bg:#101c1b;--surface:#1a2e2b;--text:#edf5f2;--border:#78988e;"
        "--link:#98e1cd;color-scheme:dark}"
        "body:has(#theme-light:checked){--bg:#f4f6f5;--surface:#fff;--text:#142c2a;"
        "--border:#718b82;--link:#075851;color-scheme:light}"
        "body{margin:0;background:var(--bg);color:var(--text);font:17px/1.6 system-ui;"
        "-webkit-tap-highlight-color:transparent}"
        "*{box-sizing:border-box}main{max-width:1120px;margin:auto;padding:36px 24px}"
        "h1{font-size:clamp(2.4rem,5vw,3.7rem);line-height:1.1;margin:12px 0;"
        "text-wrap:balance}h2,h3{text-wrap:balance}h3{margin:8px 0;overflow-wrap:anywhere}"
        "section{margin-top:36px}.run{overflow-wrap:anywhere;font-size:.9rem}"
        ".eyebrow{letter-spacing:.12em;font-size:.85rem}"
        ".cards{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:12px;"
        "margin-top:24px}.card{background:var(--surface);border:1px solid var(--border);"
        "border-radius:12px;padding:16px;min-width:0}"
        ".card strong{display:block;font-size:2rem;font-variant-numeric:tabular-nums}"
        ".card span{display:block}"
        ".coverage{display:flex;align-items:center;gap:24px;padding:24px;border-radius:12px;"
        "background:#142c2a;color:#fff;flex-wrap:wrap}.coverage strong{display:block;"
        "font-size:2.8rem;line-height:1.2}.coverage p{flex:1 1 280px;margin:0}"
        ".coverage span{display:block}.exit{border:1px solid #9bbcb1;border-radius:6px;"
        "padding:6px 12px;white-space:nowrap}.cases{display:grid;"
        "grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}"
        ".case{padding:20px;border:1px solid var(--border);background:var(--surface);"
        "border-radius:12px;min-width:0;overflow-wrap:anywhere}.case .eyebrow{margin:0}"
        ".status{display:inline-block;border:1px solid var(--border);border-radius:6px;"
        "padding:2px 8px;margin-right:8px}.score{font-size:.95rem}"
        "pre{background:var(--surface);padding:20px;border:1px solid var(--border);"
        "white-space:pre-wrap;overflow-wrap:anywhere;border-radius:8px;font-size:.9rem}"
        ".hash{overflow-wrap:anywhere;font-size:.85rem}.hashes{display:grid;"
        "grid-template-columns:180px minmax(0,1fr);gap:12px}.hashes dd{margin:0}"
        ".links{display:flex;gap:12px;flex-wrap:wrap;list-style:none;padding:0}"
        ".links a{display:inline-flex;align-items:center;min-height:44px;padding:8px 14px;"
        "background:var(--surface);border:1px solid var(--border);border-radius:8px}"
        "summary{cursor:pointer;padding:12px 0;min-height:44px}footer{margin-top:36px}"
        "a{color:var(--link)}a:hover{text-decoration:underline}"
        ".appearance input:focus,:focus-visible{outline:3px solid var(--link);outline-offset:3px}"
        ".suite-nav{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px}"
        ".suite-nav a{display:inline-flex;align-items:center;min-height:44px;padding:8px 14px;"
        "border:1px solid var(--border);border-radius:8px}"
        ".suite-nav [aria-current]{font-weight:700;text-decoration-thickness:3px}"
        ".appearance{display:flex;flex-wrap:wrap;align-items:center;gap:0 8px;"
        "width:fit-content;max-width:100%;margin:0 0 20px;padding:0 12px;"
        "border:1px solid var(--border);border-radius:8px}"
        ".appearance legend{padding:0 4px;font-size:.85rem}"
        ".appearance label{display:inline-flex;align-items:center;min-height:44px;"
        "padding:0 8px;cursor:pointer}.appearance input{accent-color:var(--link)}"
        "@media(max-width:700px){main{padding:24px 18px}.cards{grid-template-columns:"
        "repeat(2,minmax(0,1fr))}.cases{grid-template-columns:minmax(0,1fr)}"
        ".coverage{gap:16px;padding:20px}.hashes{grid-template-columns:minmax(0,1fr);"
        "gap:6px}.hashes dd{margin-bottom:12px}}"
        '</style></head><body><main id="top" tabindex="-1">'
        '<nav class="suite-nav" aria-label="Siftgrain tools">'
        '<a tabindex="0" href="#top" aria-current="page">Audit</a>'
        '<a tabindex="0" href="https://alawein.github.io/siftgrain-state/">State</a>'
        '<a tabindex="0" href="https://alawein.github.io/siftgrain-cite/">Cite</a></nav>'
        '<fieldset class="appearance"><legend>Appearance</legend>'
        '<input type="radio" name="appearance" id="theme-dark" checked>'
        '<label for="theme-dark">Dark</label>'
        '<input type="radio" name="appearance" id="theme-light">'
        '<label for="theme-light">Light</label></fieldset>'
        '<p class="eyebrow">SIFTGRAIN AUDIT / LOCAL EVIDENCE / '
        "EXPLICIT POPULATION</p>"
        f"<h1>{title}</h1><p>{label}</p><p>{description}</p>"
        f'<p class="run">Run: <code>{html.escape(str(report.get("run_id", "")))}</code></p>'
        + _links(example.get("links"))
        + first_use
        + '<div class="cards">'
        + cards
        + "</div>"
        + coverage
        + '<details class="evidence-details"><summary>'
        "Record explanations, source and provenance</summary>"
        + _case_cards(report, manifest, records)
        + source
        + how_to
        + evidence
        + "</details>"
        + "<section><h2>Inspectable report</h2><details><summary>Expand JSON report</summary><pre>"
        + content
        + "</pre></details></section>"
        '<footer><a href="https://github.com/alawein/siftgrain-audit">Source and installation</a>'
        "</footer></main></body></html>"
    )


def render_html(
    report: dict,
    *,
    manifest: dict | None = None,
    records: list[dict] | None = None,
    example: dict | None = None,
) -> str:
    return enhance(
        _render_html(report, manifest=manifest, records=records, example=example), manifest, records
    )

"""Trusted viewer assets and server-rendered trial evidence."""

import base64
import hashlib
import html
from importlib.resources import files

from eval_audit.contract import trial_plan
from eval_audit.sensitivity import score_sensitivity


def trial_view(manifest: dict | None, records: list[dict] | None) -> str:
    if manifest is None or records is None:
        return "<p>Trial details require the supplied manifest and records.</p>"
    indexed = {(row["id"], row.get("trial", 1)): row for row in records}
    cells, table = [], []
    for identifier, total in sorted(trial_plan(manifest).items()):
        strip = []
        for trial in range(1, total + 1):
            row = indexed.get((identifier, trial))
            status = row["status"] if row else "missing"
            score = str(row["score"]) if row and row["score"] is not None else "No numeric score"
            reason = row["reason"] if row else "No JSONL row was supplied."
            label = html.escape(f"{identifier}, Trial {trial}: {status}; {score}", quote=True)
            strip.append(
                f'<span class="trial-cell {status}" data-status="{status}" '
                f'role="img" aria-label="{label}" title="{label}"></span>'
            )
            table.append(
                f'<tr data-status="{status}"><th scope="row">{html.escape(identifier)}'
                f"</th><td>Trial {trial}</td><td>{status}</td><td>{html.escape(score)}</td>"
                f"<td>{html.escape(reason)}</td></tr>"
            )
        cells.append(
            f'<div class="trial-strip"><strong>{html.escape(identifier)}</strong>'
            '<div class="waffle">' + "".join(strip) + "</div></div>"
        )
    sensitivity = score_sensitivity(manifest, records)
    policies = "".join(
        f'<tr><th scope="row">{html.escape(name.replace("_", " "))}</th>'
        f"<td>{policy['denominator']}</td><td>{policy['sum']}</td>"
        f"<td>{policy['mean'] if policy['mean'] is not None else 'Undefined'}</td>"
        "</tr>"
        for name, policy in sensitivity["policies"].items()
    )
    return (
        '<section aria-labelledby="trial-title"><h2 id="trial-title">Every planned trial</h2>'
        "<p>Solid cells are scored. Crosses are errors. Dashed cells are missing. "
        'Missing cells remain in the expected population.</p><div class="strips">'
        + "".join(cells)
        + '</div><label for="status-filter">Filter trial table</label> '
        '<select id="status-filter"><option value="all">All states</option>'
        "<option>missing</option><option>errored</option><option>unscored</option>"
        '<option>scored</option></select><p id="filter-status" role="status"></p>'
        '<div class="table-scroll"><table id="trial-table"><caption>Expected trials</caption>'
        '<thead><tr><th scope="col">ID</th><th scope="col">Trial</th>'
        '<th scope="col">State</th><th scope="col">Score</th>'
        '<th scope="col">Reason</th></tr></thead><tbody>'
        + "".join(table)
        + "</tbody></table></div></section><section><h2>Score sensitivity</h2>"
        "<p>A separate descriptive policy view. Missing values are zero only in zero-fill. "
        "Errored scores contribute to availability and zero-fill, never scored-only. "
        "Means are exact rational strings, not pass@k or pass^k rates. "
        "Scores need not measure correctness or be comparable.</p>"
        '<div class="table-scroll"><table><caption>Supplied score arithmetic by policy</caption>'
        '<thead><tr><th scope="col">Policy</th><th scope="col">Denominator</th>'
        '<th scope="col">Sum</th><th scope="col">Mean</th></tr></thead><tbody>'
        + policies
        + "</tbody></table></div></section>"
    )


def enhance(page: str, manifest: dict | None, records: list[dict] | None) -> str:
    css = files("eval_audit").joinpath("tokens.css").read_text(encoding="utf-8")
    css += files("eval_audit").joinpath("viewer.css").read_text(encoding="utf-8")
    js = files("eval_audit").joinpath("viewer.js").read_text(encoding="utf-8")
    # These assets are authored code, never imported user content.
    script_hash = base64.b64encode(hashlib.sha256(js.encode()).digest()).decode()
    policy = (
        "default-src 'none'; connect-src 'none'; img-src data:; style-src 'unsafe-inline'; "
        f"script-src 'sha256-{script_hash}'; worker-src blob:; base-uri 'none'; form-action 'none';"
    )
    head = f'<meta http-equiv="Content-Security-Policy" content="{policy}">'
    head += f"<style>{css}</style><script data-census-viewer>{js}</script>"
    controls = (
        '<a class="skip" href="#evidence">Skip to evidence</a><nav aria-label="Viewer">'
        '<span class="product">Siftgrain Audit <small>evaluation completeness</small></span>'
        '<label for="appearance">Appearance</label><select id="appearance">'
        '<option value="dark">Dark</option><option value="light">Light</option></select>'
        '<label for="vibe">Vibe</label><select id="vibe"><option value="cartoon">'
        'Cartoon</option><option value="calm">Calm</option><option value="pixel">Pixel'
        '</option><option value="lab">Lab</option></select>'
        '<button id="motion" type="button" aria-pressed="false">'
        "Enable background motion</button></nav>"
    )
    page = page.replace("</head>", head + "</head>")
    page = page.replace(
        "<body><main>",
        "<body>" + controls + '<main id="evidence">'
        '<canvas id="field" width="960" height="100" aria-hidden="true"></canvas>',
    )
    anchor = '<details class="evidence-details">'
    return page.replace(anchor, trial_view(manifest, records) + anchor, 1)

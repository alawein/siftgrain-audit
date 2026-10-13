from eval_audit.core import audit
from eval_audit.report import render_html


def test_report_keeps_every_planned_trial_and_safe_text():
    manifest = {
        "schema_version": 2,
        "run_id": "r",
        "expected_ids": ["<unsafe>"],
        "trials_per_id": 3,
    }
    rows = [
        {"id": "<unsafe>", "trial": 2, "status": "errored", "score": 0, "reason": "<img src=x>"}
    ]
    page = render_html(audit(manifest, rows), manifest=manifest, records=rows)
    assert page.count('class="trial-cell ') == 3
    assert page.count('data-status="missing"') >= 2
    assert "Trial 2" in page and "errored" in page
    assert "<unsafe>" not in page and "<img src=x>" not in page
    assert 'id="status-filter"' in page
    assert 'id="vibe"' in page and "Cartoon" in page and "Calm" in page
    assert "Pixel" in page and "Lab" in page
    assert "Siftgrain Audit" in page and "Siftgrain Census" not in page
    assert "https://github.com/alawein/siftgrain-audit" in page
    assert "Content-Security-Policy" in page and "connect-src 'none'" in page
    assert "prefers-reduced-motion" in page


def test_report_without_inputs_does_not_invent_trial_states():
    manifest = {"schema_version": 1, "run_id": "r", "expected_ids": ["a"]}
    page = render_html(audit(manifest, []))
    assert "Trial details require the supplied manifest and records" in page

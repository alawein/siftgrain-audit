import json

import pytest

from siftgrain_audit.report import render_json


def test_renderer_deterministic_ascii_and_final_newline():
    report = {"z": "Arabic عربي", "a": "<script>"}
    rendered = render_json(report)
    assert rendered == render_json(dict(reversed(list(report.items()))))
    assert rendered.isascii()
    assert rendered.endswith("\n") and not rendered.endswith("\n\n")
    assert json.loads(rendered) == report


@pytest.mark.parametrize("number", [float("nan"), float("inf"), -float("inf")])
def test_renderer_rejects_nonfinite_numbers(number):
    with pytest.raises(ValueError):
        render_json({"score": number})

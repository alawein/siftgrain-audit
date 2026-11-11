import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError
from test_audit import manifest, row

from siftgrain_audit.core import audit


def validator(name):
    root = Path(__file__).resolve().parents[1]
    return Draft202012Validator(json.loads((root / "schema" / f"{name}.v1.json").read_text()))


@pytest.mark.parametrize(
    "packet",
    [
        row(score=True),
        row("scored", None),
        row("unscored", 1),
        row() | {"trial": 0},
        row() | {"extra": 1},
    ],
)
def test_record_schema_rejects_bad_shapes(packet):
    with pytest.raises(ValidationError):
        validator("result-record").validate(packet)


def test_legacy_and_extended_reports_validate():
    for population in (manifest(), manifest() | {"schema_version": 2, "trials_per_id": 2}):
        validator("manifest").validate(population)
        result = audit(population, [row()])
        validator("report").validate(result)
        del result["score_present_coverage"]
        with pytest.raises(ValidationError):
            validator("report").validate(result)


def test_version_one_report_cannot_smuggle_trial_extensions():
    with pytest.raises(ValidationError):
        validator("report").validate(audit(manifest(), [row()]) | {"complete_ids": ["a"]})

import pytest

from siftgrain_audit.cli import main


def test_help(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    assert "manifest" in capsys.readouterr().out

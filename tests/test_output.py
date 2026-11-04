import os
import tempfile

import pytest

from siftgrain_audit.output import atomic_write


def test_force_replace_failure_keeps_old_file(tmp_path, monkeypatch):
    target = tmp_path / "out.json"
    target.write_text("KEEP", encoding="utf-8")

    def fail(*args):
        raise OSError("injected replacement failure")

    monkeypatch.setattr(os, "replace", fail)
    with pytest.raises(OSError):
        atomic_write(target, "NEW", True)
    assert target.read_text() == "KEEP"
    assert list(tmp_path.iterdir()) == [target]


def test_creation_race_preserves_new_target(tmp_path, monkeypatch):
    target = tmp_path / "out.json"
    real_link = os.link

    def raced(source, dest):
        target.write_text("OTHER", encoding="utf-8")
        return real_link(source, dest)

    monkeypatch.setattr(os, "link", raced)
    with pytest.raises(FileExistsError):
        atomic_write(target, "NEW", False)
    assert target.read_text() == "OTHER"
    assert list(tmp_path.iterdir()) == [target]


def test_temporary_file_is_in_target_directory(tmp_path, monkeypatch):
    target = tmp_path / "out.json"
    real_replace = os.replace

    def checked(source, dest):
        assert source.parent == target.parent
        real_replace(source, dest)

    monkeypatch.setattr(os, "replace", checked)
    atomic_write(target, "hello\n", True)
    assert target.read_bytes() == b"hello\n"


def test_staging_write_failure_preserves_existing_bytes(tmp_path, monkeypatch):
    target = tmp_path / "out.json"
    target.write_text("KEEP", encoding="utf-8")
    original = tempfile.NamedTemporaryFile

    class FailedWriter:
        def __init__(self, *args, **kwargs):
            self.stream = original(*args, **kwargs)
            self.name = self.stream.name

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.stream.close()

        def write(self, content):
            self.stream.write("partial")
            raise OSError("injected stage write failure")

    monkeypatch.setattr(tempfile, "NamedTemporaryFile", FailedWriter)
    with pytest.raises(OSError):
        atomic_write(target, "NEW", True)
    assert target.read_text() == "KEEP"
    assert list(tmp_path.iterdir()) == [target]

import hashlib
import importlib.util
import io
import json
import sys
import tarfile
import zipfile
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "release_verifier", Path(__file__).parents[1] / "scripts/verify_release_artifacts.py"
)
assert spec and spec.loader
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


def artifacts(tmp_path, name="siftgrain-audit", version="0.3.1"):
    directory = tmp_path / "dist"
    directory.mkdir()
    stem = name.replace("-", "_") + "-" + version
    metadata = f"Name: {name}\nVersion: {version}\n".encode()
    with zipfile.ZipFile(directory / (stem + "-py3-none-any.whl"), "w") as archive:
        archive.writestr(stem + ".dist-info/METADATA", metadata)
    with tarfile.open(directory / (stem + ".tar.gz"), "w:gz") as archive:
        member = tarfile.TarInfo(stem + "/PKG-INFO")
        member.size = len(metadata)
        archive.addfile(member, io.BytesIO(metadata))
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.iterdir()}
    manifest = tmp_path / "inventory.json"
    manifest.write_text(json.dumps({"name": name, "version": version, "sha256": hashes}))
    manifest.with_name("SHA256SUMS").write_bytes(
        "".join(f"{digest}  {filename}\n" for filename, digest in sorted(hashes.items())).encode(
            "ascii"
        )
    )
    return directory, manifest


def test_exact_inventory_and_metadata(tmp_path):
    directory, manifest = artifacts(tmp_path)
    assert len(verifier.verify(directory, manifest, "siftgrain-audit", "0.3.1")) == 2


def test_create_checksum_inventory_has_exact_lf_bytes(tmp_path, monkeypatch):
    directory, manifest = artifacts(tmp_path)
    monkeypatch.chdir(Path(__file__).parents[1])
    monkeypatch.setattr(
        sys,
        "argv",
        ["verify_release_artifacts.py", str(directory), "--manifest", str(manifest), "--create"],
    )
    verifier.main()
    assert b"\r" not in manifest.with_name("SHA256SUMS").read_bytes()
    assert len(verifier.verify(directory, manifest, "siftgrain-audit", "0.3.1")) == 2


@pytest.mark.parametrize(
    "mutation",
    ["missing", "extra", "bytes", "checksum", "metadata", "missing_sums", "changed_sums"],
)
def test_modified_distribution_fails(tmp_path, mutation):
    directory, manifest = artifacts(tmp_path)
    wheel = next(directory.glob("*.whl"))
    if mutation == "missing":
        wheel.unlink()
    elif mutation == "extra":
        (directory / "SHA256SUMS").write_text("unwanted")
    elif mutation == "bytes":
        wheel.write_bytes(wheel.read_bytes() + b"changed")
    elif mutation == "checksum":
        data = json.loads(manifest.read_text())
        data["sha256"][wheel.name] = "0" * 64
        manifest.write_text(json.dumps(data))
    elif mutation == "missing_sums":
        manifest.with_name("SHA256SUMS").unlink()
    elif mutation == "changed_sums":
        manifest.with_name("SHA256SUMS").write_bytes(b"wrong checksum inventory\n")
    else:
        with zipfile.ZipFile(wheel, "w") as archive:
            archive.writestr("x.dist-info/METADATA", "Name: wrong\nVersion: 0.3.1\n")
    with pytest.raises(ValueError):
        verifier.verify(directory, manifest, "siftgrain-audit", "0.3.1")

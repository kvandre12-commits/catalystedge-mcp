"""Build and verify the deterministic CatalystEdge marketplace ZIP."""

from __future__ import annotations

import hashlib
import stat
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "marketplace" / "catalystedge"
DIST = ROOT / "dist"
ARCHIVE = DIST / "catalystedge-0.1.1.zip"
MEMBERS = ("SKILL.md", "LICENSE")
FIXED_TIMESTAMP = (2026, 1, 1, 0, 0, 0)


def validate_source() -> None:
    actual = {path.name for path in SOURCE.iterdir()}
    if actual != set(MEMBERS):
        raise ValueError(f"package must contain exactly {MEMBERS}; found {sorted(actual)}")
    for name in MEMBERS:
        path = SOURCE / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"{name} must be a regular file")
        path.read_text(encoding="utf-8")
    skill = (SOURCE / "SKILL.md").read_text(encoding="utf-8")
    if not skill.startswith("---\nname: catalystedge\n"):
        raise ValueError("SKILL.md frontmatter name must match catalystedge directory")
    if "description:" not in skill.split("---", 2)[1]:
        raise ValueError("SKILL.md requires a frontmatter description")


def build() -> str:
    validate_source()
    DIST.mkdir(exist_ok=True)
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for name in MEMBERS:
            info = zipfile.ZipInfo(f"catalystedge/{name}", FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            bundle.writestr(info, (SOURCE / name).read_bytes())
    verify_archive()
    digest = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    (DIST / "SHA256SUMS").write_text(
        f"{digest}  {ARCHIVE.name}\n",
        encoding="utf-8",
    )
    return digest


def verify_archive() -> None:
    expected = [f"catalystedge/{name}" for name in MEMBERS]
    with zipfile.ZipFile(ARCHIVE) as bundle:
        if bundle.testzip() is not None:
            raise ValueError("ZIP integrity check failed")
        if bundle.namelist() != expected:
            raise ValueError(f"unexpected archive members: {bundle.namelist()}")
        for info, name in zip(bundle.infolist(), MEMBERS, strict=True):
            path = PurePosixPath(info.filename)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError(f"unsafe ZIP path: {info.filename}")
            if stat.S_IMODE(info.external_attr >> 16) != 0o644:
                raise ValueError(f"unsafe mode for {info.filename}")
            if bundle.read(info) != (SOURCE / name).read_bytes():
                raise ValueError(f"archive content differs from source: {name}")


if __name__ == "__main__":
    sha256 = build()
    print(f"{ARCHIVE} sha256={sha256}")

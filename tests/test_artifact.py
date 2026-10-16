import hashlib
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "dist" / "catalystedge-0.1.1.zip"


def test_marketplace_artifact_is_deterministic_and_minimal():
    command = [sys.executable, str(ROOT / "scripts" / "build_skill.py")]
    subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
    first = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
    second = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    assert first == second
    with zipfile.ZipFile(ARCHIVE) as bundle:
        assert bundle.namelist() == [
            "catalystedge/SKILL.md",
            "catalystedge/LICENSE",
        ]

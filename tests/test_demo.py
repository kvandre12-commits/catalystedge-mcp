import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_demo_runs_without_network_or_key():
    completed = subprocess.run(
        [sys.executable, str(ROOT / "examples" / "demo.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)
    assert result["event"]["decision"] == "event_window_active"
    assert result["level"]["state"] == "confirmed"
    assert result["level"]["trade_permission"] is False

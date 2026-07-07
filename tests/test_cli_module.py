from __future__ import annotations

import subprocess
import sys


def test_python_module_cli_help_runs():
    completed = subprocess.run(
        [sys.executable, "-m", "worldguard", "--help"],
        text=True,
        capture_output=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "mesh-check" in completed.stdout
    assert "check" in completed.stdout

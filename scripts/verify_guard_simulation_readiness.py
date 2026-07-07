from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOME_SKILLS = Path.home() / ".codex" / "skills"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(args: list[str], cwd: Path) -> dict[str, object]:
    completed = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    return {
        "args": args,
        "cwd": str(cwd),
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def _check_version() -> dict[str, object]:
    module = importlib.import_module("worldguard")
    module_path = Path(module.__file__).resolve()
    metadata_version = importlib.metadata.version("worldguard")
    ok = (
        metadata_version == "0.1.2"
        and getattr(module, "__version__", "") == "0.1.2"
        and "WorldGurd_20260613" in str(module_path)
    )
    return {
        "check": "version_import_path",
        "ok": ok,
        "metadata_version": metadata_version,
        "module_version": getattr(module, "__version__", None),
        "module_path": str(module_path),
    }


def _check_skillguard() -> dict[str, object]:
    skill_dir = ROOT / "skills" / "worldguard"
    checks = [
        "check_route.py",
        "check_phase_order.py",
        "check_evidence.py",
        "check_quality_floor.py",
        "check_closure.py",
    ]
    runs = [_run([sys.executable, f".skillguard/checks/{check}"], skill_dir) for check in checks]
    return {"check": "source_skillguard", "ok": all(run["exit_code"] == 0 for run in runs), "runs": runs}


def _check_installed_sync() -> dict[str, object]:
    pairs = [
        (ROOT / "skills" / "worldguard" / "SKILL.md", HOME_SKILLS / "worldguard" / "SKILL.md"),
        (
            ROOT / "skills" / "worldguard" / ".skillguard" / "work-contract.json",
            HOME_SKILLS / "worldguard" / ".skillguard" / "work-contract.json",
        ),
    ]
    rows = []
    for source, installed in pairs:
        rows.append(
            {
                "source": str(source),
                "installed": str(installed),
                "ok": source.exists() and installed.exists() and _sha256(source) == _sha256(installed),
            }
        )
    return {"check": "installed_skill_sync", "ok": all(row["ok"] for row in rows), "rows": rows}


def main() -> int:
    checks = [_check_version(), _check_skillguard(), _check_installed_sync()]
    ok = all(check["ok"] for check in checks)
    print(json.dumps({"ok": ok, "checks": checks}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Verify WorldGuard's current generic SkillGuard declared-check supervision.

The historical filename is retained for callers, but optional profile and
SkillGuard-owned calibration semantics are intentionally absent.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "worldguard"
CONTROL_ROOT = SKILL_ROOT / ".skillguard"


def _skillguard_scripts(explicit: str = "") -> Path:
    candidates = [
        Path(explicit) if explicit else None,
        Path(os.environ["SKILLGUARD_SCRIPTS"]) if os.environ.get("SKILLGUARD_SCRIPTS") else None,
        Path.home() / ".codex" / "skills" / "skillguard" / "scripts",
        ROOT.parent / "SkillGuard" / ".agents" / "skills" / "skillguard" / "scripts",
    ]
    for candidate in candidates:
        if candidate is not None and (candidate / "skillguard_v2").is_dir():
            return candidate.resolve()
    raise FileNotFoundError("current generic SkillGuard scripts were not found")


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skillguard-scripts", default="")
    args = parser.parse_args(argv)
    scripts = _skillguard_scripts(args.skillguard_scripts)
    sys.path.insert(0, str(scripts))

    from skillguard_v2.contract_compiler import compile_skill_contract  # noqa: PLC0415

    source = _load(CONTROL_ROOT / "contract-source.json")
    compiled = _load(CONTROL_ROOT / "compiled-contract.json")
    manifest = _load(CONTROL_ROOT / "check-manifest.json")
    profile = source.get("depth_profile", {})
    closure_profiles = source.get("closure_profiles", [])
    source_check_ids = {
        str(row.get("check_id", ""))
        for row in source.get("checks", [])
        if isinstance(row, dict)
    }
    manifest_check_ids = {
        str(row.get("check_id", ""))
        for row in manifest.get("checks", [])
        if isinstance(row, dict)
    }

    failures: list[str] = []
    if profile.get("integration_mode") != "native-integrated":
        failures.append("integration_mode_not_native_integrated")
    if profile.get("enforcement_level") != "enforced":
        failures.append("enforcement_level_not_enforced")
    if profile.get("required_closure_profiles") != ["enforced"]:
        failures.append("depth_profile_not_single_enforced")
    if [row.get("profile_id") for row in closure_profiles if isinstance(row, dict)] != ["enforced"]:
        failures.append("contract_not_single_enforced")
    for forbidden in ("calibration", "coverage_universes", "dimensions"):
        if forbidden in source or forbidden in profile:
            failures.append(f"forbidden_generic_field:{forbidden}")
    if any("calibration" in check_id for check_id in source_check_ids):
        failures.append("optional_calibration_check_declared")
    if source.get("integration_mode") != "native-integrated":
        failures.append("top_level_integration_mode_not_native_integrated")
    if source.get("native_route_owner") != "worldguard":
        failures.append("top_level_native_route_owner_missing")
    if source.get("default_route_id") != "route:worldguard-claim-derived-depth":
        failures.append("top_level_default_route_missing")
    route_bindings = source.get("native_route_bindings", [])
    check_bindings = source.get("native_check_bindings", [])
    if {
        row.get("native_route_id") for row in route_bindings if isinstance(row, dict)
    } != set(profile.get("native_route_ids", [])):
        failures.append("top_level_native_route_bindings_incomplete")
    if {
        row.get("native_check_id") for row in check_bindings if isinstance(row, dict)
    } != set(profile.get("native_check_ids", [])):
        failures.append("top_level_native_check_bindings_incomplete")
    required_checks = {
        "check:worldguard:flowguard-contract-model",
        "check:worldguard:guard-model-contract",
        "check:worldguard:native-depth",
    }
    if not required_checks.issubset(source_check_ids & manifest_check_ids):
        failures.append("required_declared_check_missing")

    compile_result = compile_skill_contract(
        SKILL_ROOT,
        repository_root=ROOT,
        write=False,
    )
    if not compile_result.ok:
        failures.extend(f"compile:{finding.code}" for finding in compile_result.findings)

    guard_check = subprocess.run(
        [sys.executable, str(CONTROL_ROOT / "checks" / "check_guard_model_contract.py")],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if guard_check.returncode != 0:
        failures.append("target_native_guard_model_check_failed")

    from worldguard.execution_depth import build_native_depth_evidence  # noqa: PLC0415

    target_regressions = []
    fixtures = ROOT / "tests" / "fixtures" / "skillguard_depth"
    for case_id, fixture, expected_status in (
        ("deep", "deep.json", "EXECUTION_DEPTH_PASS"),
        ("shallow", "shallow.json", "SHALLOW_BLOCKED"),
        ("concentrated", "concentrated.json", "SHALLOW_BLOCKED"),
    ):
        evidence = build_native_depth_evidence(fixtures / fixture)
        observed = str(evidence.get("status", ""))
        if observed != expected_status:
            failures.append(f"target_native_depth_regression:{case_id}:{observed}")
        target_regressions.append(
            {
                "case_id": case_id,
                "expected_status": expected_status,
                "observed_status": observed,
            }
        )

    payload = {
        "schema_version": "worldguard.generic_skillguard_supervision_check.v1",
        "ok": not failures,
        "contract_hash": compiled.get("contract_hash", ""),
        "manifest_hash": manifest.get("manifest_hash", ""),
        "integration_mode": profile.get("integration_mode", ""),
        "closure_profiles": [
            row.get("profile_id") for row in closure_profiles if isinstance(row, dict)
        ],
        "declared_check_ids": sorted(source_check_ids),
        "target_native_regressions": target_regressions,
        "failures": failures,
        "claim_boundary": (
            "This focused check proves generic contract shape/parity, the bundled Guard-model "
            "oracle, and target-native fixture regressions. It does not execute a real scheduled "
            "target mesh, installation parity, parent aggregation, release, or OpenSpec archive."
        ),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Verify one WorldGuard entrypoint and seven complete internal Guard routes."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tomllib
from pathlib import Path
from typing import Any


EXPECTED_GUARDS = (
    "EventGuard",
    "AgentGuard",
    "SpaceGuard",
    "ResourceGuard",
    "CausalGuard",
    "ConflictGuard",
    "NormGuard",
)
EXPECTED_VERSION = "0.7.0"
PREDICTIVE_GUARDS = {"EventGuard", "CausalGuard"}
TERMINAL_STATUSES = ("PASS", "FAIL", "GAP", "BOUNDARY_EXCEEDED")
REQUIRED_ROW_FIELDS = {
    "route_id",
    "guard_id",
    "runner",
    "expectation_owner",
    "prediction_mode",
    "prediction_boundary",
    "response_owner",
    "purpose_validator",
    "semantic_executor_id",
    "semantic_registry",
}
GOVERNED_RUNTIME_SUFFIXES = {".py", ".json", ".yaml", ".yml"}


def _hash(path: Path) -> str:
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _runtime_inventory(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): _hash(path)
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in GOVERNED_RUNTIME_SUFFIXES
    }


def _callable_id(value: Any) -> str:
    return f"{value.__module__}:{value.__name__}"


def check(
    repository_root: Path,
    *,
    topology_path: Path | None = None,
    flowguard_alignment_path: Path | None = None,
) -> dict[str, object]:
    repository_root = repository_root.resolve()
    skill_root = repository_root / "skills" / "worldguard"
    topology_path = (
        topology_path.resolve()
        if topology_path is not None
        else skill_root / "references" / "internal-guard-routes.json"
    )
    flowguard_alignment_path = (
        flowguard_alignment_path.resolve()
        if flowguard_alignment_path is not None
        else repository_root / ".flowguard" / "run_claim_derived_coverage_checks.py"
    )
    findings: list[dict[str, object]] = []

    payload = json.loads(topology_path.read_text(encoding="utf-8"))
    rows = payload.get("routes", [])
    if not isinstance(rows, list):
        rows = []
        findings.append({"code": "topology_routes_not_list"})
    declared = {
        str(row.get("guard_id")): row
        for row in rows
        if isinstance(row, dict) and row.get("guard_id")
    }
    if len(declared) != len(rows):
        findings.append({"code": "duplicate_or_unidentified_guard_route"})
    if tuple(declared) != EXPECTED_GUARDS:
        findings.append(
            {
                "code": "declared_guard_inventory_mismatch",
                "expected": list(EXPECTED_GUARDS),
                "observed": list(declared),
            }
        )

    public = payload.get("public_entrypoint", {})
    if public != {"skill_id": "worldguard", "console_id": "worldguard"}:
        findings.append({"code": "public_entrypoint_mismatch", "observed": public})
    if tuple(payload.get("terminal_statuses", ())) != TERMINAL_STATUSES:
        findings.append({"code": "declared_terminal_status_mismatch"})

    pyproject = tomllib.loads(
        (repository_root / "pyproject.toml").read_text(encoding="utf-8")
    )
    project_version = str(pyproject.get("project", {}).get("version", ""))
    if project_version != EXPECTED_VERSION:
        findings.append(
            {
                "code": "project_version_mismatch",
                "expected": EXPECTED_VERSION,
                "observed": project_version,
            }
        )
    version_path = repository_root / "VERSION"
    source_version = (
        version_path.read_text(encoding="utf-8").strip()
        if version_path.is_file()
        else ""
    )
    if source_version != EXPECTED_VERSION:
        findings.append(
            {
                "code": "source_version_file_mismatch",
                "expected": EXPECTED_VERSION,
                "observed": source_version,
            }
        )
    readme = (repository_root / "README.md").read_text(encoding="utf-8")
    for marker in (
        f"**Source version:** `v{EXPECTED_VERSION}`",
        f"**源码版本：** `v{EXPECTED_VERSION}`",
    ):
        if marker not in readme:
            findings.append(
                {
                    "code": "readme_source_version_mismatch",
                    "expected": marker,
                }
            )
    changelog = (repository_root / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## v{EXPECTED_VERSION} " not in changelog:
        findings.append(
            {
                "code": "changelog_source_version_missing",
                "expected": EXPECTED_VERSION,
            }
        )
    scripts = pyproject.get("project", {}).get("scripts", {})
    if scripts != {"worldguard": "worldguard.cli:main"}:
        findings.append(
            {"code": "project_console_inventory_mismatch", "observed": scripts}
        )
    installed_skill_ids = sorted(
        path.parent.name
        for path in (repository_root / "skills").glob("*/SKILL.md")
    )
    if installed_skill_ids != ["worldguard"]:
        findings.append(
            {
                "code": "consumer_skill_inventory_mismatch",
                "observed": installed_skill_ids,
            }
        )

    flowguard_alignment = flowguard_alignment_path.read_text(encoding="utf-8")
    retired_runtime_path = "worldguard/skillguard_depth.py"
    current_runtime_path = "worldguard/execution_depth.py"
    if retired_runtime_path in flowguard_alignment:
        findings.append(
            {
                "code": "retired_runtime_authority_path_present",
                "path": retired_runtime_path,
            }
        )
    if flowguard_alignment.count(current_runtime_path) < 3:
        findings.append(
            {
                "code": "current_runtime_authority_alignment_incomplete",
                "path": current_runtime_path,
            }
        )

    root_runtime = repository_root / "worldguard"
    bundled_runtime = skill_root / "runtime" / "worldguard"
    root_inventory = _runtime_inventory(root_runtime)
    bundled_inventory = _runtime_inventory(bundled_runtime)
    if root_inventory != bundled_inventory:
        findings.append(
            {
                "code": "bundled_runtime_parity_mismatch",
                "missing_from_bundle": sorted(
                    root_inventory.keys() - bundled_inventory.keys()
                ),
                "extra_in_bundle": sorted(
                    bundled_inventory.keys() - root_inventory.keys()
                ),
                "different": sorted(
                    path
                    for path in root_inventory.keys() & bundled_inventory.keys()
                    if root_inventory[path] != bundled_inventory[path]
                ),
            }
        )

    added = False
    root_text = str(repository_root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
        added = True
    try:
        import worldguard as worldguard_package
        from worldguard.guard_model_contract import GUARD_MODEL_PURPOSES
        from worldguard.guards import GUARD_RUNNERS
        from worldguard.semantic import EXECUTOR_REGISTRY
        from worldguard.status import GuardStatus

        runtime_guards = tuple(GUARD_RUNNERS)
        semantic_guards = tuple(EXECUTOR_REGISTRY)
        purpose_guards = tuple(item.guard for item in GUARD_MODEL_PURPOSES)
        status_values = tuple(item.value for item in GuardStatus)
        if worldguard_package.__version__ != EXPECTED_VERSION:
            findings.append(
                {
                    "code": "runtime_version_mismatch",
                    "expected": EXPECTED_VERSION,
                    "observed": worldguard_package.__version__,
                }
            )
        for inventory_name, observed in (
            ("runner", runtime_guards),
            ("semantic", semantic_guards),
            ("purpose", purpose_guards),
        ):
            if observed != EXPECTED_GUARDS:
                findings.append(
                    {
                        "code": f"{inventory_name}_guard_inventory_mismatch",
                        "expected": list(EXPECTED_GUARDS),
                        "observed": list(observed),
                    }
                )
        if status_values != TERMINAL_STATUSES:
            findings.append(
                {
                    "code": "runtime_terminal_status_mismatch",
                    "observed": list(status_values),
                }
            )

        for guard_id in EXPECTED_GUARDS:
            row = declared.get(guard_id)
            if not isinstance(row, dict):
                continue
            missing_fields = sorted(REQUIRED_ROW_FIELDS - row.keys())
            if missing_fields:
                findings.append(
                    {
                        "code": "internal_route_fields_missing",
                        "guard_id": guard_id,
                        "fields": missing_fields,
                    }
                )
                continue
            expected_mode = (
                "claim_derived_predictive_participant"
                if guard_id in PREDICTIVE_GUARDS
                else "bounded_expectation_only"
            )
            expected_values = {
                "route_id": (
                    f"internal:worldguard:{guard_id.removesuffix('Guard').lower()}"
                ),
                "runner": _callable_id(GUARD_RUNNERS[guard_id]),
                "expectation_owner": (
                    "worldguard.contracts:GuardContract.for_guard"
                ),
                "prediction_mode": expected_mode,
                "response_owner": "worldguard.reports:GuardResult",
                "purpose_validator": (
                    "worldguard.guard_model_contract:"
                    "verify_guard_candidate_purpose_contract"
                ),
                "semantic_executor_id": (
                    EXECUTOR_REGISTRY[guard_id].binding.executor_id
                ),
                "semantic_registry": "worldguard.semantic:EXECUTOR_REGISTRY",
            }
            for field, expected in expected_values.items():
                if row.get(field) != expected:
                    findings.append(
                        {
                            "code": "internal_route_binding_mismatch",
                            "guard_id": guard_id,
                            "field": field,
                            "expected": expected,
                            "observed": row.get(field),
                        }
                    )
            if not str(row.get("prediction_boundary", "")).strip():
                findings.append(
                    {"code": "prediction_boundary_missing", "guard_id": guard_id}
                )
    finally:
        if added:
            sys.path.remove(root_text)

    return {
        "schema_version": "worldguard.internal_guard_topology_check.v1",
        "status": "pass" if not findings else "fail",
        "ok": not findings,
        "source_version": source_version,
        "public_skill_ids": installed_skill_ids,
        "project_console_ids": sorted(scripts),
        "internal_guard_ids": list(EXPECTED_GUARDS),
        "findings": findings,
        "claim_boundary": (
            "This target-native check proves the current source and bundled "
            "consumer declare one WorldGuard entrypoint and seven exact internal "
            "Guard routes. It does not prove a task-specific Guard run, factual "
            "truth, installation, release, or predictive closure."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--topology")
    parser.add_argument("--flowguard-alignment")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = check(
        Path(args.repository_root),
        topology_path=Path(args.topology) if args.topology else None,
        flowguard_alignment_path=(
            Path(args.flowguard_alignment) if args.flowguard_alignment else None
        ),
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"status={report['status']} findings={len(report['findings'])}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

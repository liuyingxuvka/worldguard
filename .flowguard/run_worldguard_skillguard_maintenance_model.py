"""Run the WorldGuard SkillGuard-maintenance FlowGuard model."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

from flowguard.review import review_scenarios


MODEL_PATH = Path(__file__).with_name("worldguard_skillguard_maintenance_model.py")
ROOT = MODEL_PATH.parents[1]


def _load_model():
    spec = importlib.util.spec_from_file_location("worldguard_skillguard_maintenance_model", MODEL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load model from {MODEL_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    sys.path.insert(0, str(MODEL_PATH.parent))
    sys.path.insert(0, str(ROOT))
    spec.loader.exec_module(module)
    return module


def _review_mesh(model) -> list[str]:
    findings: list[str] = []
    source_checks = model.CONTRACT_SOURCE["checks"]
    if model.MEMBERS != ("worldguard",):
        findings.append("maintenance unit does not contain exactly WorldGuard")
    if len(model.DECLARED_CHECKS) != 5 or len(set(model.DECLARED_CHECKS)) != 5:
        findings.append("declared check inventory is not exactly five unique ids")
    owner_ids = [row["execution_owner_id"] for row in source_checks]
    subject_ids = [row["evidence_subject_id"] for row in source_checks]
    if len(set(owner_ids)) != 5:
        findings.append("execution owners are missing or duplicated")
    if len(set(subject_ids)) != 5:
        findings.append("evidence subjects are missing or duplicated")
    if set(model.TEST_MESH["required_check_ids"]) != set(model.DECLARED_CHECKS):
        findings.append("TestMesh does not cover exactly the target declarations")
    if len(model.CONTRACT_MODEL["obligations"]) != 20:
        findings.append("existing target contract export no longer carries twenty obligations")
    if model.TEST_MESH["cross_unit_receipt_reuse"]:
        findings.append("cross-unit receipt reuse must remain disabled")
    if model.TEST_MESH["open_spec_is_test_evidence"]:
        findings.append("OpenSpec cannot be test evidence")
    if model.STRUCTURE_MESH["dependency_cycles"]:
        findings.append("maintenance structure contains a dependency cycle")
    if model.STRUCTURE_MESH["alternate_success_paths"]:
        findings.append("maintenance structure contains an alternate success path")
    local_skill_root = ROOT / ".agents" / "skills"
    if local_skill_root.exists() and any(path.is_file() for path in local_skill_root.rglob("*")):
        findings.append("obsolete local FlowGuard skill copies remain present")
    if (ROOT / ".skillguard" / "flowguard-suite" / "suite-map.json").exists():
        findings.append("obsolete local FlowGuard suite map remains present")
    canonical = ROOT / "worldguard" / "examples" / "fuel_cell" / "world_model.yaml"
    bundled = ROOT / "skills" / "worldguard" / "runtime" / "worldguard" / "examples" / "fuel_cell" / "world_model.yaml"
    if canonical.read_bytes() != bundled.read_bytes():
        findings.append("canonical and bundled fuel-cell model bytes differ")
    return findings


def main() -> int:
    model = _load_model()
    scenario_report = review_scenarios(model.scenarios())
    mesh_findings = _review_mesh(model)
    print(scenario_report.format_text(max_counterexamples=6))
    print(
        json.dumps(
            {
                "artifact_kind": "worldguard_skillguard_maintenance_model_report",
                "status": "pass" if scenario_report.ok and not mesh_findings else "blocked",
                "scenario_count": len(model.scenarios()),
                "member_count": len(model.MEMBERS),
                "declared_check_count": len(model.DECLARED_CHECKS),
                "target_obligation_count": len(model.CONTRACT_MODEL["obligations"]),
                "mesh_findings": mesh_findings,
                "claim_boundary": (
                    "This proves the modeled author-maintenance structure, order, reduction boundary, and exact check inventory only. "
                    "Native check execution, consumer installation, publication, release, and future agent behavior remain separate evidence domains."
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if scenario_report.ok and not mesh_findings else 1


if __name__ == "__main__":
    raise SystemExit(main())

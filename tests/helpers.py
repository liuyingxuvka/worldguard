from __future__ import annotations

from worldguard.contracts import GuardContract
from worldguard.guard_model_contract import (
    PROTECTED_FAILURE_CLASSES,
    build_calibration_task_purpose_declaration,
)


def attach_task_purpose_declarations(
    contract: dict,
    *,
    guards: list[str] | None = None,
) -> dict:
    """Make test intent explicit; production code has no analogous fallback."""

    task_contract_id = str(contract["contract_id"])
    run_id = str(contract.get("run_id", "worldguard-run"))
    model_instance_id = str(contract["world_model"]["model_id"])
    target_guards = guards or list(contract["claim"].get("target_guards", []))
    declarations = []
    for guard in target_guards:
        selected = next(
            item.failure_id for item in PROTECTED_FAILURE_CLASSES if item.guard == guard
        )
        declarations.append(
            build_calibration_task_purpose_declaration(
                guard,
                task_contract_id=task_contract_id,
                run_id=run_id,
                model_instance_id=model_instance_id,
                selected_failure_ids=[selected],
                purpose=f"Prevent the explicit {guard} test model from accepting its declared invalid case.",
                boundary="This test-local declaration licenses only the named native reaction.",
            )
        )
    contract["guard_purpose_declarations"] = declarations
    return contract


def make_contract(
    guard: str,
    *,
    text: str = "claim",
    requested_semantics: list[str] | None = None,
    inputs: dict | None = None,
    world_model: dict | None = None,
) -> GuardContract:
    task_contract_id = f"test:{guard}"
    run_id = "test-run"
    resolved_world_model = world_model or {"model_id": "model-001", "model_version": "test"}
    return GuardContract.from_dict(
        {
            "contract_id": task_contract_id,
            "schema_version": "worldguard.contract.v1",
            "run_id": run_id,
            "claim": {
                "claim_id": "claim-001",
                "text": text,
                "target_guards": [guard],
                "requested_semantics": requested_semantics or [],
            },
            "world_model": resolved_world_model,
            "inputs": inputs or {},
            "guard_purpose_declarations": [
                build_calibration_task_purpose_declaration(
                    guard,
                    task_contract_id=task_contract_id,
                    run_id=run_id,
                    model_instance_id=str(resolved_world_model["model_id"]),
                )
            ],
            "dependencies": {"upstream_results": [], "read_only": True},
            "output_requirements": {
                "require_ledgers": True,
                "require_counterexample_for_non_pass": True,
                "allowed_status": ["PASS", "FAIL", "GAP", "BOUNDARY_EXCEEDED"],
            },
        }
    )

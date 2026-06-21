from __future__ import annotations

from worldguard.contracts import GuardContract


def make_contract(
    guard: str,
    *,
    text: str = "claim",
    requested_semantics: list[str] | None = None,
    inputs: dict | None = None,
    world_model: dict | None = None,
) -> GuardContract:
    return GuardContract.from_dict(
        {
            "contract_id": f"test:{guard}",
            "schema_version": "worldguard.contract.v1",
            "run_id": "test-run",
            "claim": {
                "claim_id": "claim-001",
                "text": text,
                "target_guards": [guard],
                "requested_semantics": requested_semantics or [],
            },
            "world_model": world_model or {"model_id": "model-001", "model_version": "test"},
            "inputs": inputs or {},
            "dependencies": {"upstream_results": [], "read_only": True},
            "output_requirements": {
                "require_ledgers": True,
                "require_counterexample_for_non_pass": True,
                "allowed_status": ["PASS", "FAIL", "GAP", "BOUNDARY_EXCEEDED"],
            },
        }
    )

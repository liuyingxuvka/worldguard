from __future__ import annotations

import argparse
from importlib.resources import files
from typing import Any

import yaml

from worldguard.contracts import GuardContract
from worldguard.io import dump_json
from worldguard.kernel import run_worldguard

REQUIRED_GUARDS = [
    "EventGuard",
    "AgentGuard",
    "SpaceGuard",
    "ResourceGuard",
    "CausalGuard",
    "ConflictGuard",
    "NormGuard",
]

BOUNDARY_STRINGS = [
    "no real fuel-cell thermodynamics",
    "no legal compliance finding",
    "no safety certification",
    "no deployment readiness claim",
    "no market truth or strategy proof",
]


def _load_yaml(name: str) -> dict[str, Any]:
    path = files("worldguard.examples").joinpath("fuel_cell", name)
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def build_contracts() -> list[GuardContract]:
    story = _load_yaml("input_story_fragment.yaml")["input_story_fragment"]
    world = _load_yaml("world_model.yaml")["world_model"]
    state = world["initial_world_state"]
    scope_limits = story.get("scope_limits", [])
    contracts = []
    inputs = {
        "events": world.get("event_line", []),
        "beliefs": state.get("agents", {}),
        "spatial_relations": state.get("rcc8_relations", []),
        "resources": state.get("resources", {}),
        "causal_model": {
            "variables": state.get("causal_variables", []),
            "equations": state.get("causal_equations", {}),
        },
        "game_model": {"payoffs": state.get("conflict_payoffs", [])},
        "norms": state.get("norms", []),
        "facts": ["c_precheck_complete", "nda_active"],
    }
    model = {
        "model_id": world.get("model_id", "fuel_cell_company_abc_world_model_001"),
        "model_version": world.get("artifact_version", "repair-v5-artifact"),
        "scope_limits": scope_limits,
        **state,
    }
    for claim in story.get("claims", []):
        contracts.append(
            GuardContract.from_dict(
                {
                    "contract_id": f"fuel-cell:{claim['claim_id']}",
                    "schema_version": "worldguard.contract.v1",
                    "run_id": "fuel-cell-toy",
                    "claim": {
                        "claim_id": claim["claim_id"],
                        "text": claim.get("text", ""),
                        "target_guards": claim.get("target_guards", []),
                        "requested_semantics": claim.get("target_guards", []),
                    },
                    "world_model": model,
                    "inputs": inputs,
                    "dependencies": {"upstream_results": [], "read_only": True},
                    "output_requirements": {
                        "require_ledgers": True,
                        "require_counterexample_for_non_pass": True,
                        "allowed_status": ["PASS", "FAIL", "GAP", "BOUNDARY_EXCEEDED"],
                    },
                }
            )
        )
    return contracts


def run_check() -> dict[str, Any]:
    story = _load_yaml("input_story_fragment.yaml")["input_story_fragment"]
    expected = _load_yaml("expected_guard_report.yaml")["expected_guard_report"]
    ledger_outputs = _load_yaml("ledger_outputs.yaml")["ledger_outputs"]
    reports = [run_worldguard(contract) for contract in build_contracts()]
    guards_seen = sorted({result.guard for report in reports for result in report.child_results})
    statuses = [report.status.value for report in reports]
    scope_notes = [
        *story.get("scope_limits", []),
        *ledger_outputs.get("artifact_scope_note", {}).get("no_real_world_claims", []),
    ]
    toy_boundaries_ok = all(
        any(boundary in item for item in scope_notes) or boundary in str(scope_notes)
        for boundary in BOUNDARY_STRINGS
    )
    ok = (
        set(guards_seen) == set(REQUIRED_GUARDS)
        and expected.get("aggregate_status") == "FAIL"
        and "FAIL" in statuses
        and toy_boundaries_ok
    )
    return {
        "ok": ok,
        "example": "fuel_cell",
        "guards_verified": guards_seen,
        "claim_statuses": statuses,
        "expected_aggregate_status": expected.get("aggregate_status"),
        "toy_boundaries_verified": BOUNDARY_STRINGS,
        "reports": [report.to_dict() for report in reports],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("fuel_cell example requires --check")
    result = run_check()
    print(dump_json(result))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

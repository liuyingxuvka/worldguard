"""Finite ContractExhaustionMesh child for WorldGuard-owned Guard failures.

The target runtime owns the meanings, fixtures, and reactions.  This FlowGuard
child only proves that the declared finite failure inventory is exhaustively
materialized and oracle-bound; it does not create a second execution route.
"""

from __future__ import annotations

import json
from dataclasses import asdict

from flowguard import (
    ContractCoverageUniverse,
    ContractExhaustionPlan,
    ContractMutationCase,
    ContractOracle,
    review_contract_exhaustion,
)

from worldguard.guard_model_contract import PROTECTED_FAILURE_CLASSES


MODEL_ID = "worldguard-guard-model-failure-exhaustion"
PARENT_MODEL_ID = "worldguard-claim-derived-semantic-coverage"


def build_guard_model_contract_exhaustion_plan() -> ContractExhaustionPlan:
    cases = tuple(
        ContractMutationCase(
            case_id=case.failure_id,
            mutation_type="target_native_guard_failure",
            oracle_id=f"oracle:{case.code}",
            input_delta={
                "guard": case.guard,
                "layer": case.layer,
                "failure_code": case.code,
            },
            expected_status=case.expected_status,
            evidence_refs=(
                "worldguard/guard_model_contract.py",
                "tests/test_guard_model_contract.py",
            ),
            required_test_cell_id=case.failure_id,
            required_routes=("route:worldguard-claim-derived-depth",),
            description=case.blocked_claim,
            freshness_scope="worldguard_guard_model_runtime",
            model_id=MODEL_ID,
            parent_model_id=PARENT_MODEL_ID,
        )
        for case in PROTECTED_FAILURE_CLASSES
    )
    oracles = tuple(
        ContractOracle(
            oracle_id=f"oracle:{case.code}",
            expected_status=case.expected_status,
            expected_message_fields=("code",),
            description=(
                f"The target-native {case.guard} {case.layer} reaction must emit "
                f"exactly {case.code} with status {case.expected_status}."
            ),
            metadata={"guard": case.guard, "layer": case.layer, "code": case.code},
        )
        for case in PROTECTED_FAILURE_CLASSES
    )
    case_ids = tuple(case.failure_id for case in PROTECTED_FAILURE_CLASSES)
    universe = ContractCoverageUniverse(
        universe_id="universe:worldguard-guard-owned-failure-classes",
        claim_scope=(
            "Every literal failure code owned by an individual WorldGuard Guard "
            "runner or Guard semantic executor."
        ),
        source_refs=(
            "worldguard/guards/*.py",
            "worldguard/semantic.py",
            "worldguard/guard_model_contract.py",
        ),
        required_case_ids=case_ids,
        require_full_product=False,
        metadata={
            "finite": True,
            "failure_class_count": len(case_ids),
            "partition_axes": ["guard", "layer", "failure_code"],
            "non_cartesian_reason": (
                "Stable failure codes are mutually exclusive native reaction classes, "
                "not independent axes to combine."
            ),
        },
    )
    return ContractExhaustionPlan(
        plan_id=MODEL_ID,
        model_id=MODEL_ID,
        parent_model_id=PARENT_MODEL_ID,
        model_level="child",
        seed_cases=cases,
        oracles=oracles,
        coverage_universe=universe,
        require_coverage_universe=True,
        require_oracles_for_required_cases=True,
        claim_scope="finite",
        generation_policy="declared-finite-enumeration",
        allow_unbounded_scoped=False,
        source_model_ids=("worldguard-guard-model-contract", PARENT_MODEL_ID),
        required_route_ids=("route:worldguard-claim-derived-depth",),
        metadata={
            "execution_owner": ".flowguard/run_claim_derived_coverage_checks.py",
            "native_oracle": "worldguard.guard_model_contract.run_guard_model_contract",
            "claim_boundary": (
                "Mesh/provider lifecycle failures and unenumerated arbitrary defects are outside "
                "this individual-Guard protected-failure universe."
            ),
        },
    )


def review_guard_model_contract_exhaustion():
    return review_contract_exhaustion(build_guard_model_contract_exhaustion_plan())


def main() -> int:
    report = review_guard_model_contract_exhaustion()
    expected_ids = {case.failure_id for case in PROTECTED_FAILURE_CLASSES}
    generated_ids = {case.case_id for case in report.generated_cases}
    exact = len(report.generated_cases) == len(expected_ids) and generated_ids == expected_ids
    payload = {
        "schema_version": "worldguard.guard_model_contract_exhaustion_report.v1",
        "model_id": MODEL_ID,
        "ok": bool(report.ok and exact),
        "decision": report.decision,
        "confidence": report.confidence,
        "required_failure_count": len(expected_ids),
        "generated_failure_count": len(report.generated_cases),
        "exact_required_case_inventory": exact,
        "findings": [asdict(finding) for finding in report.findings],
        "claim_boundary": build_guard_model_contract_exhaustion_plan().metadata["claim_boundary"],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Portable FlowGuard export for WorldGuard's current declared-check contract."""

from __future__ import annotations

import re

import flowguard


FLOWGUARD_MODEL_MARKER = "flowguard-executable-model"


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _native_route(
    route_id: str,
    *,
    function_id: str,
    owner_id: str,
    business_intent: str,
) -> tuple[dict[str, object], dict[str, object], list[dict[str, object]]]:
    slug = _slug(route_id)
    execute = f"step:{slug}:execute"
    passed = f"terminal:{slug}:pass"
    blocked = f"terminal:{slug}:blocked"
    steps: list[dict[str, object]] = [
        {
            "step_id": execute,
            "route_id": route_id,
            "owner_id": owner_id,
            "action_kind": "native",
            "prerequisite_step_ids": [],
            "required": True,
            "terminal_kind": "",
        },
        {
            "step_id": passed,
            "route_id": route_id,
            "owner_id": owner_id,
            "action_kind": "terminal",
            "prerequisite_step_ids": [execute],
            "required": True,
            "terminal_kind": "success",
        },
        {
            "step_id": blocked,
            "route_id": route_id,
            "owner_id": owner_id,
            "action_kind": "terminal",
            "prerequisite_step_ids": [],
            "required": True,
            "terminal_kind": "blocked",
        },
    ]
    return (
        {
            "function_id": function_id,
            "business_intent": business_intent,
            "owner_id": owner_id,
            "route_ids": [route_id],
            "composable_with": [],
        },
        {
            "route_id": route_id,
            "function_id": function_id,
            "owner_id": owner_id,
            "start_step_id": execute,
            "step_ids": [row["step_id"] for row in steps],
            "success_terminal_step_id": passed,
            "blocked_terminal_step_id": blocked,
            "handoffs": [],
        },
        steps,
    )


def _internal_guard_route(
    guard_id: str,
    *,
    prediction_mode: str,
) -> tuple[dict[str, object], dict[str, object], list[dict[str, object]]]:
    """Model one complete internal Guard route without publishing a child skill."""

    guard_slug = guard_id.removesuffix("Guard").lower()
    route_id = f"internal:worldguard:{guard_slug}"
    owner_id = f"worldguard.internal.{guard_id}"
    expectation = f"step:internal-worldguard-{guard_slug}:prediction-boundary"
    response = f"step:internal-worldguard-{guard_slug}:response"
    validate = f"step:internal-worldguard-{guard_slug}:validate"
    passed = f"terminal:internal-worldguard-{guard_slug}:pass"
    blocked = f"terminal:internal-worldguard-{guard_slug}:blocked"
    steps: list[dict[str, object]] = [
        {
            "step_id": expectation,
            "route_id": route_id,
            "owner_id": owner_id,
            "action_kind": "native",
            "prerequisite_step_ids": [],
            "required": True,
            "terminal_kind": "",
        },
        {
            "step_id": response,
            "route_id": route_id,
            "owner_id": owner_id,
            "action_kind": "native",
            "prerequisite_step_ids": [expectation],
            "required": True,
            "terminal_kind": "",
        },
        {
            "step_id": validate,
            "route_id": route_id,
            "owner_id": owner_id,
            "action_kind": "verifier",
            "prerequisite_step_ids": [response],
            "required": True,
            "terminal_kind": "",
        },
        {
            "step_id": passed,
            "route_id": route_id,
            "owner_id": owner_id,
            "action_kind": "terminal",
            "prerequisite_step_ids": [validate],
            "required": True,
            "terminal_kind": "success",
        },
        {
            "step_id": blocked,
            "route_id": route_id,
            "owner_id": owner_id,
            "action_kind": "terminal",
            "prerequisite_step_ids": [],
            "required": True,
            "terminal_kind": "blocked",
        },
    ]
    function_id = f"worldguard_internal_{guard_slug}_guard"
    return (
        {
            "function_id": function_id,
            "business_intent": (
                f"preserve {guard_id} prediction boundary, response, "
                f"validation, and terminal semantics ({prediction_mode})"
            ),
            "owner_id": owner_id,
            "route_ids": [route_id],
            "composable_with": [],
        },
        {
            "route_id": route_id,
            "function_id": function_id,
            "owner_id": owner_id,
            "start_step_id": expectation,
            "step_ids": [row["step_id"] for row in steps],
            "success_terminal_step_id": passed,
            "blocked_terminal_step_id": blocked,
            "handoffs": [],
        },
        steps,
    )


def export_contract_model() -> dict[str, object]:
    owner_id = "worldguard.mesh.predictive_coverage"
    route_id = "route:worldguard-claim-derived-depth"
    depth_steps = [
        {
            "step_id": "step:derive-world-coverage-universe",
            "route_id": route_id,
            "owner_id": owner_id,
            "action_kind": "native",
            "prerequisite_step_ids": [],
            "required": True,
            "terminal_kind": "",
        },
        {
            "step_id": "step:verify-world-guard-model-contract",
            "route_id": route_id,
            "owner_id": "worldguard.guard_model_contract",
            "action_kind": "verifier",
            "prerequisite_step_ids": ["step:derive-world-coverage-universe"],
            "required": True,
            "terminal_kind": "",
        },
        {
            "step_id": "step:freeze-world-guard-purpose-contract",
            "route_id": route_id,
            "owner_id": "worldguard.guard_model_contract",
            "action_kind": "native",
            "prerequisite_step_ids": ["step:verify-world-guard-model-contract"],
            "required": True,
            "terminal_kind": "",
        },
        {
            "step_id": "step:construct-world-guard-candidates",
            "route_id": route_id,
            "owner_id": "worldguard.contracts",
            "action_kind": "native",
            "prerequisite_step_ids": ["step:freeze-world-guard-purpose-contract"],
            "required": True,
            "terminal_kind": "",
        },
        {
            "step_id": "step:verify-world-guard-candidate-purpose-bindings",
            "route_id": route_id,
            "owner_id": "worldguard.guard_model_contract",
            "action_kind": "verifier",
            "prerequisite_step_ids": ["step:construct-world-guard-candidates"],
            "required": True,
            "terminal_kind": "",
        },
        {
            "step_id": "step:execute-world-semantic-depth",
            "route_id": route_id,
            "owner_id": owner_id,
            "action_kind": "native",
            "prerequisite_step_ids": ["step:verify-world-guard-candidate-purpose-bindings"],
            "required": True,
            "terminal_kind": "",
        },
        {
            "step_id": "step:verify-world-depth-receipt",
            "route_id": route_id,
            "owner_id": owner_id,
            "action_kind": "verifier",
            "prerequisite_step_ids": ["step:execute-world-semantic-depth"],
            "required": True,
            "terminal_kind": "",
        },
        {
            "step_id": "terminal:world-depth-pass",
            "route_id": route_id,
            "owner_id": owner_id,
            "action_kind": "terminal",
            "prerequisite_step_ids": ["step:verify-world-depth-receipt"],
            "required": True,
            "terminal_kind": "success",
        },
        {
            "step_id": "terminal:world-depth-blocked",
            "route_id": route_id,
            "owner_id": owner_id,
            "action_kind": "terminal",
            "prerequisite_step_ids": [],
            "required": True,
            "terminal_kind": "blocked",
        },
    ]
    functions: list[dict[str, object]] = [
        {
            "function_id": "worldguard_claim_derived_depth",
            "business_intent": "execute and verify WorldGuard-owned predictive depth",
            "owner_id": owner_id,
            "route_ids": [route_id],
            "composable_with": [],
        }
    ]
    routes: list[dict[str, object]] = [
        {
            "route_id": route_id,
            "function_id": "worldguard_claim_derived_depth",
            "owner_id": owner_id,
            "start_step_id": "step:derive-world-coverage-universe",
            "step_ids": [row["step_id"] for row in depth_steps],
            "success_terminal_step_id": "terminal:world-depth-pass",
            "blocked_terminal_step_id": "terminal:world-depth-blocked",
            "handoffs": [],
        }
    ]
    steps = list(depth_steps)
    preserved_routes = [
        (
            "guard_investigation.claim_or_source_intake",
            "worldguard_claim_or_source_intake",
            "preserve the current claim, source, and world boundary",
        ),
        (
            "guard_investigation.evidence_model",
            "worldguard_evidence_model",
            "build or load the native world evidence model",
        ),
        (
            "guard_investigation.gap_review",
            "worldguard_gap_review",
            "review missing semantics and model-boundary gaps",
        ),
        (
            "guard_investigation.closure",
            "worldguard_closure",
            "derive bounded or predictive native closure",
        ),
        (
            "worldguard.semantic_rollout",
            "worldguard_semantic_rollout",
            "execute WorldGuard-owned semantic rollout",
        ),
    ]
    for native_route_id, function_id, intent in preserved_routes:
        function, route, route_steps = _native_route(
            native_route_id,
            function_id=function_id,
            owner_id="worldguard",
            business_intent=intent,
        )
        functions.append(function)
        routes.append(route)
        steps.extend(route_steps)

    internal_guard_validate_steps: list[str] = []
    for guard_id in (
        "EventGuard",
        "AgentGuard",
        "SpaceGuard",
        "ResourceGuard",
        "CausalGuard",
        "ConflictGuard",
        "NormGuard",
    ):
        prediction_mode = (
            "claim_derived_predictive_participant"
            if guard_id in {"EventGuard", "CausalGuard"}
            else "bounded_expectation_only"
        )
        function, route, route_steps = _internal_guard_route(
            guard_id,
            prediction_mode=prediction_mode,
        )
        functions.append(function)
        routes.append(route)
        steps.extend(route_steps)
        internal_guard_validate_steps.append(
            f"step:internal-worldguard-"
            f"{guard_id.removesuffix('Guard').lower()}:validate"
        )

    template_function, template_route, template_steps = _native_route(
        "worldguard.template_pack_builder",
        function_id="worldguard_template_pack_builder",
        owner_id="worldguard.template_packs",
        business_intent=(
            "select, compose, and validate WorldGuard-owned GuardContract or "
            "ModelMeshContract scaffolding without deciding Guard semantics"
        ),
    )
    functions.append(template_function)
    routes.append(template_route)
    steps.extend(template_steps)

    invariant_ids = [
        "worldguard_claim_routes_are_derived",
        "worldguard_discovered_node_scope_and_exclusions_are_reconciled",
        "worldguard_per_node_and_variable_native_floor_and_strata_are_executed",
        "worldguard_scenario_and_holdout_depth_is_executed",
        "worldguard_branch_intervention_counterfactual_depth_is_executed",
        "worldguard_native_receipt_is_input_bound",
        "worldguard_guard_model_purposes_are_declared",
        "worldguard_guard_owned_failure_universe_is_complete",
        "worldguard_native_failure_oracle_is_exact",
        "worldguard_formal_guard_candidates_bind_current_purpose_before_proof",
        "worldguard_template_selection_is_zero_one_many_deterministic",
        "worldguard_template_fields_have_exact_disjoint_ownership",
        "worldguard_template_instances_use_native_validators_without_semantic_takeover",
        "worldguard_target_template_projection_has_exact_unsealed_neutral_shape",
        "worldguard_target_template_projection_equals_native_candidate_inventory",
        "worldguard_target_template_projection_binds_current_route_registry_builder_and_validators",
        "worldguard_single_direct_entry",
        "worldguard_internal_guard_routes_are_complete",
        "worldguard_internal_guard_prediction_response_validation_terminal_semantics_are_preserved",
    ]
    obligations = [
        ("obligation:worldguard-claim-routes", invariant_ids[0], ["step:execute-world-semantic-depth", "step:verify-world-depth-receipt"]),
        ("obligation:worldguard-semantic-universe", invariant_ids[1], ["step:execute-world-semantic-depth", "step:verify-world-depth-receipt"]),
        ("obligation:worldguard-timepoint-strata-depth", invariant_ids[2], ["step:execute-world-semantic-depth", "step:verify-world-depth-receipt"]),
        ("obligation:worldguard-scenario-holdout-depth", invariant_ids[3], ["step:execute-world-semantic-depth", "step:verify-world-depth-receipt"]),
        ("obligation:worldguard-predictive-axes", invariant_ids[4], ["step:execute-world-semantic-depth", "step:verify-world-depth-receipt"]),
        ("obligation:worldguard-receipt-freshness", invariant_ids[5], ["step:verify-world-depth-receipt"]),
        ("obligation:worldguard-guard-model-purpose", invariant_ids[6], ["step:verify-world-guard-model-contract"]),
        ("obligation:worldguard-protected-failure-universe", invariant_ids[7], ["step:verify-world-guard-model-contract"]),
        ("obligation:worldguard-native-failure-oracle", invariant_ids[8], ["step:verify-world-guard-model-contract"]),
        ("obligation:worldguard-guard-candidate-purpose-binding", invariant_ids[9], ["step:freeze-world-guard-purpose-contract", "step:construct-world-guard-candidates", "step:verify-world-guard-candidate-purpose-bindings"]),
        ("obligation:worldguard-template-selection", invariant_ids[10], ["step:worldguard-template-pack-builder:execute"]),
        ("obligation:worldguard-template-field-ownership", invariant_ids[11], ["step:worldguard-template-pack-builder:execute"]),
        ("obligation:worldguard-template-native-validation", invariant_ids[12], ["step:worldguard-template-pack-builder:execute"]),
        ("obligation:worldguard-template-neutral-projection", invariant_ids[13], ["step:worldguard-template-pack-builder:execute"]),
        ("obligation:worldguard-template-native-candidate-inventory", invariant_ids[14], ["step:worldguard-template-pack-builder:execute"]),
        ("obligation:worldguard-template-projection-freshness", invariant_ids[15], ["step:worldguard-template-pack-builder:execute"]),
        (
            "obligation:worldguard-internal-guard-topology",
            invariant_ids[16],
            internal_guard_validate_steps,
        ),
        (
            "obligation:worldguard-internal-guard-completeness",
            invariant_ids[17],
            internal_guard_validate_steps,
        ),
        (
            "obligation:worldguard-internal-guard-semantics",
            invariant_ids[18],
            internal_guard_validate_steps,
        ),
    ]
    return {
        "schema_version": "skillguard.flowguard_model_export.v2",
        "flowguard_schema_version": str(flowguard.SCHEMA_VERSION),
        "model_id": "worldguard-skillguard-declared-checks-current",
        "parent_model_id": "worldguard-claim-derived-semantic-coverage",
        "functions": functions,
        "routes": routes,
        "steps": steps,
        "obligations": [
            {
                "obligation_id": obligation_id,
                "invariant_id": invariant_id,
                "owner_step_ids": owner_step_ids,
                "required": True,
            }
            for obligation_id, invariant_id, owner_step_ids in obligations
        ],
        "invariant_ids": invariant_ids,
        "claim_boundary": (
            "WorldGuard owns Guard purposes, the finite protected-failure inventory, native "
            "good/bad fixtures and reactions, claim routing, model execution, simulation, and judgment. "
            "This export preserves the existing Guard-investigation and semantic-rollout "
            "routes and adds only supervised target-native Guard-contract, template-construction, "
            "target-owned neutral-projection, and predictive-depth checks. SkillGuard validates "
            "and seals neutral projection shape only; template mechanics never transfer Guard semantics."
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(export_contract_model(), ensure_ascii=False, indent=2, sort_keys=True))

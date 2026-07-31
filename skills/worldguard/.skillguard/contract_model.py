"""Portable FlowGuard export for WorldGuard's current maintenance checks."""

from __future__ import annotations

import flowguard


FLOWGUARD_MODEL_MARKER = "flowguard-executable-model"


def export_contract_model() -> dict[str, object]:
    """Expose maintenance validation ownership, not duplicate domain routes."""

    route_id = "route:worldguard-claim-derived-depth"
    owner_id = "worldguard.maintenance_validation"
    model_step = "step:derive-world-coverage-universe"
    topology_step = "step:verify-worldguard-internal-topology"
    guard_contract_step = "step:verify-world-guard-model-contract"
    depth_step = "step:execute-world-semantic-depth"
    template_step = "step:worldguard-template-pack-builder:execute"
    fact_revision_step = "step:worldguard-fact-revision:execute"
    success = "terminal:world-depth-pass"
    blocked = "terminal:world-depth-blocked"

    steps = [
        {
            "step_id": model_step,
            "route_id": route_id,
            "owner_id": "worldguard.flowguard_contract",
            "action_kind": "flowguard_model",
            "prerequisite_step_ids": [],
            "required": True,
            "terminal_kind": "",
        },
        {
            "step_id": topology_step,
            "route_id": route_id,
            "owner_id": "worldguard.internal.topology",
            "action_kind": "verifier",
            "prerequisite_step_ids": [model_step],
            "required": True,
            "terminal_kind": "",
        },
        {
            "step_id": guard_contract_step,
            "route_id": route_id,
            "owner_id": "worldguard.guard_model_contract",
            "action_kind": "verifier",
            "prerequisite_step_ids": [topology_step],
            "required": True,
            "terminal_kind": "",
        },
        {
            "step_id": depth_step,
            "route_id": route_id,
            "owner_id": "worldguard.mesh.predictive_coverage",
            "action_kind": "native",
            "prerequisite_step_ids": [guard_contract_step],
            "required": True,
            "terminal_kind": "",
        },
        {
            "step_id": template_step,
            "route_id": route_id,
            "owner_id": "worldguard.template_packs",
            "action_kind": "native",
            "prerequisite_step_ids": [depth_step],
            "required": True,
            "terminal_kind": "",
        },
        {
            "step_id": fact_revision_step,
            "route_id": route_id,
            "owner_id": "worldguard.task_local_fact_revision",
            "action_kind": "native",
            "prerequisite_step_ids": [template_step],
            "required": True,
            "terminal_kind": "",
        },
        {
            "step_id": success,
            "route_id": route_id,
            "owner_id": owner_id,
            "action_kind": "terminal",
            "prerequisite_step_ids": [fact_revision_step],
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
        "worldguard_source_version_and_consumer_runtime_identity_are_frozen",
        "worldguard_fact_revision_is_four_valued_transactional_and_evidence_bound",
    ]
    obligations = [
        ("obligation:worldguard-claim-routes", invariant_ids[0], depth_step),
        ("obligation:worldguard-semantic-universe", invariant_ids[1], depth_step),
        ("obligation:worldguard-timepoint-strata-depth", invariant_ids[2], depth_step),
        ("obligation:worldguard-scenario-holdout-depth", invariant_ids[3], depth_step),
        ("obligation:worldguard-predictive-axes", invariant_ids[4], depth_step),
        ("obligation:worldguard-receipt-freshness", invariant_ids[5], depth_step),
        ("obligation:worldguard-guard-model-purpose", invariant_ids[6], guard_contract_step),
        ("obligation:worldguard-protected-failure-universe", invariant_ids[7], guard_contract_step),
        ("obligation:worldguard-native-failure-oracle", invariant_ids[8], guard_contract_step),
        (
            "obligation:worldguard-guard-candidate-purpose-binding",
            invariant_ids[9],
            guard_contract_step,
        ),
        ("obligation:worldguard-template-selection", invariant_ids[10], template_step),
        ("obligation:worldguard-template-field-ownership", invariant_ids[11], template_step),
        ("obligation:worldguard-template-native-validation", invariant_ids[12], template_step),
        ("obligation:worldguard-template-neutral-projection", invariant_ids[13], template_step),
        (
            "obligation:worldguard-template-native-candidate-inventory",
            invariant_ids[14],
            template_step,
        ),
        (
            "obligation:worldguard-template-projection-freshness",
            invariant_ids[15],
            template_step,
        ),
        ("obligation:worldguard-internal-guard-topology", invariant_ids[16], topology_step),
        (
            "obligation:worldguard-internal-guard-completeness",
            invariant_ids[17],
            topology_step,
        ),
        (
            "obligation:worldguard-internal-guard-semantics",
            invariant_ids[18],
            topology_step,
        ),
        (
            "obligation:worldguard-source-version-identity",
            invariant_ids[19],
            topology_step,
        ),
        (
            "obligation:worldguard-fact-revision",
            invariant_ids[20],
            fact_revision_step,
        ),
    ]
    return {
        "schema_version": "skillguard.flowguard_model_export.v2",
        "flowguard_schema_version": str(flowguard.SCHEMA_VERSION),
        "model_id": "worldguard-skillguard-declared-checks-current",
        "parent_model_id": "worldguard-claim-derived-semantic-coverage",
        "functions": [
            {
                "function_id": "worldguard_claim_derived_depth",
                "business_intent": (
                    "execute the six exact WorldGuard maintenance validation owners"
                ),
                "owner_id": owner_id,
                "route_ids": [route_id],
                "composable_with": [],
            }
        ],
        "routes": [
            {
                "route_id": route_id,
                "function_id": "worldguard_claim_derived_depth",
                "owner_id": owner_id,
                "start_step_id": model_step,
                "step_ids": [row["step_id"] for row in steps],
                "success_terminal_step_id": success,
                "blocked_terminal_step_id": blocked,
                "handoffs": [],
            }
        ],
        "steps": steps,
        "obligations": [
            {
                "obligation_id": obligation_id,
                "invariant_id": invariant_id,
                "owner_step_ids": [owner_step_id],
                "required": True,
            }
            for obligation_id, invariant_id, owner_step_id in obligations
        ],
        "invariant_ids": invariant_ids,
        "claim_boundary": (
            "This author-side export gives each of the six WorldGuard checks one "
            "maintenance step and one execution owner. WorldGuard's public investigation, "
            "semantic-rollout, template, fact-revision, and seven internal Guard runtime routes remain "
            "target-owned in the skill/runtime and are verified by those checks; this "
            "maintenance model does not duplicate them as alternate execution paths."
        ),
    }


if __name__ == "__main__":
    import json

    print(
        json.dumps(
            export_contract_model(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )

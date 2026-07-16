"""Full existing-model preflight for WorldGuard semantic rollout status."""

from flowguard import ExistingModelPreflight, ExistingOwnershipSnapshot, ModelContextHit, REUSE_DECISION_EXTEND_EXISTING, review_existing_model_preflight


def build_preflight() -> ExistingModelPreflight:
    purpose = ModelContextHit(
        "worldguard-guard-purpose-contract",
        model_path="worldguard/guard_model_contract.py;.flowguard/guard_candidate_purpose_order.py",
        evidence_id="filesystem-current-purpose-binding",
        responsibilities=("task/model purpose authority", "per-failure native proof", "pre-evaluation candidate verification"),
        function_blocks=("FreezeGuardPurposeContract", "VerifyGuardCandidatePurposeContract"),
        state_owned=("task_guard_purpose_declaration", "guard_candidate_purpose_binding"),
        fields_owned=("guard_purpose_declarations", "guard_purpose_contract", "selected_failure_ids"),
        side_effects_owned=("reject missing, empty, unproved, stale, wrong-instance, or out-of-order Guard candidates",),
    )
    mesh = ModelContextHit(
        "worldguard-model-mesh-core",
        model_path="worldguard/mesh.py;.flowguard/worldguard_model_mesh_core.md",
        evidence_id="filesystem-current-prechange",
        responsibilities=("mesh contract normalization", "child report aggregation", "authority and handoff checks"),
        function_blocks=("NormalizeMesh", "RunChildContract", "AggregateMeshReport"),
        state_owned=("model_nodes", "model_edges", "child_reports", "mesh_findings"),
        fields_owned=("nodes.contract", "node_reports", "aggregate_ledger", "mesh_status"),
        side_effects_owned=("emit mesh report",),
        public_entrypoints=("worldguard mesh-check",),
    )
    kernel = ModelContextHit(
        "worldguard-unit-kernel",
        model_path="worldguard/kernel.py",
        evidence_id="filesystem-current-prechange",
        responsibilities=("single GuardContract dispatch",),
        function_blocks=("RunGuardContract",),
        state_owned=("guarded_report",),
        side_effects_owned=("evaluate unit contract",),
    )
    return ExistingModelPreflight(
        "worldguard-semantic-rollout-preflight",
        "Extend WorldGuard mesh aggregation with honest semantic rollout status",
        mode="full",
        model_search_performed=True,
        search_paths=("worldguard", ".flowguard", "skills", "openspec/changes"),
        relevant_models=(mesh, kernel, purpose),
        ownership_snapshot=ExistingOwnershipSnapshot(
            function_block_owners=(("NormalizeMesh", mesh.model_id), ("AggregateMeshReport", mesh.model_id), ("RunGuardContract", kernel.model_id), ("FreezeGuardPurposeContract", purpose.model_id), ("VerifyGuardCandidatePurposeContract", purpose.model_id)),
            state_owners=(("child_reports", mesh.model_id), ("mesh_findings", mesh.model_id), ("guarded_report", kernel.model_id), ("guard_candidate_purpose_binding", purpose.model_id)),
            field_owners=(("structural_status", mesh.model_id), ("semantic_status", mesh.model_id), ("provider_status", mesh.model_id), ("depth_receipt", mesh.model_id), ("guard_purpose_contract", purpose.model_id)),
            side_effect_owners=(("emit mesh report", mesh.model_id), ("evaluate unit contract", kernel.model_id), ("reject invalid Guard candidate purpose binding", purpose.model_id)),
            public_entrypoint_owners=(("worldguard mesh-check", mesh.model_id),),
            responsibility_owners=(("child report aggregation", mesh.model_id), ("single GuardContract dispatch", kernel.model_id), ("task/model Guard purpose authority", purpose.model_id)),
        ),
        reuse_decision=REUSE_DECISION_EXTEND_EXISTING,
        downstream_routes=("field_lifecycle_mesh", "development_process_flow", "model_test_alignment", "test_mesh_maintenance"),
        behavior_field_ids=("structural_status", "semantic_status", "provider_status", "rollout_status", "depth_receipt", "guard_purpose_contract"),
        field_lifecycle_required=True,
        field_lifecycle_model_ids=(mesh.model_id,),
        rationale="Extend the existing GuardContract constructor, task/model-owned purpose authority, kernel, and semantic verifier; keep the family catalog baseline-only and do not create a parallel candidate or SkillGuard-owned world-semantics route.",
    )


if __name__ == "__main__":
    report = review_existing_model_preflight(build_preflight())
    print(report.format_text(max_findings=20))
    raise SystemExit(0 if report.ok else 1)

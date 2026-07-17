"""Full existing-model preflight for WorldGuard validating template packs."""

from flowguard import (
    DuplicateBoundaryRisk,
    ExistingModelPreflight,
    ExistingOwnershipSnapshot,
    ModelContextHit,
    REUSE_DECISION_EXTEND_EXISTING,
    review_existing_model_preflight,
)


def build_preflight() -> ExistingModelPreflight:
    contracts = ModelContextHit(
        "worldguard-contracts",
        model_path="worldguard/contracts.py;skills/worldguard/references/worldguard-contracts.md",
        evidence_id="filesystem-current-contracts-1427f4e",
        responsibilities=(
            "canonical GuardContract parsing and serialization",
            "claim-derived Guard requirements",
        ),
        function_blocks=("LoadGuardContract", "DeriveRequiredGuards", "ConstructGuardChild"),
        state_owned=("guard_contract", "claim_semantics", "derived_guard_ids"),
        fields_owned=(
            "contract_id",
            "run_id",
            "claim.*",
            "world_model.*",
            "inputs.*",
            "guard_purpose_declarations",
        ),
        side_effects_owned=("construct a canonical Guard child",),
        public_entrypoints=("GuardContract.from_dict", "GuardContract.for_guard"),
    )
    purpose = ModelContextHit(
        "worldguard-guard-purpose-contract",
        model_path="worldguard/guard_model_contract.py;.flowguard/guard_candidate_purpose_order.py",
        evidence_id="filesystem-current-purpose-binding-1427f4e",
        responsibilities=(
            "task/model Guard purpose authority",
            "per-failure native proof",
            "pre-evaluation candidate verification",
        ),
        function_blocks=(
            "ProveTaskPurposeDeclaration",
            "FreezeGuardPurposeContract",
            "VerifyGuardCandidatePurposeContract",
        ),
        state_owned=("task_guard_purpose_declaration", "guard_candidate_purpose_binding"),
        fields_owned=(
            "guard_purpose_declarations",
            "guard_purpose_contract",
            "selected_failure_ids",
            "proof_receipt_fingerprint",
        ),
        side_effects_owned=(
            "reject missing, empty, unproved, stale, wrong-instance, or out-of-order Guard candidates",
        ),
    )
    mesh = ModelContextHit(
        "worldguard-model-mesh-core",
        model_path="worldguard/mesh.py;.flowguard/worldguard_model_mesh_core.md",
        evidence_id="filesystem-current-mesh-1427f4e",
        responsibilities=(
            "canonical ModelMeshContract parsing",
            "mesh topology and semantic coverage ownership",
            "mesh execution and aggregate status",
        ),
        function_blocks=("LoadModelMeshContract", "RunModelMesh", "AggregateMeshReport"),
        state_owned=("model_nodes", "model_edges", "semantic_coverage", "mesh_report"),
        fields_owned=(
            "mesh_id",
            "nodes",
            "edges",
            "snapshots",
            "provider_availability",
            "semantic_coverage.*",
        ),
        side_effects_owned=("execute semantic mesh and emit aggregate report",),
        public_entrypoints=("ModelMeshContract.from_dict", "worldguard mesh-check"),
    )
    template_packs = ModelContextHit(
        "worldguard-template-pack-builder",
        model_path="worldguard/template_packs.py;.flowguard/worldguard_template_pack_builder.py",
        evidence_id="filesystem-current-template-pack-owner-20260717",
        responsibilities=(
            "native template manifest and registry ownership",
            "deterministic zero/one/many selection and exact applicability",
            "target-owned neutral SkillGuard projection",
            "native builder and validator content identity",
        ),
        function_blocks=(
            "SelectTemplatePack",
            "ProjectTargetOwnedNeutralCatalog",
            "ComposeTemplatePack",
            "ValidateTemplateInstance",
        ),
        state_owned=(
            "template_registry",
            "template_selection",
            "target_template_projection",
            "template_instance_receipt",
        ),
        fields_owned=(
            "template_pack_manifest.*",
            "template_selection.*",
            "skillguard_target_template_projection.*",
            "skillguard_template_catalog_spec.*",
            "template_instance_receipt.*",
        ),
        side_effects_owned=(
            "emit an unsealed target-owned neutral projection",
            "construct and natively validate a contract scaffold",
        ),
        public_entrypoints=(
            "build_skillguard_target_template_projection",
            "build_template_instance",
        ),
    )
    skillguard = ModelContextHit(
        "worldguard-skillguard-declared-checks-current",
        model_path="skills/worldguard/.skillguard/contract-source.json",
        evidence_id="skillguard-current-trio-acab8070",
        responsibilities=(
            "freeze exact WorldGuard-declared checks",
            "reconcile immutable owner receipts",
            "validate and seal the target-neutral interchange shape without selecting applicability",
        ),
        function_blocks=(
            "FreezeDeclaredCheckInventory",
            "ValidateNeutralTemplateProjection",
            "ReconcileDeclaredCheckReceipts",
        ),
        state_owned=("declared_check_inventory", "execution_depth_receipt"),
        fields_owned=("native_check_ids", "execution_owner_id", "receipt identity"),
        side_effects_owned=("block incomplete or stale declared-check closure",),
    )
    return ExistingModelPreflight(
        "worldguard-template-pack-builder-preflight",
        "Add WorldGuard-owned validating template packs before canonical GuardContract and ModelMeshContract loading",
        mode="full",
        model_search_performed=True,
        search_paths=(
            "worldguard",
            ".flowguard",
            "skills/worldguard",
            "openspec/specs",
            "openspec/changes",
            "tests",
        ),
        behavior_lookup_required=False,
        behavior_lookup_status="fallback",
        behavior_lookup_reason=(
            "No canonical BehaviorCommitmentLedger artifact is present in this repository; "
            "the current source/model/spec inventory is recorded as explicit fallback evidence."
        ),
        relevant_models=(contracts, purpose, mesh, template_packs, skillguard),
        ownership_snapshot=ExistingOwnershipSnapshot(
            function_block_owners=(
                ("LoadGuardContract", contracts.model_id),
                ("DeriveRequiredGuards", contracts.model_id),
                ("ConstructGuardChild", contracts.model_id),
                ("ProveTaskPurposeDeclaration", purpose.model_id),
                ("FreezeGuardPurposeContract", purpose.model_id),
                ("VerifyGuardCandidatePurposeContract", purpose.model_id),
                ("LoadModelMeshContract", mesh.model_id),
                ("RunModelMesh", mesh.model_id),
                ("SelectTemplatePack", template_packs.model_id),
                ("ProjectTargetOwnedNeutralCatalog", template_packs.model_id),
                ("ComposeTemplatePack", template_packs.model_id),
                ("FreezeDeclaredCheckInventory", skillguard.model_id),
                ("ValidateNeutralTemplateProjection", skillguard.model_id),
            ),
            state_owners=(
                ("guard_contract", contracts.model_id),
                ("guard_candidate_purpose_binding", purpose.model_id),
                ("model_mesh_contract", mesh.model_id),
                ("target_template_projection", template_packs.model_id),
                ("execution_depth_receipt", skillguard.model_id),
            ),
            field_owners=(
                ("claim.*", contracts.model_id),
                ("guard_purpose_declarations", purpose.model_id),
                ("guard_purpose_contract", purpose.model_id),
                ("semantic_coverage.*", mesh.model_id),
                ("skillguard_target_template_projection.*", template_packs.model_id),
                ("native_check_ids", skillguard.model_id),
            ),
            side_effect_owners=(
                ("construct Guard child", contracts.model_id),
                ("prove task purpose", purpose.model_id),
                ("execute semantic mesh", mesh.model_id),
                ("project exact native template catalog and applicability", template_packs.model_id),
                ("supervise declared checks", skillguard.model_id),
            ),
            public_entrypoint_owners=(
                ("GuardContract.from_dict", contracts.model_id),
                ("ModelMeshContract.from_dict", mesh.model_id),
                ("worldguard mesh-check", mesh.model_id),
                ("build_skillguard_target_template_projection", template_packs.model_id),
            ),
            responsibility_owners=(
                ("Guard routing", contracts.model_id),
                ("Guard purpose and native oracle meaning", purpose.model_id),
                ("mesh semantics and predictive coverage", mesh.model_id),
                ("template catalog and applicability projection", template_packs.model_id),
                ("receipt completeness only", skillguard.model_id),
            ),
        ),
        reuse_decision=REUSE_DECISION_EXTEND_EXISTING,
        proposed_new_boundaries=(),
        duplicate_risks=(
            DuplicateBoundaryRisk(
                "responsibility",
                "Guard route selection",
                contracts.model_id,
                "worldguard.template_packs",
                resolution="Template selection consumes explicit WorldGuard-derived facts and cannot derive or override required Guards.",
                rationale="Keep semantic routing with derive_required_guards; ambiguity blocks.",
                resolved=True,
            ),
            DuplicateBoundaryRisk(
                "responsibility",
                "Guard purpose and protected failure selection",
                purpose.model_id,
                "worldguard.template_packs",
                resolution="Purpose declarations and selected failure ids remain task-owned slots proved by guard_model_contract.",
                rationale="Templates provide shape only and never synthesize purpose evidence.",
                resolved=True,
            ),
            DuplicateBoundaryRisk(
                "responsibility",
                "template semantic validation",
                contracts.model_id,
                "skillguard",
                resolution="WorldGuard owns the validator registry; SkillGuard can only supervise the declared check receipt.",
                rationale="No SkillGuard target-family branch or oracle is added.",
                resolved=True,
            ),
            DuplicateBoundaryRisk(
                "responsibility",
                "template applicability projection",
                template_packs.model_id,
                skillguard.model_id,
                resolution=(
                    "WorldGuard emits one row per exact native manifest from its current selector; "
                    "SkillGuard validates the neutral shape and seals digests only."
                ),
                rationale="Central vocabulary inference, candidate invention, and target semantic ranking remain forbidden.",
                resolved=True,
            ),
        ),
        downstream_routes=(
            "field_lifecycle_mesh",
            "development_process_flow",
            "model_test_alignment",
            "test_mesh_maintenance",
        ),
        behavior_field_ids=(
            "template_pack_manifest.*",
            "template_fragment.owned_field_ids",
            "template_selection.*",
            "template_instance_receipt.*",
            "native_validator_ids",
            "skillguard_target_template_projection.*",
            "skillguard_template_catalog_spec.*",
            "skillguard_applicability_results.*",
        ),
        field_lifecycle_required=True,
        field_lifecycle_model_ids=("worldguard-template-pack-field-lifecycle",),
        rationale=(
            "Extend the existing WorldGuard template-pack owner with one neutral projection adapter. "
            "The builder owns deterministic scaffolding, exact native applicability, field composition, and identity; "
            "WorldGuard's existing contract, purpose, mesh, and semantic owners retain all domain meaning."
        ),
    )


if __name__ == "__main__":
    report = review_existing_model_preflight(build_preflight())
    print(report.format_text(max_findings=30))
    raise SystemExit(0 if report.ok else 1)

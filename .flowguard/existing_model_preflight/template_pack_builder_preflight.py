"""Full existing-model preflight for WorldGuard validating template packs."""

import importlib.util
from hashlib import sha256
from pathlib import Path

from flowguard import (
    BehaviorLookupQuery,
    DuplicateBoundaryRisk,
    ExistingModelPreflight,
    ExistingOwnershipSnapshot,
    ModelContextHit,
    REUSE_DECISION_EXTEND_EXISTING,
    query_behavior_commitments,
    review_existing_model_preflight,
)


ROOT = Path(__file__).resolve().parents[2]


def _content_evidence_id(label: str, *relative_paths: str) -> str:
    digest = sha256()
    for relative in sorted(relative_paths):
        path = ROOT / relative
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes().replace(b"\r\n", b"\n"))
        digest.update(b"\0")
    return f"{label}-{digest.hexdigest()[:16]}"


def _template_behavior_lookup():
    model_path = (
        Path(__file__).resolve().parents[1]
        / "behavior_commitment_ledger"
        / "model.py"
    )
    spec = importlib.util.spec_from_file_location(
        "worldguard_behavior_commitment_model_for_preflight",
        model_path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the canonical WorldGuard behavior ledger")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    ledger = module.build_worldguard_behavior_commitment_ledger()
    return query_behavior_commitments(
        ledger,
        BehaviorLookupQuery(
            task_summary=(
                "Add WorldGuard-owned validating template packs before canonical "
                "GuardContract and ModelMeshContract loading"
            ),
            primary_plane="product_runtime",
            canonical_terms=(
                "WorldGuard template selection",
                "zero candidates",
                "no base fallback",
            ),
            changed_paths=(
                "worldguard/template_packs.py",
                "tests/test_template_packs.py",
            ),
            workflow_families=("worldguard_template_selection",),
            top_k=1,
        ),
    )


def build_preflight() -> ExistingModelPreflight:
    behavior_lookup = _template_behavior_lookup()
    contracts = ModelContextHit(
        "worldguard-contracts",
        model_path="worldguard/contracts.py;skills/worldguard/references/worldguard-contracts.md",
        evidence_id=_content_evidence_id(
            "filesystem-current-contracts",
            "worldguard/contracts.py",
            "skills/worldguard/references/worldguard-contracts.md",
        ),
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
        evidence_id=_content_evidence_id(
            "filesystem-current-purpose-binding",
            "worldguard/guard_model_contract.py",
            ".flowguard/guard_candidate_purpose_order.py",
        ),
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
        evidence_id=_content_evidence_id(
            "filesystem-current-mesh",
            "worldguard/mesh.py",
            ".flowguard/worldguard_model_mesh_core.md",
        ),
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
        ".flowguard/worldguard_template_pack_builder.py",
        model_path="worldguard/template_packs.py;.flowguard/worldguard_template_pack_builder.py",
        evidence_id=_content_evidence_id(
            "filesystem-current-template-pack-owner",
            "worldguard/template_packs.py",
            ".flowguard/worldguard_template_pack_builder.py",
            ".flowguard/worldguard_template_pack_field_lifecycle.md",
        ),
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
        evidence_id=_content_evidence_id(
            "skillguard-current-trio",
            "skills/worldguard/.skillguard/contract-source.json",
            "skills/worldguard/.skillguard/compiled-contract.json",
            "skills/worldguard/.skillguard/check-manifest.json",
        ),
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
    behavior_ledger = ModelContextHit(
        "worldguard-v0.4-current-authority",
        model_path=".flowguard/behavior_commitment_ledger/ledger.json;.flowguard/behavior_commitment_ledger/model.py",
        evidence_id=_content_evidence_id(
            "worldguard-v0.4-behavior-ledger",
            ".flowguard/behavior_commitment_ledger/ledger.json",
            ".flowguard/behavior_commitment_ledger/model.py",
        ),
        responsibilities=(
            "register the singular current input authority",
            "register the singular template-selection authority",
            "bind both paths to current Primary Path Authority evidence with zero fallback candidates",
        ),
        function_blocks=(
            "LoadCurrentWorldGuardInput",
            "SelectExactlyOneWorldGuardTemplateOrBlock",
        ),
        state_owned=(
            "current_input_authority",
            "template_selection_authority",
        ),
        fields_owned=(
            "inputs.*",
            "template_selection.*",
        ),
        side_effects_owned=(
            "reject retired input locations",
            "block zero or multiple applicable template candidates",
        ),
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
        behavior_lookup_required=True,
        behavior_lookup_status=behavior_lookup.status,
        primary_behavior_plane=behavior_lookup.selected_plane,
        primary_commitment_hits=behavior_lookup.primary_hits,
        related_commitment_hits=behavior_lookup.related_hits,
        candidate_commitment_hits=behavior_lookup.candidate_hits,
        plane_ambiguity=behavior_lookup.plane_ambiguity,
        ledger_fingerprint=behavior_lookup.ledger_fingerprint,
        behavior_lookup_reason=(
            "The canonical WorldGuard v0.4 BehaviorCommitmentLedger resolves both changed "
            "business intents to one current path each, with current PPA evidence and zero "
            "fallback candidates."
        ),
        relevant_models=(
            contracts,
            purpose,
            mesh,
            template_packs,
            skillguard,
            behavior_ledger,
        ),
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
                ("LoadCurrentWorldGuardInput", behavior_ledger.model_id),
                (
                    "SelectExactlyOneWorldGuardTemplateOrBlock",
                    behavior_ledger.model_id,
                ),
            ),
            state_owners=(
                ("guard_contract", contracts.model_id),
                ("guard_candidate_purpose_binding", purpose.model_id),
                ("model_mesh_contract", mesh.model_id),
                ("target_template_projection", template_packs.model_id),
                ("execution_depth_receipt", skillguard.model_id),
                ("current_input_authority", behavior_ledger.model_id),
                ("template_selection_authority", behavior_ledger.model_id),
            ),
            field_owners=(
                ("claim.*", contracts.model_id),
                ("guard_purpose_declarations", purpose.model_id),
                ("guard_purpose_contract", purpose.model_id),
                ("semantic_coverage.*", mesh.model_id),
                ("skillguard_target_template_projection.*", template_packs.model_id),
                ("native_check_ids", skillguard.model_id),
                ("inputs.*", behavior_ledger.model_id),
            ),
            side_effect_owners=(
                ("construct Guard child", contracts.model_id),
                ("prove task purpose", purpose.model_id),
                ("execute semantic mesh", mesh.model_id),
                ("project exact native template catalog and applicability", template_packs.model_id),
                ("supervise declared checks", skillguard.model_id),
                ("reject retired input locations", behavior_ledger.model_id),
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
                ("changed v0.4 path authority", behavior_ledger.model_id),
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

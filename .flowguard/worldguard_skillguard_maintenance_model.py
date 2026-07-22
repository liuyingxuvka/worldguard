"""Executable FlowGuard model for WorldGuard SkillGuard maintenance.

The model imports WorldGuard's existing target contract export and governs only
author-maintenance order, structure reduction, exact declared-check ownership,
and the no-install boundary. WorldGuard retains every domain route and check.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import json
from pathlib import Path

from flowguard import (
    FunctionResult,
    Invariant,
    InvariantResult,
    Scenario,
    ScenarioExpectation,
    Workflow,
)

from skillguard_depth_contract_model import export_contract_model


FLOWGUARD_MODEL_MARKER = "flowguard-executable-model"
ROOT = Path(__file__).resolve().parents[1]
CONTRACT_SOURCE_PATH = ROOT / "skills" / "worldguard" / ".skillguard" / "contract-source.json"
CONTRACT_SOURCE = json.loads(CONTRACT_SOURCE_PATH.read_text(encoding="utf-8"))
CONTRACT_MODEL = export_contract_model()
MAINTENANCE_UNIT_ID = "unit:worldguard"
MEMBERS = ("worldguard",)
DECLARED_CHECKS = tuple(row["check_id"] for row in CONTRACT_SOURCE["checks"])

STRUCTURE_MESH = {
    "mesh_id": "worldguard.skillguard-maintenance.structure.current",
    "source_model_ids": [
        CONTRACT_MODEL["model_id"],
        "worldguard-claim-derived-semantic-coverage",
        "worldguard-guard-model-failure-exhaustion",
        "worldguard-template-pack-builder",
    ],
    "maintenance_unit_id": MAINTENANCE_UNIT_ID,
    "public_entrypoint": "skills/worldguard/SKILL.md",
    "active_authority": "skills/worldguard plus one target-owned .skillguard declaration",
    "runtime_parity_pair": [
        "worldguard",
        "skills/worldguard/runtime/worldguard",
    ],
    "project_flowguard_surface": "$CODEX_HOME/skills current clean consumer",
    "reduction_candidates": [
        {
            "path": ".agents/skills/**",
            "proof_status": "dependency_search_complete",
            "target_action": "remove",
            "required_next_route": "flowguard-development-process-flow",
            "prior_tracked_path_count": 136,
        },
        {
            "path": ".skillguard/flowguard-suite/suite-map.json",
            "proof_status": "dependency_search_complete",
            "target_action": "remove",
            "required_next_route": "flowguard-development-process-flow",
            "prior_tracked_path_count": 1,
        },
    ],
    "dependency_cycles": [],
    "alternate_success_paths": [],
}

TEST_MESH = {
    "mesh_id": "worldguard.skillguard-maintenance.tests.current",
    "source_model_id": "worldguard.skillguard-maintenance.process.current",
    "inventory_revision": "one-member-five-target-declared-checks",
    "parent_gate": "unit:worldguard:affected-validation",
    "required_check_ids": list(DECLARED_CHECKS),
    "check_owners": [
        {
            "check_id": row["check_id"],
            "execution_owner_id": row["execution_owner_id"],
            "evidence_subject_id": row["evidence_subject_id"],
            "obligation_ids": list(row["covers_obligation_ids"]),
            "dependency_ids": list(row["depends_on_check_ids"]),
        }
        for row in CONTRACT_SOURCE["checks"]
    ],
    "open_spec_is_test_evidence": False,
    "cross_unit_receipt_reuse": False,
}

DEVELOPMENT_PROCESS = {
    "model_id": "worldguard.skillguard-maintenance.process.current",
    "modes": {
        "plan_detailing": "not_needed",
        "strategy_selection": "active:material-rework-risk",
        "agent_workflow": "active",
        "execution_freshness": "active",
    },
    "ordered_steps": [
        "openspec-context",
        "existing-model-preflight",
        "dependency-proof",
        "flowguard-structure-and-test-boundary",
        "skillguard-author-adoption",
        "direct-current-contract-compile",
        "runtime-byte-normalization",
        "obsolete-author-copy-removal",
        "same-unit-five-check-validation",
        "consumer-projection-diff",
        "bounded-local-closure",
    ],
    "hard_stops": [
        "peer-write-overlap",
        "live-local-flowguard-copy-dependency",
        "inferred-domain-check",
        "runtime-byte-mismatch",
        "stale-or-nonterminal-declared-evidence",
        "consumer-author-state-leak",
        "global-install-attempt",
    ],
    "freshness_domains": [
        "repository-source",
        "flowguard-models",
        "skillguard-contract-authority",
        "owner-evidence",
        "runtime-parity",
        "consumer-projection",
        "git-worktree",
    ],
    "excluded_claims": ["installation", "publication", "release", "future-agent-behavior"],
}


@dataclass(frozen=True)
class MaintenanceRequest:
    action: str
    check_id: str = ""
    member_count: int = 1
    declared_check_count: int = 5
    target_contract_current: bool = True
    local_copy_dependency_present: bool = False
    global_flowguard_consumer_current: bool = True
    runtime_bytes_equal: bool = True
    retain_obsolete_authority: bool = False
    check_status: str = "pass"
    consumer_has_author_leak: bool = False
    activate_installation: bool = False


@dataclass(frozen=True)
class MaintenanceState:
    phase: str = "planned"
    maintenance_unit_id: str = ""
    members: tuple[str, ...] = ()
    structure_reduced: bool = False
    validated_check_ids: tuple[str, ...] = ()
    terminal_status: str = ""
    domain_check_additions: int = 0
    duplicate_authority_count: int = 0
    installation_activated: bool = False


def _append_once(values: tuple[str, ...], value: str) -> tuple[str, ...]:
    return values if value in values else (*values, value)


class BindAuthorUnit:
    name = "BindAuthorUnit"
    accepted_input_type = MaintenanceRequest
    reads = ("action", "member_count", "declared_check_count", "target_contract_current")
    writes = ("phase", "maintenance_unit_id", "members", "terminal_status", "domain_check_additions")
    input_description = "one explicit WorldGuard author-maintenance request"
    output_description = "one-member current authority or a visible block"
    idempotency = "the same target declaration binds the same single unit"

    def apply(self, request: MaintenanceRequest, state: MaintenanceState):
        if request.action != "adopt":
            yield FunctionResult(request, state, label="adoption_not_requested")
            return
        if state.phase != "planned":
            yield FunctionResult(request, replace(state, phase="blocked", terminal_status="order"), label="maintenance_order_blocked")
            return
        if not request.target_contract_current:
            yield FunctionResult(request, replace(state, phase="blocked", terminal_status="target_contract"), label="target_contract_blocked")
            return
        if request.member_count != 1 or request.declared_check_count != len(DECLARED_CHECKS):
            additions = max(0, request.declared_check_count - len(DECLARED_CHECKS))
            yield FunctionResult(request, replace(state, phase="blocked", terminal_status="inventory", domain_check_additions=additions), label="declared_inventory_blocked")
            return
        yield FunctionResult(
            request,
            replace(state, phase="adopted", maintenance_unit_id=MAINTENANCE_UNIT_ID, members=MEMBERS),
            label="author_unit_bound",
        )


class ReduceDuplicateStructure:
    name = "ReduceDuplicateStructure"
    accepted_input_type = MaintenanceRequest
    reads = (
        "action",
        "local_copy_dependency_present",
        "global_flowguard_consumer_current",
        "runtime_bytes_equal",
        "retain_obsolete_authority",
    )
    writes = ("phase", "structure_reduced", "terminal_status", "duplicate_authority_count")
    input_description = "dependency proof plus runtime and global-consumer identity"
    output_description = "singular current structure or a visible block"
    idempotency = "the same proof selects one current project tool surface"

    def apply(self, request: MaintenanceRequest, state: MaintenanceState):
        if request.action != "reduce":
            yield FunctionResult(request, state, label="reduction_not_requested")
            return
        if state.phase != "adopted":
            yield FunctionResult(request, replace(state, phase="blocked", terminal_status="order"), label="maintenance_order_blocked")
            return
        if request.local_copy_dependency_present:
            yield FunctionResult(request, replace(state, phase="blocked", terminal_status="live_dependency"), label="local_copy_dependency_blocked")
            return
        if not request.global_flowguard_consumer_current:
            yield FunctionResult(request, replace(state, phase="blocked", terminal_status="global_consumer"), label="global_flowguard_consumer_blocked")
            return
        if not request.runtime_bytes_equal:
            yield FunctionResult(request, replace(state, phase="blocked", terminal_status="runtime_bytes"), label="runtime_byte_identity_blocked")
            return
        if request.retain_obsolete_authority:
            yield FunctionResult(
                request,
                replace(state, phase="blocked", terminal_status="duplicate_authority", duplicate_authority_count=1),
                label="duplicate_authority_blocked",
            )
            return
        yield FunctionResult(request, replace(state, phase="reduced", structure_reduced=True), label="singular_structure_ready")


class ValidateDeclaredCheck:
    name = "ValidateDeclaredCheck"
    accepted_input_type = MaintenanceRequest
    reads = ("action", "check_id", "check_status", "structure_reduced")
    writes = ("phase", "validated_check_ids", "terminal_status", "domain_check_additions")
    input_description = "one exact target-declared check owner result"
    output_description = "one current check identity or a visible block"
    idempotency = "each declared check id is attached at most once"

    def apply(self, request: MaintenanceRequest, state: MaintenanceState):
        if request.action != "validate":
            yield FunctionResult(request, state, label="validation_not_requested")
            return
        if not state.structure_reduced:
            yield FunctionResult(request, replace(state, phase="blocked", terminal_status="order"), label="maintenance_order_blocked")
            return
        if request.check_id not in DECLARED_CHECKS:
            yield FunctionResult(request, replace(state, phase="blocked", terminal_status="foreign_check", domain_check_additions=1), label="nondeclared_check_blocked")
            return
        if request.check_status != "pass":
            yield FunctionResult(request, replace(state, phase="blocked", terminal_status=request.check_status), label="declared_evidence_blocked")
            return
        validated = _append_once(state.validated_check_ids, request.check_id)
        yield FunctionResult(request, replace(state, phase="validating", validated_check_ids=validated), label=f"validated_{request.check_id}")


class AuditConsumerProjection:
    name = "AuditConsumerProjection"
    accepted_input_type = MaintenanceRequest
    reads = ("action", "consumer_has_author_leak", "activate_installation")
    writes = ("phase", "terminal_status", "installation_activated")
    input_description = "one clean consumer projection comparison"
    output_description = "local terminal evidence without installation"
    idempotency = "the same source and installed identities produce one comparison result"

    def apply(self, request: MaintenanceRequest, state: MaintenanceState):
        if request.action != "project":
            yield FunctionResult(request, state, label="projection_not_requested")
            return
        if set(state.validated_check_ids) != set(DECLARED_CHECKS):
            yield FunctionResult(request, replace(state, phase="blocked", terminal_status="projection_order"), label="maintenance_order_blocked")
            return
        if request.consumer_has_author_leak:
            yield FunctionResult(request, replace(state, phase="blocked", terminal_status="consumer_leak"), label="consumer_author_leak_blocked")
            return
        if request.activate_installation:
            yield FunctionResult(
                request,
                replace(state, phase="blocked", terminal_status="installation_scope", installation_activated=True),
                label="installation_activation_blocked",
            )
            return
        yield FunctionResult(request, replace(state, phase="terminal", terminal_status="pass"), label="unit_terminal_pass")


def maintenance_invariants() -> tuple[Invariant, ...]:
    def one_unit(state: MaintenanceState, _trace):
        if state.maintenance_unit_id and (
            state.maintenance_unit_id != MAINTENANCE_UNIT_ID or state.members != MEMBERS
        ):
            return InvariantResult.fail("author maintenance escaped the sole WorldGuard unit")
        return InvariantResult.pass_()

    def no_added_depth(state: MaintenanceState, _trace):
        if state.domain_check_additions:
            return InvariantResult.fail("SkillGuard attempted to add target-domain depth")
        return InvariantResult.pass_()

    def singular_authority(state: MaintenanceState, _trace):
        if state.duplicate_authority_count:
            return InvariantResult.fail("obsolete FlowGuard author authority remained active")
        return InvariantResult.pass_()

    def no_install(state: MaintenanceState, _trace):
        if state.installation_activated:
            return InvariantResult.fail("local maintenance activated a global installation")
        return InvariantResult.pass_()

    def exact_checks(state: MaintenanceState, _trace):
        if not set(state.validated_check_ids).issubset(set(DECLARED_CHECKS)):
            return InvariantResult.fail("validation contains a non-declared check")
        return InvariantResult.pass_()

    return (
        Invariant("one_worldguard_unit", "One author unit owns exactly one WorldGuard skill.", one_unit),
        Invariant("skillguard_adds_no_domain_depth", "Only the target's five declared checks may be supervised.", no_added_depth),
        Invariant("singular_flowguard_authority", "The global consumer is the sole project FlowGuard skill surface.", singular_authority),
        Invariant("no_global_install", "Local source maintenance does not activate installation.", no_install),
        Invariant("exact_five_check_inventory", "Validated checks remain a subset of five target declarations.", exact_checks),
    )


INVARIANTS = maintenance_invariants()


def build_workflow() -> Workflow:
    return Workflow(
        (BindAuthorUnit(), ReduceDuplicateStructure(), ValidateDeclaredCheck(), AuditConsumerProjection()),
        name="worldguard_skillguard_maintenance",
    )


def _good_sequence() -> tuple[MaintenanceRequest, ...]:
    return (
        MaintenanceRequest("adopt"),
        MaintenanceRequest("reduce"),
        *(MaintenanceRequest("validate", check_id=check_id) for check_id in DECLARED_CHECKS),
        MaintenanceRequest("project"),
    )


def scenarios() -> tuple[Scenario, ...]:
    workflow = build_workflow()
    validated = tuple(MaintenanceRequest("validate", check_id=check_id) for check_id in DECLARED_CHECKS)
    return (
        Scenario(
            name="WGM01_current_one_member_closure",
            description="Current adoption, singular structure, five declared checks, and clean projection close locally.",
            initial_state=MaintenanceState(),
            external_input_sequence=_good_sequence(),
            expected=ScenarioExpectation(expected_status="ok", required_trace_labels=("author_unit_bound", "singular_structure_ready", "unit_terminal_pass"), summary="one-member maintenance closes without install"),
            workflow=workflow,
            invariants=INVARIANTS,
        ),
        Scenario(
            name="WGM02_live_copy_dependency_blocks",
            description="A live dependency prevents deletion of the local FlowGuard copies.",
            initial_state=MaintenanceState(),
            external_input_sequence=(MaintenanceRequest("adopt"), MaintenanceRequest("reduce", local_copy_dependency_present=True)),
            expected=ScenarioExpectation(expected_status="ok", required_trace_labels=("local_copy_dependency_blocked",), summary="live dependency is visible and blocks reduction"),
            workflow=workflow,
            invariants=INVARIANTS,
        ),
        Scenario(
            name="WGM03_inferred_sixth_check_blocks",
            description="A nondeclared sixth check cannot enter the target inventory.",
            initial_state=MaintenanceState(),
            external_input_sequence=(MaintenanceRequest("adopt"), MaintenanceRequest("reduce"), MaintenanceRequest("validate", check_id="check:skillguard:invented-depth")),
            expected=ScenarioExpectation(expected_status="violation", expected_violation_names=("skillguard_adds_no_domain_depth",), required_trace_labels=("nondeclared_check_blocked",), summary="inferred target depth violates the hard boundary"),
            workflow=workflow,
            invariants=INVARIANTS,
        ),
        Scenario(
            name="WGM04_runtime_byte_mismatch_blocks",
            description="Package and bundled runtime bytes must match before reduction closes.",
            initial_state=MaintenanceState(),
            external_input_sequence=(MaintenanceRequest("adopt"), MaintenanceRequest("reduce", runtime_bytes_equal=False)),
            expected=ScenarioExpectation(expected_status="ok", required_trace_labels=("runtime_byte_identity_blocked",), summary="byte drift remains a visible blocker"),
            workflow=workflow,
            invariants=INVARIANTS,
        ),
        Scenario(
            name="WGM05_duplicate_authority_blocks",
            description="The obsolete local author-style suite cannot remain a second authority.",
            initial_state=MaintenanceState(),
            external_input_sequence=(MaintenanceRequest("adopt"), MaintenanceRequest("reduce", retain_obsolete_authority=True)),
            expected=ScenarioExpectation(expected_status="violation", expected_violation_names=("singular_flowguard_authority",), required_trace_labels=("duplicate_authority_blocked",), summary="duplicate author authority violates the reduction contract"),
            workflow=workflow,
            invariants=INVARIANTS,
        ),
        Scenario(
            name="WGM06_install_activation_blocks",
            description="Projection comparison cannot activate a global installation.",
            initial_state=MaintenanceState(),
            external_input_sequence=(MaintenanceRequest("adopt"), MaintenanceRequest("reduce"), *validated, MaintenanceRequest("project", activate_installation=True)),
            expected=ScenarioExpectation(expected_status="violation", expected_violation_names=("no_global_install",), required_trace_labels=("installation_activation_blocked",), summary="global activation violates the local scope"),
            workflow=workflow,
            invariants=INVARIANTS,
        ),
    )


__all__ = [
    "CONTRACT_MODEL",
    "DECLARED_CHECKS",
    "DEVELOPMENT_PROCESS",
    "INVARIANTS",
    "MAINTENANCE_UNIT_ID",
    "MEMBERS",
    "STRUCTURE_MESH",
    "TEST_MESH",
    "build_workflow",
    "scenarios",
]

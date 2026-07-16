"""FlowGuard model for task-declared Guard purpose and proof ordering.

The family catalog is only a capability/oracle baseline. A real Guard
candidate is admitted only after the current task/model instance declares one
or more failures and proves each selected failure with task-local native cases.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

from flowguard import FunctionResult, Invariant, InvariantResult, Workflow
from flowguard.explorer import Explorer


@dataclass(frozen=True)
class CandidateRequest:
    family_catalog_available: bool = True
    task_declaration_present: bool = True
    selected_failures_nonempty: bool = True
    selected_oracles_known: bool = True
    task_good_case_present: bool = True
    exactly_one_bad_per_failure: bool = True
    native_proof_passes: bool = True
    candidate_constructed_before_task_proof: bool = False
    candidate_binding_present: bool = True
    candidate_fingerprint_current: bool = True
    model_instance_matches: bool = True
    verifier_runs_before_guard_evaluation: bool = True


@dataclass(frozen=True)
class ProvenTaskPurpose:
    request: CandidateRequest


@dataclass(frozen=True)
class CandidateReady:
    request: CandidateRequest


@dataclass(frozen=True)
class GuardEvaluationReady:
    task_contract_bound: bool


@dataclass(frozen=True)
class Blocked:
    reason: str


@dataclass(frozen=True)
class State:
    family_baseline_ready: bool = False
    task_purpose_declared: bool = False
    task_purpose_proven: bool = False
    task_binding_frozen: bool = False
    candidate_constructed: bool = False
    candidate_verified: bool = False
    guard_evaluation_started: bool = False


class DeclareAndProveTaskPurpose:
    name = "DeclareAndProveTaskPurpose"
    reads = ()
    writes = (
        "family_baseline_ready",
        "task_purpose_declared",
        "task_purpose_proven",
        "task_binding_frozen",
    )
    accepted_input_type = CandidateRequest
    input_description = "CandidateRequest x initial state"
    output_description = "ProvenTaskPurpose or Blocked"
    idempotency = "The same declaration, cases, native oracles, and identities yield one proof binding."

    def apply(self, request: CandidateRequest, state: State) -> Iterable[FunctionResult]:
        if not request.family_catalog_available:
            yield FunctionResult(
                Blocked("guard_family_oracle_catalog_missing"), state, "family_catalog_missing_blocked"
            )
            return
        if not request.task_declaration_present:
            yield FunctionResult(
                Blocked("task_model_purpose_declaration_missing"), state, "task_declaration_missing_blocked"
            )
            return
        if not request.selected_failures_nonempty:
            yield FunctionResult(
                Blocked("task_model_selected_failures_empty"), state, "selected_failures_empty_blocked"
            )
            return
        if not request.selected_oracles_known:
            yield FunctionResult(
                Blocked("task_model_selected_oracle_unknown"), state, "selected_oracle_unknown_blocked"
            )
            return
        if not request.task_good_case_present:
            yield FunctionResult(
                Blocked("task_model_known_good_missing"), state, "task_good_missing_blocked"
            )
            return
        if not request.exactly_one_bad_per_failure:
            yield FunctionResult(
                Blocked("task_model_bad_case_cardinality_invalid"), state, "task_bad_cardinality_blocked"
            )
            return
        if not request.native_proof_passes:
            yield FunctionResult(
                Blocked("task_model_native_purpose_proof_failed"),
                state,
                "native_purpose_proof_failed_blocked",
            )
            return
        if request.candidate_constructed_before_task_proof:
            yield FunctionResult(
                Blocked("candidate_constructed_before_task_purpose_proof"),
                state,
                "premature_candidate_blocked",
            )
            return
        yield FunctionResult(
            ProvenTaskPurpose(request),
            replace(
                state,
                family_baseline_ready=True,
                task_purpose_declared=True,
                task_purpose_proven=True,
                task_binding_frozen=True,
            ),
            "task_purpose_declared_and_proven",
        )


class ConstructGuardCandidate:
    name = "ConstructGuardCandidate"
    reads = ("task_binding_frozen",)
    writes = ("candidate_constructed",)
    accepted_input_type = ProvenTaskPurpose
    input_description = "ProvenTaskPurpose x state"
    output_description = "CandidateReady or Blocked"
    idempotency = "One frozen task binding produces one exact Guard candidate binding."

    def apply(self, input_obj: ProvenTaskPurpose, state: State) -> Iterable[FunctionResult]:
        if not (
            state.task_purpose_declared and state.task_purpose_proven and state.task_binding_frozen
        ):
            yield FunctionResult(Blocked("candidate_requires_task_purpose_proof"), state, "purpose_order_blocked")
            return
        yield FunctionResult(
            CandidateReady(input_obj.request),
            replace(state, candidate_constructed=True),
            "candidate_constructed",
        )


class VerifyCandidateBeforeGuardEvaluation:
    name = "VerifyCandidateBeforeGuardEvaluation"
    reads = ("task_binding_frozen", "candidate_constructed")
    writes = ("candidate_verified", "guard_evaluation_started")
    accepted_input_type = CandidateReady
    input_description = "Guard candidate x current task/model contract"
    output_description = "GuardEvaluationReady or Blocked"
    idempotency = "Verification compares exact task, proof, model, and candidate identities without mutation."

    def apply(self, input_obj: CandidateReady, state: State) -> Iterable[FunctionResult]:
        request = input_obj.request
        if not state.task_binding_frozen or not state.candidate_constructed:
            yield FunctionResult(Blocked("candidate_verifier_order_invalid"), state, "purpose_order_blocked")
            return
        if not request.candidate_binding_present:
            yield FunctionResult(
                Blocked("guard_candidate_task_purpose_missing"), state, "candidate_purpose_missing_blocked"
            )
            return
        if not request.candidate_fingerprint_current:
            yield FunctionResult(
                Blocked("guard_candidate_task_purpose_stale"), state, "candidate_purpose_stale_blocked"
            )
            return
        if not request.model_instance_matches:
            yield FunctionResult(
                Blocked("guard_candidate_model_instance_mismatch"),
                state,
                "candidate_model_instance_mismatch_blocked",
            )
            return
        if not request.verifier_runs_before_guard_evaluation:
            yield FunctionResult(
                Blocked("guard_evaluation_started_before_task_purpose_verifier"),
                state,
                "candidate_verifier_order_blocked",
            )
            return
        yield FunctionResult(
            GuardEvaluationReady(True),
            replace(state, candidate_verified=True, guard_evaluation_started=True),
            "guard_evaluation_ready",
        )


def family_baseline_never_authorizes_candidate(state: State, trace: object) -> InvariantResult:
    if state.candidate_constructed and not (
        state.task_purpose_declared and state.task_purpose_proven and state.task_binding_frozen
    ):
        return InvariantResult.fail(
            "A family baseline authorized a candidate without a declared and proven task/model purpose"
        )
    return InvariantResult.pass_()


def guard_evaluation_requires_current_candidate(state: State, trace: object) -> InvariantResult:
    if state.guard_evaluation_started and not (
        state.task_purpose_declared
        and state.task_purpose_proven
        and state.task_binding_frozen
        and state.candidate_constructed
        and state.candidate_verified
    ):
        return InvariantResult.fail(
            "Guard evaluation started without a declared, proven, frozen, constructed, and verified task-bound candidate"
        )
    return InvariantResult.pass_()


EXTERNAL_INPUTS = (
    CandidateRequest(),
    CandidateRequest(family_catalog_available=False),
    CandidateRequest(task_declaration_present=False),
    CandidateRequest(selected_failures_nonempty=False),
    CandidateRequest(selected_oracles_known=False),
    CandidateRequest(task_good_case_present=False),
    CandidateRequest(exactly_one_bad_per_failure=False),
    CandidateRequest(native_proof_passes=False),
    CandidateRequest(candidate_constructed_before_task_proof=True),
    CandidateRequest(candidate_binding_present=False),
    CandidateRequest(candidate_fingerprint_current=False),
    CandidateRequest(model_instance_matches=False),
    CandidateRequest(verifier_runs_before_guard_evaluation=False),
)

INVARIANTS = (
    Invariant(
        "family_baseline_never_authorizes_candidate",
        "The family capability catalog is regression evidence, never the current task purpose authority.",
        family_baseline_never_authorizes_candidate,
    ),
    Invariant(
        "guard_evaluation_requires_current_candidate",
        "Every Guard evaluation follows task declaration, per-failure proof, binding, construction, and exact verification.",
        guard_evaluation_requires_current_candidate,
    ),
)

MAX_SEQUENCE_LENGTH = 3


def build_workflow() -> Workflow:
    return Workflow(
        (
            DeclareAndProveTaskPurpose(),
            ConstructGuardCandidate(),
            VerifyCandidateBeforeGuardEvaluation(),
        ),
        name="worldguard_guard_candidate_purpose_order",
    )


def initial_state() -> State:
    return State()


def terminal_predicate(current_input: object, state: State, trace: object) -> bool:
    return isinstance(current_input, (Blocked, GuardEvaluationReady))


def review_guard_candidate_purpose_order():
    return Explorer(
        workflow=build_workflow(),
        initial_states=(initial_state(),),
        external_inputs=EXTERNAL_INPUTS,
        invariants=INVARIANTS,
        max_sequence_length=MAX_SEQUENCE_LENGTH,
        terminal_predicate=terminal_predicate,
        required_labels=(
            "task_purpose_declared_and_proven",
            "candidate_constructed",
            "guard_evaluation_ready",
            "family_catalog_missing_blocked",
            "task_declaration_missing_blocked",
            "selected_failures_empty_blocked",
            "selected_oracle_unknown_blocked",
            "task_good_missing_blocked",
            "task_bad_cardinality_blocked",
            "native_purpose_proof_failed_blocked",
            "premature_candidate_blocked",
            "candidate_purpose_missing_blocked",
            "candidate_purpose_stale_blocked",
            "candidate_model_instance_mismatch_blocked",
            "candidate_verifier_order_blocked",
        ),
    ).explore()


if __name__ == "__main__":
    report = review_guard_candidate_purpose_order()
    print(report.format_text())
    raise SystemExit(0 if report.ok else 1)

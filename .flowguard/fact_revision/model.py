"""Executable FlowGuard model for WorldGuard task-local fact revision."""

from __future__ import annotations

from dataclasses import dataclass, replace

from flowguard import (
    FunctionResult,
    Invariant,
    InvariantResult,
    Scenario,
    ScenarioExpectation,
    Workflow,
)


FLOWGUARD_MODEL_MARKER = "flowguard-executable-model"


@dataclass(frozen=True)
class RevisionRequest:
    action: str
    base_current: bool = True
    preservation_ok: bool = True
    has_contradiction: bool = False
    contradiction_acknowledged: bool = False
    regression_current: bool = True
    holdout_current: bool = True
    evidence_cardinality_exact: bool = True
    task_owner_current: bool = True


@dataclass(frozen=True)
class RevisionState:
    phase: str = "planned"
    preview_frozen: bool = False
    base_current: bool = True
    preservation_ok: bool = True
    contradiction_visible: bool = False
    contradiction_acknowledged: bool = False
    regression_current: bool = False
    holdout_current: bool = False
    evidence_cardinality_exact: bool = False
    activated: bool = False
    task_owner_current: bool = False
    revalidation_required: bool = False
    task_closed: bool = False
    terminal_status: str = ""


class BuildFactRevisionPreview:
    """Map one preview request and current state to every allowed next state."""

    name = "BuildFactRevisionPreview"
    accepted_input_type = RevisionRequest
    reads = ("action", "base_current", "preservation_ok", "has_contradiction")
    writes = (
        "phase",
        "preview_frozen",
        "base_current",
        "preservation_ok",
        "contradiction_visible",
        "terminal_status",
    )
    input_description = "one immutable task-local fact-revision preview request"
    output_description = "one frozen preview or a visible typed block"
    idempotency = "the same base and transaction produce the same preview state"

    def apply(self, request: RevisionRequest, state: RevisionState):
        if request.action != "preview":
            yield FunctionResult(request, state, label="preview_not_requested")
            return
        if state.phase != "planned":
            yield FunctionResult(
                request,
                replace(state, phase="blocked", terminal_status="order"),
                label="preview_order_blocked",
            )
            return
        if not request.base_current:
            yield FunctionResult(
                request,
                replace(
                    state,
                    phase="blocked",
                    base_current=False,
                    terminal_status="stale_base",
                ),
                label="stale_base_blocked",
            )
            return
        if not request.preservation_ok:
            yield FunctionResult(
                request,
                replace(
                    state,
                    phase="blocked",
                    preservation_ok=False,
                    terminal_status="preservation",
                ),
                label="preservation_change_blocked",
            )
            return
        yield FunctionResult(
            request,
            replace(
                state,
                phase="previewed",
                preview_frozen=True,
                base_current=True,
                preservation_ok=True,
                contradiction_visible=request.has_contradiction,
            ),
            label=(
                "contradiction_visible_in_preview"
                if request.has_contradiction
                else "preview_frozen"
            ),
        )


class ActivateFactRevision:
    """Map one activation request and current preview to every allowed terminal."""

    name = "ActivateFactRevision"
    accepted_input_type = RevisionRequest
    reads = (
        "action",
        "contradiction_acknowledged",
        "regression_current",
        "holdout_current",
        "evidence_cardinality_exact",
        "task_owner_current",
    )
    writes = (
        "phase",
        "contradiction_acknowledged",
        "regression_current",
        "holdout_current",
        "evidence_cardinality_exact",
        "activated",
        "task_owner_current",
        "revalidation_required",
        "terminal_status",
    )
    input_description = "one activation request bound to the exact preview"
    output_description = "activated or one visible evidence/acknowledgement block"
    idempotency = "one transaction id may produce at most one activation receipt"

    def apply(self, request: RevisionRequest, state: RevisionState):
        if request.action == "unsafe_activate":
            yield FunctionResult(
                request,
                replace(
                    state,
                    phase="terminal",
                    activated=True,
                    terminal_status="unsafe",
                ),
                label="unsafe_activation_attempted",
            )
            return
        if request.action != "activate":
            yield FunctionResult(request, state, label="activation_not_requested")
            return
        if state.phase != "previewed" or not state.preview_frozen:
            yield FunctionResult(
                request,
                replace(state, phase="blocked", terminal_status="missing_preview"),
                label="missing_preview_blocked",
            )
            return
        if state.contradiction_visible and not request.contradiction_acknowledged:
            yield FunctionResult(
                request,
                replace(
                    state,
                    phase="blocked",
                    contradiction_acknowledged=False,
                    terminal_status="contradiction_acknowledgement",
                ),
                label="unacknowledged_contradiction_blocked",
            )
            return
        if (
            not request.regression_current
            or not request.holdout_current
            or not request.evidence_cardinality_exact
            or not request.task_owner_current
        ):
            yield FunctionResult(
                request,
                replace(
                    state,
                    phase="blocked",
                    contradiction_acknowledged=request.contradiction_acknowledged,
                    regression_current=request.regression_current,
                    holdout_current=request.holdout_current,
                    evidence_cardinality_exact=request.evidence_cardinality_exact,
                    task_owner_current=request.task_owner_current,
                    terminal_status="evidence",
                ),
                label="activation_evidence_blocked",
            )
            return
        yield FunctionResult(
            request,
            replace(
                state,
                phase="terminal",
                contradiction_acknowledged=request.contradiction_acknowledged,
                regression_current=True,
                holdout_current=True,
                evidence_cardinality_exact=True,
                task_owner_current=True,
                activated=True,
                revalidation_required=True,
                terminal_status="task_local_revalidation_required",
            ),
            label="revision_activated_for_task_local_revalidation",
        )


def revision_invariants() -> tuple[Invariant, ...]:
    def no_stale_activation(state: RevisionState, _trace):
        if state.activated and not state.base_current:
            return InvariantResult.fail("stale base reached activation")
        return InvariantResult.pass_()

    def preservation(state: RevisionState, _trace):
        if state.activated and not state.preservation_ok:
            return InvariantResult.fail("preserved fact changed during activation")
        return InvariantResult.pass_()

    def contradiction_visible(state: RevisionState, _trace):
        if state.activated and state.contradiction_visible and not state.contradiction_acknowledged:
            return InvariantResult.fail("contradiction was activated without acknowledgement")
        return InvariantResult.pass_()

    def evidence_bound(state: RevisionState, _trace):
        if state.activated and not (
            state.preview_frozen
            and state.regression_current
            and state.holdout_current
            and state.evidence_cardinality_exact
        ):
            return InvariantResult.fail(
                "activation is not bound to a frozen preview and current regression/holdout evidence"
            )
        return InvariantResult.pass_()

    def activation_returns_to_same_owner(state: RevisionState, _trace):
        if state.activated and not (
            state.task_owner_current
            and state.revalidation_required
            and not state.task_closed
            and state.terminal_status == "task_local_revalidation_required"
        ):
            return InvariantResult.fail(
                "fact activation bypassed same-owner task-local revalidation"
            )
        return InvariantResult.pass_()

    return (
        Invariant(
            "fact_revision_requires_current_base",
            "A stale base cannot reach activation.",
            no_stale_activation,
        ),
        Invariant(
            "fact_revision_preserves_declared_facts",
            "Declared preserved facts cannot change.",
            preservation,
        ),
        Invariant(
            "fact_revision_surfaces_contradictions",
            "A visible contradiction requires explicit activation acknowledgement.",
            contradiction_visible,
        ),
        Invariant(
            "fact_revision_activation_is_evidence_bound",
            "Activation requires the frozen preview plus current regression and holdout evidence.",
            evidence_bound,
        ),
        Invariant(
            "fact_revision_activation_returns_to_same_task_owner",
            "Activation is an intermediate candidate handoff and never task closure.",
            activation_returns_to_same_owner,
        ),
    )


INVARIANTS = revision_invariants()


def build_workflow() -> Workflow:
    return Workflow(
        (BuildFactRevisionPreview(), ActivateFactRevision()),
        name="worldguard_fact_revision",
    )


def scenarios() -> tuple[Scenario, ...]:
    workflow = build_workflow()
    return (
        Scenario(
            name="WFR01_current_revision_activates",
            description="A current preview with complete evidence activates.",
            initial_state=RevisionState(),
            external_input_sequence=(
                RevisionRequest("preview"),
                RevisionRequest("activate"),
            ),
            expected=ScenarioExpectation(
                expected_status="ok",
                required_trace_labels=(
                    "preview_frozen",
                    "revision_activated_for_task_local_revalidation",
                ),
                summary="current evidence-bound fact candidate returns for task-local revalidation",
            ),
            workflow=workflow,
            invariants=INVARIANTS,
        ),
        Scenario(
            name="WFR02_contradiction_needs_acknowledgement",
            description="A contradiction stays visible and blocks unacknowledged activation.",
            initial_state=RevisionState(),
            external_input_sequence=(
                RevisionRequest("preview", has_contradiction=True),
                RevisionRequest("activate", contradiction_acknowledged=False),
            ),
            expected=ScenarioExpectation(
                expected_status="ok",
                required_trace_labels=(
                    "contradiction_visible_in_preview",
                    "unacknowledged_contradiction_blocked",
                ),
                summary="visible contradiction blocks until acknowledged",
            ),
            workflow=workflow,
            invariants=INVARIANTS,
        ),
        Scenario(
            name="WFR03_stale_base_blocks",
            description="A stale base cannot produce an activatable preview.",
            initial_state=RevisionState(),
            external_input_sequence=(RevisionRequest("preview", base_current=False),),
            expected=ScenarioExpectation(
                expected_status="ok",
                required_trace_labels=("stale_base_blocked",),
                summary="stale base is a visible block",
            ),
            workflow=workflow,
            invariants=INVARIANTS,
        ),
        Scenario(
            name="WFR04_preservation_change_blocks",
            description="A requested change to a preserved fact is rejected.",
            initial_state=RevisionState(),
            external_input_sequence=(
                RevisionRequest("preview", preservation_ok=False),
            ),
            expected=ScenarioExpectation(
                expected_status="ok",
                required_trace_labels=("preservation_change_blocked",),
                summary="preservation violation is a visible block",
            ),
            workflow=workflow,
            invariants=INVARIANTS,
        ),
        Scenario(
            name="WFR05_missing_holdout_blocks",
            description="Activation requires current holdout evidence.",
            initial_state=RevisionState(),
            external_input_sequence=(
                RevisionRequest("preview"),
                RevisionRequest("activate", holdout_current=False),
            ),
            expected=ScenarioExpectation(
                expected_status="ok",
                required_trace_labels=("preview_frozen", "activation_evidence_blocked"),
                summary="missing holdout evidence blocks activation",
            ),
            workflow=workflow,
            invariants=INVARIANTS,
        ),
        Scenario(
            name="WFR06_unsafe_activation_is_counterexample",
            description="A bypass that activates without preview or evidence violates the hard invariant.",
            initial_state=RevisionState(),
            external_input_sequence=(RevisionRequest("unsafe_activate"),),
            expected=ScenarioExpectation(
                expected_status="violation",
                expected_violation_names=(
                    "fact_revision_activation_is_evidence_bound",
                    "fact_revision_activation_returns_to_same_task_owner",
                ),
                required_trace_labels=("unsafe_activation_attempted",),
                summary="unsafe activation is rejected by the model",
            ),
            workflow=workflow,
            invariants=INVARIANTS,
        ),
        Scenario(
            name="WFR07_duplicate_evidence_kind_blocks",
            description="Duplicate regression or holdout evidence cannot replace the exact pair.",
            initial_state=RevisionState(),
            external_input_sequence=(
                RevisionRequest("preview"),
                RevisionRequest("activate", evidence_cardinality_exact=False),
            ),
            expected=ScenarioExpectation(
                expected_status="ok",
                required_trace_labels=("preview_frozen", "activation_evidence_blocked"),
                summary="duplicate evidence cardinality blocks activation",
            ),
            workflow=workflow,
            invariants=INVARIANTS,
        ),
    )


__all__ = ["INVARIANTS", "build_workflow", "scenarios"]

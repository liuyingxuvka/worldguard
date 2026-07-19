"""Executable FlowGuard models for WorldGuard semantic rollout.

Both blocks implement Input x State -> Set(Output x State).  The first models
the lifecycle of the new status/receipt fields; the second models runtime
ordering.  They deliberately keep semantic ownership inside WorldGuard.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

from flowguard import FunctionResult, Invariant, InvariantResult, Workflow
from flowguard.explorer import Explorer


@dataclass(frozen=True)
class Tick:
    pass


@dataclass(frozen=True)
class Action:
    name: str


@dataclass(frozen=True)
class FieldState:
    aggregate_status_preserved: bool = False
    component_statuses_added: bool = False
    bindings_added: bool = False
    receipt_added: bool = False
    conservative_projection_added: bool = False


class FieldLifecycleBlock:
    """Tick x FieldState -> Set(Action x FieldState)."""

    name = "FieldLifecycleBlock"

    def apply(self, _input: Tick, state: FieldState) -> Iterable[FunctionResult]:
        if not state.aggregate_status_preserved:
            yield _result(
                "aggregate_status_preserved",
                replace(state, aggregate_status_preserved=True),
            )
        elif not state.component_statuses_added:
            yield _result("component_statuses_added", replace(state, component_statuses_added=True))
        elif not state.bindings_added:
            yield _result("typed_bindings_added", replace(state, bindings_added=True))
        elif not state.receipt_added:
            yield _result("native_receipt_added", replace(state, receipt_added=True))
        elif not state.conservative_projection_added:
            yield _result("conservative_projection_added", replace(state, conservative_projection_added=True))


@dataclass(frozen=True)
class RolloutState:
    contract_loaded: bool = False
    structural_checked: bool = False
    provider_checked: bool = False
    semantic_executed: bool = False
    aggregate_projected: bool = False
    portable_native_runtime_bound: bool = False
    receipt_emitted: bool = False


class SemanticRolloutBlock:
    """Tick x RolloutState -> Set(Action x RolloutState)."""

    name = "SemanticRolloutBlock"

    def apply(self, _input: Tick, state: RolloutState) -> Iterable[FunctionResult]:
        if not state.contract_loaded:
            yield _result("contract_loaded", replace(state, contract_loaded=True))
        elif not state.structural_checked:
            yield _result("structural_checked", replace(state, structural_checked=True))
        elif not state.provider_checked:
            yield _result("provider_checked", replace(state, provider_checked=True))
        elif not state.semantic_executed:
            yield _result("semantic_executed_or_explicitly_skipped", replace(state, semantic_executed=True))
        elif not state.aggregate_projected:
            yield _result("fail_closed_projection_applied", replace(state, aggregate_projected=True))
        elif not state.portable_native_runtime_bound:
            yield _result(
                "portable_native_runtime_bound",
                replace(state, portable_native_runtime_bound=True),
            )
        elif not state.receipt_emitted:
            yield _result("native_depth_receipt_emitted", replace(state, receipt_emitted=True))


def _result(label: str, state: object) -> FunctionResult:
    return FunctionResult(output=Action(label), new_state=state, label=label)


def _field_invariant(state: FieldState, _trace) -> InvariantResult:
    if state.component_statuses_added and not state.aggregate_status_preserved:
        return InvariantResult.fail(
            "component statuses replaced rather than preserved aggregate status"
        )
    if state.bindings_added and not state.component_statuses_added:
        return InvariantResult.fail("bindings exist before component status ownership")
    if state.receipt_added and not state.bindings_added:
        return InvariantResult.fail("receipt exists without typed binding provenance")
    if state.conservative_projection_added and not state.receipt_added:
        return InvariantResult.fail("aggregate projection exists before native receipt")
    return InvariantResult.pass_()


def _rollout_invariant(state: RolloutState, _trace) -> InvariantResult:
    if state.structural_checked and not state.contract_loaded:
        return InvariantResult.fail("structural checks ran before contract load")
    if state.provider_checked and not state.structural_checked:
        return InvariantResult.fail("provider status was inferred before structural checks")
    if state.semantic_executed and not state.provider_checked:
        return InvariantResult.fail("semantic execution bypassed provider status")
    if state.aggregate_projected and not state.semantic_executed:
        return InvariantResult.fail("aggregate pass could be projected from structure alone")
    if state.portable_native_runtime_bound and not state.aggregate_projected:
        return InvariantResult.fail("portable runtime bound before conservative projection")
    if state.receipt_emitted and not state.portable_native_runtime_bound:
        return InvariantResult.fail("receipt emitted without the installed portable native runtime")
    return InvariantResult.pass_()


def _explore(block, initial_state, invariant, labels, success):
    report = Explorer(
        workflow=Workflow((block,), name=block.name),
        initial_states=(initial_state,),
        external_inputs=(Tick(),),
        invariants=(Invariant(name=f"{block.name}_ordering", description="Required ownership and rollout order", predicate=invariant),),
        max_sequence_length=len(labels) + 1,
        terminal_predicate=lambda _input, state, _trace: success(state),
        success_predicate=lambda state, _trace: success(state),
        required_labels=labels,
        progress_steps=0,
    ).explore()
    return {
        "ok": report.ok,
        "summary": report.summary,
        "violation_count": len(report.violations),
        "reachability_failure_count": len(report.reachability_failures),
    }


def run_checks() -> dict[str, object]:
    field_labels = (
        "aggregate_status_preserved",
        "component_statuses_added",
        "typed_bindings_added",
        "native_receipt_added",
        "conservative_projection_added",
    )
    rollout_labels = (
        "contract_loaded",
        "structural_checked",
        "provider_checked",
        "semantic_executed_or_explicitly_skipped",
        "fail_closed_projection_applied",
        "portable_native_runtime_bound",
        "native_depth_receipt_emitted",
    )
    field = _explore(
        FieldLifecycleBlock(),
        FieldState(),
        _field_invariant,
        field_labels,
        lambda state: state.conservative_projection_added,
    )
    rollout = _explore(
        SemanticRolloutBlock(),
        RolloutState(),
        _rollout_invariant,
        rollout_labels,
        lambda state: state.receipt_emitted,
    )
    hazards = {
        "semantic_without_provider": bool(
            not _rollout_invariant(RolloutState(semantic_executed=True), ()).ok
        ),
        "aggregate_from_structure_only": bool(
            not _rollout_invariant(
                RolloutState(contract_loaded=True, structural_checked=True, aggregate_projected=True),
                (),
            ).ok
        ),
        "receipt_without_binding": bool(
            not _field_invariant(
                FieldState(
                    aggregate_status_preserved=True,
                    component_statuses_added=True,
                    receipt_added=True,
                ),
                (),
            ).ok
        ),
        "receipt_without_portable_native_runtime": bool(
            not _rollout_invariant(RolloutState(receipt_emitted=True), ()).ok
        ),
    }
    return {
        "ok": field["ok"] and rollout["ok"] and all(hazards.values()),
        "field_lifecycle": field,
        "semantic_rollout": rollout,
        "hazards": hazards,
    }

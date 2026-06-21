from __future__ import annotations

from worldguard.contracts import GuardContract
from worldguard.status import GuardStatus

from ._helpers import error, result, semantics_text


def run(contract: GuardContract):
    guard = "EventGuard"
    text = semantics_text(contract)
    events = contract.inputs.get("events") or contract.world_model.data.get("event_line") or []
    event_model = contract.inputs.get("event_model", {})

    if any(word in text for word in ["numeric", "dynamics", "thermodynamics", "continuous"]):
        return result(
            contract,
            guard,
            GuardStatus.BOUNDARY_EXCEEDED,
            channel="boundary",
            impact="marks_boundary",
            boundary={"owner": guard, "unsupported_claim_parts": ["numeric_dynamics"]},
            errors=[error("EVENT_BOUNDARY_NUMERIC_DYNAMICS", "EventGuard does not own numeric dynamics.")],
        )

    if not events and not event_model:
        return result(
            contract,
            guard,
            GuardStatus.GAP,
            channel="gap",
            impact="creates_gap",
            missing_slots=[{"needed": "events or event_model"}],
            errors=[error("EVENT_MISSING_EVENT_MODEL", "No event model was supplied.")],
        )

    if event_model.get("exclusive_violation") or event_model.get("contradictory_fluents"):
        return result(
            contract,
            guard,
            GuardStatus.FAIL,
            channel="event",
            impact="supports_fail",
            errors=[error("EVENT_CONTRADICTORY_FLUENTS", "Contradictory fluents are declared.")],
            counterexamples=[{"kind": "trace", "steps": event_model.get("contradictory_fluents", [])}],
        )

    missing = event_model.get("missing_axioms", [])
    if missing:
        return result(
            contract,
            guard,
            GuardStatus.GAP,
            channel="gap",
            impact="creates_gap",
            missing_slots=[{"needed": item} for item in missing],
            errors=[error("EVENT_MISSING_INITIATION_AXIOM", "Required event axiom is missing.")],
        )

    return result(
        contract,
        guard,
        GuardStatus.PASS,
        channel="event",
        impact="supports_pass",
        payload={"events_observed": len(events) or len(event_model.get("events", []))},
        supported=True,
        consumed_inputs={"events": events, "event_model": event_model},
    )

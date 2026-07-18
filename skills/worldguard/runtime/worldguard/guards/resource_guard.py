from __future__ import annotations

from worldguard.contracts import GuardContract
from worldguard.status import GuardStatus

from ._helpers import error, result, semantics_text


def run(contract: GuardContract):
    guard = "ResourceGuard"
    text = semantics_text(contract)
    resources = contract.inputs.get("resources") or contract.world_model.data.get("resources") or {}
    places = resources.get("places", {}) if isinstance(resources, dict) else {}
    transitions = resources.get("transitions", []) if isinstance(resources, dict) else []
    capacities = resources.get("capacities", {}) if isinstance(resources, dict) else {}

    if any(word in text for word in ["permission", "authorized", "forbidden", "obligation"]):
        return result(
            contract,
            guard,
            GuardStatus.BOUNDARY_EXCEEDED,
            channel="boundary",
            impact="marks_boundary",
            boundary={"owner": guard, "unsupported_claim_parts": ["norm_authorization"]},
            errors=[error("RESOURCE_BOUNDARY_NORM_AUTHORIZATION", "ResourceGuard does not own permission.")],
        )

    if not places or not transitions:
        return result(
            contract,
            guard,
            GuardStatus.GAP,
            channel="gap",
            impact="creates_gap",
            missing_slots=[{"needed": "places and transitions"}],
            errors=[error("RESOURCE_MISSING_RESOURCE_MODEL", "No CPN resource model was supplied.")],
        )

    for transition in transitions:
        for need in transition.get("consumes", []):
            tokens = places.get(need.get("place"), [])
            available = sum(
                token.get("qty", 0) for token in tokens if token.get("color") == need.get("color")
            )
            if available < need.get("qty", 0):
                return result(
                    contract,
                    guard,
                    GuardStatus.GAP,
                    channel="gap",
                    impact="creates_gap",
                    missing_slots=[
                        {
                            "transition": transition.get("id"),
                            "place": need.get("place"),
                            "color": need.get("color"),
                            "required_qty": need.get("qty"),
                            "available_qty": available,
                        }
                    ],
                    errors=[error("RESOURCE_MISSING_TOKEN", "Required colored token is missing.")],
                )
        for produced in transition.get("produces", []):
            capacity = capacities.get(produced.get("place"))
            if capacity is not None and produced.get("qty", 0) > capacity:
                return result(
                    contract,
                    guard,
                    GuardStatus.FAIL,
                    channel="resource",
                    impact="supports_fail",
                    errors=[error("RESOURCE_CAPACITY_OVERFLOW", "Produced tokens exceed place capacity.")],
                    counterexamples=[{"kind": "trace", "steps": [produced]}],
                )

    return result(
        contract,
        guard,
        GuardStatus.PASS,
        channel="resource",
        impact="supports_pass",
        payload={"transition_count": len(transitions)},
        supported=True,
        consumed_inputs={"resources": resources},
    )

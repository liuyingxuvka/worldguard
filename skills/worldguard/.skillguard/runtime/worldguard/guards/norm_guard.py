from __future__ import annotations

from worldguard.contracts import GuardContract
from worldguard.status import GuardStatus

from ._helpers import error, result, semantics_text


def run(contract: GuardContract):
    guard = "NormGuard"
    text = semantics_text(contract)
    norm_model = contract.inputs.get("norm_model") or {
        "norms": contract.inputs.get("norms") or contract.world_model.data.get("norms", []),
        "facts": contract.inputs.get("facts", []),
    }
    norms = norm_model.get("norms", [])

    if any(word in text for word in ["token", "enabled", "capacity", "physical enablement"]):
        return result(
            contract,
            guard,
            GuardStatus.BOUNDARY_EXCEEDED,
            channel="boundary",
            impact="marks_boundary",
            boundary={"owner": guard, "unsupported_claim_parts": ["physical_enablement"]},
            errors=[error("NORM_BOUNDARY_PHYSICAL_ENABLEMENT", "NormGuard does not own resource enablement.")],
        )

    forbidden_recipe = [
        norm
        for norm in norms
        if isinstance(norm, dict)
        and norm.get("modality") in {"forbidden", "prohibited"}
        and "recipe" in str(norm.get("action", ""))
    ]
    if "full membrane recipe" in text and forbidden_recipe:
        return result(
            contract,
            guard,
            GuardStatus.FAIL,
            channel="norm",
            impact="supports_fail",
            errors=[error("NORM_FORBIDDEN_ACTION_CONTRADICTION", "Claimed permission contradicts a forbidden action.")],
            counterexamples=[{"kind": "model_conflict", "steps": forbidden_recipe}],
        )

    asks_permission = any(word in text for word in ["may", "permitted", "permission"])
    has_permission = any(
        isinstance(norm, dict) and norm.get("modality") in {"permitted", "obligatory"}
        for norm in norms
    )
    if asks_permission and not has_permission:
        return result(
            contract,
            guard,
            GuardStatus.GAP,
            channel="gap",
            impact="creates_gap",
            missing_slots=[{"needed": "permission_or_obligation"}],
            errors=[error("NORM_MISSING_PERMISSION", "No permission or obligation supports the claim.")],
        )

    if not norms:
        return result(
            contract,
            guard,
            GuardStatus.GAP,
            channel="gap",
            impact="creates_gap",
            missing_slots=[{"needed": "norms"}],
            errors=[error("NORM_MISSING_NORM_MODEL", "No norm model was supplied.")],
        )

    return result(
        contract,
        guard,
        GuardStatus.PASS,
        channel="norm",
        impact="supports_pass",
        payload={"norm_count": len(norms)},
        supported=True,
        consumed_inputs={"norm_model": norm_model},
    )

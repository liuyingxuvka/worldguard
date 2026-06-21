from __future__ import annotations

from worldguard.contracts import GuardContract
from worldguard.status import GuardStatus

from ._helpers import error, result, semantics_text


def run(contract: GuardContract):
    guard = "ConflictGuard"
    text = semantics_text(contract)
    game_model = contract.inputs.get("game_model") or {
        "payoffs": contract.world_model.data.get("conflict_payoffs", []),
        "transitions": contract.world_model.data.get("conflict_transitions", []),
    }
    payoffs = game_model.get("payoffs", [])
    transitions = game_model.get("transitions", [])

    if any(word in text for word in ["obligation", "permission", "forbidden", "deontic"]):
        return result(
            contract,
            guard,
            GuardStatus.BOUNDARY_EXCEEDED,
            channel="boundary",
            impact="marks_boundary",
            boundary={"owner": guard, "unsupported_claim_parts": ["deontic_obligation"]},
            errors=[error("CONFLICT_BOUNDARY_DEONTIC_OBLIGATION", "ConflictGuard does not own norms.")],
        )

    for transition in transitions:
        probs = transition.get("probabilities")
        if probs and abs(sum(probs) - 1.0) > 0.0001:
            return result(
                contract,
                guard,
                GuardStatus.FAIL,
                channel="conflict",
                impact="supports_fail",
                errors=[error("CONFLICT_INVALID_PROBABILITY", "Transition probabilities do not sum to 1.")],
                counterexamples=[{"kind": "trace", "steps": [transition]}],
            )

    if "full membrane recipe" in text and any("C_block_recipe_release" in str(row) for row in payoffs):
        return result(
            contract,
            guard,
            GuardStatus.FAIL,
            channel="conflict",
            impact="supports_fail",
            errors=[error("CONFLICT_POLICY_CONTRADICTION", "Declared payoff policy contradicts full recipe sharing.")],
            counterexamples=[{"kind": "trace", "steps": payoffs}],
        )

    if not payoffs:
        return result(
            contract,
            guard,
            GuardStatus.GAP,
            channel="gap",
            impact="creates_gap",
            missing_slots=[{"needed": "payoff_vector"}],
            errors=[error("CONFLICT_MISSING_PAYOFF", "Payoff evidence is missing.")],
        )

    return result(
        contract,
        guard,
        GuardStatus.PASS,
        channel="conflict",
        impact="supports_pass",
        payload={"payoff_count": len(payoffs)},
        supported=True,
        consumed_inputs={"game_model": game_model},
    )

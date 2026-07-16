from __future__ import annotations

from worldguard.contracts import GuardContract
from worldguard.status import GuardStatus

from ._helpers import error, result, semantics_text


def run(contract: GuardContract):
    guard = "AgentGuard"
    text = semantics_text(contract)
    agents = contract.inputs.get("beliefs") or contract.world_model.data.get("agents") or {}
    agent_model = contract.inputs.get("agent_model", {})

    if any(word in text for word in ["payoff", "equilibrium", "causal effect", "permission"]):
        return result(
            contract,
            guard,
            GuardStatus.BOUNDARY_EXCEEDED,
            channel="boundary",
            impact="marks_boundary",
            boundary={"owner": guard, "unsupported_claim_parts": ["non_bdi_semantics"]},
            errors=[error("AGENT_BOUNDARY_NON_BDI", "AgentGuard only owns BDI-style checks.")],
        )

    if agent_model.get("conflicting_intentions"):
        return result(
            contract,
            guard,
            GuardStatus.FAIL,
            channel="agent",
            impact="supports_fail",
            errors=[error("AGENT_CONFLICTING_INTENTIONS", "Conflicting intentions are declared.")],
            counterexamples=[{"kind": "model_conflict", "steps": agent_model["conflicting_intentions"]}],
        )

    missing = agent_model.get("missing_beliefs") or agent_model.get("missing_slots") or []
    if missing or not agents:
        return result(
            contract,
            guard,
            GuardStatus.GAP,
            channel="gap",
            impact="creates_gap",
            missing_slots=[{"belief": item} for item in (missing or ["agent beliefs"])],
            errors=[error("AGENT_MISSING_BELIEF", "Required BDI slot is missing.")],
        )

    return result(
        contract,
        guard,
        GuardStatus.PASS,
        channel="agent",
        impact="supports_pass",
        payload={"agent_count": len(agents) if hasattr(agents, "__len__") else 1},
        supported=True,
        consumed_inputs={"agents": agents, "agent_model": agent_model},
    )

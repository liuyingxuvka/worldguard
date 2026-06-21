from __future__ import annotations

from worldguard.contracts import GuardContract
from worldguard.status import GuardStatus

from ._helpers import error, result, semantics_text


def _has_cycle(edges: list[list[str] | tuple[str, str]]) -> bool:
    graph: dict[str, list[str]] = {}
    for edge in edges:
        if len(edge) != 2:
            continue
        graph.setdefault(edge[0], []).append(edge[1])
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        for child in graph.get(node, []):
            if visit(child):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in graph)


def run(contract: GuardContract):
    guard = "CausalGuard"
    text = semantics_text(contract)
    causal_model = contract.inputs.get("causal_model") or {
        "variables": contract.world_model.data.get("causal_variables", []),
        "equations": contract.world_model.data.get("causal_equations", {}),
        "graph": contract.world_model.data.get("causal_graph", []),
    }
    variables = causal_model.get("variables", [])
    equations = causal_model.get("equations", {})
    graph = causal_model.get("graph", [])

    if any(word in text for word in ["then", "after", "temporal story", "because story"]):
        return result(
            contract,
            guard,
            GuardStatus.BOUNDARY_EXCEEDED,
            channel="boundary",
            impact="marks_boundary",
            boundary={"owner": guard, "unsupported_claim_parts": ["temporal_story_without_scm"]},
            errors=[error("CAUSAL_BOUNDARY_TEMPORAL_STORY", "Temporal order alone is not SCM evidence.")],
        )

    if graph and _has_cycle(graph):
        return result(
            contract,
            guard,
            GuardStatus.FAIL,
            channel="causal",
            impact="supports_fail",
            errors=[error("CAUSAL_CYCLE", "SCM graph contains a directed cycle.")],
            counterexamples=[{"kind": "model_conflict", "steps": graph}],
        )

    missing_equations = [var for var in variables if var not in equations]
    if not variables or not equations:
        return result(
            contract,
            guard,
            GuardStatus.GAP,
            channel="gap",
            impact="creates_gap",
            missing_slots=[{"variable": var, "needed": "structural_equation"} for var in (missing_equations or ["variables/equations"])],
            errors=[error("CAUSAL_MISSING_STRUCTURAL_EQUATION", "Required SCM equation is missing.")],
        )

    return result(
        contract,
        guard,
        GuardStatus.PASS,
        channel="causal",
        impact="supports_pass",
        payload={"variables": variables},
        supported=True,
        consumed_inputs={"causal_model": causal_model},
    )

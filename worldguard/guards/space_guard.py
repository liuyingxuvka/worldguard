from __future__ import annotations

from collections import defaultdict

from worldguard.contracts import GuardContract
from worldguard.status import GuardStatus

from ._helpers import error, result, semantics_text


def run(contract: GuardContract):
    guard = "SpaceGuard"
    text = semantics_text(contract)
    relations = (
        contract.inputs.get("spatial_relations")
        or contract.world_model.data.get("rcc8_relations")
        or contract.world_model.relations.get("rcc8_relations", [])
    )

    if any(word in text for word in ["meters", "distance", "metric", "geometry"]):
        return result(
            contract,
            guard,
            GuardStatus.BOUNDARY_EXCEEDED,
            channel="boundary",
            impact="marks_boundary",
            boundary={"owner": guard, "unsupported_claim_parts": ["metric_geometry"]},
            errors=[error("SPACE_BOUNDARY_METRIC_GEOMETRY", "RCC8 does not own metric distance.")],
        )

    if not relations:
        return result(
            contract,
            guard,
            GuardStatus.GAP,
            channel="gap",
            impact="creates_gap",
            missing_slots=[{"needed": "rcc8 relation"}],
            errors=[error("SPACE_MISSING_RELATION", "No spatial relation was supplied.")],
        )

    seen = defaultdict(set)
    for rel in relations:
        if isinstance(rel, dict):
            key = (rel.get("at"), rel.get("x"), rel.get("y"))
            seen[key].add(rel.get("relation"))
    conflicts = [key for key, values in seen.items() if len(values) > 1]
    if conflicts:
        return result(
            contract,
            guard,
            GuardStatus.FAIL,
            channel="space",
            impact="supports_fail",
            errors=[error("SPACE_RCC8_CONTRADICTION", "Multiple RCC8 base relations conflict.")],
            counterexamples=[{"kind": "model_conflict", "steps": [{"pair": key} for key in conflicts]}],
        )

    return result(
        contract,
        guard,
        GuardStatus.PASS,
        channel="space",
        impact="supports_pass",
        payload={"relation_count": len(relations)},
        supported=True,
        consumed_inputs={"spatial_relations": relations},
    )

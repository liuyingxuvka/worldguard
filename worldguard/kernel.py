from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .contracts import GuardContract
from .guards import GUARD_RUNNERS
from .reports import GuardResult, GuardedReport


def run_worldguard(contract: GuardContract | Mapping[str, Any]) -> GuardedReport:
    if not isinstance(contract, GuardContract):
        contract = GuardContract.from_dict(dict(contract))

    child_results: list[GuardResult] = []
    for guard in contract.claim.target_guards:
        if guard not in GUARD_RUNNERS:
            raise ValueError(f"unknown guard: {guard}")
        guard_contract = contract.for_guard(
            guard,
            upstream_results=[result.to_dict() for result in child_results],
        )
        child_results.append(GUARD_RUNNERS[guard](guard_contract))
    return GuardedReport.from_results(child_results, scope_limits=contract.world_model.scope_limits)

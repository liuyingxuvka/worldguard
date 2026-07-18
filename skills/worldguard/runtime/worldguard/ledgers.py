from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


LEDGER_CHANNELS = {
    "event",
    "agent",
    "space",
    "resource",
    "causal",
    "conflict",
    "norm",
    "error",
    "gap",
    "boundary",
    "counterexample",
    "aggregate",
}

STATUS_IMPACTS = {
    "supports_pass",
    "supports_fail",
    "creates_gap",
    "marks_boundary",
    "informational",
}


@dataclass(frozen=True)
class LedgerEntry:
    ledger_entry_id: str
    run_id: str
    claim_id: str
    guard: str
    channel: str
    status_impact: str
    payload: dict[str, Any] = field(default_factory=dict)
    source_refs: list[str] = field(default_factory=list)
    read_only_for_downstream: bool = True
    created_at_step: str = ""

    def __post_init__(self) -> None:
        if self.channel not in LEDGER_CHANNELS:
            raise ValueError(f"unknown ledger channel: {self.channel}")
        if self.status_impact not in STATUS_IMPACTS:
            raise ValueError(f"unknown status impact: {self.status_impact}")
        if not self.read_only_for_downstream:
            raise ValueError("ledger entries must be read-only for downstream")

    def to_dict(self) -> dict[str, Any]:
        return {
            "ledger_entry_id": self.ledger_entry_id,
            "run_id": self.run_id,
            "claim_id": self.claim_id,
            "guard": self.guard,
            "channel": self.channel,
            "status_impact": self.status_impact,
            "payload": self.payload,
            "source_refs": self.source_refs,
            "read_only_for_downstream": self.read_only_for_downstream,
            "created_at_step": self.created_at_step,
        }


def ledger_entry(
    *,
    run_id: str,
    claim_id: str,
    guard: str,
    channel: str,
    status_impact: str,
    payload: dict[str, Any] | None = None,
    source_refs: list[str] | None = None,
    step: str = "",
) -> LedgerEntry:
    safe_step = step or guard
    return LedgerEntry(
        ledger_entry_id=f"{run_id}:{claim_id}:{guard}:{channel}:{safe_step}",
        run_id=run_id,
        claim_id=claim_id,
        guard=guard,
        channel=channel,
        status_impact=status_impact,
        payload=payload or {},
        source_refs=source_refs or [],
        created_at_step=safe_step,
    )

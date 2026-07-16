from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .ledgers import LedgerEntry
from .status import GuardStatus, aggregate_statuses, coerce_status


@dataclass(frozen=True)
class GuardResult:
    result_id: str
    contract_id: str
    guard: str
    status: GuardStatus
    supported_claims: list[str] = field(default_factory=list)
    rejected_claims: list[str] = field(default_factory=list)
    missing_slots: list[dict[str, Any]] = field(default_factory=list)
    boundary_exceeded: dict[str, Any] = field(default_factory=dict)
    errors: list[dict[str, Any]] = field(default_factory=list)
    counterexamples: list[dict[str, Any]] = field(default_factory=list)
    ledgers: dict[str, list[LedgerEntry]] = field(default_factory=dict)
    assumptions_used: list[str] = field(default_factory=list)
    scope_limits: list[str] = field(default_factory=list)
    consumed_inputs: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", coerce_status(self.status))
        if self.status != GuardStatus.PASS and not (
            self.missing_slots or self.boundary_exceeded or self.errors or self.counterexamples
        ):
            raise ValueError(f"{self.guard} {self.status} result lacks non-pass evidence")
        if not self.ledgers:
            raise ValueError(f"{self.guard} result lacks ledgers")

    def all_ledgers(self) -> list[LedgerEntry]:
        entries: list[LedgerEntry] = []
        for channel_entries in self.ledgers.values():
            entries.extend(channel_entries)
        return entries

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_id": self.result_id,
            "contract_id": self.contract_id,
            "guard": self.guard,
            "status": self.status.value,
            "supported_claims": self.supported_claims,
            "rejected_claims": self.rejected_claims,
            "missing_slots": self.missing_slots,
            "boundary_exceeded": self.boundary_exceeded,
            "errors": self.errors,
            "counterexamples": self.counterexamples,
            "ledgers": {
                channel: [entry.to_dict() for entry in entries]
                for channel, entries in self.ledgers.items()
            },
            "assumptions_used": self.assumptions_used,
            "scope_limits": self.scope_limits,
            "consumed_inputs": self.consumed_inputs,
        }


@dataclass(frozen=True)
class GuardedReport:
    status: GuardStatus
    child_results: list[GuardResult]
    aggregate_ledger: list[LedgerEntry]
    scope_limits: list[str] = field(default_factory=list)

    @classmethod
    def from_results(cls, child_results: list[GuardResult], scope_limits: list[str] | None = None) -> "GuardedReport":
        aggregate = []
        for result in child_results:
            aggregate.extend(result.all_ledgers())
        return cls(
            status=aggregate_statuses([result.status for result in child_results]),
            child_results=child_results,
            aggregate_ledger=aggregate,
            scope_limits=scope_limits or [],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "child_results": [result.to_dict() for result in self.child_results],
            "aggregate_ledger": [entry.to_dict() for entry in self.aggregate_ledger],
            "scope_limits": self.scope_limits,
        }

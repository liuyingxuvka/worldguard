"""Task-local four-valued fact revision with transactional activation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping, Sequence


FACT_REVISION_SCHEMA_VERSION = "worldguard.fact_revision.v1"


def _text(value: Any, label: str) -> str:
    result = str(value or "").strip()
    if not result:
        raise ValueError(f"{label} must be non-empty")
    return result


def _strict(data: Mapping[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise ValueError(f"{label} has unknown fields: {', '.join(unknown)}")


def _fingerprint(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


class FactPolarity(StrEnum):
    POSITIVE = "positive"
    NEGATIVE = "negative"


class FactTruthState(StrEnum):
    TRUE = "true"
    FALSE = "false"
    BOTH = "both"
    NEITHER = "neither"


class FactRevisionEvidenceKind(StrEnum):
    REGRESSION = "regression"
    HOLDOUT = "holdout"


@dataclass(frozen=True)
class WorldFact:
    fact_id: str
    description: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "fact_id", _text(self.fact_id, "fact_id"))
        object.__setattr__(self, "description", str(self.description).strip())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "WorldFact":
        _strict(data, {"fact_id", "description"}, "world fact")
        return cls(
            fact_id=data.get("fact_id", ""),
            description=data.get("description", ""),
        )

    def to_dict(self) -> dict[str, str]:
        return {"fact_id": self.fact_id, "description": self.description}


@dataclass(frozen=True)
class SignedFact:
    fact_id: str
    polarity: FactPolarity

    def __post_init__(self) -> None:
        object.__setattr__(self, "fact_id", _text(self.fact_id, "fact_id"))
        object.__setattr__(self, "polarity", FactPolarity(self.polarity))

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SignedFact":
        _strict(data, {"fact_id", "polarity"}, "signed fact")
        return cls(
            fact_id=data.get("fact_id", ""),
            polarity=FactPolarity(data.get("polarity", "")),
        )

    def to_dict(self) -> dict[str, str]:
        return {"fact_id": self.fact_id, "polarity": self.polarity.value}


@dataclass(frozen=True)
class FactSupport:
    support_id: str
    fact_id: str
    polarity: FactPolarity
    source_id: str
    evidence_id: str
    derived_by_rule_id: str = ""
    antecedent_support_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in ("support_id", "fact_id", "source_id", "evidence_id"):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        object.__setattr__(self, "polarity", FactPolarity(self.polarity))
        object.__setattr__(
            self,
            "derived_by_rule_id",
            str(self.derived_by_rule_id).strip(),
        )
        object.__setattr__(
            self,
            "antecedent_support_ids",
            tuple(sorted(set(self.antecedent_support_ids))),
        )
        if bool(self.derived_by_rule_id) != bool(self.antecedent_support_ids):
            raise ValueError(
                "derived support requires both rule id and antecedent support ids"
            )

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "FactSupport":
        _strict(
            data,
            {
                "support_id",
                "fact_id",
                "polarity",
                "source_id",
                "evidence_id",
                "derived_by_rule_id",
                "antecedent_support_ids",
            },
            "fact support",
        )
        return cls(
            support_id=data.get("support_id", ""),
            fact_id=data.get("fact_id", ""),
            polarity=FactPolarity(data.get("polarity", "")),
            source_id=data.get("source_id", ""),
            evidence_id=data.get("evidence_id", ""),
            derived_by_rule_id=data.get("derived_by_rule_id", ""),
            antecedent_support_ids=tuple(
                str(item) for item in data.get("antecedent_support_ids", [])
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "support_id": self.support_id,
            "fact_id": self.fact_id,
            "polarity": self.polarity.value,
            "source_id": self.source_id,
            "evidence_id": self.evidence_id,
            "derived_by_rule_id": self.derived_by_rule_id,
            "antecedent_support_ids": list(self.antecedent_support_ids),
        }


@dataclass(frozen=True)
class StrictFactRule:
    rule_id: str
    antecedents: tuple[SignedFact, ...]
    consequent: SignedFact
    source_id: str
    evidence_id: str

    def __post_init__(self) -> None:
        for name in ("rule_id", "source_id", "evidence_id"):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        antecedents = tuple(
            sorted(
                self.antecedents,
                key=lambda item: (item.fact_id, item.polarity.value),
            )
        )
        if not antecedents:
            raise ValueError("strict rule requires at least one antecedent")
        if len(antecedents) != len(
            {(item.fact_id, item.polarity) for item in antecedents}
        ):
            raise ValueError("strict rule antecedents must be unique")
        object.__setattr__(self, "antecedents", antecedents)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "StrictFactRule":
        _strict(
            data,
            {
                "rule_id",
                "antecedents",
                "consequent",
                "source_id",
                "evidence_id",
            },
            "strict fact rule",
        )
        return cls(
            rule_id=data.get("rule_id", ""),
            antecedents=tuple(
                SignedFact.from_dict(item)
                for item in data.get("antecedents", [])
            ),
            consequent=SignedFact.from_dict(data.get("consequent", {})),
            source_id=data.get("source_id", ""),
            evidence_id=data.get("evidence_id", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "antecedents": [item.to_dict() for item in self.antecedents],
            "consequent": self.consequent.to_dict(),
            "source_id": self.source_id,
            "evidence_id": self.evidence_id,
        }


@dataclass(frozen=True)
class FactWorldSnapshot:
    snapshot_id: str
    facts: tuple[WorldFact, ...]
    supports: tuple[FactSupport, ...]
    rules: tuple[StrictFactRule, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "snapshot_id",
            _text(self.snapshot_id, "snapshot_id"),
        )
        facts = tuple(sorted(self.facts, key=lambda item: item.fact_id))
        supports = tuple(sorted(self.supports, key=lambda item: item.support_id))
        rules = tuple(sorted(self.rules, key=lambda item: item.rule_id))
        for label, values, key in (
            ("fact", facts, lambda item: item.fact_id),
            ("support", supports, lambda item: item.support_id),
            ("rule", rules, lambda item: item.rule_id),
        ):
            ids = [key(item) for item in values]
            if len(ids) != len(set(ids)):
                raise ValueError(f"{label} ids must be unique")
        fact_ids = {item.fact_id for item in facts}
        if not fact_ids:
            raise ValueError("fact world snapshot requires at least one fact")
        for support in supports:
            if support.fact_id not in fact_ids:
                raise ValueError(
                    f"support references unknown fact: {support.fact_id}"
                )
        for rule in rules:
            signed = (*rule.antecedents, rule.consequent)
            unknown = sorted(
                {item.fact_id for item in signed if item.fact_id not in fact_ids}
            )
            if unknown:
                raise ValueError(
                    "strict rule references unknown facts: "
                    + ", ".join(unknown)
                )
        object.__setattr__(self, "facts", facts)
        object.__setattr__(self, "supports", supports)
        object.__setattr__(self, "rules", rules)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "FactWorldSnapshot":
        _strict(
            data,
            {
                "artifact_kind",
                "schema_version",
                "snapshot_id",
                "facts",
                "supports",
                "rules",
                "fingerprint",
            },
            "fact world snapshot",
        )
        return cls(
            snapshot_id=data.get("snapshot_id", ""),
            facts=tuple(
                WorldFact.from_dict(item) for item in data.get("facts", [])
            ),
            supports=tuple(
                FactSupport.from_dict(item)
                for item in data.get("supports", [])
            ),
            rules=tuple(
                StrictFactRule.from_dict(item)
                for item in data.get("rules", [])
            ),
        )

    def identity_payload(self) -> dict[str, Any]:
        return {
            "artifact_kind": "worldguard.fact_world_snapshot",
            "schema_version": FACT_REVISION_SCHEMA_VERSION,
            "snapshot_id": self.snapshot_id,
            "facts": [item.to_dict() for item in self.facts],
            "supports": [item.to_dict() for item in self.supports],
            "rules": [item.to_dict() for item in self.rules],
        }

    @property
    def fingerprint(self) -> str:
        return _fingerprint(self.identity_payload())

    def to_dict(self) -> dict[str, Any]:
        return {**self.identity_payload(), "fingerprint": self.fingerprint}


@dataclass(frozen=True)
class FactStateExpectation:
    fact_id: str
    expected_state: FactTruthState

    def __post_init__(self) -> None:
        object.__setattr__(self, "fact_id", _text(self.fact_id, "fact_id"))
        object.__setattr__(
            self,
            "expected_state",
            FactTruthState(self.expected_state),
        )

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "FactStateExpectation":
        _strict(data, {"fact_id", "expected_state"}, "fact expectation")
        return cls(
            fact_id=data.get("fact_id", ""),
            expected_state=FactTruthState(data.get("expected_state", "")),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "fact_id": self.fact_id,
            "expected_state": self.expected_state.value,
        }


@dataclass(frozen=True)
class FactRevisionTransaction:
    transaction_id: str
    base_fingerprint: str
    additions: tuple[FactSupport, ...] = ()
    retraction_support_ids: tuple[str, ...] = ()
    preserved_fact_ids: tuple[str, ...] = ()
    expected_terminal_deltas: tuple[FactStateExpectation, ...] = ()
    task_id: str = ""
    iteration: int = 0
    max_iterations: int = 8
    remaining_predictive_gap_ids: tuple[str, ...] = ()
    next_actions: tuple[str, ...] = ()
    terminal_reason: str = "continue_iteration"

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "transaction_id",
            _text(self.transaction_id, "transaction_id"),
        )
        object.__setattr__(
            self,
            "base_fingerprint",
            _text(self.base_fingerprint, "base_fingerprint"),
        )
        object.__setattr__(self, "task_id", str(self.task_id).strip())
        object.__setattr__(self, "iteration", int(self.iteration))
        object.__setattr__(self, "max_iterations", max(1, int(self.max_iterations)))
        object.__setattr__(self, "remaining_predictive_gap_ids", tuple(sorted({_text(item, "remaining_predictive_gap_ids") for item in self.remaining_predictive_gap_ids})))
        object.__setattr__(self, "next_actions", tuple(sorted({_text(item, "next_actions") for item in self.next_actions})))
        object.__setattr__(self, "terminal_reason", str(self.terminal_reason).strip() or "continue_iteration")
        if self.iteration < 0:
            raise ValueError("iteration must be non-negative")
        additions = tuple(
            sorted(self.additions, key=lambda item: item.support_id)
        )
        if len(additions) != len({item.support_id for item in additions}):
            raise ValueError("transaction addition support ids must be unique")
        object.__setattr__(self, "additions", additions)
        for name in ("retraction_support_ids", "preserved_fact_ids"):
            values = tuple(
                sorted({_text(item, name) for item in getattr(self, name)})
            )
            object.__setattr__(self, name, values)
        expectations = tuple(
            sorted(
                self.expected_terminal_deltas,
                key=lambda item: item.fact_id,
            )
        )
        if len(expectations) != len({item.fact_id for item in expectations}):
            raise ValueError("expected terminal delta fact ids must be unique")
        object.__setattr__(
            self,
            "expected_terminal_deltas",
            expectations,
        )

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "FactRevisionTransaction":
        _strict(
            data,
            {
                "transaction_id",
                "base_fingerprint",
                "additions",
                "retraction_support_ids",
                "preserved_fact_ids",
                "expected_terminal_deltas",
                "task_id",
                "iteration",
                "max_iterations",
                "remaining_predictive_gap_ids",
                "next_actions",
                "terminal_reason",
            },
            "fact revision transaction",
        )
        return cls(
            transaction_id=data.get("transaction_id", ""),
            base_fingerprint=data.get("base_fingerprint", ""),
            additions=tuple(
                FactSupport.from_dict(item)
                for item in data.get("additions", [])
            ),
            retraction_support_ids=tuple(
                str(item)
                for item in data.get("retraction_support_ids", [])
            ),
            preserved_fact_ids=tuple(
                str(item) for item in data.get("preserved_fact_ids", [])
            ),
            expected_terminal_deltas=tuple(
                FactStateExpectation.from_dict(item)
                for item in data.get("expected_terminal_deltas", [])
            ),
            task_id=data.get("task_id", ""),
            iteration=data.get("iteration", 0),
            max_iterations=data.get("max_iterations", 8),
            remaining_predictive_gap_ids=tuple(str(item) for item in data.get("remaining_predictive_gap_ids", [])),
            next_actions=tuple(str(item) for item in data.get("next_actions", [])),
            terminal_reason=data.get("terminal_reason", "continue_iteration"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "base_fingerprint": self.base_fingerprint,
            "additions": [item.to_dict() for item in self.additions],
            "retraction_support_ids": list(self.retraction_support_ids),
            "preserved_fact_ids": list(self.preserved_fact_ids),
            "expected_terminal_deltas": [
                item.to_dict() for item in self.expected_terminal_deltas
            ],
            "task_id": self.task_id,
            "iteration": self.iteration,
            "max_iterations": self.max_iterations,
            "remaining_predictive_gap_ids": list(self.remaining_predictive_gap_ids),
            "next_actions": list(self.next_actions),
            "terminal_reason": self.terminal_reason,
        }


@dataclass(frozen=True)
class FactStateProjection:
    fact_id: str
    state: FactTruthState
    positive_support_ids: tuple[str, ...]
    negative_support_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "fact_id": self.fact_id,
            "state": self.state.value,
            "positive_support_ids": list(self.positive_support_ids),
            "negative_support_ids": list(self.negative_support_ids),
        }


@dataclass(frozen=True)
class FactStateDelta:
    fact_id: str
    before: FactTruthState
    after: FactTruthState
    changed_support_ids: tuple[str, ...]
    rule_chain_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "fact_id": self.fact_id,
            "before": self.before.value,
            "after": self.after.value,
            "changed_support_ids": list(self.changed_support_ids),
            "rule_chain_ids": list(self.rule_chain_ids),
        }


@dataclass(frozen=True)
class FactRevisionPreview:
    transaction_id: str
    base_snapshot_id: str
    base_fingerprint: str
    candidate_snapshot: FactWorldSnapshot
    before_states: tuple[FactStateProjection, ...]
    after_states: tuple[FactStateProjection, ...]
    deltas: tuple[FactStateDelta, ...]
    contradiction_fact_ids: tuple[str, ...]
    preserved_fact_ids: tuple[str, ...]
    changed_preserved_fact_ids: tuple[str, ...]
    closure_iterations: int
    closure_terminated: bool
    finding_codes: tuple[str, ...]
    status: str
    task_id: str = ""
    iteration: int = 0
    remaining_predictive_gap_ids: tuple[str, ...] = ()
    next_actions: tuple[str, ...] = ()
    terminal_reason: str = "continue_iteration"

    def identity_payload(self) -> dict[str, Any]:
        return {
            "artifact_kind": "worldguard.fact_revision_preview",
            "schema_version": FACT_REVISION_SCHEMA_VERSION,
            "transaction_id": self.transaction_id,
            "base_snapshot_id": self.base_snapshot_id,
            "base_fingerprint": self.base_fingerprint,
            "candidate_snapshot": self.candidate_snapshot.to_dict(),
            "before_states": [item.to_dict() for item in self.before_states],
            "after_states": [item.to_dict() for item in self.after_states],
            "deltas": [item.to_dict() for item in self.deltas],
            "contradiction_fact_ids": list(self.contradiction_fact_ids),
            "preserved_fact_ids": list(self.preserved_fact_ids),
            "changed_preserved_fact_ids": list(
                self.changed_preserved_fact_ids
            ),
            "closure_iterations": self.closure_iterations,
            "closure_terminated": self.closure_terminated,
            "finding_codes": list(self.finding_codes),
            "status": self.status,
            "task_id": self.task_id,
            "iteration": self.iteration,
            "remaining_predictive_gap_ids": list(self.remaining_predictive_gap_ids),
            "next_actions": list(self.next_actions),
            "terminal_reason": self.terminal_reason,
            "claim_boundary": (
                "This preview is a copy-based task-local fact revision. Four-"
                "valued states describe support inside the supplied snapshot; "
                "they are not WorldGuard Guard terminal statuses and do not "
                "establish factual truth."
            ),
        }

    @property
    def fingerprint(self) -> str:
        return _fingerprint(self.identity_payload())

    def to_dict(self) -> dict[str, Any]:
        return {**self.identity_payload(), "fingerprint": self.fingerprint}


@dataclass(frozen=True)
class FactRevisionEvidenceBinding:
    evidence_id: str
    kind: FactRevisionEvidenceKind
    status: str
    current: bool
    subject_fingerprint: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "evidence_id",
            _text(self.evidence_id, "evidence_id"),
        )
        object.__setattr__(self, "kind", FactRevisionEvidenceKind(self.kind))
        object.__setattr__(self, "status", str(self.status).strip().lower())
        object.__setattr__(
            self,
            "subject_fingerprint",
            _text(self.subject_fingerprint, "subject_fingerprint"),
        )
        if not isinstance(self.current, bool):
            raise ValueError("evidence current must be boolean")

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "FactRevisionEvidenceBinding":
        _strict(
            data,
            {
                "evidence_id",
                "kind",
                "status",
                "current",
                "subject_fingerprint",
            },
            "fact revision evidence",
        )
        return cls(
            evidence_id=data.get("evidence_id", ""),
            kind=FactRevisionEvidenceKind(data.get("kind", "")),
            status=data.get("status", ""),
            current=data.get("current", False),
            subject_fingerprint=data.get("subject_fingerprint", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "kind": self.kind.value,
            "status": self.status,
            "current": self.current,
            "subject_fingerprint": self.subject_fingerprint,
        }


@dataclass(frozen=True)
class FactRevisionActivationRequest:
    activation_id: str
    expected_preview_fingerprint: str
    acknowledged_contradiction_fact_ids: tuple[str, ...]
    evidence: tuple[FactRevisionEvidenceBinding, ...]
    prior_activation_transaction_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "activation_id",
            _text(self.activation_id, "activation_id"),
        )
        object.__setattr__(
            self,
            "expected_preview_fingerprint",
            _text(
                self.expected_preview_fingerprint,
                "expected_preview_fingerprint",
            ),
        )
        for name in (
            "acknowledged_contradiction_fact_ids",
            "prior_activation_transaction_ids",
        ):
            object.__setattr__(
                self,
                name,
                tuple(sorted({_text(item, name) for item in getattr(self, name)})),
            )
        evidence = tuple(
            sorted(self.evidence, key=lambda item: item.evidence_id)
        )
        if len(evidence) != len({item.evidence_id for item in evidence}):
            raise ValueError("activation evidence ids must be unique")
        object.__setattr__(self, "evidence", evidence)

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "FactRevisionActivationRequest":
        _strict(
            data,
            {
                "activation_id",
                "expected_preview_fingerprint",
                "acknowledged_contradiction_fact_ids",
                "evidence",
                "prior_activation_transaction_ids",
            },
            "fact revision activation request",
        )
        return cls(
            activation_id=data.get("activation_id", ""),
            expected_preview_fingerprint=data.get(
                "expected_preview_fingerprint",
                "",
            ),
            acknowledged_contradiction_fact_ids=tuple(
                str(item)
                for item in data.get(
                    "acknowledged_contradiction_fact_ids",
                    [],
                )
            ),
            evidence=tuple(
                FactRevisionEvidenceBinding.from_dict(item)
                for item in data.get("evidence", [])
            ),
            prior_activation_transaction_ids=tuple(
                str(item)
                for item in data.get(
                    "prior_activation_transaction_ids",
                    [],
                )
            ),
        )


@dataclass(frozen=True)
class FactRevisionActivationReceipt:
    activation_id: str
    transaction_id: str
    base_fingerprint: str
    preview_fingerprint: str
    candidate_fingerprint: str
    evidence_ids: tuple[str, ...]
    contradiction_fact_ids: tuple[str, ...]
    finding_codes: tuple[str, ...]
    status: str
    activated: bool
    terminal_reason: str = "continue_iteration"

    def identity_payload(self) -> dict[str, Any]:
        return {
            "artifact_kind": "worldguard.fact_revision_activation_receipt",
            "schema_version": FACT_REVISION_SCHEMA_VERSION,
            "activation_id": self.activation_id,
            "transaction_id": self.transaction_id,
            "base_fingerprint": self.base_fingerprint,
            "preview_fingerprint": self.preview_fingerprint,
            "candidate_fingerprint": self.candidate_fingerprint,
            "evidence_ids": list(self.evidence_ids),
            "contradiction_fact_ids": list(self.contradiction_fact_ids),
            "finding_codes": list(self.finding_codes),
            "status": self.status,
            "activated": self.activated,
            "terminal_reason": self.terminal_reason,
            "claim_boundary": (
                "Activation accepts only this task-local fact snapshot and does "
                "not mutate WorldGuard rules, reusable defaults, installed "
                "skills, or any global truth library."
            ),
        }

    @property
    def fingerprint(self) -> str:
        return _fingerprint(self.identity_payload())

    def to_dict(self) -> dict[str, Any]:
        return {**self.identity_payload(), "fingerprint": self.fingerprint}


@dataclass(frozen=True)
class FactRevisionActivationResult:
    receipt: FactRevisionActivationReceipt
    activated_snapshot: FactWorldSnapshot | None
    preview: FactRevisionPreview

    def to_dict(self) -> dict[str, Any]:
        return {
            "receipt": self.receipt.to_dict(),
            "activated_snapshot": (
                self.activated_snapshot.to_dict()
                if self.activated_snapshot
                else None
            ),
            "preview": self.preview.to_dict(),
        }


def _truth_state(
    positive_support_ids: Sequence[str],
    negative_support_ids: Sequence[str],
) -> FactTruthState:
    positive = bool(positive_support_ids)
    negative = bool(negative_support_ids)
    if positive and negative:
        return FactTruthState.BOTH
    if positive:
        return FactTruthState.TRUE
    if negative:
        return FactTruthState.FALSE
    return FactTruthState.NEITHER


def _project_states(
    facts: Sequence[WorldFact],
    supports: Sequence[FactSupport],
) -> tuple[FactStateProjection, ...]:
    projections: list[FactStateProjection] = []
    for fact in sorted(facts, key=lambda item: item.fact_id):
        positive = tuple(
            sorted(
                item.support_id
                for item in supports
                if item.fact_id == fact.fact_id
                and item.polarity == FactPolarity.POSITIVE
            )
        )
        negative = tuple(
            sorted(
                item.support_id
                for item in supports
                if item.fact_id == fact.fact_id
                and item.polarity == FactPolarity.NEGATIVE
            )
        )
        projections.append(
            FactStateProjection(
                fact_id=fact.fact_id,
                state=_truth_state(positive, negative),
                positive_support_ids=positive,
                negative_support_ids=negative,
            )
        )
    return tuple(projections)


def _close_supports(
    supports: Sequence[FactSupport],
    rules: Sequence[StrictFactRule],
) -> tuple[tuple[FactSupport, ...], int, bool]:
    support_by_id = {item.support_id: item for item in supports}
    max_iterations = len(rules) + 1
    for iteration in range(1, max_iterations + 1):
        changed = False
        signed_supports: dict[tuple[str, FactPolarity], list[FactSupport]] = {}
        for support in support_by_id.values():
            signed_supports.setdefault(
                (support.fact_id, support.polarity),
                [],
            ).append(support)
        for values in signed_supports.values():
            values.sort(key=lambda item: item.support_id)
        for rule in sorted(rules, key=lambda item: item.rule_id):
            witnesses: list[FactSupport] = []
            for antecedent in rule.antecedents:
                candidates = signed_supports.get(
                    (antecedent.fact_id, antecedent.polarity),
                    [],
                )
                if not candidates:
                    break
                witnesses.append(candidates[0])
            else:
                support_id = f"derived:{rule.rule_id}"
                expected = FactSupport(
                    support_id=support_id,
                    fact_id=rule.consequent.fact_id,
                    polarity=rule.consequent.polarity,
                    source_id=rule.source_id,
                    evidence_id=rule.evidence_id,
                    derived_by_rule_id=rule.rule_id,
                    antecedent_support_ids=tuple(
                        item.support_id for item in witnesses
                    ),
                )
                existing = support_by_id.get(support_id)
                if existing is not None and existing != expected:
                    raise ValueError(
                        f"derived support id collision: {support_id}"
                    )
                if existing is None:
                    support_by_id[support_id] = expected
                    changed = True
        if not changed:
            return (
                tuple(
                    sorted(
                        support_by_id.values(),
                        key=lambda item: item.support_id,
                    )
                ),
                iteration,
                True,
            )
    return (
        tuple(
            sorted(
                support_by_id.values(),
                key=lambda item: item.support_id,
            )
        ),
        max_iterations,
        False,
    )


def _delta(
    before: FactStateProjection,
    after: FactStateProjection,
    support_by_id: Mapping[str, FactSupport],
) -> FactStateDelta:
    before_ids = set(before.positive_support_ids + before.negative_support_ids)
    after_ids = set(after.positive_support_ids + after.negative_support_ids)
    changed = tuple(sorted(before_ids ^ after_ids))
    rule_ids = tuple(
        sorted(
            {
                support_by_id[item].derived_by_rule_id
                for item in changed
                if item in support_by_id
                and support_by_id[item].derived_by_rule_id
            }
        )
    )
    return FactStateDelta(
        fact_id=before.fact_id,
        before=before.state,
        after=after.state,
        changed_support_ids=changed,
        rule_chain_ids=rule_ids,
    )


def preview_fact_revision(
    base: FactWorldSnapshot,
    transaction: FactRevisionTransaction,
) -> FactRevisionPreview:
    findings: list[str] = []
    if transaction.base_fingerprint != base.fingerprint:
        findings.append("stale_base_fingerprint")
    fact_ids = {item.fact_id for item in base.facts}
    unknown_preserved = sorted(
        set(transaction.preserved_fact_ids) - fact_ids
    )
    if unknown_preserved:
        findings.append("preserved_fact_unknown")
    unknown_expected = sorted(
        {
            item.fact_id
            for item in transaction.expected_terminal_deltas
            if item.fact_id not in fact_ids
        }
    )
    if unknown_expected:
        findings.append("expected_delta_fact_unknown")
    try:
        before_supports, before_iterations, before_terminated = _close_supports(
            base.supports,
            base.rules,
        )
    except ValueError:
        before_supports = base.supports
        before_iterations = 0
        before_terminated = False
        findings.append("base_closure_invalid")
    support_by_id = {
        item.support_id: item
        for item in before_supports
        if not item.derived_by_rule_id
    }
    known_support_ids = {item.support_id for item in before_supports}
    unknown_retractions = sorted(
        set(transaction.retraction_support_ids) - known_support_ids
    )
    if unknown_retractions:
        findings.append("retraction_support_unknown")
    for support_id in transaction.retraction_support_ids:
        support_by_id.pop(support_id, None)
    for addition in transaction.additions:
        if addition.fact_id not in fact_ids:
            findings.append("addition_fact_unknown")
            continue
        if addition.support_id in support_by_id:
            findings.append("addition_support_id_conflict")
            continue
        support_by_id[addition.support_id] = addition
    try:
        after_supports, after_iterations, after_terminated = _close_supports(
            tuple(support_by_id.values()),
            base.rules,
        )
    except ValueError:
        after_supports = tuple(
            sorted(support_by_id.values(), key=lambda item: item.support_id)
        )
        after_iterations = 0
        after_terminated = False
        findings.append("candidate_closure_invalid")
    before_states = _project_states(base.facts, before_supports)
    after_states = _project_states(base.facts, after_supports)
    before_by_id = {item.fact_id: item for item in before_states}
    after_by_id = {item.fact_id: item for item in after_states}
    all_supports = {
        item.support_id: item
        for item in (*before_supports, *after_supports)
    }
    deltas = tuple(
        _delta(before_by_id[fact_id], after_by_id[fact_id], all_supports)
        for fact_id in sorted(fact_ids)
        if before_by_id[fact_id].state != after_by_id[fact_id].state
    )
    changed_preserved = tuple(
        fact_id
        for fact_id in transaction.preserved_fact_ids
        if fact_id in before_by_id
        and before_by_id[fact_id].state != after_by_id[fact_id].state
    )
    if changed_preserved:
        findings.append("preserved_fact_changed")
    for expectation in transaction.expected_terminal_deltas:
        observed = after_by_id.get(expectation.fact_id)
        if observed is not None and observed.state != expectation.expected_state:
            findings.append("expected_terminal_delta_mismatch")
    closure_terminated = before_terminated and after_terminated
    if not closure_terminated:
        findings.append("closure_not_terminated")
    candidate = FactWorldSnapshot(
        snapshot_id=f"candidate:{transaction.transaction_id}",
        facts=base.facts,
        supports=after_supports,
        rules=base.rules,
    )
    contradiction_ids = tuple(
        item.fact_id
        for item in after_states
        if item.state == FactTruthState.BOTH
    )
    unique_findings = tuple(sorted(set(findings)))
    return FactRevisionPreview(
        transaction_id=transaction.transaction_id,
        base_snapshot_id=base.snapshot_id,
        base_fingerprint=base.fingerprint,
        candidate_snapshot=candidate,
        before_states=before_states,
        after_states=after_states,
        deltas=deltas,
        contradiction_fact_ids=contradiction_ids,
        preserved_fact_ids=transaction.preserved_fact_ids,
        changed_preserved_fact_ids=changed_preserved,
        closure_iterations=before_iterations + after_iterations,
        closure_terminated=closure_terminated,
        finding_codes=unique_findings,
        status="ready" if not unique_findings else "blocked",
        task_id=transaction.task_id,
        iteration=transaction.iteration,
        remaining_predictive_gap_ids=transaction.remaining_predictive_gap_ids,
        next_actions=transaction.next_actions,
        terminal_reason=(
            "iteration_limit"
            if transaction.remaining_predictive_gap_ids
            and transaction.iteration >= transaction.max_iterations
            else transaction.terminal_reason
        ),
    )


def activate_fact_revision(
    current_base: FactWorldSnapshot,
    transaction: FactRevisionTransaction,
    request: FactRevisionActivationRequest,
) -> FactRevisionActivationResult:
    preview = preview_fact_revision(current_base, transaction)
    findings = list(preview.finding_codes)
    if request.expected_preview_fingerprint != preview.fingerprint:
        findings.append("preview_fingerprint_stale")
    if transaction.transaction_id in request.prior_activation_transaction_ids:
        findings.append("transaction_already_activated")
    if (
        set(request.acknowledged_contradiction_fact_ids)
        != set(preview.contradiction_fact_ids)
    ):
        findings.append("contradiction_visibility_not_acknowledged")
    evidence_by_kind = {
        kind: [
            item
            for item in request.evidence
            if item.kind == kind
        ]
        for kind in FactRevisionEvidenceKind
    }
    for kind in FactRevisionEvidenceKind:
        if not evidence_by_kind[kind]:
            findings.append(f"missing_{kind.value}_evidence")
    for evidence in request.evidence:
        if (
            evidence.status != "pass"
            or not evidence.current
            or evidence.subject_fingerprint != preview.fingerprint
        ):
            findings.append("activation_evidence_not_current_pass")
    unique_findings = tuple(sorted(set(findings)))
    activated = not unique_findings
    receipt = FactRevisionActivationReceipt(
        activation_id=request.activation_id,
        transaction_id=transaction.transaction_id,
        base_fingerprint=current_base.fingerprint,
        preview_fingerprint=preview.fingerprint,
        candidate_fingerprint=preview.candidate_snapshot.fingerprint,
        evidence_ids=tuple(item.evidence_id for item in request.evidence),
        contradiction_fact_ids=preview.contradiction_fact_ids,
        finding_codes=unique_findings,
        status="activated" if activated else "blocked",
        activated=activated,
        terminal_reason=(
            "iteration_limit"
            if preview.remaining_predictive_gap_ids
            and preview.iteration >= transaction.max_iterations
            else (
                preview.terminal_reason
                if preview.remaining_predictive_gap_ids
                else "model_closed_for_task"
            )
        ),
    )
    return FactRevisionActivationResult(
        receipt=receipt,
        activated_snapshot=preview.candidate_snapshot if activated else None,
        preview=preview,
    )


__all__ = [
    "FACT_REVISION_SCHEMA_VERSION",
    "FactPolarity",
    "FactRevisionActivationReceipt",
    "FactRevisionActivationRequest",
    "FactRevisionActivationResult",
    "FactRevisionEvidenceBinding",
    "FactRevisionEvidenceKind",
    "FactRevisionPreview",
    "FactRevisionTransaction",
    "FactStateDelta",
    "FactStateExpectation",
    "FactStateProjection",
    "FactSupport",
    "FactTruthState",
    "FactWorldSnapshot",
    "SignedFact",
    "StrictFactRule",
    "WorldFact",
    "activate_fact_revision",
    "preview_fact_revision",
]

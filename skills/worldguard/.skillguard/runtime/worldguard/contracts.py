from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SEMANTIC_GUARD_ROUTES: dict[str, tuple[str, ...]] = {
    "event": ("EventGuard",),
    "events": ("EventGuard",),
    "temporal": ("EventGuard",),
    "timeline": ("EventGuard",),
    "agent": ("AgentGuard",),
    "bdi": ("AgentGuard",),
    "space": ("SpaceGuard",),
    "spatial": ("SpaceGuard",),
    "rcc8": ("SpaceGuard",),
    "resource": ("ResourceGuard",),
    "conservation": ("ResourceGuard",),
    "causal": ("CausalGuard",),
    "causality": ("CausalGuard",),
    "intervention": ("CausalGuard",),
    "counterfactual": ("CausalGuard",),
    "conflict": ("ConflictGuard",),
    "game": ("ConflictGuard",),
    "norm": ("NormGuard",),
    "normative": ("NormGuard",),
    "prediction": ("EventGuard", "CausalGuard"),
    "predictive": ("EventGuard", "CausalGuard"),
    "forecast": ("EventGuard", "CausalGuard"),
    "future_outcome": ("EventGuard", "CausalGuard"),
}

PREDICTIVE_SEMANTICS = {"prediction", "predictive", "forecast", "future_outcome"}
PREDICTIVE_TEXT_MARKERS = (
    " predict",
    "forecast",
    "will happen",
    "will occur",
    "future outcome",
    "next state",
)


@dataclass(frozen=True)
class ClaimAtom:
    atom_id: str
    text: str = ""
    requested_semantics: list[str] = field(default_factory=list)
    predictive_intent: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ClaimAtom":
        requested = data.get("requested_semantics", data.get("semantics", []))
        if isinstance(requested, str):
            requested = [requested]
        return cls(
            atom_id=str(data.get("atom_id", data.get("id", ""))),
            text=str(data.get("text", "")),
            requested_semantics=[str(item) for item in requested],
            predictive_intent=bool(data.get("predictive_intent", data.get("predictive", False))),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "atom_id": self.atom_id,
            "text": self.text,
            "requested_semantics": self.requested_semantics,
            "predictive_intent": self.predictive_intent,
        }


@dataclass(frozen=True)
class Claim:
    claim_id: str
    text: str
    target_guards: list[str] = field(default_factory=list)
    requested_semantics: list[str] = field(default_factory=list)
    atoms: list[ClaimAtom] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Claim":
        target_guards = data.get("target_guards", data.get("target_guard", []))
        if isinstance(target_guards, str):
            target_guards = [target_guards]
        requested_semantics = data.get("requested_semantics", [])
        if isinstance(requested_semantics, str):
            requested_semantics = [requested_semantics]
        return cls(
            claim_id=str(data.get("claim_id", "")),
            text=str(data.get("text", "")),
            target_guards=list(target_guards),
            requested_semantics=[str(item) for item in requested_semantics],
            atoms=[ClaimAtom.from_dict(item) for item in data.get("atoms", [])],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "text": self.text,
            "target_guards": self.target_guards,
            "requested_semantics": self.requested_semantics,
            "atoms": [atom.to_dict() for atom in self.atoms],
        }


def claim_predictive_intent(claim: Claim) -> bool:
    semantics = {
        str(item).strip().lower()
        for item in claim.requested_semantics
        if str(item).strip()
    }
    semantics.update(
        str(item).strip().lower()
        for atom in claim.atoms
        for item in atom.requested_semantics
        if str(item).strip()
    )
    text = f" {claim.text.lower()}"
    return bool(
        any(atom.predictive_intent for atom in claim.atoms)
        or semantics.intersection(PREDICTIVE_SEMANTICS)
        or any(marker in text for marker in PREDICTIVE_TEXT_MARKERS)
    )


def claim_semantics(claim: Claim) -> tuple[str, ...]:
    values = [*claim.requested_semantics]
    values.extend(item for atom in claim.atoms for item in atom.requested_semantics)
    if claim_predictive_intent(claim):
        values.append("predictive")
    return tuple(dict.fromkeys(str(item).strip().lower() for item in values if str(item).strip()))


def derive_required_guards(claim: Claim) -> tuple[str, ...]:
    """Derive target-owned Guard requirements from claim semantics, not caller route choice."""

    guards: list[str] = []
    semantics = claim_semantics(claim)
    for semantic in semantics:
        guards.extend(SEMANTIC_GUARD_ROUTES.get(semantic, ()))
    if not semantics:
        # Legacy contracts without semantic structure remain runnable, but cannot
        # prove that the caller's route list was complete.
        guards.extend(claim.target_guards)
    return tuple(dict.fromkeys(guards))


def unmapped_claim_semantics(claim: Claim) -> tuple[str, ...]:
    return tuple(
        semantic
        for semantic in claim_semantics(claim)
        if semantic not in SEMANTIC_GUARD_ROUTES
    )


@dataclass(frozen=True)
class WorldModel:
    model_id: str
    model_version: str
    entities: dict[str, Any] = field(default_factory=dict)
    relations: dict[str, Any] = field(default_factory=dict)
    assumptions: list[str] = field(default_factory=list)
    scope_limits: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorldModel":
        return cls(
            model_id=str(data.get("model_id", "")),
            model_version=str(data.get("model_version", data.get("artifact_version", ""))),
            entities=dict(data.get("entities", {})),
            relations=dict(data.get("relations", {})),
            assumptions=list(data.get("assumptions", [])),
            scope_limits=list(data.get("scope_limits", [])),
            data=dict(data),
        )

    def to_dict(self) -> dict[str, Any]:
        result = dict(self.data)
        result.update(
            {
                "model_id": self.model_id,
                "model_version": self.model_version,
                "entities": self.entities,
                "relations": self.relations,
                "assumptions": self.assumptions,
                "scope_limits": self.scope_limits,
            }
        )
        return result


@dataclass(frozen=True)
class GuardDependencies:
    upstream_results: list[Any] = field(default_factory=list)
    read_only: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "GuardDependencies":
        data = data or {}
        return cls(
            upstream_results=list(data.get("upstream_results", [])),
            read_only=bool(data.get("read_only", True)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "upstream_results": self.upstream_results,
            "read_only": self.read_only,
        }


@dataclass(frozen=True)
class OutputRequirements:
    require_ledgers: bool = True
    require_counterexample_for_non_pass: bool = True
    allowed_status: list[str] = field(
        default_factory=lambda: ["PASS", "FAIL", "GAP", "BOUNDARY_EXCEEDED"]
    )

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "OutputRequirements":
        data = data or {}
        return cls(
            require_ledgers=bool(data.get("require_ledgers", True)),
            require_counterexample_for_non_pass=bool(
                data.get("require_counterexample_for_non_pass", True)
            ),
            allowed_status=list(
                data.get("allowed_status", ["PASS", "FAIL", "GAP", "BOUNDARY_EXCEEDED"])
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "require_ledgers": self.require_ledgers,
            "require_counterexample_for_non_pass": self.require_counterexample_for_non_pass,
            "allowed_status": self.allowed_status,
        }


@dataclass(frozen=True)
class GuardPurposeContractBinding:
    """Frozen target-owned purpose authority carried by one Guard candidate."""

    schema_version: str
    guard: str
    purpose_id: str
    purpose: str
    blocked_claims: tuple[str, ...]
    boundary: str
    family_contract_fingerprint: str
    guard_contract_fingerprint: str
    family_guard_ids: tuple[str, ...]
    protected_failure_ids: tuple[str, ...]
    declaration_id: str
    task_contract_id: str
    run_id: str
    model_instance_id: str
    declaration_fingerprint: str
    proof_receipt_fingerprint: str
    declaration_payload: dict[str, Any]
    proof_receipt: dict[str, Any]
    frozen_for_candidate_id: str
    purpose_frozen_sequence: int = 1
    candidate_constructed_sequence: int = 2

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GuardPurposeContractBinding":
        return cls(
            schema_version=str(data.get("schema_version", "")),
            guard=str(data.get("guard", "")),
            purpose_id=str(data.get("purpose_id", "")),
            purpose=str(data.get("purpose", "")),
            blocked_claims=tuple(str(item) for item in data.get("blocked_claims", [])),
            boundary=str(data.get("boundary", "")),
            family_contract_fingerprint=str(data.get("family_contract_fingerprint", "")),
            guard_contract_fingerprint=str(data.get("guard_contract_fingerprint", "")),
            family_guard_ids=tuple(str(item) for item in data.get("family_guard_ids", [])),
            protected_failure_ids=tuple(
                str(item) for item in data.get("protected_failure_ids", [])
            ),
            declaration_id=str(data.get("declaration_id", "")),
            task_contract_id=str(data.get("task_contract_id", "")),
            run_id=str(data.get("run_id", "")),
            model_instance_id=str(data.get("model_instance_id", "")),
            declaration_fingerprint=str(data.get("declaration_fingerprint", "")),
            proof_receipt_fingerprint=str(data.get("proof_receipt_fingerprint", "")),
            declaration_payload=dict(data.get("declaration_payload", {})),
            proof_receipt=dict(data.get("proof_receipt", {})),
            frozen_for_candidate_id=str(data.get("frozen_for_candidate_id", "")),
            purpose_frozen_sequence=int(data.get("purpose_frozen_sequence", 0)),
            candidate_constructed_sequence=int(data.get("candidate_constructed_sequence", 0)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "guard": self.guard,
            "purpose_id": self.purpose_id,
            "purpose": self.purpose,
            "blocked_claims": list(self.blocked_claims),
            "boundary": self.boundary,
            "family_contract_fingerprint": self.family_contract_fingerprint,
            "guard_contract_fingerprint": self.guard_contract_fingerprint,
            "family_guard_ids": list(self.family_guard_ids),
            "protected_failure_ids": list(self.protected_failure_ids),
            "declaration_id": self.declaration_id,
            "task_contract_id": self.task_contract_id,
            "run_id": self.run_id,
            "model_instance_id": self.model_instance_id,
            "declaration_fingerprint": self.declaration_fingerprint,
            "proof_receipt_fingerprint": self.proof_receipt_fingerprint,
            "declaration_payload": self.declaration_payload,
            "proof_receipt": self.proof_receipt,
            "frozen_for_candidate_id": self.frozen_for_candidate_id,
            "purpose_frozen_sequence": self.purpose_frozen_sequence,
            "candidate_constructed_sequence": self.candidate_constructed_sequence,
        }


@dataclass(frozen=True)
class GuardContract:
    contract_id: str
    schema_version: str
    run_id: str
    claim: Claim
    world_model: WorldModel
    inputs: dict[str, Any] = field(default_factory=dict)
    dependencies: GuardDependencies = field(default_factory=GuardDependencies)
    output_requirements: OutputRequirements = field(default_factory=OutputRequirements)
    guard_purpose_declarations: tuple[dict[str, Any], ...] = ()
    guard_purpose_contract: GuardPurposeContractBinding | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GuardContract":
        return cls(
            contract_id=str(data.get("contract_id", "")),
            schema_version=str(data.get("schema_version", "worldguard.contract.v1")),
            run_id=str(data.get("run_id", "worldguard-run")),
            claim=Claim.from_dict(data.get("claim", {})),
            world_model=WorldModel.from_dict(data.get("world_model", {})),
            inputs=dict(data.get("inputs", {})),
            dependencies=GuardDependencies.from_dict(data.get("dependencies")),
            output_requirements=OutputRequirements.from_dict(data.get("output_requirements")),
            guard_purpose_declarations=tuple(
                dict(item)
                for item in data.get("guard_purpose_declarations", [])
                if isinstance(item, dict)
            ),
            guard_purpose_contract=(
                GuardPurposeContractBinding.from_dict(data["guard_purpose_contract"])
                if isinstance(data.get("guard_purpose_contract"), dict)
                else None
            ),
        )

    def for_guard(self, guard: str, upstream_results: list[Any] | None = None) -> "GuardContract":
        # Freeze the target-owned purpose authority before constructing the
        # formal child candidate.  The runtime verifier rechecks this exact
        # binding immediately before either guard or semantic proof executes.
        from .guard_model_contract import freeze_guard_purpose_contract

        dependencies = GuardDependencies(upstream_results=upstream_results or [], read_only=True)
        candidate_contract_id = f"{self.contract_id}:{guard}"
        matching_declarations = [
            item
            for item in self.guard_purpose_declarations
            if str(item.get("guard", "")) == guard
        ]
        if len(matching_declarations) != 1:
            from .guard_model_contract import GuardCandidatePurposeError

            raise GuardCandidatePurposeError(
                "GUARD_TASK_PURPOSE_DECLARATION_MISSING_OR_DUPLICATE",
                "Every formal Guard child requires exactly one explicit task-model-instance purpose declaration.",
                details={
                    "guard": guard,
                    "task_contract_id": self.contract_id,
                    "declaration_count": len(matching_declarations),
                },
            )
        purpose_binding = freeze_guard_purpose_contract(
            guard,
            candidate_contract_id=candidate_contract_id,
            task_contract_id=self.contract_id,
            run_id=self.run_id,
            model_instance_id=self.world_model.model_id,
            declaration=matching_declarations[0],
        )
        claim = Claim(
            claim_id=self.claim.claim_id,
            text=self.claim.text,
            target_guards=[guard],
            requested_semantics=self.claim.requested_semantics,
            atoms=self.claim.atoms,
        )
        return GuardContract(
            contract_id=candidate_contract_id,
            schema_version=self.schema_version,
            run_id=self.run_id,
            claim=claim,
            world_model=self.world_model,
            inputs=self.inputs,
            dependencies=dependencies,
            output_requirements=self.output_requirements,
            guard_purpose_declarations=self.guard_purpose_declarations,
            guard_purpose_contract=purpose_binding,
        )

    def to_dict(self) -> dict[str, Any]:
        result = {
            "contract_id": self.contract_id,
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "claim": self.claim.to_dict(),
            "world_model": self.world_model.to_dict(),
            "inputs": self.inputs,
            "dependencies": self.dependencies.to_dict(),
            "output_requirements": self.output_requirements.to_dict(),
            "guard_purpose_declarations": [
                dict(item) for item in self.guard_purpose_declarations
            ],
        }
        if self.guard_purpose_contract is not None:
            result["guard_purpose_contract"] = self.guard_purpose_contract.to_dict()
        return result

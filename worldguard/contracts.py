from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Claim:
    claim_id: str
    text: str
    target_guards: list[str]
    requested_semantics: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Claim":
        target_guards = data.get("target_guards", data.get("target_guard", []))
        if isinstance(target_guards, str):
            target_guards = [target_guards]
        return cls(
            claim_id=str(data.get("claim_id", "")),
            text=str(data.get("text", "")),
            target_guards=list(target_guards),
            requested_semantics=list(data.get("requested_semantics", [])),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "text": self.text,
            "target_guards": self.target_guards,
            "requested_semantics": self.requested_semantics,
        }


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
class GuardContract:
    contract_id: str
    schema_version: str
    run_id: str
    claim: Claim
    world_model: WorldModel
    inputs: dict[str, Any] = field(default_factory=dict)
    dependencies: GuardDependencies = field(default_factory=GuardDependencies)
    output_requirements: OutputRequirements = field(default_factory=OutputRequirements)

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
        )

    def for_guard(self, guard: str, upstream_results: list[Any] | None = None) -> "GuardContract":
        dependencies = GuardDependencies(upstream_results=upstream_results or [], read_only=True)
        claim = Claim(
            claim_id=self.claim.claim_id,
            text=self.claim.text,
            target_guards=[guard],
            requested_semantics=self.claim.requested_semantics,
        )
        return GuardContract(
            contract_id=f"{self.contract_id}:{guard}",
            schema_version=self.schema_version,
            run_id=self.run_id,
            claim=claim,
            world_model=self.world_model,
            inputs=self.inputs,
            dependencies=dependencies,
            output_requirements=self.output_requirements,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "claim": self.claim.to_dict(),
            "world_model": self.world_model.to_dict(),
            "inputs": self.inputs,
            "dependencies": self.dependencies.to_dict(),
            "output_requirements": self.output_requirements.to_dict(),
        }

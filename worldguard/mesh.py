from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping
from typing import Any

from .contracts import GuardContract
from .ledgers import LedgerEntry, ledger_entry
from .kernel import run_worldguard
from .reports import GuardedReport
from .status import GuardStatus, aggregate_statuses, coerce_status


FRESHNESS_STATUSES = {"current", "stale", "unknown"}
EDGE_RELATIONS = {
    "parent_child",
    "depends_on",
    "refines",
    "replaces",
    "conflicts_with",
    "consumes_output_of",
    "same_world_version",
    "supersedes",
}
CYCLE_RELATIONS = {
    "parent_child",
    "depends_on",
    "refines",
    "replaces",
    "consumes_output_of",
    "supersedes",
}


@dataclass(frozen=True)
class ModelAuthority:
    owns: list[str] = field(default_factory=list)
    excludes: list[str] = field(default_factory=list)
    scope_limits: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | None) -> "ModelAuthority":
        data = data or {}
        return cls(
            owns=list(data.get("owns", [])),
            excludes=list(data.get("excludes", [])),
            scope_limits=list(data.get("scope_limits", [])),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "owns": self.owns,
            "excludes": self.excludes,
            "scope_limits": self.scope_limits,
        }


@dataclass(frozen=True)
class ModelNode:
    model_id: str
    model_version: str = ""
    model_kind: str = "world_model"
    authority: ModelAuthority = field(default_factory=ModelAuthority)
    freshness_status: str = "current"
    contract: GuardContract | None = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ModelNode":
        contract_data = data.get("contract")
        freshness_status = str(data.get("freshness_status", "current"))
        if freshness_status not in FRESHNESS_STATUSES:
            freshness_status = "unknown"
        return cls(
            model_id=str(data.get("model_id", "")),
            model_version=str(data.get("model_version", "")),
            model_kind=str(data.get("model_kind", "world_model")),
            authority=ModelAuthority.from_dict(data.get("authority")),
            freshness_status=freshness_status,
            contract=GuardContract.from_dict(contract_data) if contract_data else None,
        )

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "model_id": self.model_id,
            "model_version": self.model_version,
            "model_kind": self.model_kind,
            "authority": self.authority.to_dict(),
            "freshness_status": self.freshness_status,
        }
        if self.contract:
            data["contract"] = self.contract.to_dict()
        return data


@dataclass(frozen=True)
class ModelEdge:
    edge_id: str
    source_model_id: str
    target_model_id: str
    relation: str = "depends_on"
    output_refs: list[str] = field(default_factory=list)
    allowed_use: list[str] = field(default_factory=list)
    forbidden_use: list[str] = field(default_factory=list)
    read_only: bool = True
    requires_current_source: bool = True

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ModelEdge":
        relation = str(data.get("relation", "depends_on"))
        if relation not in EDGE_RELATIONS:
            relation = "depends_on"
        return cls(
            edge_id=str(data.get("edge_id", "")),
            source_model_id=str(data.get("source_model_id", "")),
            target_model_id=str(data.get("target_model_id", "")),
            relation=relation,
            output_refs=list(data.get("output_refs", [])),
            allowed_use=list(data.get("allowed_use", [])),
            forbidden_use=list(data.get("forbidden_use", [])),
            read_only=bool(data.get("read_only", True)),
            requires_current_source=bool(data.get("requires_current_source", True)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "source_model_id": self.source_model_id,
            "target_model_id": self.target_model_id,
            "relation": self.relation,
            "output_refs": self.output_refs,
            "allowed_use": self.allowed_use,
            "forbidden_use": self.forbidden_use,
            "read_only": self.read_only,
            "requires_current_source": self.requires_current_source,
        }


@dataclass(frozen=True)
class WorldStateSnapshot:
    snapshot_id: str
    model_ids: list[str] = field(default_factory=list)
    status: str = "current"
    notes: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "WorldStateSnapshot":
        return cls(
            snapshot_id=str(data.get("snapshot_id", "")),
            model_ids=list(data.get("model_ids", [])),
            status=str(data.get("status", "current")),
            notes=list(data.get("notes", [])),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "model_ids": self.model_ids,
            "status": self.status,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class ModelMeshContract:
    mesh_id: str
    schema_version: str = "worldguard.model_mesh.v1"
    run_id: str = "worldguard-mesh-run"
    nodes: list[ModelNode] = field(default_factory=list)
    edges: list[ModelEdge] = field(default_factory=list)
    snapshots: list[WorldStateSnapshot] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ModelMeshContract":
        return cls(
            mesh_id=str(data.get("mesh_id", "")),
            schema_version=str(data.get("schema_version", "worldguard.model_mesh.v1")),
            run_id=str(data.get("run_id", "worldguard-mesh-run")),
            nodes=[ModelNode.from_dict(item) for item in data.get("nodes", [])],
            edges=[ModelEdge.from_dict(item) for item in data.get("edges", [])],
            snapshots=[
                WorldStateSnapshot.from_dict(item) for item in data.get("snapshots", [])
            ],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "mesh_id": self.mesh_id,
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "snapshots": [snapshot.to_dict() for snapshot in self.snapshots],
        }


@dataclass(frozen=True)
class MeshFinding:
    finding_id: str
    status: GuardStatus
    code: str
    message: str
    node_id: str = ""
    edge_id: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", coerce_status(self.status))

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "status": self.status.value,
            "code": self.code,
            "message": self.message,
            "node_id": self.node_id,
            "edge_id": self.edge_id,
            "evidence": self.evidence,
        }


@dataclass(frozen=True)
class MeshReport:
    status: GuardStatus
    node_reports: dict[str, GuardedReport] = field(default_factory=dict)
    findings: list[MeshFinding] = field(default_factory=list)
    aggregate_ledger: list[LedgerEntry] = field(default_factory=list)
    scope_limits: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", coerce_status(self.status))

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "node_reports": {
                model_id: report.to_dict() for model_id, report in self.node_reports.items()
            },
            "findings": [finding.to_dict() for finding in self.findings],
            "aggregate_ledger": [entry.to_dict() for entry in self.aggregate_ledger],
            "scope_limits": self.scope_limits,
        }


def run_model_mesh(mesh: ModelMeshContract | Mapping[str, Any]) -> MeshReport:
    if not isinstance(mesh, ModelMeshContract):
        mesh = ModelMeshContract.from_dict(dict(mesh))

    node_reports: dict[str, GuardedReport] = {}
    findings: list[MeshFinding] = []
    aggregate_ledger: list[LedgerEntry] = []
    node_ids: set[str] = set()
    duplicate_ids: set[str] = set()

    for node in mesh.nodes:
        if node.model_id in node_ids:
            duplicate_ids.add(node.model_id)
        node_ids.add(node.model_id)
        findings.extend(_authority_findings(mesh, node))
        if node.contract is not None:
            report = run_worldguard(node.contract)
            node_reports[node.model_id] = report
            aggregate_ledger.extend(report.aggregate_ledger)

    for model_id in sorted(duplicate_ids):
        findings.append(
            _finding(
                mesh,
                GuardStatus.FAIL,
                "MESH_DUPLICATE_MODEL_ID",
                "Duplicate model ids make mesh topology ambiguous.",
                node_id=model_id,
                evidence={"model_id": model_id},
            )
        )

    for edge in mesh.edges:
        findings.extend(_edge_findings(mesh, edge, node_ids, {node.model_id: node for node in mesh.nodes}))

    for cycle in _cycles(mesh.edges):
        findings.append(
            _finding(
                mesh,
                GuardStatus.FAIL,
                "MESH_DEPENDENCY_CYCLE",
                "Mesh dependency edges contain a cycle.",
                evidence={"cycle": cycle},
            )
        )

    aggregate_ledger.extend(_finding_ledgers(mesh, findings))
    statuses = [report.status for report in node_reports.values()]
    statuses.extend(finding.status for finding in findings)
    status = aggregate_statuses(statuses) if statuses else GuardStatus.GAP
    scope_limits = []
    for node in mesh.nodes:
        scope_limits.extend(node.authority.scope_limits)
    return MeshReport(
        status=status,
        node_reports=node_reports,
        findings=findings,
        aggregate_ledger=aggregate_ledger,
        scope_limits=scope_limits,
    )


def _authority_findings(mesh: ModelMeshContract, node: ModelNode) -> list[MeshFinding]:
    if node.contract is None:
        return []
    requested = set(node.contract.claim.requested_semantics)
    excluded = requested.intersection(node.authority.excludes)
    if excluded:
        return [
            _finding(
                mesh,
                GuardStatus.BOUNDARY_EXCEEDED,
                "MESH_AUTHORITY_EXCLUDED_SEMANTIC",
                "Node contract requests semantics excluded by model authority.",
                node_id=node.model_id,
                evidence={"excluded_semantics": sorted(excluded)},
            )
        ]
    missing = requested.difference(node.authority.owns)
    if node.authority.owns and missing:
        return [
            _finding(
                mesh,
                GuardStatus.GAP,
                "MESH_AUTHORITY_UNOWNED_SEMANTIC",
                "Node contract requests semantics not owned by model authority.",
                node_id=node.model_id,
                evidence={"unowned_semantics": sorted(missing)},
            )
        ]
    return []


def _edge_findings(
    mesh: ModelMeshContract,
    edge: ModelEdge,
    node_ids: set[str],
    nodes_by_id: dict[str, ModelNode],
) -> list[MeshFinding]:
    findings: list[MeshFinding] = []
    if edge.source_model_id not in node_ids:
        findings.append(
            _finding(
                mesh,
                GuardStatus.GAP,
                "MESH_MISSING_SOURCE_NODE",
                "Handoff source model id is missing from mesh nodes.",
                edge_id=edge.edge_id,
                evidence=edge.to_dict(),
            )
        )
    if edge.target_model_id not in node_ids:
        findings.append(
            _finding(
                mesh,
                GuardStatus.GAP,
                "MESH_MISSING_TARGET_NODE",
                "Handoff target model id is missing from mesh nodes.",
                edge_id=edge.edge_id,
                evidence=edge.to_dict(),
            )
        )
    if not edge.read_only:
        findings.append(
            _finding(
                mesh,
                GuardStatus.FAIL,
                "MESH_MUTABLE_HANDOFF",
                "Mesh handoffs must be read-only.",
                edge_id=edge.edge_id,
                evidence=edge.to_dict(),
            )
        )
    forbidden = sorted(set(edge.output_refs).intersection(edge.forbidden_use))
    if forbidden:
        findings.append(
            _finding(
                mesh,
                GuardStatus.FAIL,
                "MESH_FORBIDDEN_DOWNSTREAM_USE",
                "Downstream handoff consumes output refs listed as forbidden.",
                edge_id=edge.edge_id,
                evidence={"forbidden_refs": forbidden, "edge": edge.to_dict()},
            )
        )
    if edge.allowed_use:
        unallowed = sorted(set(edge.output_refs).difference(edge.allowed_use))
        if unallowed:
            findings.append(
                _finding(
                    mesh,
                    GuardStatus.BOUNDARY_EXCEEDED,
                    "MESH_UNALLOWED_DOWNSTREAM_USE",
                    "Downstream handoff consumes output refs outside the allowed-use boundary.",
                    edge_id=edge.edge_id,
                    evidence={"unallowed_refs": unallowed, "edge": edge.to_dict()},
                )
            )
    source = nodes_by_id.get(edge.source_model_id)
    if edge.requires_current_source and source and source.freshness_status != "current":
        findings.append(
            _finding(
                mesh,
                GuardStatus.GAP,
                "MESH_STALE_SOURCE",
                "Handoff requires current source evidence but source is not current.",
                node_id=edge.source_model_id,
                edge_id=edge.edge_id,
                evidence={"freshness_status": source.freshness_status, "edge": edge.to_dict()},
            )
        )
    return findings


def _cycles(edges: list[ModelEdge]) -> list[list[str]]:
    graph: dict[str, list[str]] = {}
    for edge in edges:
        if edge.relation in CYCLE_RELATIONS:
            graph.setdefault(edge.source_model_id, []).append(edge.target_model_id)

    visiting: list[str] = []
    visited: set[str] = set()
    cycles: list[list[str]] = []

    def visit(node: str) -> None:
        if node in visiting:
            cycles.append([*visiting[visiting.index(node) :], node])
            return
        if node in visited:
            return
        visiting.append(node)
        for child in graph.get(node, []):
            visit(child)
        visiting.pop()
        visited.add(node)

    for node in list(graph):
        visit(node)
    return cycles


def _finding(
    mesh: ModelMeshContract,
    status: GuardStatus,
    code: str,
    message: str,
    *,
    node_id: str = "",
    edge_id: str = "",
    evidence: dict[str, Any] | None = None,
) -> MeshFinding:
    suffix = node_id or edge_id or str(len(code))
    return MeshFinding(
        finding_id=f"{mesh.run_id}:{mesh.mesh_id}:{code}:{suffix}",
        status=status,
        code=code,
        message=message,
        node_id=node_id,
        edge_id=edge_id,
        evidence=evidence or {},
    )


def _finding_ledgers(mesh: ModelMeshContract, findings: list[MeshFinding]) -> list[LedgerEntry]:
    entries = []
    for finding in findings:
        if finding.status == GuardStatus.FAIL:
            impact = "supports_fail"
            channel = "aggregate"
        elif finding.status == GuardStatus.GAP:
            impact = "creates_gap"
            channel = "gap"
        elif finding.status == GuardStatus.BOUNDARY_EXCEEDED:
            impact = "marks_boundary"
            channel = "boundary"
        else:
            impact = "informational"
            channel = "aggregate"
        entries.append(
            ledger_entry(
                run_id=mesh.run_id,
                claim_id=mesh.mesh_id,
                guard="ModelMesh",
                channel=channel,
                status_impact=impact,
                payload=finding.to_dict(),
                step=finding.code,
            )
        )
    return entries

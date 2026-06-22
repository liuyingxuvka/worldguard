import json

import yaml

from worldguard import ModelMeshContract, MeshReport, run_model_mesh
from worldguard.cli import main
from worldguard.status import GuardStatus


def pass_mesh():
    return {
        "mesh_id": "mesh-pass",
        "run_id": "mesh-test",
        "nodes": [
            {
                "model_id": "event-source",
                "model_version": "v1",
                "freshness_status": "current",
                "authority": {"owns": ["event"], "excludes": ["norm"]},
                "contract": {
                    "contract_id": "event-contract",
                    "run_id": "mesh-test",
                    "claim": {
                        "claim_id": "event-claim",
                        "text": "operator starts after precheck",
                        "target_guards": ["EventGuard"],
                        "requested_semantics": ["event"],
                    },
                    "world_model": {"model_id": "event-model", "model_version": "v1"},
                    "inputs": {"events": [{"event_id": "e1", "initiates": "ready"}]},
                },
            },
            {
                "model_id": "norm-target",
                "model_version": "v1",
                "freshness_status": "current",
                "authority": {"owns": ["norm"], "excludes": ["resource"]},
                "contract": {
                    "contract_id": "norm-contract",
                    "run_id": "mesh-test",
                    "claim": {
                        "claim_id": "norm-claim",
                        "text": "operator may start",
                        "target_guards": ["NormGuard"],
                        "requested_semantics": ["norm"],
                    },
                    "world_model": {"model_id": "norm-model", "model_version": "v1"},
                    "inputs": {"norms": [{"modality": "permitted", "action": "start"}]},
                },
            },
        ],
        "edges": [
            {
                "edge_id": "event-to-norm",
                "source_model_id": "event-source",
                "target_model_id": "norm-target",
                "relation": "consumes_output_of",
                "output_refs": ["ready"],
                "allowed_use": ["ready"],
                "forbidden_use": [],
                "read_only": True,
                "requires_current_source": True,
            }
        ],
    }


def test_model_mesh_pass_preserves_child_ledgers():
    report = run_model_mesh(pass_mesh())

    assert report.status == GuardStatus.PASS
    assert set(report.node_reports) == {"event-source", "norm-target"}
    assert any(entry.channel == "event" for entry in report.aggregate_ledger)
    assert any(entry.channel == "norm" for entry in report.aggregate_ledger)


def test_child_gap_prevents_mesh_pass_and_preserves_gap_ledger():
    mesh = pass_mesh()
    mesh["nodes"][0]["contract"]["inputs"] = {}

    report = run_model_mesh(mesh)

    assert report.status == GuardStatus.GAP
    assert any(entry.channel == "gap" for entry in report.aggregate_ledger)


def test_authority_excluded_semantic_marks_boundary():
    mesh = pass_mesh()
    mesh["nodes"][1]["authority"]["excludes"] = ["norm"]

    report = run_model_mesh(mesh)

    assert report.status == GuardStatus.BOUNDARY_EXCEEDED
    assert any(finding.code == "MESH_AUTHORITY_EXCLUDED_SEMANTIC" for finding in report.findings)


def test_forbidden_handoff_use_fails_mesh():
    mesh = pass_mesh()
    mesh["edges"][0]["output_refs"] = ["secret"]
    mesh["edges"][0]["forbidden_use"] = ["secret"]

    report = run_model_mesh(mesh)

    assert report.status == GuardStatus.FAIL
    assert any(finding.code == "MESH_FORBIDDEN_DOWNSTREAM_USE" for finding in report.findings)


def test_unallowed_handoff_use_marks_boundary():
    mesh = pass_mesh()
    mesh["edges"][0]["output_refs"] = ["unexpected"]
    mesh["edges"][0]["allowed_use"] = ["ready"]

    report = run_model_mesh(mesh)

    assert report.status == GuardStatus.BOUNDARY_EXCEEDED
    assert any(finding.code == "MESH_UNALLOWED_DOWNSTREAM_USE" for finding in report.findings)


def test_stale_source_creates_gap_when_current_source_required():
    mesh = pass_mesh()
    mesh["nodes"][0]["freshness_status"] = "stale"

    report = run_model_mesh(mesh)

    assert report.status == GuardStatus.GAP
    assert any(finding.code == "MESH_STALE_SOURCE" for finding in report.findings)


def test_dependency_cycle_fails_mesh():
    mesh = {
        "mesh_id": "cycle-mesh",
        "run_id": "mesh-test",
        "nodes": [{"model_id": "a"}, {"model_id": "b"}],
        "edges": [
            {"edge_id": "a-b", "source_model_id": "a", "target_model_id": "b"},
            {"edge_id": "b-a", "source_model_id": "b", "target_model_id": "a"},
        ],
    }

    report = run_model_mesh(mesh)

    assert report.status == GuardStatus.FAIL
    assert any(finding.code == "MESH_DEPENDENCY_CYCLE" for finding in report.findings)


def test_public_api_exports_model_mesh():
    mesh = ModelMeshContract.from_dict(pass_mesh())
    report = run_model_mesh(mesh)

    assert isinstance(report, MeshReport)


def test_cli_mesh_check_outputs_json(tmp_path, capsys):
    path = tmp_path / "mesh.yaml"
    path.write_text(yaml.safe_dump(pass_mesh()), encoding="utf-8")

    assert main(["mesh-check", "--mesh", str(path)]) == 0
    data = json.loads(capsys.readouterr().out)

    assert data["status"] == "PASS"
    assert set(data["node_reports"]) == {"event-source", "norm-target"}

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "skills"
    / "worldguard"
    / "scripts"
    / "check_internal_guard_topology.py"
)
SPEC = importlib.util.spec_from_file_location(
    "worldguard_internal_topology_check", SCRIPT
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _payload() -> dict:
    return json.loads(
        (
            ROOT
            / "skills"
            / "worldguard"
            / "references"
            / "internal-guard-routes.json"
        ).read_text(encoding="utf-8")
    )


def test_current_worldguard_has_one_entry_and_seven_internal_routes():
    report = MODULE.check(ROOT)

    assert report["ok"], report["findings"]
    assert report["public_skill_ids"] == ["worldguard"]
    assert report["project_console_ids"] == ["worldguard"]
    assert report["source_version"] == "0.5.0"
    assert len(report["internal_guard_ids"]) == 7


def test_source_version_identity_drift_is_rejected(monkeypatch):
    monkeypatch.setattr(MODULE, "EXPECTED_VERSION", "9.9.9")

    report = MODULE.check(ROOT)

    assert not report["ok"]
    assert "source_version_file_mismatch" in {
        finding["code"] for finding in report["findings"]
    }


def test_missing_internal_route_is_rejected(tmp_path: Path):
    payload = _payload()
    payload["routes"] = payload["routes"][:-1]
    topology = tmp_path / "topology.json"
    topology.write_text(json.dumps(payload), encoding="utf-8")

    report = MODULE.check(ROOT, topology_path=topology)

    assert not report["ok"]
    assert "declared_guard_inventory_mismatch" in {
        finding["code"] for finding in report["findings"]
    }


def test_non_predictive_guard_cannot_claim_predictive_mode(tmp_path: Path):
    payload = _payload()
    agent = next(
        row for row in payload["routes"] if row["guard_id"] == "AgentGuard"
    )
    agent["prediction_mode"] = "claim_derived_predictive_participant"
    topology = tmp_path / "topology.json"
    topology.write_text(json.dumps(payload), encoding="utf-8")

    report = MODULE.check(ROOT, topology_path=topology)

    assert not report["ok"]
    assert any(
        finding["code"] == "internal_route_binding_mismatch"
        and finding.get("guard_id") == "AgentGuard"
        and finding.get("field") == "prediction_mode"
        for finding in report["findings"]
    )


def test_retired_runtime_authority_path_is_rejected(tmp_path: Path):
    alignment = tmp_path / "run_claim_derived_coverage_checks.py"
    alignment.write_text(
        "\n".join(
            (
                '"worldguard/skillguard_depth.py"',
                '"worldguard/execution_depth.py"',
                '"worldguard/execution_depth.py"',
                '"worldguard/execution_depth.py"',
            )
        ),
        encoding="utf-8",
    )

    report = MODULE.check(ROOT, flowguard_alignment_path=alignment)

    assert not report["ok"]
    assert "retired_runtime_authority_path_present" in {
        finding["code"] for finding in report["findings"]
    }

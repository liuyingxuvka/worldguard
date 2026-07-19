from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = (
    ROOT / "openspec/changes/harden-guard-simulation-readiness/verification-contract.yaml",
    ROOT / "openspec/changes/enforce-claim-derived-semantic-coverage/verification-contract.yaml",
    ROOT / "openspec/changes/add-worldguard-template-pack-builder/verification-contract.yaml",
)


def test_active_changes_use_target_owned_read_only_evidence_references() -> None:
    for contract in CONTRACTS:
        payload = yaml.safe_load(contract.read_text(encoding="utf-8"))
        assert len(payload["checks"]) == 1
        check = payload["checks"][0]
        assert check["kind"] == "immutable_evidence_reference"
        assert "command" not in check and "execution_owner" not in check
        assert check["semantic_check_id"]
        assert set(check["artifact_ref"]) == {
            "ref_path",
            "expected_schema",
            "expected_status",
        }
        assert check["artifact_ref"]["ref_path"].startswith(
            f"work/verification/{payload['change']}/"
        )
        assert check["artifact_ref"]["expected_status"] == "passed"
        assert check["consumer"] == "worldguard.release-gate"
        assert check["execution_policy"] == {
            "owner_execution_allowed": False,
            "resume_allowed": False,
            "verification_mode": "read_only_replay",
        }
        serialized = contract.read_text(encoding="utf-8")
        assert "provider_id:" not in serialized
        assert "portable-receipt.v1" not in serialized
        assert "openspec.verify-change" not in serialized
        assert "--resume" not in serialized

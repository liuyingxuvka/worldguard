from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = (
    ROOT / "openspec/changes/harden-guard-simulation-readiness/verification-contract.yaml",
    ROOT / "openspec/changes/enforce-claim-derived-semantic-coverage/verification-contract.yaml",
)


def test_openspec_only_consumes_one_external_parent_receipt() -> None:
    for contract in CONTRACTS:
        payload = yaml.safe_load(contract.read_text(encoding="utf-8"))
        assert len(payload["checks"]) == 1
        check = payload["checks"][0]
        assert check["kind"] == "receipt"
        assert "command" not in check and "execution_owner" not in check
        assert check["semantic_check_id"] and check["execution_id"]
        assert check["semantic_check_id"] != check["execution_id"]
        assert set(check["receipt_ref"]) == {"provider_id", "work_package_id", "adapter", "ref_path"}
        assert check["receipt_ref"]["provider_id"] == "skillguard"
        assert check["receipt_ref"]["adapter"] == "portable-receipt.v1"
        assert check["receipt_ref"]["work_package_id"] == payload["change"]
        assert check["receipt_ref"]["ref_path"].startswith(f"work/verification/{payload['change']}/")
        assert "--resume" not in contract.read_text(encoding="utf-8")

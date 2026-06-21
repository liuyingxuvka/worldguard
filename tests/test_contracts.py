import pytest

from worldguard.contracts import GuardContract
from worldguard.reports import GuardResult
from worldguard.status import GuardStatus


def test_target_guard_alias_normalizes_to_target_guards():
    contract = GuardContract.from_dict(
        {
            "contract_id": "c1",
            "run_id": "r1",
            "claim": {"claim_id": "claim", "text": "text", "target_guard": "EventGuard"},
            "world_model": {"model_id": "m1", "model_version": "v1"},
        }
    )

    assert contract.claim.target_guards == ["EventGuard"]
    assert "target_guard" not in contract.claim.to_dict()


def test_non_pass_result_requires_evidence():
    with pytest.raises(ValueError, match="lacks non-pass evidence"):
        GuardResult(
            result_id="r",
            contract_id="c",
            guard="EventGuard",
            status=GuardStatus.GAP,
            ledgers={"gap": []},
        )


def test_contract_serializes_canonical_fields():
    contract = GuardContract.from_dict(
        {
            "contract_id": "c1",
            "schema_version": "worldguard.contract.v1",
            "run_id": "r1",
            "claim": {"claim_id": "claim", "text": "text", "target_guards": ["NormGuard"]},
            "world_model": {"model_id": "m1", "model_version": "v1", "scope_limits": ["toy"]},
            "inputs": {"norms": []},
        }
    )

    data = contract.to_dict()
    assert data["claim"]["target_guards"] == ["NormGuard"]
    assert data["dependencies"]["read_only"] is True
    assert data["output_requirements"]["require_ledgers"] is True

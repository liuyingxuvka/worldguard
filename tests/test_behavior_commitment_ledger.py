from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from flowguard import review_behavior_commitment_ledger


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / ".flowguard" / "behavior_commitment_ledger" / "model.py"


def _load_model():
    spec = importlib.util.spec_from_file_location(
        "worldguard_behavior_commitment_model",
        MODEL_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_primary_path_authority_is_current_and_has_no_fallback_candidates():
    model = _load_model()
    reports = model.build_primary_path_reports()

    assert all(report.ok for report in reports)
    assert all(report.fallback_candidate_ids == () for report in reports)
    assert {report.primary_path_id for report in reports} == {
        model.INPUT_PATH_ID,
        model.TEMPLATE_PATH_ID,
    }


def test_behavior_commitment_ledger_covers_both_changed_authorities():
    model = _load_model()
    report = review_behavior_commitment_ledger(
        model.build_worldguard_behavior_commitment_ledger()
    )

    assert report.ok
    assert set(report.covered_commitment_ids) == {
        model.INPUT_COMMITMENT_ID,
        model.TEMPLATE_COMMITMENT_ID,
    }
    assert set(report.path_sensitive_commitment_ids) == {
        model.INPUT_COMMITMENT_ID,
        model.TEMPLATE_COMMITMENT_ID,
    }


def test_validation_shards_share_only_the_declared_validator_authority():
    model = _load_model()
    input_specific = set(model.INPUT_EVIDENCE_FILES)
    template_specific = set(model.TEMPLATE_EVIDENCE_FILES)
    shared = set(model.SHARED_EVIDENCE_FILES)
    input_files = set(model.EVIDENCE_FILES_BY_SHARD["input"])
    template_files = set(model.EVIDENCE_FILES_BY_SHARD["template"])

    assert input_specific
    assert template_specific
    assert input_specific.isdisjoint(template_specific)
    assert input_files & template_files == shared
    assert set(model.current_fingerprints("input")) == input_files
    assert set(model.current_fingerprints("template")) == template_files
    assert "tests/test_template_packs.py" not in input_files
    assert "tests/test_contracts.py" not in template_files


def test_each_current_validation_receipt_binds_only_its_named_shard():
    model = _load_model()

    for shard_id, path in model.VALIDATION_PATHS.items():
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["shard_id"] == shard_id
        assert payload["artifact_fingerprints"] == model.current_fingerprints(
            shard_id
        )
        assert payload["receipt_hash"] == model.validation_receipt_hash(payload)

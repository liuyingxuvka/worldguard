from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from worldguard.cli import main
from worldguard.task_local_revision import (
    CandidateWorldModelRevision,
    ObservedWorldSnapshot,
    PredictionSnapshot,
    compare_observed_world,
    evaluate_candidate_world_revision,
    freeze_prediction_snapshot,
)

ROOT = Path(__file__).resolve().parents[1]


def _model(tmp_path: Path, name: str, text: str) -> dict[str, str]:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return {
        "model_id": f"model:{name}",
        "model_version": "1",
        "path": name,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _prediction(model: dict[str, str], prediction_id: str = "prediction-1") -> dict:
    return {
        "prediction_id": prediction_id,
        "model": model,
        "prediction_sequence": 10,
        "initial_state": {"temperature": 70.0},
        "intervention": {"cooling_command": 0.7},
        "expected_values": [
            {
                "expectation_id": "value-voltage",
                "target_id": "voltage",
                "expected_value": 0.72,
                "tolerance": 0.02,
                "mismatch_category": "causal_relation",
                "weakening_condition": "voltage lies outside the declared tolerance",
            }
        ],
        "expected_relationships": [
            {
                "expectation_id": "relation-command-before-response",
                "relationship_id": "command-before-response",
                "left": "cooling_command",
                "relation": "before",
                "right": "temperature_response",
                "mismatch_category": "transition",
                "weakening_condition": "the response precedes or lacks the command",
            }
        ],
        "weakening_conditions": [
            "voltage misses its tolerance",
            "the declared command-response ordering is absent",
        ],
    }


def _observation(
    prediction_id: str = "prediction-1",
    *,
    observation_id: str = "observation-1",
    voltage: float = 0.73,
    include_relationship: bool = True,
) -> dict:
    relationships = []
    if include_relationship:
        relationships.append(
            {
                "relationship_id": "command-before-response",
                "left": "cooling_command",
                "relation": "before",
                "right": "temperature_response",
            }
        )
    return {
        "observation_id": observation_id,
        "prediction_id": prediction_id,
        "observation_sequence": 11,
        "source_ref": f"test://{observation_id}",
        "values": {"voltage": voltage},
        "relationships": relationships,
    }


def _comparison(
    tmp_path: Path,
    candidate: dict[str, str],
    *,
    observation_id: str,
) -> dict:
    prediction = PredictionSnapshot.from_dict(
        _prediction(candidate, prediction_id=f"prediction-{observation_id}")
    )
    observation = ObservedWorldSnapshot.from_dict(
        _observation(
            prediction.prediction_id,
            observation_id=observation_id,
        )
    )
    return compare_observed_world(prediction, observation, base_dir=tmp_path)


def _revision(
    base: dict[str, str],
    candidate: dict[str, str],
    original: dict,
    holdout: dict,
    *,
    candidate_applied: bool = False,
    rollback_model: dict[str, str] | None = None,
) -> dict:
    return {
        "revision_id": "revision-1",
        "prediction_id": "prediction-1",
        "base_model": base,
        "candidate_model": candidate,
        "revision_kind": "update_causal_relation",
        "triggering_mismatch_ids": ["prediction-1:value-voltage:contradicted"],
        "required_revalidation_ids": ["original", "holdout"],
        "revalidations": [
            {
                "check_id": "original",
                "role": "original_scenario",
                "candidate_model": candidate,
                "semantic_rollout_status": "PASS",
                "empirical_comparison": original,
                "evidence_ref": "test://original",
            },
            {
                "check_id": "holdout",
                "role": "real_holdout_observation",
                "candidate_model": candidate,
                "semantic_rollout_status": "PASS",
                "empirical_comparison": holdout,
                "evidence_ref": "test://holdout",
            },
        ],
        "candidate_applied": candidate_applied,
        "rollback_model": rollback_model,
    }


def test_prediction_snapshot_freezes_current_model(tmp_path: Path) -> None:
    prediction = PredictionSnapshot.from_dict(_prediction(_model(tmp_path, "v1.json", "{}")))

    first = freeze_prediction_snapshot(prediction, base_dir=tmp_path)
    second = freeze_prediction_snapshot(prediction, base_dir=tmp_path)

    assert first["status"] == "pass"
    assert first["prediction_fingerprint"] == second["prediction_fingerprint"]
    assert first["model_identity"]["status"] == "current"


def test_observation_must_be_later_than_prediction(tmp_path: Path) -> None:
    prediction = PredictionSnapshot.from_dict(_prediction(_model(tmp_path, "v1.json", "{}")))
    row = _observation()
    row["observation_sequence"] = 10

    with pytest.raises(ValueError, match="strictly later"):
        compare_observed_world(
            prediction,
            ObservedWorldSnapshot.from_dict(row),
            base_dir=tmp_path,
        )


def test_numeric_values_and_relationships_are_compared_and_retained(
    tmp_path: Path,
) -> None:
    prediction = PredictionSnapshot.from_dict(_prediction(_model(tmp_path, "v1.json", "{}")))
    observation = ObservedWorldSnapshot.from_dict(_observation())

    receipt = compare_observed_world(prediction, observation, base_dir=tmp_path)

    assert receipt["status"] == "pass"
    assert len(receipt["matches"]) == 2
    value_match = next(row for row in receipt["matches"] if row["expectation_kind"] == "value")
    relation_match = next(
        row for row in receipt["matches"] if row["expectation_kind"] == "relationship"
    )
    assert value_match["actual_value"] == 0.73
    assert relation_match["actual_relationship"]["relation"] == "before"


def test_missing_and_contradicted_expectations_keep_native_categories(
    tmp_path: Path,
) -> None:
    prediction = PredictionSnapshot.from_dict(_prediction(_model(tmp_path, "v1.json", "{}")))
    observation = ObservedWorldSnapshot.from_dict(
        _observation(voltage=0.61, include_relationship=False)
    )

    receipt = compare_observed_world(prediction, observation, base_dir=tmp_path)

    assert receipt["status"] == "fail"
    by_code = {row["mismatch_code"]: row for row in receipt["mismatches"]}
    assert by_code["value_outside_tolerance"]["mismatch_category"] == "causal_relation"
    assert by_code["expected_relationship_missing"]["mismatch_category"] == "transition"


def test_candidate_acceptance_requires_both_revalidation_roles(tmp_path: Path) -> None:
    base = _model(tmp_path, "v1.json", '{"version": 1}')
    candidate = _model(tmp_path, "v2.json", '{"version": 2}')
    original = _comparison(tmp_path, candidate, observation_id="original")
    holdout = _comparison(tmp_path, candidate, observation_id="holdout")
    revision = CandidateWorldModelRevision.from_dict(
        _revision(base, candidate, original, holdout)
    )

    receipt = evaluate_candidate_world_revision(revision, base_dir=tmp_path)

    assert receipt["disposition"] == "accepted"
    assert receipt["base_model_preserved"] is True
    assert all(
        item["effective_status"] == "pass"
        for item in receipt["revalidation_results"]
    )


def test_semantic_rollout_alone_cannot_replace_real_holdout_comparison(
    tmp_path: Path,
) -> None:
    base = _model(tmp_path, "v1.json", '{"version": 1}')
    candidate = _model(tmp_path, "v2.json", '{"version": 2}')
    original = _comparison(tmp_path, candidate, observation_id="original")
    holdout = _comparison(tmp_path, candidate, observation_id="holdout")
    holdout["status"] = "fail"
    holdout["mismatches"] = [{"mismatch_id": "holdout:reality"}]
    revision = CandidateWorldModelRevision.from_dict(
        _revision(base, candidate, original, holdout)
    )

    receipt = evaluate_candidate_world_revision(revision, base_dir=tmp_path)

    assert receipt["disposition"] == "rejected"
    holdout_result = next(
        item
        for item in receipt["revalidation_results"]
        if item["role"] == "real_holdout_observation"
    )
    assert holdout_result["semantic_rollout_status"] == "pass"
    assert "empirical_comparison_non_pass" in holdout_result["issues"]


def test_failed_unapplied_candidate_is_rejected_without_overwriting_base(
    tmp_path: Path,
) -> None:
    base = _model(tmp_path, "v1.json", '{"version": 1}')
    candidate = _model(tmp_path, "v2.json", '{"version": 2}')
    original = _comparison(tmp_path, candidate, observation_id="original")
    holdout = _comparison(tmp_path, candidate, observation_id="holdout")
    row = _revision(base, candidate, original, holdout)
    row["revalidations"][0]["semantic_rollout_status"] = "FAIL"

    receipt = evaluate_candidate_world_revision(
        CandidateWorldModelRevision.from_dict(row),
        base_dir=tmp_path,
    )

    assert receipt["disposition"] == "rejected"
    assert receipt["base_model_preserved"] is True
    assert (tmp_path / "v1.json").read_text(encoding="utf-8") == '{"version": 1}'


def test_failed_applied_candidate_rolls_back_to_exact_current_base(
    tmp_path: Path,
) -> None:
    base = _model(tmp_path, "v1.json", '{"version": 1}')
    candidate = _model(tmp_path, "v2.json", '{"version": 2}')
    original = _comparison(tmp_path, candidate, observation_id="original")
    holdout = _comparison(tmp_path, candidate, observation_id="holdout")
    row = _revision(
        base,
        candidate,
        original,
        holdout,
        candidate_applied=True,
        rollback_model=base,
    )
    row["revalidations"][1]["semantic_rollout_status"] = "GAP"

    receipt = evaluate_candidate_world_revision(
        CandidateWorldModelRevision.from_dict(row),
        base_dir=tmp_path,
    )

    assert receipt["disposition"] == "rolled_back"
    assert receipt["rollback_model"]["actual_sha256"] == base["sha256"]


def test_candidate_must_not_alias_base(tmp_path: Path) -> None:
    base = _model(tmp_path, "v1.json", '{"version": 1}')
    original = _comparison(tmp_path, base, observation_id="original")
    holdout = _comparison(tmp_path, base, observation_id="holdout")
    revision = CandidateWorldModelRevision.from_dict(
        _revision(base, base, original, holdout)
    )

    receipt = evaluate_candidate_world_revision(revision, base_dir=tmp_path)

    assert receipt["disposition"] == "blocked"
    assert "candidate_not_distinct_from_base" in receipt["identity_findings"]


def test_task_model_cli_freezes_and_compares(tmp_path: Path, capsys) -> None:
    prediction_path = tmp_path / "prediction.json"
    observation_path = tmp_path / "observation.json"
    prediction_path.write_text(
        json.dumps(_prediction(_model(tmp_path, "v1.json", "{}"))),
        encoding="utf-8",
    )
    observation_path.write_text(json.dumps(_observation()), encoding="utf-8")

    assert main(["task-model", "freeze", str(prediction_path)]) == 0
    frozen = json.loads(capsys.readouterr().out)
    assert frozen["artifact_kind"] == "worldguard_prediction_snapshot_receipt"

    assert (
        main(
            [
                "task-model",
                "compare",
                str(prediction_path),
                str(observation_path),
            ]
        )
        == 0
    )
    compared = json.loads(capsys.readouterr().out)
    assert compared["status"] == "pass"


def test_bundled_task_local_runtime_matches_source_and_version() -> None:
    bundled_root = (
        ROOT / "skills" / "worldguard" / "runtime" / "worldguard"
    )
    for relative_path in ("task_local_revision.py", "cli.py", "__init__.py"):
        assert (ROOT / "worldguard" / relative_path).read_bytes() == (
            bundled_root / relative_path
        ).read_bytes()
    assert '__version__ = "0.6.0"' in (
        bundled_root / "__init__.py"
    ).read_text(encoding="utf-8")


def test_task_local_prediction_requires_independent_coverage_inventory(tmp_path: Path) -> None:
    row = _prediction(_model(tmp_path, "v1.json", "{}"))
    row["task_id"] = "task-1"
    with pytest.raises(ValueError, match="coverage_ids"):
        PredictionSnapshot.from_dict(row)


def test_compare_receipt_exposes_open_gap_and_closure_reason(tmp_path: Path) -> None:
    model = _model(tmp_path, "v1.json", "{}")
    row = _prediction(model)
    row.update({"task_id": "task-1", "purpose": "predict voltage", "coverage_ids": ["value-voltage", "command-before-response"]})
    prediction = PredictionSnapshot.from_dict(row)
    observation = ObservedWorldSnapshot.from_dict(
        _observation(include_relationship=False)
    )
    receipt = compare_observed_world(prediction, observation, base_dir=tmp_path)
    assert receipt["terminal_reason"] == "continue_iteration"
    assert receipt["open_gap_ids"]
    assert receipt["next_actions"]


def test_candidate_with_predictive_gap_continues_instead_of_accepting(tmp_path: Path) -> None:
    base = _model(tmp_path, "v1.json", "{\"version\": 1}")
    candidate = _model(tmp_path, "v2.json", "{\"version\": 2}")
    original = _comparison(tmp_path, candidate, observation_id="original")
    holdout = _comparison(tmp_path, candidate, observation_id="holdout")
    row = _revision(base, candidate, original, holdout)
    row.update({
        "task_id": "task-1",
        "iteration": 1,
        "remaining_predictive_gap_ids": ["scenario:new-regime"],
        "next_actions": ["acquire_holdout"],
    })
    receipt = evaluate_candidate_world_revision(
        CandidateWorldModelRevision.from_dict(row),
        base_dir=tmp_path,
    )
    assert receipt["disposition"] == "continue_iteration"
    assert receipt["terminal_reason"] == "continue_iteration"

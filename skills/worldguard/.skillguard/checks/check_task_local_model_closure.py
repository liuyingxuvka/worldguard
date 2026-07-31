"""Run WorldGuard's bundled strict task-local model-closure scenarios."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[4]
RUNTIME = ROOT / "skills" / "worldguard" / "runtime"
sys.path.insert(0, str(RUNTIME))

from worldguard.task_local_revision import (  # noqa: E402
    TASK_LOCAL_REVISION_SCHEMA_VERSION,
    CandidateWorldModelRevision,
    ObservedWorldRelationship,
    ObservedWorldSnapshot,
    PredictionSnapshot,
    RevalidationRole,
    WorldModelIdentity,
    bind_semantic_rollout_receipt,
    bind_task_local_native_depth_receipt,
    bind_world_revalidation_receipt,
    compare_observed_world,
    coverage_universe_fingerprint,
    evaluate_candidate_world_revision,
    freeze_prediction_snapshot,
    observation_evidence_fingerprint,
)


def _fp(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _model(root: Path, name: str, content: str) -> dict[str, str]:
    path = root / name
    path.write_text(content, encoding="utf-8")
    return {
        "model_id": f"model:{name}",
        "model_version": "1",
        "path": name,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _prediction(
    model: dict[str, str],
    prediction_id: str,
    *,
    iteration: int = 0,
    prior_gap_ids: list[str] | None = None,
) -> dict:
    coverage_ids = ["value-voltage", "relation-command-before-response"]
    prior = prior_gap_ids or []
    return {
        "schema_version": TASK_LOCAL_REVISION_SCHEMA_VERSION,
        "prediction_id": prediction_id,
        "task_id": "task:native-task-local",
        "purpose": "predict voltage and command-response ordering",
        "coverage_universe_id": "coverage:native-task-local",
        "coverage_universe_owner_id": "owner:independent-native-inventory",
        "coverage_universe_source_ref": "native://independent-coverage",
        "coverage_universe_fingerprint": coverage_universe_fingerprint(
            universe_id="coverage:native-task-local",
            owner_id="owner:independent-native-inventory",
            source_ref="native://independent-coverage",
            coverage_ids=coverage_ids,
        ),
        "coverage_ids": coverage_ids,
        "assumptions": ["the voltage sensor uses the declared unit"],
        "unknowns": ["unobserved environmental load may alter the response"],
        "iteration": iteration,
        "max_iterations": 4,
        "predecessor_iteration_fingerprint": "root" if iteration == 0 else "a" * 64,
        "prior_gap_ids": prior,
        "prior_gap_fingerprints": [] if iteration == 0 else [_fp(prior)],
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


def _comparison(
    root: Path,
    model: dict[str, str],
    prediction_id: str,
    observation_id: str,
    voltage: float,
    *,
    iteration: int = 0,
    prior_gap_ids: list[str] | None = None,
) -> tuple[PredictionSnapshot, dict]:
    prediction = PredictionSnapshot.from_dict(
        _prediction(model, prediction_id, iteration=iteration, prior_gap_ids=prior_gap_ids)
    )
    relationship = ObservedWorldRelationship(
        relationship_id="command-before-response",
        left="cooling_command",
        relation="before",
        right="temperature_response",
    )
    source_ref = f"native://{observation_id}"
    evidence_fingerprint = observation_evidence_fingerprint(
        observation_id=observation_id,
        prediction_id=prediction_id,
        observation_sequence=11,
        source_ref=source_ref,
        values={"voltage": voltage},
        relationships=(relationship,),
        external_inputs=(),
    )
    observation = ObservedWorldSnapshot.from_dict(
        {
            "schema_version": TASK_LOCAL_REVISION_SCHEMA_VERSION,
            "observation_id": observation_id,
            "prediction_id": prediction_id,
            "observation_sequence": 11,
            "source_ref": source_ref,
            "values": {"voltage": voltage},
            "relationships": [relationship.to_dict()],
            "evidence_id": f"evidence:{observation_id}",
            "evidence_fingerprint": evidence_fingerprint,
            "external_inputs": [],
        }
    )
    return prediction, compare_observed_world(prediction, observation, base_dir=root)


def _revalidation(candidate: dict[str, str], role: RevalidationRole, comparison: dict) -> dict:
    identity = WorldModelIdentity.from_dict(candidate)
    semantic = bind_semantic_rollout_receipt(
        receipt_id=f"semantic:{role.value}",
        task_id="task:native-task-local",
        role=role,
        candidate_model=identity,
        semantic_status="pass",
        source_result={
            "artifact_kind": "worldguard.semantic_execution",
            "status": "PASS",
            "scenario": role.value,
            "candidate_sha256": candidate["sha256"],
        },
        evidence_ref=f"native://semantic/{role.value}",
    )
    return bind_world_revalidation_receipt(
        check_id=role.value,
        role=role,
        candidate_model=identity,
        semantic_receipt=semantic,
        empirical_comparison=comparison,
    )


def _revision(
    root: Path,
    base: dict[str, str],
    candidate: dict[str, str],
    *,
    gaps: list[str] | None = None,
    licensed: bool = True,
    iteration: int = 0,
    prior_gap_ids: list[str] | None = None,
) -> dict:
    comparison_args = {"iteration": iteration, "prior_gap_ids": prior_gap_ids}
    prediction, base_comparison = _comparison(
        root, base, "prediction:base", "observation:construction", 0.60, **comparison_args
    )
    _, original = _comparison(
        root, candidate, "prediction:original", "observation:original", 0.73, **comparison_args
    )
    _, holdout = _comparison(
        root, candidate, "prediction:holdout", "observation:holdout", 0.72, **comparison_args
    )
    depth = bind_task_local_native_depth_receipt(
        prediction,
        WorldModelIdentity.from_dict(candidate),
        {
            "receipt_id": "depth:native-current",
            "receipt_version": "worldguard.native_depth.v2",
            "mesh_fingerprint": "mesh:native-current",
            "coverage_fingerprint": "coverage:native-current",
            "predictive_gaps": gaps or [],
            "quantitative_coverage": {"expected_state_count": 2, "executed_state_count": 2},
            "predictive_claim_licensed": licensed and not gaps,
        },
        base_dir=root,
        binding_id="depth-binding:native",
    )
    return {
        "schema_version": TASK_LOCAL_REVISION_SCHEMA_VERSION,
        "revision_id": "revision:native",
        "prediction_id": prediction.prediction_id,
        "base_model": base,
        "candidate_model": candidate,
        "revision_kind": "update_causal_relation",
        "prediction_receipt": freeze_prediction_snapshot(prediction, base_dir=root),
        "comparison_receipt": base_comparison,
        "native_depth_receipt": depth,
        "candidate_build_evidence_fingerprints": [base_comparison["observation_evidence_fingerprint"]],
        "required_revalidation_ids": [
            RevalidationRole.ORIGINAL_SCENARIO.value,
            RevalidationRole.REAL_HOLDOUT_OBSERVATION.value,
        ],
        "revalidations": [
            _revalidation(candidate, RevalidationRole.ORIGINAL_SCENARIO, original),
            _revalidation(candidate, RevalidationRole.REAL_HOLDOUT_OBSERVATION, holdout),
        ],
        "candidate_applied": False,
        "rollback_model": None,
        "external_inputs": [],
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="worldguard-task-local-") as temp:
        root = Path(temp)
        base = _model(root, "base.json", '{"version": 1}')
        candidate = _model(root, "candidate.json", '{"version": 2}')
        accepted = evaluate_candidate_world_revision(
            CandidateWorldModelRevision.from_dict(_revision(root, base, candidate)),
            base_dir=root,
        )
        gapped = evaluate_candidate_world_revision(
            CandidateWorldModelRevision.from_dict(
                _revision(root, base, candidate, gaps=["branch:new-regime"])
            ),
            base_dir=root,
        )
        unlicensed = evaluate_candidate_world_revision(
            CandidateWorldModelRevision.from_dict(
                _revision(root, base, candidate, licensed=False)
            ),
            base_dir=root,
        )
        prior_gap_ids = ["native:branch:old-regime"]
        later_closed = evaluate_candidate_world_revision(
            CandidateWorldModelRevision.from_dict(
                _revision(
                    root,
                    base,
                    candidate,
                    iteration=1,
                    prior_gap_ids=prior_gap_ids,
                )
            ),
            base_dir=root,
        )
        dependent_row = _revision(root, base, candidate)
        holdout_fp = dependent_row["revalidations"][1]["empirical_comparison"]["observation_evidence_fingerprint"]
        dependent_row["candidate_build_evidence_fingerprints"].append(holdout_fp)
        dependent = evaluate_candidate_world_revision(
            CandidateWorldModelRevision.from_dict(dependent_row),
            base_dir=root,
        )
        legacy_row = _prediction(base, "prediction:legacy")
        legacy_row.pop("unknowns")
        legacy_rejected = False
        try:
            PredictionSnapshot.from_dict(legacy_row)
        except ValueError:
            legacy_rejected = True

    checks = {
        "strict_current_closes": accepted["terminal_reason"] == "model_closed_for_task",
        "native_gap_continues": (
            gapped["terminal_reason"] == "continue_iteration"
            and gapped["predictive_gap_categories"]["branch"] == ["branch:new-regime"]
        ),
        "unlicensed_prediction_stays_open": "native:predictive_claim_not_licensed" in unlicensed["current_gap_ids"],
        "later_iteration_resolves_exact_prior_gaps": (
            later_closed["terminal_reason"] == "model_closed_for_task"
            and later_closed["resolved_gap_ids"] == prior_gap_ids
        ),
        "dependent_holdout_rejected": dependent["disposition"] == "rejected",
        "legacy_shape_rejected": legacy_rejected,
    }
    payload = {
        "artifact_kind": "worldguard_task_local_model_closure_native_check",
        "schema_version": "worldguard.task_local_model_closure_native_check.v1",
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "claim_boundary": (
            "This native check covers the bundled strict task-local prediction, native-depth binding, "
            "derived-gap, and independent-holdout closure path only; it does not establish factual truth, "
            "installation, publication, or release."
        ),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

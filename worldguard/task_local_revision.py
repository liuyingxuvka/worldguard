"""Task-local empirical prediction and reversible world-model revision.

This module deliberately sits beside, rather than inside, WorldGuard's
structural and semantic executors.  It freezes one exact task model before an
observation, compares only explicitly declared values and relationships, and
evaluates a separate candidate model without writing either artifact.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Mapping


SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


class WorldMismatchCategory(StrEnum):
    INITIAL_STATE = "initial_state"
    TRANSITION = "transition"
    CAUSAL_RELATION = "causal_relation"
    RESOURCE = "resource"
    AGENT = "agent"
    OBSERVATION_MAPPING = "observation_mapping"
    OTHER = "other"


class WorldRevisionKind(StrEnum):
    UPDATE_INITIAL_STATE = "update_initial_state"
    UPDATE_TRANSITION = "update_transition"
    UPDATE_CAUSAL_RELATION = "update_causal_relation"
    UPDATE_RESOURCE = "update_resource"
    UPDATE_AGENT = "update_agent"
    UPDATE_OBSERVATION_MAPPING = "update_observation_mapping"
    UPDATE_BOUNDARY = "update_boundary"


class RevalidationRole(StrEnum):
    ORIGINAL_SCENARIO = "original_scenario"
    REAL_HOLDOUT_OBSERVATION = "real_holdout_observation"


_REVALIDATION_STATUSES = {"pass", "fail", "gap", "blocked", "not_run"}


def _strict_fields(data: Mapping[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise ValueError(f"{label} has unknown fields: {', '.join(unknown)}")


def _text(value: Any, label: str) -> str:
    result = str(value or "").strip()
    if not result:
        raise ValueError(f"{label} must be non-empty")
    return result


def _finite(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be a finite number")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a finite number") from exc
    if not math.isfinite(result):
        raise ValueError(f"{label} must be a finite number")
    return result


def _fingerprint(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _resolve_path(base_dir: Path, path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else base_dir / path


@dataclass(frozen=True)
class WorldModelIdentity:
    model_id: str
    model_version: str
    path: str
    sha256: str

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "WorldModelIdentity":
        _strict_fields(
            data,
            {"model_id", "model_version", "path", "sha256"},
            "world model identity",
        )
        sha256 = _text(data.get("sha256"), "sha256").lower()
        if not SHA256_RE.fullmatch(sha256):
            raise ValueError("sha256 must contain exactly 64 hexadecimal characters")
        return cls(
            model_id=_text(data.get("model_id"), "model_id"),
            model_version=_text(data.get("model_version"), "model_version"),
            path=_text(data.get("path"), "path"),
            sha256=sha256,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "model_version": self.model_version,
            "path": self.path,
            "sha256": self.sha256,
        }


@dataclass(frozen=True)
class ExpectedWorldValue:
    expectation_id: str
    target_id: str
    expected_value: float
    tolerance: float
    mismatch_category: WorldMismatchCategory
    weakening_condition: str

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ExpectedWorldValue":
        _strict_fields(
            data,
            {
                "expectation_id",
                "target_id",
                "expected_value",
                "tolerance",
                "mismatch_category",
                "weakening_condition",
            },
            "expected world value",
        )
        tolerance = _finite(data.get("tolerance", 0.0), "tolerance")
        if tolerance < 0:
            raise ValueError("tolerance must be non-negative")
        try:
            category = WorldMismatchCategory(
                _text(data.get("mismatch_category"), "mismatch_category")
            )
        except ValueError as exc:
            raise ValueError("mismatch_category is not a WorldGuard-native category") from exc
        return cls(
            expectation_id=_text(data.get("expectation_id"), "expectation_id"),
            target_id=_text(data.get("target_id"), "target_id"),
            expected_value=_finite(data.get("expected_value"), "expected_value"),
            tolerance=tolerance,
            mismatch_category=category,
            weakening_condition=_text(
                data.get("weakening_condition"), "weakening_condition"
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "expectation_id": self.expectation_id,
            "target_id": self.target_id,
            "expected_value": self.expected_value,
            "tolerance": self.tolerance,
            "mismatch_category": self.mismatch_category.value,
            "weakening_condition": self.weakening_condition,
        }


@dataclass(frozen=True)
class ExpectedWorldRelationship:
    expectation_id: str
    relationship_id: str
    left: str
    relation: str
    right: str
    mismatch_category: WorldMismatchCategory
    weakening_condition: str

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ExpectedWorldRelationship":
        _strict_fields(
            data,
            {
                "expectation_id",
                "relationship_id",
                "left",
                "relation",
                "right",
                "mismatch_category",
                "weakening_condition",
            },
            "expected world relationship",
        )
        try:
            category = WorldMismatchCategory(
                _text(data.get("mismatch_category"), "mismatch_category")
            )
        except ValueError as exc:
            raise ValueError("mismatch_category is not a WorldGuard-native category") from exc
        return cls(
            expectation_id=_text(data.get("expectation_id"), "expectation_id"),
            relationship_id=_text(data.get("relationship_id"), "relationship_id"),
            left=_text(data.get("left"), "left"),
            relation=_text(data.get("relation"), "relation"),
            right=_text(data.get("right"), "right"),
            mismatch_category=category,
            weakening_condition=_text(
                data.get("weakening_condition"), "weakening_condition"
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "expectation_id": self.expectation_id,
            "relationship_id": self.relationship_id,
            "left": self.left,
            "relation": self.relation,
            "right": self.right,
            "mismatch_category": self.mismatch_category.value,
            "weakening_condition": self.weakening_condition,
        }


@dataclass(frozen=True)
class PredictionSnapshot:
    prediction_id: str
    model: WorldModelIdentity
    prediction_sequence: int
    initial_state: dict[str, Any]
    intervention: dict[str, Any]
    expected_values: tuple[ExpectedWorldValue, ...]
    expected_relationships: tuple[ExpectedWorldRelationship, ...]
    weakening_conditions: tuple[str, ...]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PredictionSnapshot":
        _strict_fields(
            data,
            {
                "prediction_id",
                "model",
                "prediction_sequence",
                "initial_state",
                "intervention",
                "expected_values",
                "expected_relationships",
                "weakening_conditions",
            },
            "prediction snapshot",
        )
        model = data.get("model")
        if not isinstance(model, Mapping):
            raise ValueError("prediction model must be a mapping")
        initial_state = data.get("initial_state", {})
        intervention = data.get("intervention", {})
        if not isinstance(initial_state, Mapping) or not isinstance(intervention, Mapping):
            raise ValueError("initial_state and intervention must be mappings")
        try:
            sequence = int(data.get("prediction_sequence"))
        except (TypeError, ValueError) as exc:
            raise ValueError("prediction_sequence must be a non-negative integer") from exc
        if sequence < 0 or isinstance(data.get("prediction_sequence"), bool):
            raise ValueError("prediction_sequence must be a non-negative integer")
        value_rows = data.get("expected_values", [])
        relationship_rows = data.get("expected_relationships", [])
        if not isinstance(value_rows, list) or not isinstance(relationship_rows, list):
            raise ValueError("expected_values and expected_relationships must be lists")
        expected_values = tuple(
            ExpectedWorldValue.from_dict(row)
            for row in value_rows
            if isinstance(row, Mapping)
        )
        expected_relationships = tuple(
            ExpectedWorldRelationship.from_dict(row)
            for row in relationship_rows
            if isinstance(row, Mapping)
        )
        if len(expected_values) != len(value_rows) or len(expected_relationships) != len(
            relationship_rows
        ):
            raise ValueError("prediction expectations must be mappings")
        if not expected_values and not expected_relationships:
            raise ValueError("prediction requires at least one expected value or relationship")
        expectation_ids = [
            *(row.expectation_id for row in expected_values),
            *(row.expectation_id for row in expected_relationships),
        ]
        if len(expectation_ids) != len(set(expectation_ids)):
            raise ValueError("expectation ids must be unique")
        weakening = data.get("weakening_conditions", [])
        if not isinstance(weakening, list):
            raise ValueError("weakening_conditions must be a list")
        weakening_conditions = tuple(
            _text(item, "weakening condition") for item in weakening
        )
        if not weakening_conditions or len(weakening_conditions) != len(
            set(weakening_conditions)
        ):
            raise ValueError("weakening_conditions must be non-empty and unique")
        return cls(
            prediction_id=_text(data.get("prediction_id"), "prediction_id"),
            model=WorldModelIdentity.from_dict(model),
            prediction_sequence=sequence,
            initial_state=dict(initial_state),
            intervention=dict(intervention),
            expected_values=expected_values,
            expected_relationships=expected_relationships,
            weakening_conditions=weakening_conditions,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "prediction_id": self.prediction_id,
            "model": self.model.to_dict(),
            "prediction_sequence": self.prediction_sequence,
            "initial_state": self.initial_state,
            "intervention": self.intervention,
            "expected_values": [item.to_dict() for item in self.expected_values],
            "expected_relationships": [
                item.to_dict() for item in self.expected_relationships
            ],
            "weakening_conditions": list(self.weakening_conditions),
        }


@dataclass(frozen=True)
class ObservedWorldRelationship:
    relationship_id: str
    left: str
    relation: str
    right: str

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ObservedWorldRelationship":
        _strict_fields(
            data,
            {"relationship_id", "left", "relation", "right"},
            "observed world relationship",
        )
        return cls(
            relationship_id=_text(data.get("relationship_id"), "relationship_id"),
            left=_text(data.get("left"), "left"),
            relation=_text(data.get("relation"), "relation"),
            right=_text(data.get("right"), "right"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "relationship_id": self.relationship_id,
            "left": self.left,
            "relation": self.relation,
            "right": self.right,
        }


@dataclass(frozen=True)
class ObservedWorldSnapshot:
    observation_id: str
    prediction_id: str
    observation_sequence: int
    source_ref: str
    values: dict[str, float]
    relationships: tuple[ObservedWorldRelationship, ...]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ObservedWorldSnapshot":
        _strict_fields(
            data,
            {
                "observation_id",
                "prediction_id",
                "observation_sequence",
                "source_ref",
                "values",
                "relationships",
            },
            "observed world snapshot",
        )
        try:
            sequence = int(data.get("observation_sequence"))
        except (TypeError, ValueError) as exc:
            raise ValueError("observation_sequence must be a non-negative integer") from exc
        if sequence < 0 or isinstance(data.get("observation_sequence"), bool):
            raise ValueError("observation_sequence must be a non-negative integer")
        values = data.get("values", {})
        relationships = data.get("relationships", [])
        if not isinstance(values, Mapping) or not isinstance(relationships, list):
            raise ValueError("observation values must be a mapping and relationships a list")
        normalized_values = {
            _text(key, "observed value target"): _finite(
                value, f"observed value for {key}"
            )
            for key, value in values.items()
        }
        normalized_relationships = tuple(
            ObservedWorldRelationship.from_dict(row)
            for row in relationships
            if isinstance(row, Mapping)
        )
        if len(normalized_relationships) != len(relationships):
            raise ValueError("observed relationships must be mappings")
        relationship_ids = [item.relationship_id for item in normalized_relationships]
        if len(relationship_ids) != len(set(relationship_ids)):
            raise ValueError("observed relationship ids must be unique")
        if not normalized_values and not normalized_relationships:
            raise ValueError("observation requires at least one actual value or relationship")
        return cls(
            observation_id=_text(data.get("observation_id"), "observation_id"),
            prediction_id=_text(data.get("prediction_id"), "prediction_id"),
            observation_sequence=sequence,
            source_ref=_text(data.get("source_ref"), "source_ref"),
            values=normalized_values,
            relationships=normalized_relationships,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "prediction_id": self.prediction_id,
            "observation_sequence": self.observation_sequence,
            "source_ref": self.source_ref,
            "values": self.values,
            "relationships": [item.to_dict() for item in self.relationships],
        }


@dataclass(frozen=True)
class WorldRevalidationReceipt:
    check_id: str
    role: RevalidationRole
    candidate_model: WorldModelIdentity
    semantic_rollout_status: str
    empirical_comparison: dict[str, Any]
    evidence_ref: str

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "WorldRevalidationReceipt":
        _strict_fields(
            data,
            {
                "check_id",
                "role",
                "candidate_model",
                "semantic_rollout_status",
                "empirical_comparison",
                "evidence_ref",
            },
            "world revalidation receipt",
        )
        candidate = data.get("candidate_model")
        comparison = data.get("empirical_comparison")
        if not isinstance(candidate, Mapping) or not isinstance(comparison, Mapping):
            raise ValueError("candidate_model and empirical_comparison must be mappings")
        try:
            role = RevalidationRole(_text(data.get("role"), "role"))
        except ValueError as exc:
            raise ValueError("revalidation role is not supported") from exc
        status = _text(
            data.get("semantic_rollout_status"), "semantic_rollout_status"
        ).lower()
        if status not in _REVALIDATION_STATUSES:
            raise ValueError("semantic_rollout_status is not supported")
        return cls(
            check_id=_text(data.get("check_id"), "check_id"),
            role=role,
            candidate_model=WorldModelIdentity.from_dict(candidate),
            semantic_rollout_status=status,
            empirical_comparison=dict(comparison),
            evidence_ref=_text(data.get("evidence_ref"), "evidence_ref"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "role": self.role.value,
            "candidate_model": self.candidate_model.to_dict(),
            "semantic_rollout_status": self.semantic_rollout_status,
            "empirical_comparison": self.empirical_comparison,
            "evidence_ref": self.evidence_ref,
        }


@dataclass(frozen=True)
class CandidateWorldModelRevision:
    revision_id: str
    prediction_id: str
    base_model: WorldModelIdentity
    candidate_model: WorldModelIdentity
    revision_kind: WorldRevisionKind
    triggering_mismatch_ids: tuple[str, ...]
    required_revalidation_ids: tuple[str, ...]
    revalidations: tuple[WorldRevalidationReceipt, ...]
    candidate_applied: bool
    rollback_model: WorldModelIdentity | None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "CandidateWorldModelRevision":
        _strict_fields(
            data,
            {
                "revision_id",
                "prediction_id",
                "base_model",
                "candidate_model",
                "revision_kind",
                "triggering_mismatch_ids",
                "required_revalidation_ids",
                "revalidations",
                "candidate_applied",
                "rollback_model",
            },
            "candidate world-model revision",
        )
        base = data.get("base_model")
        candidate = data.get("candidate_model")
        if not isinstance(base, Mapping) or not isinstance(candidate, Mapping):
            raise ValueError("base_model and candidate_model must be mappings")
        try:
            revision_kind = WorldRevisionKind(
                _text(data.get("revision_kind"), "revision_kind")
            )
        except ValueError as exc:
            raise ValueError("revision_kind is not a task-local WorldGuard operation") from exc
        mismatch_rows = data.get("triggering_mismatch_ids", [])
        required_rows = data.get("required_revalidation_ids", [])
        revalidation_rows = data.get("revalidations", [])
        if not all(
            isinstance(rows, list)
            for rows in (mismatch_rows, required_rows, revalidation_rows)
        ):
            raise ValueError(
                "triggering_mismatch_ids, required_revalidation_ids, and revalidations must be lists"
            )
        mismatch_ids = tuple(_text(item, "mismatch id") for item in mismatch_rows)
        required_ids = tuple(
            _text(item, "required revalidation id") for item in required_rows
        )
        if not mismatch_ids or len(mismatch_ids) != len(set(mismatch_ids)):
            raise ValueError("triggering_mismatch_ids must be non-empty and unique")
        if not required_ids or len(required_ids) != len(set(required_ids)):
            raise ValueError("required_revalidation_ids must be non-empty and unique")
        revalidations = tuple(
            WorldRevalidationReceipt.from_dict(row)
            for row in revalidation_rows
            if isinstance(row, Mapping)
        )
        if len(revalidations) != len(revalidation_rows):
            raise ValueError("revalidations must be mappings")
        check_ids = [item.check_id for item in revalidations]
        if len(check_ids) != len(set(check_ids)) or set(check_ids) != set(required_ids):
            raise ValueError(
                "revalidations must be unique and exactly equal required_revalidation_ids"
            )
        roles = {item.role for item in revalidations}
        if not {
            RevalidationRole.ORIGINAL_SCENARIO,
            RevalidationRole.REAL_HOLDOUT_OBSERVATION,
        }.issubset(roles):
            raise ValueError(
                "candidate revision requires original_scenario and real_holdout_observation"
            )
        candidate_applied = data.get("candidate_applied", False)
        if not isinstance(candidate_applied, bool):
            raise ValueError("candidate_applied must be boolean")
        rollback = data.get("rollback_model")
        if candidate_applied and not isinstance(rollback, Mapping):
            raise ValueError("an applied candidate requires rollback_model")
        if not candidate_applied and rollback is not None:
            raise ValueError("rollback_model is only valid after candidate application")
        return cls(
            revision_id=_text(data.get("revision_id"), "revision_id"),
            prediction_id=_text(data.get("prediction_id"), "prediction_id"),
            base_model=WorldModelIdentity.from_dict(base),
            candidate_model=WorldModelIdentity.from_dict(candidate),
            revision_kind=revision_kind,
            triggering_mismatch_ids=mismatch_ids,
            required_revalidation_ids=required_ids,
            revalidations=revalidations,
            candidate_applied=candidate_applied,
            rollback_model=(
                WorldModelIdentity.from_dict(rollback)
                if isinstance(rollback, Mapping)
                else None
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "revision_id": self.revision_id,
            "prediction_id": self.prediction_id,
            "base_model": self.base_model.to_dict(),
            "candidate_model": self.candidate_model.to_dict(),
            "revision_kind": self.revision_kind.value,
            "triggering_mismatch_ids": list(self.triggering_mismatch_ids),
            "required_revalidation_ids": list(self.required_revalidation_ids),
            "revalidations": [item.to_dict() for item in self.revalidations],
            "candidate_applied": self.candidate_applied,
            "rollback_model": (
                self.rollback_model.to_dict() if self.rollback_model else None
            ),
        }


def _identity_receipt(identity: WorldModelIdentity, base_dir: Path) -> dict[str, Any]:
    path = _resolve_path(base_dir, identity.path)
    actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ""
    return {
        **identity.to_dict(),
        "resolved_path": str(path.resolve()) if path.exists() else str(path),
        "actual_sha256": actual,
        "status": "current" if actual == identity.sha256 else "stale",
    }


def freeze_prediction_snapshot(
    prediction: PredictionSnapshot,
    *,
    base_dir: Path,
) -> dict[str, Any]:
    model = _identity_receipt(prediction.model, base_dir)
    return {
        "artifact_kind": "worldguard_prediction_snapshot_receipt",
        "receipt_version": "1.0",
        "status": "pass" if model["status"] == "current" else "blocked",
        "prediction_id": prediction.prediction_id,
        "prediction_sequence": prediction.prediction_sequence,
        "model_identity": model,
        "prediction_fingerprint": _fingerprint(prediction.to_dict()),
        "expected_value_count": len(prediction.expected_values),
        "expected_relationship_count": len(prediction.expected_relationships),
        "weakening_conditions": list(prediction.weakening_conditions),
        "claim_boundary": (
            "This receipt freezes only the declared task model, initial state, "
            "intervention, expectations, weakening conditions, and sequence. It does "
            "not prove that the expectations exhaust the real world."
        ),
    }


def compare_observed_world(
    prediction: PredictionSnapshot,
    observation: ObservedWorldSnapshot,
    *,
    base_dir: Path,
) -> dict[str, Any]:
    if observation.prediction_id != prediction.prediction_id:
        raise ValueError("observation prediction_id does not match the prediction snapshot")
    if observation.observation_sequence <= prediction.prediction_sequence:
        raise ValueError(
            "observation_sequence must be strictly later than prediction_sequence"
        )
    frozen = freeze_prediction_snapshot(prediction, base_dir=base_dir)
    if frozen["status"] != "pass":
        raise ValueError("prediction snapshot model identity is not current")

    matches: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    for expected in prediction.expected_values:
        actual = observation.values.get(expected.target_id)
        common = {
            "expectation_id": expected.expectation_id,
            "expectation_kind": "value",
            "target_id": expected.target_id,
            "mismatch_category": expected.mismatch_category.value,
            "expected_value": expected.expected_value,
            "tolerance": expected.tolerance,
            "weakening_condition": expected.weakening_condition,
        }
        if actual is None:
            mismatches.append(
                {
                    **common,
                    "mismatch_id": (
                        f"{prediction.prediction_id}:{expected.expectation_id}:missing"
                    ),
                    "mismatch_code": "expected_value_missing",
                    "actual_value": None,
                }
            )
        elif abs(actual - expected.expected_value) > expected.tolerance:
            mismatches.append(
                {
                    **common,
                    "mismatch_id": (
                        f"{prediction.prediction_id}:{expected.expectation_id}:contradicted"
                    ),
                    "mismatch_code": "value_outside_tolerance",
                    "actual_value": actual,
                }
            )
        else:
            matches.append({**common, "actual_value": actual})

    observed_relationships = {
        item.relationship_id: item for item in observation.relationships
    }
    for expected in prediction.expected_relationships:
        actual = observed_relationships.get(expected.relationship_id)
        common = {
            "expectation_id": expected.expectation_id,
            "expectation_kind": "relationship",
            "relationship_id": expected.relationship_id,
            "mismatch_category": expected.mismatch_category.value,
            "expected_relationship": {
                "left": expected.left,
                "relation": expected.relation,
                "right": expected.right,
            },
            "weakening_condition": expected.weakening_condition,
        }
        if actual is None:
            mismatches.append(
                {
                    **common,
                    "mismatch_id": (
                        f"{prediction.prediction_id}:{expected.expectation_id}:missing"
                    ),
                    "mismatch_code": "expected_relationship_missing",
                    "actual_relationship": None,
                }
            )
        elif (
            actual.left,
            actual.relation,
            actual.right,
        ) != (expected.left, expected.relation, expected.right):
            mismatches.append(
                {
                    **common,
                    "mismatch_id": (
                        f"{prediction.prediction_id}:{expected.expectation_id}:contradicted"
                    ),
                    "mismatch_code": "relationship_contradicted",
                    "actual_relationship": {
                        "left": actual.left,
                        "relation": actual.relation,
                        "right": actual.right,
                    },
                }
            )
        else:
            matches.append(
                {
                    **common,
                    "actual_relationship": {
                        "left": actual.left,
                        "relation": actual.relation,
                        "right": actual.right,
                    },
                }
            )

    return {
        "artifact_kind": "worldguard_observed_world_comparison_receipt",
        "receipt_version": "1.0",
        "status": "pass" if not mismatches else "fail",
        "prediction_id": prediction.prediction_id,
        "observation_id": observation.observation_id,
        "prediction_sequence": prediction.prediction_sequence,
        "observation_sequence": observation.observation_sequence,
        "source_ref": observation.source_ref,
        "model_identity": frozen["model_identity"],
        "prediction_fingerprint": frozen["prediction_fingerprint"],
        "observation_fingerprint": _fingerprint(observation.to_dict()),
        "matches": matches,
        "mismatches": mismatches,
        "mismatch_ids": [item["mismatch_id"] for item in mismatches],
        "claim_boundary": (
            "This empirical comparison covers only declared values and relationships "
            "against the supplied observation. Missing expectations fail visibly; "
            "extra observations are not treated as complete world coverage."
        ),
    }


def _same_identity(left: WorldModelIdentity, right: WorldModelIdentity) -> bool:
    return left.to_dict() == right.to_dict()


def _comparison_binds_candidate(
    comparison: Mapping[str, Any],
    candidate: WorldModelIdentity,
) -> bool:
    identity = comparison.get("model_identity")
    if not isinstance(identity, Mapping):
        return False
    return (
        str(identity.get("model_id", "")) == candidate.model_id
        and str(identity.get("model_version", "")) == candidate.model_version
        and str(identity.get("path", "")) == candidate.path
        and str(identity.get("sha256", "")).lower() == candidate.sha256
        and str(identity.get("actual_sha256", "")).lower() == candidate.sha256
        and str(identity.get("status", "")).lower() == "current"
    )


def evaluate_candidate_world_revision(
    revision: CandidateWorldModelRevision,
    *,
    base_dir: Path,
) -> dict[str, Any]:
    base = _identity_receipt(revision.base_model, base_dir)
    candidate = _identity_receipt(revision.candidate_model, base_dir)
    identity_findings: list[str] = []
    if base["status"] != "current":
        identity_findings.append("base_model_identity_stale")
    if candidate["status"] != "current":
        identity_findings.append("candidate_model_identity_stale")
    if (
        Path(base["resolved_path"]) == Path(candidate["resolved_path"])
        or base["actual_sha256"] == candidate["actual_sha256"]
    ):
        identity_findings.append("candidate_not_distinct_from_base")

    check_results: list[dict[str, Any]] = []
    for check in revision.revalidations:
        issues: list[str] = []
        declared_candidate = _identity_receipt(check.candidate_model, base_dir)
        if not _same_identity(check.candidate_model, revision.candidate_model):
            issues.append("revalidation_candidate_identity_mismatch")
        if declared_candidate["status"] != "current":
            issues.append("revalidation_candidate_identity_stale")
        if check.semantic_rollout_status != "pass":
            issues.append("semantic_rollout_non_pass")
        comparison = check.empirical_comparison
        if (
            comparison.get("artifact_kind")
            != "worldguard_observed_world_comparison_receipt"
        ):
            issues.append("empirical_comparison_receipt_invalid")
        elif str(comparison.get("status", "")).lower() != "pass":
            issues.append("empirical_comparison_non_pass")
        if not _comparison_binds_candidate(comparison, revision.candidate_model):
            issues.append("empirical_comparison_candidate_identity_mismatch")
        check_results.append(
            {
                "check_id": check.check_id,
                "role": check.role.value,
                "semantic_rollout_status": check.semantic_rollout_status,
                "empirical_comparison_status": str(
                    comparison.get("status", "")
                ).lower(),
                "evidence_ref": check.evidence_ref,
                "effective_status": "pass" if not issues else "fail",
                "issues": issues,
                "empirical_comparison_fingerprint": _fingerprint(comparison),
            }
        )

    failed = [
        item["check_id"]
        for item in check_results
        if item["effective_status"] != "pass"
    ]
    rollback = None
    if identity_findings:
        disposition = "blocked"
    elif not failed:
        disposition = "accepted"
    elif not revision.candidate_applied:
        disposition = "rejected"
    else:
        assert revision.rollback_model is not None
        rollback = _identity_receipt(revision.rollback_model, base_dir)
        if (
            rollback["status"] == "current"
            and _same_identity(revision.rollback_model, revision.base_model)
        ):
            disposition = "rolled_back"
        else:
            disposition = "blocked"
            identity_findings.append("rollback_identity_does_not_match_current_base")

    return {
        "artifact_kind": "worldguard_task_model_revision_receipt",
        "receipt_version": "1.0",
        "status": (
            "pass"
            if disposition in {"accepted", "rejected", "rolled_back"}
            else "blocked"
        ),
        "revision_id": revision.revision_id,
        "prediction_id": revision.prediction_id,
        "revision_kind": revision.revision_kind.value,
        "disposition": disposition,
        "base_model": base,
        "candidate_model": candidate,
        "rollback_model": rollback,
        "triggering_mismatch_ids": list(revision.triggering_mismatch_ids),
        "required_revalidation_ids": list(revision.required_revalidation_ids),
        "revalidation_results": check_results,
        "failed_revalidation_ids": failed,
        "identity_findings": identity_findings,
        "base_model_preserved": base["status"] == "current",
        "revision_fingerprint": _fingerprint(revision.to_dict()),
        "claim_boundary": (
            "This read-only decision applies only to the exact task-local base, "
            "candidate, mismatches, semantic receipts, and real observations. It "
            "never edits WorldGuard, core thresholds, installed skills, or reusable defaults."
        ),
    }


__all__ = [
    "CandidateWorldModelRevision",
    "ExpectedWorldRelationship",
    "ExpectedWorldValue",
    "ObservedWorldRelationship",
    "ObservedWorldSnapshot",
    "PredictionSnapshot",
    "RevalidationRole",
    "WorldMismatchCategory",
    "WorldModelIdentity",
    "WorldRevisionKind",
    "WorldRevalidationReceipt",
    "compare_observed_world",
    "evaluate_candidate_world_revision",
    "freeze_prediction_snapshot",
]

"""Target-side helpers for the current SkillGuard native-depth wire.

This module owns no target-domain policy.  It only binds a target-owned native
receipt to the exact current SkillGuard run and writes immutable artifacts.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


class CurrentProtocolError(ValueError):
    """Fail-closed target adapter error."""


def _skillguard_runtime() -> Mapping[str, Any]:
    candidates = []
    explicit = os.environ.get("SKILLGUARD_SCRIPTS_ROOT", "").strip()
    if explicit:
        candidates.append(Path(explicit))
    candidates.append(Path.home() / ".codex" / "skills" / "skillguard" / "scripts")
    for candidate in candidates:
        if (candidate / "skillguard_v2" / "depth_evidence_protocol.py").is_file():
            if str(candidate) not in sys.path:
                sys.path.insert(0, str(candidate))
            break
    try:
        from skillguard_v2.calibration_evidence_protocol import (
            IMPORTANT_OBLIGATION_BLOCKER,
            TARGET_NATIVE_CALIBRATION_OBSERVATION_SCHEMA,
            TARGET_NATIVE_OUTCOME_AUTHORITY,
            build_target_native_calibration_evidence,
            calibration_contract_surface,
            calibration_input_manifest,
        )
        from skillguard_v2.contract_compiler import canonical_hash, canonical_json_bytes
        from skillguard_v2.depth_evidence_protocol import build_target_native_depth_evidence
        from skillguard_v2.dynamic_depth import (
            build_child_universe,
            build_native_floor_receipt,
            build_object_scope_attestation,
        )
        from skillguard_v2.native_evidence_identity import (
            TARGET_NATIVE_DEPTH_RECEIPT_SCHEMA,
            build_target_native_receipt,
            depth_profile_hash,
            native_receipt_bytes,
        )
    except ImportError as exc:
        raise CurrentProtocolError("current SkillGuard runtime is unavailable") from exc
    return locals()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CurrentProtocolError(f"JSON object required: {path}")
    return value


def _write_atomic(path: Path, body: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_bytes(body)
    os.replace(temporary, path)


def _run_context(run_root: Path, check_id: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    run = _load(run_root / "run.json")
    contract = _load(run_root / "contract.json")
    matches = [row for row in contract.get("checks", []) if isinstance(row, dict) and row.get("check_id") == check_id]
    if len(matches) != 1:
        raise CurrentProtocolError(f"current check missing or ambiguous: {check_id}")
    return run, contract, matches[0]


def emit_native_depth(
    *,
    run_root: Path,
    check_id: str,
    output_relative: str,
    universe_id: str,
    observation_origin: str,
    domain_receipt: Mapping[str, Any],
    native_objects: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Write one current target-native depth envelope.

    Capability fixtures and scheduled production share the target evaluator,
    but retain disjoint typed identities.  A production check therefore cannot
    reuse an empty fixture identity.
    """

    runtime = _skillguard_runtime()
    canonical_hash = runtime["canonical_hash"]
    canonical_json_bytes = runtime["canonical_json_bytes"]
    run_root = run_root.resolve()
    run, contract, check = _run_context(run_root, check_id)
    profile = contract.get("depth_profile", {})
    if not isinstance(profile, Mapping):
        raise CurrentProtocolError("current depth profile missing")
    evidence_domain = str(check.get("depth_evidence_domain", ""))
    if evidence_domain not in {"capability_validation", "scheduled_production"}:
        raise CurrentProtocolError("satellite depth check has unsupported evidence domain")
    target_skill_id = str(contract.get("skill_id", ""))
    owner_id = str(profile.get("native_owner_id", ""))
    route_id = str(check.get("native_route_id", ""))
    obligations = sorted(str(item) for item in check.get("covers_obligation_ids", []))
    if not target_skill_id or not owner_id or not route_id or not obligations:
        raise CurrentProtocolError("current native identity is incomplete")
    if str(domain_receipt.get("status", "")) != "pass":
        raise CurrentProtocolError("target-native depth did not pass")
    object_rows = sorted(
        (dict(row) for row in native_objects),
        key=lambda row: str(row.get("object_id", "")),
    )
    object_ids = [str(row.get("object_id", "")) for row in object_rows]
    if not object_ids or any(not item for item in object_ids) or len(object_ids) != len(set(object_ids)):
        raise CurrentProtocolError("complete unique native object universe required")
    request = run.get("request", {})
    if not isinstance(request, Mapping):
        raise CurrentProtocolError("run request missing")
    target_input_fingerprint = str(request.get("target_input_fingerprint", "")).upper()
    if len(target_input_fingerprint) != 64:
        raise CurrentProtocolError("target input fingerprint missing")
    expected_domain_identity = {
        "target_skill_id": target_skill_id,
        "native_owner_id": owner_id,
        "native_route_id": route_id,
        "check_id": check_id,
        "run_id": str(run.get("run_id", "")),
        "contract_hash": str(run.get("contract_hash", "")),
        "request_fingerprint": str(run.get("request_fingerprint", "")),
        "target_input_fingerprint": target_input_fingerprint,
        "evidence_domain": evidence_domain,
    }
    for field, expected in expected_domain_identity.items():
        if str(domain_receipt.get(field, "")) != expected:
            raise CurrentProtocolError(f"target-native receipt identity mismatch: {field}")
    if not str(domain_receipt.get("native_receipt_id", "")):
        raise CurrentProtocolError("target-native receipt id missing")
    if len(str(domain_receipt.get("native_receipt_hash", ""))) != 64:
        raise CurrentProtocolError("target-native receipt hash missing")
    if sorted(str(item) for item in domain_receipt.get("target_obligation_ids", [])) != obligations:
        raise CurrentProtocolError("target-native receipt obligation identity mismatch")
    raw_schedule = domain_receipt.get("scheduled_production_identity", {})
    if evidence_domain == "scheduled_production":
        if not isinstance(raw_schedule, Mapping) or not raw_schedule:
            raise CurrentProtocolError("scheduled production identity missing from target-native receipt")
        schedule = dict(raw_schedule)
    else:
        if raw_schedule not in (None, {}):
            raise CurrentProtocolError("non-production evidence cannot carry a scheduled production identity")
        schedule = {}
    profile_universes = [row for row in profile.get("coverage_universes", []) if isinstance(row, Mapping) and row.get("universe_id") == universe_id]
    if len(profile_universes) != 1:
        raise CurrentProtocolError(f"declared universe missing: {universe_id}")
    profile_universe = profile_universes[0]
    policy_map = check.get("depth_universe_policy_fingerprints", {})
    if not isinstance(policy_map, Mapping) or universe_id not in policy_map:
        raise CurrentProtocolError("compiled universe policy fingerprint missing")
    items = [
        {
            "item_id": f"{object_id}:native-depth",
            "object_id": object_id,
            "object_class_id": str(row.get("object_class_id", "native_object")),
            "stratum_ids": ["native-depth"],
            "critical": bool(row.get("critical", True)),
        }
        for object_id, row in zip(object_ids, object_rows)
    ]
    selected_ids = [row["item_id"] for row in items]
    scope_attestation = runtime["build_object_scope_attestation"](
        discovery_algorithm_id=f"{target_skill_id}.native-object-inventory.v1",
        discovery_input_fingerprint=target_input_fingerprint,
        discovered_object_ids=object_ids,
        declared_object_ids=object_ids,
        excluded_objects=(),
    )
    precommitted_at = datetime.now(timezone.utc).isoformat()
    floors = []
    for item in items:
        child = runtime["build_child_universe"](
            parent_universe_id=universe_id,
            owner_id=owner_id,
            object_id=item["object_id"],
            eligible_item_ids=[item["item_id"]],
            discovery_input_fingerprint=target_input_fingerprint,
        )
        floor = runtime["build_native_floor_receipt"](
            algorithm_id=f"{target_skill_id}.native-object-floor.v1",
            algorithm_version="1",
            algorithm_input_eligible_count=1,
            algorithm_input_fingerprint=child["universe_fingerprint"],
            minimum_selected_count=1,
            minimum_evaluated_count=1,
            minimum_validated_count=1,
            minimum_coverage=1.0,
            required_strata_ids=["native-depth"],
            precommitted_at=precommitted_at,
            receipt_ref=f"{target_skill_id}:{item['object_id']}:native-floor",
        )
        floors.append({"object_id": item["object_id"], **floor})
    domain_hash = canonical_hash(domain_receipt)
    domain_obligations = {
        str(row.get("obligation_id", "")): dict(row)
        for row in domain_receipt.get("native_obligation_evidence", [])
        if isinstance(row, Mapping)
    }
    if set(domain_obligations) != set(obligations):
        raise CurrentProtocolError("target-native receipt must contain the exact obligation set")
    for obligation_id in obligations:
        row = domain_obligations.get(obligation_id)
        if (
            row is None
            or str(row.get("status", "")) != "pass"
            or not str(row.get("native_object_id", ""))
            or not str(row.get("evidence_ref", ""))
            or len(str(row.get("evidence_sha256", ""))) != 64
            or not isinstance(row.get("content"), Mapping)
        ):
            raise CurrentProtocolError(
                f"target-native per-obligation evidence missing or blocked: {obligation_id}"
            )
    created_at = datetime.now(timezone.utc).isoformat()
    receipt_id = f"native-receipt:{target_skill_id}:{domain_hash[:24].lower()}"
    observations = []
    for index, obligation_id in enumerate(obligations):
        content = {
            "domain_receipt_sha256": domain_hash,
            "obligation_id": obligation_id,
            "native_obligation_evidence": domain_obligations.get(obligation_id, {}),
            "native_object_results": object_rows if index == 0 else [],
            "native_object_results_sha256": canonical_hash(object_rows),
        }
        observations.append(
            {
                "observation_id": f"observation:{target_skill_id}:{obligation_id}",
                "observation_origin": observation_origin,
                "native_object_id": f"native-object:{target_skill_id}:{obligation_id}",
                "target_obligation_ids": [obligation_id],
                "content": content,
            }
        )
    common = {
        "target_skill_id": target_skill_id,
        "target_contract_hash": str(run.get("contract_hash", "")),
        "depth_profile_hash": runtime["depth_profile_hash"](contract),
        "native_owner_id": owner_id,
        "native_route_id": route_id,
        "native_check_id": check_id,
        "run_id": str(run.get("run_id", "")),
        "target_obligation_ids": obligations,
        "evidence_domain": evidence_domain,
        "scheduled_production_identity": schedule,
    }
    receipt = runtime["build_target_native_receipt"](
        {
            "schema_version": runtime["TARGET_NATIVE_DEPTH_RECEIPT_SCHEMA"],
            **common,
            "native_receipt_id": receipt_id,
            "created_at": created_at,
            "observations": observations,
        }
    )
    receipt_bytes = runtime["native_receipt_bytes"](receipt)
    receipt_hash = hashlib.sha256(receipt_bytes).hexdigest().upper()
    receipt_relative = Path("native-receipts") / f"{receipt_hash[:24].lower()}.json"
    _write_atomic(run_root / receipt_relative, receipt_bytes)
    ranges = []
    for index, obligation_id in enumerate(obligations):
        content = observations[index]["content"]
        locator_base = {
            "schema_version": "skillguard.native_semantic_locator.v1",
            "locator_type": "json_pointer.v1",
            "resolver_owner_id": owner_id,
            "native_object_id": observations[index]["native_object_id"],
            "native_coordinate": f"/observations/{index}/content",
            "content_sha256": canonical_hash(content),
        }
        ranges.append(
            {
                "range_id": f"range:{target_skill_id}:{obligation_id}",
                "kind": "semantic",
                "obligation_ids": [obligation_id],
                "universe_id": universe_id,
                "semantic_locator": {**locator_base, "locator_fingerprint": canonical_hash(locator_base)},
            }
        )
    allowed_scope = list(profile_universe.get("allowed_claim_scope", []))
    if not allowed_scope:
        raise CurrentProtocolError("dynamic universe allowed claim scope missing")
    universe = {
        "universe_id": universe_id,
        "inventory_items": items,
        "selected_item_ids": selected_ids,
        "evaluated_item_ids": selected_ids,
        "validated_item_ids": selected_ids,
        "requested_claim_scope": allowed_scope,
        "covered_claim_scope": allowed_scope,
        "policy_fingerprint": str(policy_map[universe_id]),
        "object_scope_attestation": scope_attestation,
        "object_native_floor_receipts": floors,
    }
    evidence = runtime["build_target_native_depth_evidence"](
        {
            "schema_version": "skillguard.native_depth_evidence.v2",
            "run_id": common["run_id"],
            **common,
            "request_fingerprint": str(run.get("request_fingerprint", "")),
            "target_input_fingerprint": target_input_fingerprint,
            "native_receipt_id": receipt_id,
            "native_receipt_hash": receipt_hash,
            "native_receipt_artifact_ref": {"path_token": "run_root", "relative_path": receipt_relative.as_posix()},
            "native_receipt_created_at": created_at,
            "universes": [universe],
            "depth_contribution_ranges": ranges,
        }
    )
    output = (run_root / output_relative).resolve()
    output.relative_to(run_root)
    _write_atomic(output, canonical_json_bytes(evidence))
    return evidence


def emit_dynamic_native_depth(
    *,
    run_root: Path,
    check_id: str,
    output_relative: str,
    observation_origin: str,
    domain_receipt: Mapping[str, Any],
    universes: Sequence[Mapping[str, Any]],
    universe_obligations: Mapping[str, Sequence[str]],
) -> dict[str, Any]:
    """Bind rich target-native universes to the current V2 evidence wire.

    The target remains the sole owner of each universe and adequacy decision.
    This function only writes an immutable receipt and exact JSON-pointer
    locators; it never expands a catalog or manufactures ordinal ranges.
    """

    runtime = _skillguard_runtime()
    canonical_hash = runtime["canonical_hash"]
    canonical_json_bytes = runtime["canonical_json_bytes"]
    run_root = run_root.resolve()
    run, contract, check = _run_context(run_root, check_id)
    profile = contract.get("depth_profile", {})
    if not isinstance(profile, Mapping):
        raise CurrentProtocolError("current depth profile missing")
    target_skill_id = str(contract.get("skill_id", ""))
    owner_id = str(profile.get("native_owner_id", ""))
    route_id = str(check.get("native_route_id", ""))
    obligations = sorted(str(item) for item in check.get("covers_obligation_ids", []))
    evidence_domain = str(check.get("depth_evidence_domain", ""))
    if not target_skill_id or not owner_id or not route_id or not obligations:
        raise CurrentProtocolError("current native identity is incomplete")
    if evidence_domain not in {"capability_validation", "scheduled_production"}:
        raise CurrentProtocolError("unsupported current depth evidence domain")
    request = run.get("request", {})
    if not isinstance(request, Mapping):
        raise CurrentProtocolError("run request missing")
    target_input_fingerprint = str(request.get("target_input_fingerprint", "")).upper()
    if len(target_input_fingerprint) != 64:
        raise CurrentProtocolError("target input fingerprint missing")
    expected_domain_identity = {
        "target_skill_id": target_skill_id,
        "native_owner_id": owner_id,
        "native_route_id": route_id,
        "check_id": check_id,
        "run_id": str(run.get("run_id", "")),
        "contract_hash": str(run.get("contract_hash", "")),
        "request_fingerprint": str(run.get("request_fingerprint", "")),
        "target_input_fingerprint": target_input_fingerprint,
        "evidence_domain": evidence_domain,
    }
    for field, expected in expected_domain_identity.items():
        if str(domain_receipt.get(field, "")) != expected:
            raise CurrentProtocolError(f"target-native receipt identity mismatch: {field}")
    if not str(domain_receipt.get("native_receipt_id", "")):
        raise CurrentProtocolError("target-native receipt id missing")
    if len(str(domain_receipt.get("native_receipt_hash", ""))) != 64:
        raise CurrentProtocolError("target-native receipt hash missing")
    raw_schedule = domain_receipt.get("scheduled_production_identity", {})
    if evidence_domain == "scheduled_production":
        if not isinstance(raw_schedule, Mapping) or not raw_schedule:
            raise CurrentProtocolError("scheduled production identity missing from target-native receipt")
        schedule = dict(raw_schedule)
    else:
        if raw_schedule not in (None, {}):
            raise CurrentProtocolError("non-production evidence cannot carry a scheduled production identity")
        schedule = {}
    if sorted(str(item) for item in domain_receipt.get("target_obligation_ids", [])) != obligations:
        raise CurrentProtocolError("target-native receipt obligation identity mismatch")
    universe_rows = [dict(row) for row in universes]
    universe_ids = [str(row.get("universe_id", "")) for row in universe_rows]
    if (
        not universe_ids
        or any(not item for item in universe_ids)
        or len(universe_ids) != len(set(universe_ids))
    ):
        raise CurrentProtocolError("complete unique native universes required")
    policy_map = check.get("depth_universe_policy_fingerprints", {})
    if not isinstance(policy_map, Mapping):
        raise CurrentProtocolError("compiled universe policy fingerprints missing")
    for row in universe_rows:
        universe_id = str(row["universe_id"])
        expected_policy = str(policy_map.get(universe_id, ""))
        if not expected_policy or str(row.get("policy_fingerprint", "")) != expected_policy:
            raise CurrentProtocolError(f"native universe policy mismatch: {universe_id}")

    obligation_rows: dict[str, list[dict[str, Any]]] = {}
    for raw_row in domain_receipt.get("native_obligation_evidence", []):
        if not isinstance(raw_row, Mapping):
            continue
        row = dict(raw_row)
        row_obligations = [
            str(item) for item in row.get("target_obligation_ids", []) if str(item)
        ]
        if not row_obligations and row.get("obligation_id"):
            row_obligations = [str(row["obligation_id"])]
        for obligation_id in row_obligations:
            obligation_rows.setdefault(obligation_id, []).append(row)
    if set(obligation_rows) != set(obligations):
        raise CurrentProtocolError("target-native receipt must contain the exact obligation set")
    if set(universe_obligations) != set(universe_ids):
        raise CurrentProtocolError("native universe-to-obligation map must be exact")
    domain_hash = canonical_hash(domain_receipt)
    observations: list[dict[str, Any]] = []
    covered: set[str] = set()
    for row in universe_rows:
        universe_id = str(row["universe_id"])
        mapped = sorted({str(item) for item in universe_obligations.get(universe_id, [])})
        if not mapped or not set(mapped).issubset(obligations):
            raise CurrentProtocolError(f"invalid obligation mapping: {universe_id}")
        for obligation_id in mapped:
            native_rows = obligation_rows.get(obligation_id, [])
            if not native_rows:
                raise CurrentProtocolError(
                    f"target-native per-obligation evidence missing: {obligation_id}"
                )
            for native_row in native_rows:
                if (
                    str(native_row.get("status", "")) != "pass"
                    or not str(native_row.get("native_object_id", ""))
                    or not str(native_row.get("evidence_ref", ""))
                    or len(str(native_row.get("evidence_sha256", ""))) != 64
                    or not isinstance(native_row.get("content"), Mapping)
                ):
                    raise CurrentProtocolError(
                        f"target-native evidence row incomplete: {obligation_id}"
                    )
            covered.add(obligation_id)
            content = {
                "domain_receipt_sha256": domain_hash,
                "universe_id": universe_id,
                "target_obligation_id": obligation_id,
                "native_universe": row,
                "native_obligation_evidence": native_rows,
            }
            observations.append(
                {
                    "observation_id": (
                        f"observation:{target_skill_id}:{universe_id}:{obligation_id}"
                    ),
                    "observation_origin": observation_origin,
                    "native_object_id": (
                        f"native-universe:{target_skill_id}:{universe_id}:{obligation_id}"
                    ),
                    "target_obligation_ids": [obligation_id],
                    "content": content,
                }
            )
    if covered != set(obligations):
        raise CurrentProtocolError(
            "native observation map does not cover exact check obligations: "
            + ",".join(sorted(set(obligations) - covered))
        )

    common = {
        "target_skill_id": target_skill_id,
        "target_contract_hash": str(run.get("contract_hash", "")),
        "depth_profile_hash": runtime["depth_profile_hash"](contract),
        "native_owner_id": owner_id,
        "native_route_id": route_id,
        "native_check_id": check_id,
        "run_id": str(run.get("run_id", "")),
        "target_obligation_ids": obligations,
        "evidence_domain": evidence_domain,
        "scheduled_production_identity": schedule,
    }
    created_at = datetime.now(timezone.utc).isoformat()
    receipt_seed = canonical_hash(
        {"common": common, "domain_receipt_sha256": domain_hash, "observations": observations}
    )
    receipt_id = f"native-receipt:{target_skill_id}:{receipt_seed[:24].lower()}"
    receipt = runtime["build_target_native_receipt"](
        {
            "schema_version": runtime["TARGET_NATIVE_DEPTH_RECEIPT_SCHEMA"],
            **common,
            "native_receipt_id": receipt_id,
            "created_at": created_at,
            "observations": observations,
        }
    )
    receipt_bytes = runtime["native_receipt_bytes"](receipt)
    receipt_hash = hashlib.sha256(receipt_bytes).hexdigest().upper()
    receipt_relative = Path("native-receipts") / f"{receipt_hash[:24].lower()}.json"
    _write_atomic(run_root / receipt_relative, receipt_bytes)

    ranges: list[dict[str, Any]] = []
    for index, observation in enumerate(observations):
        content = observation["content"]
        locator_base = {
            "schema_version": "skillguard.native_semantic_locator.v1",
            "locator_type": "json_pointer.v1",
            "resolver_owner_id": owner_id,
            "native_object_id": observation["native_object_id"],
            "native_coordinate": f"/observations/{index}/content",
            "content_sha256": canonical_hash(content),
        }
        obligation_key = "-".join(observation["target_obligation_ids"])
        ranges.append(
            {
                "range_id": f"range:{target_skill_id}:{index}:{obligation_key}",
                "kind": "semantic",
                "obligation_ids": list(observation["target_obligation_ids"]),
                "universe_id": (
                    str(content.get("universe_id", ""))
                    or universe_ids[0]
                ),
                "semantic_locator": {
                    **locator_base,
                    "locator_fingerprint": canonical_hash(locator_base),
                },
            }
        )
    evidence = runtime["build_target_native_depth_evidence"](
        {
            "schema_version": "skillguard.native_depth_evidence.v2",
            **common,
            "request_fingerprint": str(run.get("request_fingerprint", "")),
            "target_input_fingerprint": target_input_fingerprint,
            "native_receipt_id": receipt_id,
            "native_receipt_hash": receipt_hash,
            "native_receipt_artifact_ref": {
                "path_token": "run_root",
                "relative_path": receipt_relative.as_posix(),
            },
            "native_receipt_created_at": created_at,
            "universes": universe_rows,
            "depth_contribution_ranges": ranges,
        }
    )
    output = (run_root / output_relative).resolve()
    output.relative_to(run_root)
    _write_atomic(output, canonical_json_bytes(evidence))
    return evidence


def emit_native_calibration(
    *,
    repository_root: Path,
    run_root: Path,
    check_id: str,
    fixture_relative: str,
    declared_inputs: Sequence[str],
    output_relative: str,
    domain_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    """Write one target-native positive or genuinely shallow calibration pair member."""

    runtime = _skillguard_runtime()
    canonical_hash = runtime["canonical_hash"]
    canonical_json_bytes = runtime["canonical_json_bytes"]
    repository_root = repository_root.resolve()
    run_root = run_root.resolve()
    run, contract, check = _run_context(run_root, check_id)
    profile = contract.get("depth_profile", {})
    calibration = profile.get("calibration", {}) if isinstance(profile, Mapping) else {}
    matches = []
    if isinstance(calibration, Mapping):
        for case_kind, key in (("positive", "positive_cases"), ("shallow", "shallow_cases")):
            matches.extend((case_kind, row) for row in calibration.get(key, []) if isinstance(row, Mapping) and row.get("native_check_id") == check_id)
    if len(matches) != 1:
        raise CurrentProtocolError(f"exactly one calibration case required: {check_id}")
    case_kind, declared_case = matches[0]
    surface = runtime["calibration_contract_surface"](
        contract=contract,
        check=check,
        case_kind=case_kind,
        declared_case=declared_case,
    )
    request = run.get("request", {})
    if not isinstance(request, Mapping):
        raise CurrentProtocolError("calibration run request missing")
    expected_domain_identity = {
        "target_skill_id": surface["target_skill_id"],
        "native_owner_id": surface["native_owner_id"],
        "native_route_id": surface["native_route_id"],
        "check_id": check_id,
        "run_id": str(run.get("run_id", "")),
        "contract_hash": str(run.get("contract_hash", "")),
        "request_fingerprint": str(run.get("request_fingerprint", "")),
        "target_input_fingerprint": str(request.get("target_input_fingerprint", "")),
        "evidence_domain": surface["evidence_domain"],
    }
    for field, expected in expected_domain_identity.items():
        if str(domain_receipt.get(field, "")) != str(expected):
            raise CurrentProtocolError(
                f"target-native calibration identity mismatch: {field}"
            )
    if not str(domain_receipt.get("native_receipt_id", "")):
        raise CurrentProtocolError("target-native calibration receipt id missing")
    if len(str(domain_receipt.get("native_receipt_hash", ""))) != 64:
        raise CurrentProtocolError("target-native calibration receipt hash missing")
    important = list(surface["important_obligation_ids"])
    if sorted(str(item) for item in domain_receipt.get("target_obligation_ids", [])) != sorted(important):
        raise CurrentProtocolError("target-native calibration obligation identity mismatch")
    if dict(domain_receipt.get("scheduled_production_identity", {})):
        raise CurrentProtocolError("fixture calibration cannot carry production identity")
    manifest = runtime["calibration_input_manifest"](repository_root, list(declared_inputs))
    normalized_fixture = Path(fixture_relative).as_posix()
    if normalized_fixture != Path(str(declared_case.get("fixture_path", ""))).as_posix():
        raise CurrentProtocolError("fixture does not match current calibration contract")
    if manifest["calibration_input_paths"] != sorted(Path(str(item)).as_posix() for item in declared_case.get("calibration_input_paths", [])):
        raise CurrentProtocolError("calibration input set is stale")
    if manifest["calibration_input_hashes"] != declared_case.get("calibration_input_hashes") or manifest["input_fingerprint"] != declared_case.get("input_fingerprint"):
        raise CurrentProtocolError("calibration input identity is stale")
    expected_pass = case_kind == "positive"
    actual_pass = str(domain_receipt.get("status", "")) == "pass"
    if actual_pass != expected_pass:
        raise CurrentProtocolError("target-native calibration outcome does not match case kind")
    omitted = str(surface.get("omitted_important_obligation_id", ""))
    raw_results = domain_receipt.get("native_calibration_obligation_results", [])
    if not isinstance(raw_results, list):
        raise CurrentProtocolError("target-native calibration obligation results missing")
    result_map: dict[str, dict[str, Any]] = {}
    for raw_result in raw_results:
        if not isinstance(raw_result, Mapping):
            raise CurrentProtocolError("target-native calibration result must be an object")
        result = dict(raw_result)
        obligation_id = str(result.get("obligation_id", ""))
        if not obligation_id or obligation_id in result_map:
            raise CurrentProtocolError("target-native calibration obligations must be exact and unique")
        if (
            str(result.get("status", "")) not in {"pass", "blocked"}
            or not str(result.get("evidence_ref", ""))
            or len(str(result.get("evidence_sha256", ""))) != 64
            or not isinstance(result.get("content"), Mapping)
        ):
            raise CurrentProtocolError(
                f"target-native calibration result incomplete: {obligation_id}"
            )
        result_map[obligation_id] = result
    if set(result_map) != set(important):
        raise CurrentProtocolError("target-native calibration did not evaluate every important obligation")
    blocked = sorted(
        obligation_id
        for obligation_id, result in result_map.items()
        if result["status"] == "blocked"
    )
    if expected_pass and blocked:
        raise CurrentProtocolError("positive native calibration contains a blocked obligation")
    if not expected_pass and blocked != [omitted]:
        raise CurrentProtocolError("shallow native calibration must block exactly the omitted obligation")
    covered = sorted(
        obligation_id
        for obligation_id, result in result_map.items()
        if result["status"] == "pass"
    )
    blocker = "none" if expected_pass else runtime["IMPORTANT_OBLIGATION_BLOCKER"]
    observed_status = "EXECUTION_DEPTH_PASS" if expected_pass else "SHALLOW_BLOCKED"
    created_at = datetime.now(timezone.utc).isoformat()
    domain_hash = canonical_hash(domain_receipt)
    receipt_id = (
        f"calibration-receipt:{contract['skill_id']}:"
        f"{declared_case['case_id']}:{domain_hash.lower()}"
    )
    common = {
        "target_skill_id": surface["target_skill_id"],
        "target_contract_hash": str(run.get("contract_hash", "")),
        "depth_profile_hash": surface["depth_profile_hash"],
        "native_owner_id": surface["native_owner_id"],
        "native_route_id": surface["native_route_id"],
        "native_check_id": surface["native_check_id"],
        "check_id": check_id,
        "calibration_check_id": check_id,
        "run_id": str(run.get("run_id", "")),
        "request_fingerprint": str(run.get("request_fingerprint", "")),
        "target_input_fingerprint": str(request.get("target_input_fingerprint", "")),
        "target_obligation_ids": important,
        "evidence_domain": surface["evidence_domain"],
        "evaluator_id": surface["evaluator_id"],
        "evaluator_version": surface["evaluator_version"],
        "calibration_pair_id": surface["calibration_pair_id"],
        "input_family_fingerprint": surface["input_family_fingerprint"],
        "important_obligation_ids": important,
        "covered_important_obligation_ids": covered,
        "required_capability_ids": list(surface["required_capability_ids"]),
        "covered_capability_ids": list(surface["required_capability_ids"]),
        "omitted_important_obligation_id": omitted,
        "native_blocker_code": blocker,
        "native_blocker_obligation_id": omitted,
        "outcome_authority": runtime["TARGET_NATIVE_OUTCOME_AUTHORITY"],
        "case_id": str(declared_case["case_id"]),
        "case_kind": case_kind,
        "fixture_path": normalized_fixture,
        "fixture_sha256": manifest["calibration_input_hashes"][normalized_fixture],
        "calibration_input_paths": manifest["calibration_input_paths"],
        "calibration_input_hashes": manifest["calibration_input_hashes"],
        "input_fingerprint": manifest["input_fingerprint"],
        "observed_status": observed_status,
        "observed_blocker_code": blocker,
        "native_receipt_id": receipt_id,
        "native_receipt_created_at": created_at,
    }
    native_receipt = {"schema_version": runtime["TARGET_NATIVE_CALIBRATION_OBSERVATION_SCHEMA"], **common}
    native_receipt["receipt_hash"] = canonical_hash(native_receipt)
    receipt_bytes = canonical_json_bytes(native_receipt)
    receipt_hash = hashlib.sha256(receipt_bytes).hexdigest().upper()
    receipt_relative = Path("calibration-native-receipts") / f"{receipt_hash[:24].lower()}.json"
    _write_atomic(run_root / receipt_relative, receipt_bytes)
    evidence = runtime["build_target_native_calibration_evidence"](
        {
            "schema_version": "skillguard.native_depth_calibration_evidence.v2",
            **common,
            "native_receipt_hash": receipt_hash,
            "native_receipt_artifact_ref": {"path_token": "run_root", "relative_path": receipt_relative.as_posix()},
        }
    )
    output = (run_root / output_relative).resolve()
    output.relative_to(run_root)
    _write_atomic(output, canonical_json_bytes(evidence))
    return evidence

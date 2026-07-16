"""Execute one WorldGuard-owned V2 depth calibration case."""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping


def _canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest().upper()


def _load(path: Path) -> Mapping[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError(f"JSON object required: {path}")
    return payload


def _case(contract: Mapping[str, Any], check_id: str) -> tuple[str, Mapping[str, Any]]:
    profile = contract.get("depth_profile", {})
    calibration = profile.get("calibration", {}) if isinstance(profile, Mapping) else {}
    matches: list[tuple[str, Mapping[str, Any]]] = []
    if isinstance(calibration, Mapping):
        for case_kind, key in (("positive", "positive_cases"), ("shallow", "shallow_cases")):
            rows = calibration.get(key, [])
            if isinstance(rows, list):
                matches.extend(
                    (case_kind, row)
                    for row in rows
                    if isinstance(row, Mapping) and row.get("native_check_id") == check_id
                )
    if len(matches) != 1:
        raise ValueError(f"exactly one calibration case required for {check_id}")
    return matches[0]


def _input_manifest(repository_root: Path, paths: list[str]) -> dict[str, Any]:
    normalized = sorted(Path(path).as_posix() for path in paths)
    if not normalized or len(normalized) != len(set(normalized)):
        raise ValueError("calibration inputs must be unique and non-empty")
    hashes: dict[str, str] = {}
    for relative in normalized:
        candidate = (repository_root / relative).resolve()
        candidate.relative_to(repository_root)
        hashes[relative] = hashlib.sha256(candidate.read_bytes()).hexdigest().upper()
    return {
        "calibration_input_paths": normalized,
        "calibration_input_hashes": hashes,
        "input_fingerprint": _canonical_hash(
            {
                "calibration_inputs": [
                    {"path": path, "sha256": hashes[path]} for path in normalized
                ]
            }
        ),
    }


def _activate_bundled_runtime(repository_root: Path) -> Path:
    """Select the installed skill's calibration runtime without source fallback."""

    runtime_root = (repository_root / ".skillguard" / "runtime").resolve()
    package_root = runtime_root / "worldguard"
    required_modules = (
        package_root / "__init__.py",
        package_root / "skillguard_depth.py",
        package_root / "skillguard_current_protocol.py",
    )
    missing = [path.name for path in required_modules if not path.is_file()]
    if missing:
        raise ValueError(
            "formal calibration requires the bundled WorldGuard runtime; missing: "
            + ", ".join(sorted(missing))
        )
    sys.path.insert(0, str(runtime_root))
    return package_root


def _require_bundled_module(symbol: object, package_root: Path) -> None:
    module_name = str(getattr(symbol, "__module__", ""))
    module = sys.modules.get(module_name)
    module_path = Path(str(getattr(module, "__file__", ""))).resolve()
    try:
        module_path.relative_to(package_root)
    except ValueError as exc:
        raise ValueError(
            "formal calibration loaded WorldGuard outside the bundled skill runtime"
        ) from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--repository-root", required=True)
    parser.add_argument("--target-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--input", action="append", required=True)
    parser.add_argument("--check-id", required=True)
    args = parser.parse_args(argv)

    run_root = Path(args.run_root).resolve()
    repository_root = Path(args.repository_root).resolve()
    output = (run_root / args.output).resolve()
    output.relative_to(run_root)
    run = _load(run_root / "run.json")
    contract = _load(run_root / "contract.json")
    case_kind, declared = _case(contract, args.check_id)
    fixture_path = Path(str(declared["fixture_path"])).as_posix()
    if Path(args.fixture).as_posix() != fixture_path:
        raise ValueError("fixture argument does not match the declared case")
    supplied = sorted(Path(path).as_posix() for path in args.input)
    declared_inputs = sorted(
        Path(str(path)).as_posix()
        for path in declared.get("calibration_input_paths", [])
    )
    if supplied != declared_inputs:
        raise ValueError("input arguments do not match the declared input set")
    manifest = _input_manifest(repository_root, supplied)
    if manifest["calibration_input_hashes"] != declared.get("calibration_input_hashes"):
        raise ValueError("calibration input hashes are stale")
    if manifest["input_fingerprint"] != declared.get("input_fingerprint"):
        raise ValueError("calibration input fingerprint is stale")
    fixture_hash = manifest["calibration_input_hashes"].get(fixture_path, "")
    if fixture_hash != declared.get("fixture_sha256"):
        raise ValueError("calibration fixture hash is stale")

    bundled_package_root = _activate_bundled_runtime(repository_root)
    from worldguard.skillguard_depth import build_native_depth_evidence  # noqa: PLC0415
    _require_bundled_module(build_native_depth_evidence, bundled_package_root)

    observed = build_native_depth_evidence(repository_root / fixture_path)
    status = str(observed["status"])
    blocker = str(observed["primary_blocker_code"])
    fixture = _load(repository_root / fixture_path)
    if fixture.get("case_id") != declared.get("case_id"):
        raise ValueError("calibration fixture case id mismatch")
    if {
        "expected_status",
        "expected_blocker_code",
        "observed_status",
        "observed_blocker_code",
    }.intersection(fixture):
        raise ValueError("calibration fixture must not self-report outcomes")

    from worldguard.skillguard_current_protocol import (  # noqa: PLC0415
        emit_native_calibration,
    )
    _require_bundled_module(emit_native_calibration, bundled_package_root)

    important_obligations = [
        "obligation:worldguard-claim-routes",
        "obligation:worldguard-predictive-axes",
        "obligation:worldguard-receipt-freshness",
        "obligation:worldguard-scenario-holdout-depth",
        "obligation:worldguard-semantic-universe",
        "obligation:worldguard-timepoint-strata-depth",
    ]
    blocked_obligation = None
    if status != "EXECUTION_DEPTH_PASS":
        blocked_obligation = {
            "time_horizon_depth_incomplete": (
                "obligation:worldguard-timepoint-strata-depth"
            )
        }.get(blocker)
        if blocked_obligation is None:
            raise ValueError(f"unmapped WorldGuard calibration blocker: {blocker}")
    native_rows = [
        row
        for row in observed.get("native_obligation_evidence", [])
        if isinstance(row, Mapping)
    ]
    calibration_results = []
    for obligation_id in important_obligations:
        relevant = [
            dict(row)
            for row in native_rows
            if obligation_id in row.get("target_obligation_ids", [])
        ]
        if not relevant:
            raise ValueError(f"WorldGuard calibration evidence missing: {obligation_id}")
        content = {
            "case_id": observed["case_id"],
            "obligation_id": obligation_id,
            "native_obligation_evidence": relevant,
            "native_blocker_code": (
                blocker if obligation_id == blocked_obligation else "none"
            ),
        }
        calibration_results.append(
            {
                "obligation_id": obligation_id,
                "status": "blocked" if obligation_id == blocked_obligation else "pass",
                "evidence_ref": f"worldguard:calibration:{observed['case_id']}:{obligation_id}",
                "evidence_sha256": _canonical_hash(content),
                "content": content,
            }
        )

    domain_receipt = {
        **dict(observed),
        "target_skill_id": "worldguard",
        "native_owner_id": "worldguard.mesh.predictive_coverage",
        "native_route_id": "route:worldguard-claim-derived-depth",
        "check_id": args.check_id,
        "run_id": str(run["run_id"]),
        "contract_hash": str(run["contract_hash"]),
        "request_fingerprint": str(run["request_fingerprint"]),
        "target_input_fingerprint": str(run["request"]["target_input_fingerprint"]),
        "target_obligation_ids": important_obligations,
        "scheduled_production_identity": {},
        "evidence_domain": "fixture_calibration",
        "status": "pass" if status == "EXECUTION_DEPTH_PASS" else "blocked",
        "native_blocker_code": blocker,
        "native_calibration_obligation_results": calibration_results,
    }
    emit_native_calibration(
        repository_root=repository_root,
        run_root=run_root,
        check_id=args.check_id,
        fixture_relative=fixture_path,
        declared_inputs=supplied,
        output_relative=args.output,
        domain_receipt=domain_receipt,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

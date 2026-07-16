"""Run WorldGuard's target-owned depth check under generic SkillGuard supervision."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping


def _load_object(path: Path) -> Mapping[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError(f"JSON object required: {path}")
    return payload


def _resolve_input(repository_root: Path, run: Mapping[str, Any]) -> Path:
    request = run.get("request", {})
    if not isinstance(request, Mapping):
        raise ValueError("run request missing")
    raw_paths = request.get("target_input_paths", [])
    if isinstance(raw_paths, (str, bytes)) or not isinstance(raw_paths, list):
        raise ValueError("target_input_paths must be an array")
    if len(raw_paths) != 1:
        raise ValueError(
            "exactly one current target input containing a WorldGuard mesh is required"
        )
    candidates: list[Path] = []
    for raw in raw_paths:
        candidate = (repository_root / str(raw)).resolve()
        try:
            candidate.relative_to(repository_root)
        except ValueError as exc:
            raise ValueError(f"target input outside repository: {raw}") from exc
        payload = _load_object(candidate)
        if isinstance(payload.get("mesh"), Mapping):
            candidates.append(candidate)
    if len(candidates) != 1:
        raise ValueError(
            "exactly one current target input containing a WorldGuard mesh is required"
        )
    return candidates[0]


def _declared_check(run_root: Path, check_id: str) -> Mapping[str, Any]:
    manifest = _load_object(run_root / "check-manifest.json")
    rows = manifest.get("checks", [])
    if isinstance(rows, (str, bytes)) or not isinstance(rows, list):
        raise ValueError("run check manifest is invalid")
    matches = [
        row
        for row in rows
        if isinstance(row, Mapping) and row.get("check_id") == check_id
    ]
    if len(matches) != 1:
        raise ValueError(f"declared check missing or ambiguous: {check_id}")
    return matches[0]


def _activate_bundled_runtime(repository_root: Path) -> Path:
    """Select the installed skill's formal runtime without any source fallback."""

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
            "formal depth requires the bundled WorldGuard runtime; missing: "
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
            "formal depth loaded WorldGuard outside the bundled skill runtime"
        ) from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--repository-root", required=True)
    parser.add_argument("--target-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--check-id", required=True)
    args = parser.parse_args(argv)

    run_root = Path(args.run_root).resolve()
    repository_root = Path(args.repository_root).resolve()
    target_root = Path(args.target_root).resolve()
    output = (run_root / args.output).resolve()
    try:
        output.relative_to(run_root)
    except ValueError as exc:
        raise SystemExit(f"output outside run root: {args.output}") from exc

    bundled_package_root = _activate_bundled_runtime(repository_root)
    from worldguard.skillguard_depth import (  # noqa: PLC0415
        build_target_native_depth_envelope,
        target_native_policy_fingerprints,
    )
    _require_bundled_module(build_target_native_depth_envelope, bundled_package_root)
    _require_bundled_module(target_native_policy_fingerprints, bundled_package_root)

    run = _load_object(run_root / "run.json")
    check = _declared_check(run_root, args.check_id)
    fixture = _resolve_input(target_root, run)
    fixture_payload = _load_object(fixture)
    if fixture_payload.get("input_origin") != "target_native_scheduled_execution":
        raise ValueError(
            "scheduled production requires a target-native scheduled execution input; relabeling calibration is forbidden"
        )
    schedule = fixture_payload.get("scheduled_production_identity", {})
    if not isinstance(schedule, Mapping) or not schedule:
        raise ValueError("scheduled production identity missing from target-native receipt")
    request = run.get("request", {})
    assert isinstance(request, Mapping)
    native_projection = build_target_native_depth_envelope(
        fixture,
        run_binding={
            "run_id": run["run_id"],
            "contract_hash": run["contract_hash"],
            "request_fingerprint": run["request_fingerprint"],
            "target_input_fingerprint": request["target_input_fingerprint"],
            "evidence_domain": "scheduled_production",
            "scheduled_production_identity": dict(schedule),
        },
        check_id=args.check_id,
        policy_fingerprints=target_native_policy_fingerprints(),
    )
    expected_obligations = sorted(
        str(item) for item in check.get("covers_obligation_ids", []) if str(item)
    )
    observed_obligations = sorted(
        str(item) for item in native_projection.get("target_obligation_ids", []) if str(item)
    )
    evidence_rows = [
        row
        for row in native_projection.get("native_obligation_evidence", [])
        if isinstance(row, Mapping)
    ]
    predictive_claim_licensed = bool(
        evidence_rows
        and all(str(row.get("status", "")) == "pass" for row in evidence_rows)
    )
    ok = bool(
        predictive_claim_licensed
        and expected_obligations
        and observed_obligations == expected_obligations
    )
    payload = {
        "schema_version": "worldguard.declared_native_depth_check.v1",
        "ok": ok,
        "check_id": args.check_id,
        "evidence_domain": "scheduled_production",
        "scheduled_production_identity": dict(schedule),
        "target_obligation_ids": observed_obligations,
        "expected_obligation_ids": expected_obligations,
        "predictive_claim_licensed": predictive_claim_licensed,
        "native_projection": native_projection,
        "claim_boundary": (
            "This target-owned check proves only the declared mesh input's bounded predictive "
            "depth. Generic SkillGuard supervises its exit status and exact inputs but does not "
            "own or reinterpret WorldGuard policy."
        ),
    }
    body = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.{os.getpid()}.tmp")
    temporary.write_bytes(body)
    os.replace(temporary, output)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

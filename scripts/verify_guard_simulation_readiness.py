from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
HOME_SKILLS = Path.home() / ".codex" / "skills"
PACKAGE_NAME = "worldguard"
TARGET_SKILL_ID = "worldguard"
SOURCE_SKILL = ROOT / "skills" / TARGET_SKILL_ID
INSTALLED_SKILL = HOME_SKILLS / TARGET_SKILL_ID
CONSUMER_RELEASE_SCHEMA = "consumer.skill_distribution.current"
CONSUMER_RELEASE_FILE = "consumer-release.json"
CURRENT_AUTHOR_AUTHORITY_FILES = (
    "contract-source.json",
    "compiled-contract.json",
    "check-manifest.json",
)
FORBIDDEN_AUTHOR_V1_FILES = (
    "check_manifest.json",
    "work-contract.json",
    "check.py",
    "checks/check_closure.py",
    "checks/check_evidence.py",
    "checks/check_phase_order.py",
    "checks/check_quality_floor.py",
    "checks/check_route.py",
    "skillguard_closure_policy.json",
    "skillguard_evidence_rules.json",
    "skillguard_manifest.json",
    "skillguard_profile.json",
    "skillguard_skill_contract.json",
    "skillguard_progress_ledger.jsonl",
)
FORBIDDEN_AUTHOR_V1_DIRS = ("ai_judgments", "evidence", "reports", "runs")
RETIREMENT_RECEIPT = "retirement-completion-receipt.json"
EXCLUDED_TREE_NAMES = frozenset(
    {".git", ".hg", ".svn", "__pycache__", ".pytest_cache", ".mypy_cache"}
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().lower()


def _canonical_hash(payload: object) -> str:
    body = (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    return hashlib.sha256(body).hexdigest().upper()


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _relative_files(
    root: Path,
    *,
    exclude_author_control: bool,
    exclude_manifest: bool,
) -> dict[str, Path]:
    rows: dict[str, Path] = {}
    if not root.is_dir():
        return rows
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in EXCLUDED_TREE_NAMES for part in relative.parts):
            continue
        normalized = relative.as_posix()
        if exclude_author_control and (
            normalized == ".skillguard" or normalized.startswith(".skillguard/")
        ):
            continue
        if exclude_manifest and normalized == CONSUMER_RELEASE_FILE:
            continue
        if path.is_file() or path.is_symlink():
            rows[normalized] = path
    return rows


def _check_package_identity() -> dict[str, Any]:
    module = importlib.import_module(PACKAGE_NAME)
    module_path = Path(module.__file__).resolve()
    metadata_version = importlib.metadata.version(PACKAGE_NAME)
    module_version = str(getattr(module, "__version__", ""))
    return {
        "check": "canonical_package_identity",
        "ok": metadata_version == module_version and _is_within(module_path, ROOT),
        "metadata_version": metadata_version,
        "module_version": module_version,
        "module_path": str(module_path),
        "expected_repository_root": str(ROOT.resolve()),
    }


def _former_author_residuals(control_root: Path) -> list[str]:
    found = [
        relative
        for relative in FORBIDDEN_AUTHOR_V1_FILES
        if (control_root / relative).is_file()
    ]
    for relative in FORBIDDEN_AUTHOR_V1_DIRS:
        directory = control_root / relative
        if directory.is_dir() and any(path.is_file() for path in directory.rglob("*")):
            found.append(f"{relative}/**")
    if any(
        path.is_file()
        for cache in control_root.rglob("__pycache__")
        for path in cache.rglob("*")
    ):
        found.append("**/__pycache__/**")
    return sorted(found)


def _retirement_receipt_status(
    control_root: Path,
    target_skill_id: str,
) -> dict[str, Any]:
    path = control_root / RETIREMENT_RECEIPT
    if not path.is_file():
        return {
            "ok": False,
            "path": str(path),
            "reason": "expanded_scope_retirement_receipt_missing",
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {
            "ok": False,
            "path": str(path),
            "reason": f"invalid_retirement_receipt:{exc}",
        }
    ok = (
        payload.get("schema_version")
        == "worldguard.skillguard-retirement-completion.current"
        and payload.get("status") == "retired"
        and payload.get("target_skill_id") == target_skill_id
        and payload.get("source_residual_scan", {}).get("residual_count") == 0
        and payload.get("installed_residual_scan", {}).get("residual_count") == 0
        and payload.get("installation_currentness", {}).get("status") == "passed"
    )
    return {
        "ok": ok,
        "path": str(path),
        "receipt_id": payload.get("receipt_id"),
        "target_skill_id": payload.get("target_skill_id"),
        "source_residual_count": payload.get("source_residual_scan", {}).get(
            "residual_count"
        ),
        "installed_residual_count": payload.get("installed_residual_scan", {}).get(
            "residual_count"
        ),
        "installation_currentness": payload.get("installation_currentness", {}).get(
            "status"
        ),
    }


def _source_authority_status(
    skill_root: Path,
    target_skill_id: str,
) -> dict[str, Any]:
    control_root = skill_root / ".skillguard"
    missing = [
        relative
        for relative in CURRENT_AUTHOR_AUTHORITY_FILES
        if not (control_root / relative).is_file()
    ]
    residuals = _former_author_residuals(control_root)
    retirement = _retirement_receipt_status(control_root, target_skill_id)
    return {
        "ok": not missing and not residuals and retirement["ok"],
        "skill_root": str(skill_root),
        "missing_current_authority": missing,
        "former_author_residuals": residuals,
        "retirement_receipt": retirement,
        "claim_boundary": (
            "This check covers only author-side SkillGuard control state in the "
            "maintainer source. That state must not enter the consumer."
        ),
    }


def _load_consumer_manifest(installed_skill: Path) -> tuple[dict[str, Any], list[str]]:
    path = installed_skill / CONSUMER_RELEASE_FILE
    findings: list[str] = []
    if not path.is_file():
        return {}, ["consumer_release_manifest_missing"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}, ["consumer_release_manifest_invalid_json"]
    if not isinstance(payload, dict):
        return {}, ["consumer_release_manifest_not_object"]

    unsigned = dict(payload)
    stored_manifest_hash = unsigned.pop("manifest_hash", None)
    if (
        payload.get("schema_version") != CONSUMER_RELEASE_SCHEMA
        or payload.get("projection_id") != "projection:consumer-distribution"
        or payload.get("skill_id") != TARGET_SKILL_ID
        or payload.get("author_control_excluded") is not True
        or stored_manifest_hash != _canonical_hash(unsigned)
    ):
        findings.append("consumer_release_manifest_invalid")

    files = payload.get("files")
    if not isinstance(files, list) or not files:
        findings.append("consumer_release_files_invalid")
        files = []
    normalized_rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in files:
        if not isinstance(row, Mapping):
            findings.append("consumer_release_file_row_invalid")
            continue
        relative = str(row.get("path", "")).replace("\\", "/")
        content_hash = str(row.get("content_hash", ""))
        relative_path = Path(*relative.split("/")) if relative else Path()
        if (
            not relative
            or relative in seen
            or relative.startswith("/")
            or ".." in relative_path.parts
            or relative == CONSUMER_RELEASE_FILE
            or relative == ".skillguard"
            or relative.startswith(".skillguard/")
            or not content_hash.startswith("sha256:")
            or len(content_hash) != 71
        ):
            findings.append(f"consumer_release_file_row_unsafe:{relative}")
            continue
        seen.add(relative)
        normalized_rows.append({"path": relative, "content_hash": content_hash})

    identity = {
        "schema_version": payload.get("schema_version"),
        "skill_id": payload.get("skill_id"),
        "projection_id": payload.get("projection_id"),
        "files": normalized_rows,
        "author_control_excluded": payload.get("author_control_excluded"),
    }
    if payload.get("release_id") != _canonical_hash(identity):
        findings.append("consumer_release_id_mismatch")
    return payload, findings


def _consumer_projection_status(
    source_skill: Path,
    installed_skill: Path,
) -> dict[str, Any]:
    manifest, findings = _load_consumer_manifest(installed_skill)
    expected = {
        str(row.get("path", "")): str(row.get("content_hash", ""))
        for row in manifest.get("files", [])
        if isinstance(row, Mapping)
    }
    source_files = _relative_files(
        source_skill,
        exclude_author_control=True,
        exclude_manifest=True,
    )
    installed_files = _relative_files(
        installed_skill,
        exclude_author_control=False,
        exclude_manifest=True,
    )

    installed_author_control = sorted(
        relative
        for relative in installed_files
        if relative == ".skillguard" or relative.startswith(".skillguard/")
    )
    for relative in installed_author_control:
        findings.append(f"consumer_author_control_path_present:{relative}")

    source_paths = set(source_files)
    installed_paths = set(installed_files) - set(installed_author_control)
    expected_paths = set(expected)
    for relative in sorted(expected_paths - source_paths):
        findings.append(f"source_projection_file_missing:{relative}")
    for relative in sorted(source_paths - expected_paths):
        findings.append(f"source_projection_file_unexpected:{relative}")
    for relative in sorted(expected_paths - installed_paths):
        findings.append(f"consumer_file_missing:{relative}")
    for relative in sorted(installed_paths - expected_paths):
        findings.append(f"consumer_file_unexpected:{relative}")

    rows: list[dict[str, Any]] = []
    for relative in sorted(expected_paths & source_paths & installed_paths):
        source_path = source_files[relative]
        installed_path = installed_files[relative]
        source_hash = (
            f"sha256:{_sha256(source_path)}" if source_path.is_file() else "symlink"
        )
        installed_hash = (
            f"sha256:{_sha256(installed_path)}"
            if installed_path.is_file()
            else "symlink"
        )
        ok = (
            source_path.is_file()
            and installed_path.is_file()
            and expected[relative] == source_hash == installed_hash
        )
        rows.append(
            {
                "relative_path": relative,
                "expected_hash": expected[relative],
                "source_hash": source_hash,
                "installed_hash": installed_hash,
                "ok": ok,
            }
        )
        if not ok:
            findings.append(f"consumer_file_hash_mismatch:{relative}")

    findings = sorted(set(findings))
    return {
        "ok": not findings,
        "source_skill": str(source_skill.resolve()),
        "installed_skill": str(installed_skill.resolve()),
        "release_id": str(manifest.get("release_id", "")),
        "manifest_hash": str(manifest.get("manifest_hash", "")),
        "expected_member_count": len(expected_paths),
        "source_member_count": len(source_paths),
        "installed_member_count": len(installed_paths),
        "installed_author_control_paths": installed_author_control,
        "findings": findings,
        "rows": rows,
        "claim_boundary": (
            "This check proves exact target-owned source/manifest/installed byte "
            "parity and zero installed .skillguard paths. It executes no domain owner."
        ),
    }


def main() -> int:
    package = _check_package_identity()
    source_authority = _source_authority_status(SOURCE_SKILL, TARGET_SKILL_ID)
    consumer_projection = _consumer_projection_status(SOURCE_SKILL, INSTALLED_SKILL)
    ok = package["ok"] and source_authority["ok"] and consumer_projection["ok"]
    result = {
        "artifact_kind": "worldguard_release_readiness_audit",
        "ok": ok,
        "package": package,
        "source_authority": source_authority,
        "consumer_projection": consumer_projection,
        "installation_currentness": {
            "status": "passed" if consumer_projection["ok"] else "blocked",
            "release_id": consumer_projection["release_id"],
            "manifest_hash": consumer_projection["manifest_hash"],
        },
        "failures": [
            label
            for label, status in (
                ("package_identity_not_current", package["ok"]),
                ("source_authority_not_current", source_authority["ok"]),
                ("consumer_projection_not_current", consumer_projection["ok"]),
            )
            if not status
        ],
        "claim_boundary": (
            "Pass proves current package identity, current author-only SkillGuard "
            "control, and one exact clean standalone WorldGuard consumer projection. "
            "It does not prove a real target claim, factual truth, or future AI behavior."
        ),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

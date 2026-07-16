from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HOME_SKILLS = Path.home() / ".codex" / "skills"
PACKAGE_NAME = "worldguard"
SKILLS = (
    ("worldguard", "skills/worldguard", "worldguard"),
)
CURRENT_AUTHORITY_FILES = (
    "contract-source.json",
    "compiled-contract.json",
    "check-manifest.json",
)
FORBIDDEN_V1_FILES = (
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
FORBIDDEN_V1_DIRS = ("ai_judgments", "evidence", "reports", "runs")
RETIREMENT_RECEIPT = "retirement-completion-receipt.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().lower()


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


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


def _residuals(control_root: Path) -> list[str]:
    found = [
        relative
        for relative in FORBIDDEN_V1_FILES
        if (control_root / relative).is_file()
    ]
    for relative in FORBIDDEN_V1_DIRS:
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


def _retirement_receipt_status(control_root: Path, target_skill_id: str) -> dict[str, Any]:
    path = control_root / RETIREMENT_RECEIPT
    if not path.is_file():
        return {"ok": False, "path": str(path), "reason": "expanded_scope_retirement_receipt_missing"}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "path": str(path), "reason": f"invalid_retirement_receipt:{exc}"}
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
        "source_residual_count": payload.get("source_residual_scan", {}).get("residual_count"),
        "installed_residual_count": payload.get("installed_residual_scan", {}).get("residual_count"),
        "installation_currentness": payload.get("installation_currentness", {}).get("status"),
    }


def _authority_status(skill_root: Path, target_skill_id: str) -> dict[str, Any]:
    control_root = skill_root / ".skillguard"
    missing = [
        relative
        for relative in CURRENT_AUTHORITY_FILES
        if not (control_root / relative).is_file()
    ]
    residuals = _residuals(control_root)
    retirement = _retirement_receipt_status(control_root, target_skill_id)
    return {
        "ok": not missing and not residuals and retirement["ok"],
        "skill_root": str(skill_root),
        "missing_current_authority": missing,
        "former_v1_residuals": residuals,
        "retirement_receipt": retirement,
    }


def _parity_status(source_skill: Path, installed_skill: Path) -> dict[str, Any]:
    relatives = [
        Path("SKILL.md"),
        *(Path(".skillguard") / name for name in CURRENT_AUTHORITY_FILES),
        Path(".skillguard") / RETIREMENT_RECEIPT,
    ]
    if (source_skill / "agents" / "openai.yaml").is_file():
        relatives.append(Path("agents") / "openai.yaml")
    rows: list[dict[str, Any]] = []
    for relative in relatives:
        source = source_skill / relative
        installed = installed_skill / relative
        source_hash = _sha256(source) if source.is_file() else None
        installed_hash = _sha256(installed) if installed.is_file() else None
        rows.append(
            {
                "relative_path": relative.as_posix(),
                "source_sha256": source_hash,
                "installed_sha256": installed_hash,
                "ok": source_hash is not None and source_hash == installed_hash,
            }
        )
    return {"ok": all(row["ok"] for row in rows), "rows": rows}


def _skill_status(target_skill_id: str, source_relative: str, installed_name: str) -> dict[str, Any]:
    source_skill = (ROOT / source_relative).resolve()
    installed_skill = (HOME_SKILLS / installed_name).resolve()
    source = _authority_status(source_skill, target_skill_id)
    installed = _authority_status(installed_skill, target_skill_id)
    parity = _parity_status(source_skill, installed_skill)
    return {
        "target_skill_id": target_skill_id,
        "ok": source["ok"] and installed["ok"] and parity["ok"],
        "source": source,
        "installed": installed,
        "source_installed_authority_parity": parity,
    }


def main() -> int:
    package = _check_package_identity()
    skills = [_skill_status(*row) for row in SKILLS]
    ok = package["ok"] and all(skill["ok"] for skill in skills)
    result = {
        "artifact_kind": "guard_family_current_runtime_authority_audit",
        "ok": ok,
        "package": package,
        "skills": skills,
        "installation_currentness": {
            "status": "external_exact_receipt_required",
            "claim_boundary": "Byte parity here does not prove issuance, terminal closure, parent consumption, or installation-currentness replay.",
        },
        "claim_boundary": "Pass proves canonical package identity, exact current generic authority-file presence, expanded former-authority residual absence, expanded-scope retirement receipt presence, and limited source/install authority parity. It executes no native owner and cannot close production by itself.",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

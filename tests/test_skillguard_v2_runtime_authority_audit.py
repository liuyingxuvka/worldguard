from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def _source_file_hash(path: Path) -> str:
    body = path.read_bytes()
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError:
        pass
    else:
        body = text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    return hashlib.sha256(body).hexdigest().upper()
SCRIPT = ROOT / "scripts" / "verify_guard_simulation_readiness.py"
PRIMARY_ROOT = ROOT / "skills" / "worldguard"
DEPTH_BRIDGE = PRIMARY_ROOT / ".skillguard/checks/emit_native_depth_evidence.py"
BRIDGE_PATHS = (DEPTH_BRIDGE,)
GUARD_MODEL_CHECK = PRIMARY_ROOT / ".skillguard/checks/check_guard_model_contract.py"


def _load_audit_module():
    spec = importlib.util.spec_from_file_location("guard_v2_authority_audit_under_test", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_current_authority(root: Path, target_skill_id: str) -> None:
    control = root / ".skillguard"
    control.mkdir(parents=True)
    (root / "SKILL.md").write_text("current prompt\n", encoding="utf-8")
    for name in ("contract-source.json", "compiled-contract.json", "check-manifest.json"):
        (control / name).write_text(json.dumps({"name": name}), encoding="utf-8")
    (control / "retirement-completion-receipt.json").write_text(
        json.dumps(
            {
                "schema_version": "worldguard.skillguard-retirement-completion.current",
                "status": "retired",
                "target_skill_id": target_skill_id,
                "receipt_id": "retirement-current",
                "source_residual_scan": {"residual_count": 0},
                "installed_residual_scan": {"residual_count": 0},
                "installation_currentness": {"status": "passed"},
            }
        ),
        encoding="utf-8",
    )


def test_expanded_residual_scan_blocks_generic_checker_and_mutable_report(tmp_path: Path) -> None:
    audit = _load_audit_module()
    skill = tmp_path / "skill"
    _write_current_authority(skill, "target-skill")
    assert audit._authority_status(skill, "target-skill")["ok"] is True

    generic = skill / ".skillguard" / "checks" / "check_route.py"
    generic.parent.mkdir(parents=True)
    generic.write_text("raise SystemExit(0)\n", encoding="utf-8")
    status = audit._authority_status(skill, "target-skill")
    assert status["ok"] is False
    assert "checks/check_route.py" in status["former_v1_residuals"]

    generic.unlink()
    mutable = skill / ".skillguard" / "reports" / "current_closure.json"
    mutable.parent.mkdir(parents=True)
    mutable.write_text("{}\n", encoding="utf-8")
    status = audit._authority_status(skill, "target-skill")
    assert status["ok"] is False
    assert "reports/**" in status["former_v1_residuals"]


def test_narrow_receipt_cannot_hide_residual_and_parity_is_exact(tmp_path: Path) -> None:
    audit = _load_audit_module()
    source = tmp_path / "source"
    installed = tmp_path / "installed"
    _write_current_authority(source, "target-skill")
    _write_current_authority(installed, "target-skill")
    assert audit._parity_status(source, installed)["ok"] is True

    installed.joinpath("SKILL.md").write_text("changed prompt\n", encoding="utf-8")
    assert audit._parity_status(source, installed)["ok"] is False

    residual = source / ".skillguard" / "skillguard_manifest.json"
    residual.write_text("{}\n", encoding="utf-8")
    status = audit._authority_status(source, "target-skill")
    assert status["retirement_receipt"]["ok"] is True
    assert status["ok"] is False
    assert "skillguard_manifest.json" in status["former_v1_residuals"]


def test_former_v1_retirement_receipt_is_never_current_authority(tmp_path: Path) -> None:
    audit = _load_audit_module()
    skill = tmp_path / "skill"
    _write_current_authority(skill, "target-skill")
    current = skill / ".skillguard" / "retirement-completion-receipt.json"
    current.unlink()
    former = skill / ".skillguard" / "v1-retirement-completion-receipt.json"
    former.write_text(
        json.dumps(
            {
                "status": "retired",
                "target_skill_id": "target-skill",
                "receipt_id": "former-v1",
                "residual_scan": {"residual_count": 0},
            }
        ),
        encoding="utf-8",
    )

    status = audit._authority_status(skill, "target-skill")
    assert status["ok"] is False
    assert status["retirement_receipt"]["reason"] == "expanded_scope_retirement_receipt_missing"


def test_primary_contract_uses_generic_supervision_and_binds_portable_runtime() -> None:
    contract = json.loads((PRIMARY_ROOT / ".skillguard/contract-source.json").read_text(encoding="utf-8"))
    compiled = json.loads((PRIMARY_ROOT / ".skillguard/compiled-contract.json").read_text(encoding="utf-8"))
    profile = contract["depth_profile"]

    runtime_path = "skills/worldguard/runtime/worldguard"
    assert runtime_path in contract["implementation_paths"]
    assert len(compiled["source_fingerprints"][f"implementation:{runtime_path}"]) == 64
    assert profile["integration_mode"] == "native-integrated"
    assert profile["enforcement_level"] == "enforced"
    assert profile["required_closure_profiles"] == ["enforced"]
    assert contract["closure_profiles"] == [
        {
            "profile_id": "enforced",
            "required_obligation_ids": contract["closure_profiles"][0]["required_obligation_ids"],
        }
    ]
    for forbidden in ("calibration", "coverage_universes", "dimensions"):
        assert forbidden not in profile
        assert forbidden not in contract
    assert not any("calibration" in check["check_id"] for check in contract["checks"])

    checks = {check["check_id"]: check for check in contract["checks"]}
    for check_id in ("check:worldguard:native-depth", "check:worldguard:guard-model-contract"):
        selectors = checks[check_id]["input_selectors"]
        assert any(
            item.get("path") == runtime_path
            or str(item.get("path", "")).startswith(f"{runtime_path}/")
            for item in selectors
        )
    for bridge in BRIDGE_PATHS:
        text = bridge.read_text(encoding="utf-8")
        assert "_activate_bundled_runtime(" in text
        assert "source_root" not in text
        assert "portable_target_runtime" not in text
    assert "sys.path.insert(0, str(RUNTIME_ROOT))" in GUARD_MODEL_CHECK.read_text(encoding="utf-8")


def test_formal_depth_rejects_missing_bundled_runtime_without_source_fallback(
    tmp_path: Path,
) -> None:
    bridge = _load_module(DEPTH_BRIDGE, "worldguard_depth_bridge_under_test")
    skill_root = tmp_path / "installed-skill"
    skill_root.mkdir()

    with pytest.raises(ValueError, match="bundled WorldGuard runtime"):
        bridge._activate_bundled_runtime(skill_root)


def test_formal_depth_selects_only_the_skill_bundled_runtime(tmp_path: Path) -> None:
    bridge = _load_module(DEPTH_BRIDGE, "worldguard_depth_bridge_runtime_under_test")
    skill_root = tmp_path / "installed-skill"
    package_root = skill_root / "runtime" / "worldguard"
    package_root.mkdir(parents=True)
    for name in ("__init__.py", "execution_depth.py", "skillguard_current_protocol.py"):
        package_root.joinpath(name).write_text("# bundled\n", encoding="utf-8")

    assert bridge._activate_bundled_runtime(skill_root) == package_root.resolve()

"""Run WorldGuard's own template-pack oracle from the bundled runtime."""

from __future__ import annotations

import json
import sys
from pathlib import Path


TARGET_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ROOT = (TARGET_ROOT / ".skillguard" / "runtime").resolve()
sys.path.insert(0, str(RUNTIME_ROOT))

from worldguard.template_packs import run_template_pack_contract  # noqa: E402


def main() -> int:
    module_path = Path(sys.modules[run_template_pack_contract.__module__].__file__).resolve()
    try:
        module_path.relative_to(RUNTIME_ROOT)
        bundled_runtime_current = True
    except ValueError:
        bundled_runtime_current = False

    report = run_template_pack_contract()
    payload = {
        "schema_version": "worldguard.skillguard_template_pack_check.v1",
        "ok": bool(bundled_runtime_current and report["ok"]),
        "bundled_runtime_current": bundled_runtime_current,
        "runtime_module": str(module_path),
        "manifest_count": report["manifest_count"],
        "base_pack_count": report["base_pack_count"],
        "candidate_pack_count": report["candidate_pack_count"],
        "registry_fingerprint": report["registry_fingerprint"],
        "projection_schema_version": report["projection_schema_version"],
        "projection_root_fields": report["projection_root_fields"],
        "observations": report["observations"],
        "failures": report["failures"],
        "claim_boundary": report["claim_boundary"],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

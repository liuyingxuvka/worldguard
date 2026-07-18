"""Run WorldGuard's own Guard-model oracle from the bundled formal runtime."""

from __future__ import annotations

import json
import sys
from pathlib import Path


TARGET_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ROOT = (TARGET_ROOT / "runtime").resolve()
sys.path.insert(0, str(RUNTIME_ROOT))

from worldguard.guard_model_contract import run_guard_model_contract  # noqa: E402


def main() -> int:
    module_path = Path(sys.modules[run_guard_model_contract.__module__].__file__).resolve()
    try:
        module_path.relative_to(RUNTIME_ROOT)
        bundled_runtime_current = True
    except ValueError:
        bundled_runtime_current = False

    report = run_guard_model_contract()
    payload = {
        "schema_version": "worldguard.skillguard_guard_model_check.v1",
        "ok": bool(bundled_runtime_current and report["ok"]),
        "bundled_runtime_current": bundled_runtime_current,
        "runtime_module": str(module_path),
        "purpose_count": report["purpose_count"],
        "native_good_count": report["native_good_count"],
        "protected_failure_count": report["protected_failure_count"],
        "known_bad_count": report["known_bad_count"],
        "candidate_binding_count": report["candidate_binding_count"],
        "universe_fingerprint": report["universe_fingerprint"],
        "failures": report["failures"],
        "claim_boundary": report["claim_boundary"],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

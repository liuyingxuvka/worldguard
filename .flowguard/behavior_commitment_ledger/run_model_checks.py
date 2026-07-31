"""Read-only FlowGuard regression runner for WorldGuard's behavior ledger."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from flowguard import review_behavior_commitment_ledger


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent))

from model import (  # noqa: E402
    build_primary_path_reports,
    build_worldguard_behavior_commitment_ledger,
)


def main() -> int:
    primary_reports = build_primary_path_reports()
    ledger_report = review_behavior_commitment_ledger(
        build_worldguard_behavior_commitment_ledger()
    )
    findings = [
        f"primary_path_{index}_blocked"
        for index, report in enumerate(primary_reports, start=1)
        if not report.ok
    ]
    if not ledger_report.ok:
        findings.append("behavior_commitment_ledger_blocked")
    print(
        json.dumps(
            {
                "artifact_kind": "worldguard_behavior_commitment_model_report",
                "status": "pass" if not findings else "blocked",
                "primary_path_count": len(primary_reports),
                "commitment_count": len(
                    build_worldguard_behavior_commitment_ledger().commitments
                ),
                "findings": findings,
                "claim_boundary": (
                    "This read-only runner proves current primary-path and behavior-ledger evidence only. "
                    "It does not execute tests, mutate receipts, install, publish, or release."
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())

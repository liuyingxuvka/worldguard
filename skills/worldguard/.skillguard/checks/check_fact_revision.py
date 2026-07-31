"""Run WorldGuard's bundled task-local fact-revision native scenarios."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
RUNTIME = ROOT / "skills" / "worldguard" / "runtime"
sys.path.insert(0, str(RUNTIME))

from worldguard.fact_revision import (  # noqa: E402
    FactPolarity,
    FactRevisionActivationRequest,
    FactRevisionEvidenceBinding,
    FactRevisionEvidenceKind,
    FactRevisionTransaction,
    FactStateExpectation,
    FactSupport,
    FactTruthState,
    FactWorldSnapshot,
    SignedFact,
    StrictFactRule,
    WorldFact,
    activate_fact_revision,
    preview_fact_revision,
)


def _base() -> FactWorldSnapshot:
    return FactWorldSnapshot(
        snapshot_id="native:fact-revision-base",
        facts=(
            WorldFact("fact:a"),
            WorldFact("fact:b"),
            WorldFact("fact:c"),
            WorldFact("fact:unrelated"),
        ),
        supports=(
            FactSupport(
                "support:a-positive",
                "fact:a",
                FactPolarity.POSITIVE,
                "source:native",
                "evidence:a",
            ),
            FactSupport(
                "support:b-positive",
                "fact:b",
                FactPolarity.POSITIVE,
                "source:native",
                "evidence:b",
            ),
        ),
        rules=(
            StrictFactRule(
                "rule:a-to-c",
                (SignedFact("fact:a", FactPolarity.POSITIVE),),
                SignedFact("fact:c", FactPolarity.POSITIVE),
                "source:native-rule",
                "evidence:native-rule",
            ),
        ),
    )


def main() -> int:
    base = _base()
    transaction = FactRevisionTransaction(
        transaction_id="transaction:native-both",
        base_fingerprint=base.fingerprint,
        additions=(
            FactSupport(
                "support:a-negative",
                "fact:a",
                FactPolarity.NEGATIVE,
                "source:counterevidence",
                "evidence:a-negative",
            ),
        ),
        preserved_fact_ids=("fact:b",),
        expected_terminal_deltas=(
            FactStateExpectation("fact:a", FactTruthState.BOTH),
        ),
    )
    preview = preview_fact_revision(base, transaction)
    state_by_fact = {item.fact_id: item.state for item in preview.after_states}
    evidence = tuple(
        FactRevisionEvidenceBinding(
            evidence_id=f"evidence:{kind.value}",
            kind=kind,
            status="pass",
            current=True,
            subject_fingerprint=preview.fingerprint,
        )
        for kind in FactRevisionEvidenceKind
    )
    activated = activate_fact_revision(
        base,
        transaction,
        FactRevisionActivationRequest(
            activation_id="activation:native",
            expected_preview_fingerprint=preview.fingerprint,
            acknowledged_contradiction_fact_ids=("fact:a",),
            evidence=evidence,
        ),
    )
    broken_transaction = FactRevisionTransaction(
        transaction_id="transaction:break-preservation",
        base_fingerprint=base.fingerprint,
        additions=(
            FactSupport(
                "support:b-negative",
                "fact:b",
                FactPolarity.NEGATIVE,
                "source:counterevidence",
                "evidence:b-negative",
            ),
        ),
        preserved_fact_ids=("fact:b",),
    )
    broken = preview_fact_revision(base, broken_transaction)
    checks = {
        "both_visible": state_by_fact.get("fact:a") == FactTruthState.BOTH,
        "no_explosion": (
            state_by_fact.get("fact:unrelated") == FactTruthState.NEITHER
        ),
        "base_immutable": all(
            item.support_id != "support:a-negative" for item in base.supports
        ),
        "activation_bound": activated.receipt.activated,
        "preservation_blocks": (
            broken.status == "blocked"
            and "preserved_fact_changed" in broken.finding_codes
        ),
    }
    payload = {
        "artifact_kind": "worldguard_fact_revision_native_check",
        "schema_version": "worldguard.fact_revision_native_check.v1",
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "preview_fingerprint": preview.fingerprint,
        "activation_receipt_fingerprint": activated.receipt.fingerprint,
        "claim_boundary": (
            "This native check covers bundled task-local four-valued revision "
            "semantics only; it does not establish factual truth or a Guard "
            "terminal result."
        ),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

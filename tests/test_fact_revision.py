from __future__ import annotations

import pytest

from worldguard.fact_revision import (
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
from worldguard.task_local_revision import TASK_LOCAL_REVISION_OWNER_ID


def _base() -> FactWorldSnapshot:
    return FactWorldSnapshot(
        snapshot_id="world:accepted-v1",
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
                "source:observation",
                "evidence:a",
            ),
            FactSupport(
                "support:b-positive",
                "fact:b",
                FactPolarity.POSITIVE,
                "source:observation",
                "evidence:b",
            ),
        ),
        rules=(
            StrictFactRule(
                rule_id="rule:a-implies-c",
                antecedents=(
                    SignedFact("fact:a", FactPolarity.POSITIVE),
                ),
                consequent=SignedFact(
                    "fact:c",
                    FactPolarity.POSITIVE,
                ),
                source_id="source:strict-rule",
                evidence_id="evidence:rule-a-c",
            ),
        ),
    )


def _transaction(**kwargs) -> FactRevisionTransaction:
    return FactRevisionTransaction(
        task_id="task-1",
        task_local_owner_id=TASK_LOCAL_REVISION_OWNER_ID,
        iteration=0,
        predecessor_iteration_fingerprint="root",
        **kwargs,
    )


def _state(preview, fact_id: str) -> FactTruthState:
    return next(
        item.state for item in preview.after_states if item.fact_id == fact_id
    )


def test_positive_and_negative_support_yield_both_without_explosion() -> None:
    base = _base()
    transaction = _transaction(
        transaction_id="revision:add-negative-a",
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
        expected_terminal_deltas=(
            FactStateExpectation("fact:a", FactTruthState.BOTH),
        ),
    )
    preview = preview_fact_revision(base, transaction)
    assert preview.status == "ready"
    assert _state(preview, "fact:a") == FactTruthState.BOTH
    assert _state(preview, "fact:unrelated") == FactTruthState.NEITHER
    assert preview.contradiction_fact_ids == ("fact:a",)
    assert base.fingerprint == transaction.base_fingerprint
    assert all(
        support.support_id != "support:a-negative"
        for support in base.supports
    )


def test_retraction_recomputes_strict_closure_and_preserves_independent_fact() -> None:
    base = _base()
    transaction = _transaction(
        transaction_id="revision:retract-a",
        base_fingerprint=base.fingerprint,
        retraction_support_ids=("support:a-positive",),
        preserved_fact_ids=("fact:b",),
        expected_terminal_deltas=(
            FactStateExpectation("fact:a", FactTruthState.NEITHER),
            FactStateExpectation("fact:c", FactTruthState.NEITHER),
        ),
    )
    preview = preview_fact_revision(base, transaction)
    assert preview.status == "ready"
    assert _state(preview, "fact:a") == FactTruthState.NEITHER
    assert _state(preview, "fact:c") == FactTruthState.NEITHER
    assert _state(preview, "fact:b") == FactTruthState.TRUE
    assert preview.changed_preserved_fact_ids == ()


def test_preserved_fact_change_blocks_with_support_delta() -> None:
    base = _base()
    transaction = _transaction(
        transaction_id="revision:break-preservation",
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
    preview = preview_fact_revision(base, transaction)
    assert preview.status == "blocked"
    assert preview.changed_preserved_fact_ids == ("fact:b",)
    assert "preserved_fact_changed" in preview.finding_codes
    delta = next(item for item in preview.deltas if item.fact_id == "fact:b")
    assert delta.changed_support_ids == ("support:b-negative",)


def test_stale_base_fingerprint_blocks_preview() -> None:
    base = _base()
    old_transaction = _transaction(
        transaction_id="revision:stale",
        base_fingerprint=base.fingerprint,
    )
    changed_base = FactWorldSnapshot(
        snapshot_id="world:accepted-v2",
        facts=base.facts,
        supports=(
            *base.supports,
            FactSupport(
                "support:unrelated-positive",
                "fact:unrelated",
                FactPolarity.POSITIVE,
                "source:new",
                "evidence:new",
            ),
        ),
        rules=base.rules,
    )
    preview = preview_fact_revision(changed_base, old_transaction)
    assert preview.status == "blocked"
    assert "stale_base_fingerprint" in preview.finding_codes


def test_activation_requires_current_regression_and_holdout_evidence() -> None:
    base = _base()
    transaction = _transaction(
        transaction_id="revision:activate-both",
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
    result = activate_fact_revision(
        base,
        transaction,
        FactRevisionActivationRequest(
            activation_id="activation:one",
            task_id="task-1",
            task_local_owner_id=TASK_LOCAL_REVISION_OWNER_ID,
            expected_preview_fingerprint=preview.fingerprint,
            expected_candidate_model_fingerprint=preview.candidate_snapshot.fingerprint,
            acknowledged_contradiction_fact_ids=("fact:a",),
            evidence=evidence,
        ),
    )
    assert result.receipt.status == "activated"
    assert result.receipt.activated is True
    assert result.activated_snapshot is not None
    assert result.receipt.contradiction_fact_ids == ("fact:a",)
    assert result.receipt.terminal_reason == "task_local_revalidation_required"
    assert result.receipt.revalidation_required is True
    assert result.receipt.task_local_owner_id == TASK_LOCAL_REVISION_OWNER_ID


def test_missing_holdout_evidence_keeps_activation_blocked() -> None:
    base = _base()
    transaction = _transaction(
        transaction_id="revision:missing-holdout",
        base_fingerprint=base.fingerprint,
    )
    preview = preview_fact_revision(base, transaction)
    result = activate_fact_revision(
        base,
        transaction,
        FactRevisionActivationRequest(
            activation_id="activation:blocked",
            task_id="task-1",
            task_local_owner_id=TASK_LOCAL_REVISION_OWNER_ID,
            expected_preview_fingerprint=preview.fingerprint,
            expected_candidate_model_fingerprint=preview.candidate_snapshot.fingerprint,
            acknowledged_contradiction_fact_ids=(),
            evidence=(
                FactRevisionEvidenceBinding(
                    evidence_id="evidence:regression",
                    kind=FactRevisionEvidenceKind.REGRESSION,
                    status="pass",
                    current=True,
                    subject_fingerprint=preview.fingerprint,
                ),
            ),
        ),
    )
    assert result.receipt.status == "blocked"
    assert result.activated_snapshot is None
    assert "missing_holdout_evidence" in result.receipt.finding_codes


def test_duplicate_fact_evidence_kind_cannot_substitute_for_exact_pair() -> None:
    base = _base()
    transaction = _transaction(
        transaction_id="revision:duplicate-regression",
        base_fingerprint=base.fingerprint,
    )
    preview = preview_fact_revision(base, transaction)
    evidence = (
        FactRevisionEvidenceBinding(
            evidence_id="evidence:regression-one",
            kind=FactRevisionEvidenceKind.REGRESSION,
            status="pass",
            current=True,
            subject_fingerprint=preview.fingerprint,
        ),
        FactRevisionEvidenceBinding(
            evidence_id="evidence:regression-two",
            kind=FactRevisionEvidenceKind.REGRESSION,
            status="pass",
            current=True,
            subject_fingerprint=preview.fingerprint,
        ),
        FactRevisionEvidenceBinding(
            evidence_id="evidence:holdout",
            kind=FactRevisionEvidenceKind.HOLDOUT,
            status="pass",
            current=True,
            subject_fingerprint=preview.fingerprint,
        ),
    )
    result = activate_fact_revision(
        base,
        transaction,
        FactRevisionActivationRequest(
            activation_id="activation:duplicate-regression",
            task_id="task-1",
            task_local_owner_id=TASK_LOCAL_REVISION_OWNER_ID,
            expected_preview_fingerprint=preview.fingerprint,
            expected_candidate_model_fingerprint=preview.candidate_snapshot.fingerprint,
            acknowledged_contradiction_fact_ids=(),
            evidence=evidence,
        ),
    )
    assert result.receipt.status == "blocked"
    assert "duplicate_regression_evidence" in result.receipt.finding_codes


def test_prior_activation_transaction_id_blocks_duplicate_activation() -> None:
    base = _base()
    transaction = _transaction(
        transaction_id="revision:already-used",
        base_fingerprint=base.fingerprint,
    )
    preview = preview_fact_revision(base, transaction)
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
    result = activate_fact_revision(
        base,
        transaction,
        FactRevisionActivationRequest(
            activation_id="activation:duplicate",
            task_id="task-1",
            task_local_owner_id=TASK_LOCAL_REVISION_OWNER_ID,
            expected_preview_fingerprint=preview.fingerprint,
            expected_candidate_model_fingerprint=preview.candidate_snapshot.fingerprint,
            acknowledged_contradiction_fact_ids=(),
            evidence=evidence,
            prior_activation_transaction_ids=("revision:already-used",),
        ),
    )
    assert result.receipt.status == "blocked"
    assert "transaction_already_activated" in result.receipt.finding_codes


def test_fact_activation_cannot_claim_model_closed_for_task() -> None:
    base = _base()
    transaction = _transaction(
        transaction_id="revision:no-direct-close",
        base_fingerprint=base.fingerprint,
    )
    preview = preview_fact_revision(base, transaction)
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
    result = activate_fact_revision(
        base,
        transaction,
        FactRevisionActivationRequest(
            activation_id="activation:no-direct-close",
            task_id="task-1",
            task_local_owner_id=TASK_LOCAL_REVISION_OWNER_ID,
            expected_preview_fingerprint=preview.fingerprint,
            expected_candidate_model_fingerprint=preview.candidate_snapshot.fingerprint,
            acknowledged_contradiction_fact_ids=(),
            evidence=evidence,
        ),
    )
    assert result.receipt.activated is True
    assert result.receipt.terminal_reason == "task_local_revalidation_required"
    assert "model_closed_for_task" not in result.receipt.to_dict().values()


def test_legacy_fact_transaction_shape_is_rejected() -> None:
    base = _base()
    with pytest.raises(ValueError, match="unknown fields|missing current fields"):
        FactRevisionTransaction.from_dict(
            {
                "transaction_id": "revision:legacy",
                "base_fingerprint": base.fingerprint,
                "additions": [],
                "retraction_support_ids": [],
                "preserved_fact_ids": [],
                "expected_terminal_deltas": [],
                "task_id": "task-1",
                "iteration": 0,
                "max_iterations": 8,
                "remaining_predictive_gap_ids": [],
                "next_actions": [],
                "terminal_reason": "model_closed_for_task",
            }
        )

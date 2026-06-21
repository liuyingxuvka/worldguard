import pytest

from worldguard.ledgers import LedgerEntry, ledger_entry


def test_ledger_entry_defaults_read_only():
    entry = ledger_entry(
        run_id="run",
        claim_id="claim",
        guard="EventGuard",
        channel="event",
        status_impact="supports_pass",
    )

    assert entry.read_only_for_downstream is True
    assert entry.to_dict()["channel"] == "event"


def test_ledger_rejects_mutable_downstream_entry():
    with pytest.raises(ValueError, match="read-only"):
        LedgerEntry(
            ledger_entry_id="id",
            run_id="run",
            claim_id="claim",
            guard="EventGuard",
            channel="event",
            status_impact="supports_pass",
            read_only_for_downstream=False,
        )

from enum import StrEnum
from typing import Iterable


class GuardStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    GAP = "GAP"
    BOUNDARY_EXCEEDED = "BOUNDARY_EXCEEDED"


def coerce_status(value: str | GuardStatus) -> GuardStatus:
    if isinstance(value, GuardStatus):
        return value
    return GuardStatus(str(value))


def aggregate_statuses(statuses: Iterable[str | GuardStatus]) -> GuardStatus:
    normalized = [coerce_status(status) for status in statuses]
    if any(status == GuardStatus.FAIL for status in normalized):
        return GuardStatus.FAIL
    if any(status == GuardStatus.GAP for status in normalized):
        return GuardStatus.GAP
    if any(status == GuardStatus.BOUNDARY_EXCEEDED for status in normalized):
        return GuardStatus.BOUNDARY_EXCEEDED
    if normalized and all(status == GuardStatus.PASS for status in normalized):
        return GuardStatus.PASS
    return GuardStatus.GAP

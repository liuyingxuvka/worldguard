"""WorldGuard public runtime API."""

from .contracts import GuardContract
from .kernel import run_worldguard
from .reports import GuardResult, GuardedReport
from .status import GuardStatus

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "GuardContract",
    "GuardResult",
    "GuardStatus",
    "GuardedReport",
    "run_worldguard",
]

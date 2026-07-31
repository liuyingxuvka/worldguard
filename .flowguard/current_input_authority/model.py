"""Canonical manifest owner for WorldGuard's current-input semantic model."""

from __future__ import annotations

from pathlib import Path
import sys


FLOWGUARD_MODEL_MARKER = "flowguard-executable-model"
IMPLEMENTATION_ROOT = Path(__file__).resolve().parent.parent
if str(IMPLEMENTATION_ROOT) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION_ROOT))

from semantic_rollout_model import (  # noqa: E402,F401
    FieldLifecycleBlock,
    FieldState,
    RolloutState,
    SemanticRolloutBlock,
    run_checks,
)


__all__ = [
    "FieldLifecycleBlock",
    "FieldState",
    "RolloutState",
    "SemanticRolloutBlock",
    "run_checks",
]

"""Canonical manifest owner for WorldGuard's template-selection model."""

from __future__ import annotations

from pathlib import Path
import sys


FLOWGUARD_MODEL_MARKER = "flowguard-executable-model"
IMPLEMENTATION_ROOT = Path(__file__).resolve().parent.parent
if str(IMPLEMENTATION_ROOT) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION_ROOT))

from worldguard_template_pack_builder import (  # noqa: E402,F401
    INVARIANTS,
    State,
    build_workflow,
    review_template_pack_builder,
)


__all__ = [
    "INVARIANTS",
    "State",
    "build_workflow",
    "review_template_pack_builder",
]

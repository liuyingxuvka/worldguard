"""Repository-side loader for the portable skill-local FlowGuard export."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


FLOWGUARD_MODEL_MARKER = "flowguard-executable-model"
_MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "worldguard"
    / ".skillguard"
    / "contract_model.py"
)


def export_contract_model() -> dict[str, Any]:
    spec = importlib.util.spec_from_file_location(
        "worldguard_skillguard_contract_model", _MODEL_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load portable contract model: {_MODEL_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.export_contract_model()


if __name__ == "__main__":
    import json

    print(json.dumps(export_contract_model(), ensure_ascii=False, indent=2, sort_keys=True))

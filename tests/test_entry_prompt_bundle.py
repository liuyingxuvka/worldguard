from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "worldguard" / "scripts" / "check_entry_prompt_bundle.py"
SPEC = importlib.util.spec_from_file_location("worldguard_prompt_bundle", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
SKILL_ROOT = ROOT / "skills" / "worldguard"


def _compose(**facts):
    return MODULE.compose_prompt_bundle(SKILL_ROOT, facts)


def test_bounded_event_bundle_stays_light():
    report = _compose(
        task_shape="unit_contract",
        requested_semantics=["event"],
        target_guards=["EventGuard"],
    )

    assert report["ok"], report["findings"]
    assert report["derived_guard_ids"] == ["EventGuard"]
    assert "references/task-local-model-deepening.md" not in report["bundle_paths"]
    assert "references/model-mesh.md" not in report["bundle_paths"]
    assert "references/template-packs.md" not in report["bundle_paths"]


def test_predictive_bundle_derives_event_and_causal_and_loads_deepening():
    report = _compose(
        task_shape="unit_contract",
        requested_semantics=["prediction"],
        predictive_intent=True,
        target_guards=["EventGuard"],
    )

    assert report["ok"], report["findings"]
    assert report["derived_guard_ids"] == ["EventGuard", "CausalGuard"]
    assert report["caller_target_guard_omissions"] == ["CausalGuard"]
    assert "references/task-local-model-deepening.md" in report["bundle_paths"]


def test_mesh_handoff_loads_only_mesh_handoff_and_guard_material():
    report = _compose(
        task_shape="model_mesh",
        requested_semantics=["agent", "normative"],
        handoff_present=True,
    )

    assert report["ok"], report["findings"]
    assert report["derived_guard_ids"] == ["AgentGuard", "NormGuard"]
    assert "references/model-mesh.md" in report["bundle_paths"]
    assert "references/handoff-contracts.md" in report["bundle_paths"]
    assert "references/task-local-model-deepening.md" not in report["bundle_paths"]


def test_template_shape_does_not_invent_guard_routes():
    report = _compose(task_shape="template_pack", requested_semantics=[])

    assert report["ok"], report["findings"]
    assert report["derived_guard_ids"] == []
    assert "references/template-packs.md" in report["bundle_paths"]
    assert "references/guard-model-contract.md" not in report["bundle_paths"]


def test_shape_ambiguity_blocks_without_guessing():
    report = _compose(
        task_shape_candidates=["unit_contract", "model_mesh"],
        requested_semantics=["event"],
    )

    assert not report["ok"]
    assert "task_shape_not_exact" in {item["code"] for item in report["findings"]}


def test_unmapped_semantics_block():
    report = _compose(task_shape="unit_contract", requested_semantics=["quantum_oracle"])

    assert not report["ok"]
    assert "claim_semantics_unmapped" in {item["code"] for item in report["findings"]}


def test_missing_mandatory_reference_blocks(tmp_path: Path):
    topology = json.loads(
        (SKILL_ROOT / "references" / "internal-guard-routes.json").read_text(
            encoding="utf-8"
        )
    )
    topology["task_shapes"][0]["reference_path"] = "references/missing.md"
    topology_path = tmp_path / "routes.json"
    topology_path.write_text(json.dumps(topology), encoding="utf-8")

    report = MODULE.compose_prompt_bundle(
        SKILL_ROOT,
        {"task_shape": "unit_contract", "requested_semantics": ["event"]},
        topology_path=topology_path,
    )

    assert not report["ok"]
    assert any(
        item["code"] == "mandatory_prompt_reference_missing"
        and item.get("path") == "references/missing.md"
        for item in report["findings"]
    )


def test_prompt_budget_blocks_after_mandatory_paths_are_composed(tmp_path: Path):
    topology = json.loads(
        (SKILL_ROOT / "references" / "internal-guard-routes.json").read_text(
            encoding="utf-8"
        )
    )
    topology["prompt_budget"]["selected_bundle_max_characters"] = 1
    topology_path = tmp_path / "routes.json"
    topology_path.write_text(json.dumps(topology), encoding="utf-8")

    report = MODULE.compose_prompt_bundle(
        SKILL_ROOT,
        {"task_shape": "unit_contract", "requested_semantics": ["event"]},
        topology_path=topology_path,
    )

    assert not report["ok"]
    assert "selected_prompt_bundle_budget_exceeded" in {
        item["code"] for item in report["findings"]
    }

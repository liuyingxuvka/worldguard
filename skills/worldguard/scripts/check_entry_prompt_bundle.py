#!/usr/bin/env python3
"""Compose and validate one WorldGuard selected prompt bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PREDICTIVE_SEMANTICS = {"prediction", "predictive", "forecast", "future_outcome"}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def compose_prompt_bundle(
    skill_root: Path,
    facts: dict[str, Any],
    *,
    topology_path: Path | None = None,
) -> dict[str, Any]:
    skill_root = skill_root.resolve()
    topology_path = topology_path or skill_root / "references" / "internal-guard-routes.json"
    topology = _load_json(topology_path)
    findings: list[dict[str, Any]] = []

    candidates = facts.get("task_shape_candidates")
    if candidates is None:
        direct_shape = facts.get("task_shape")
        candidates = [direct_shape] if isinstance(direct_shape, str) and direct_shape else []
    if not isinstance(candidates, list) or any(not isinstance(item, str) for item in candidates):
        candidates = []
        findings.append({"code": "task_shape_candidates_invalid"})
    candidates = list(dict.fromkeys(item.strip() for item in candidates if item.strip()))
    shape_rows = {
        row["shape_id"]: row
        for row in topology.get("task_shapes", [])
        if isinstance(row, dict) and isinstance(row.get("shape_id"), str)
    }
    if len(candidates) != 1:
        findings.append(
            {
                "code": "task_shape_not_exact",
                "candidates": candidates,
                "missing_discriminator": "unit_contract|model_mesh|task_local_revision|template_pack",
            }
        )
        selected_shape = ""
    else:
        selected_shape = candidates[0]
        if selected_shape not in shape_rows:
            findings.append(
                {"code": "task_shape_unsupported", "task_shape": selected_shape}
            )

    semantics_value = facts.get("requested_semantics", [])
    if isinstance(semantics_value, str):
        semantics_value = [semantics_value]
    if not isinstance(semantics_value, list) or any(
        not isinstance(item, str) for item in semantics_value
    ):
        semantics_value = []
        findings.append({"code": "requested_semantics_invalid"})
    semantics = tuple(
        dict.fromkeys(item.strip().lower() for item in semantics_value if item.strip())
    )

    routes = [row for row in topology.get("routes", []) if isinstance(row, dict)]
    semantics_to_guards: dict[str, list[str]] = {}
    for row in routes:
        guard_id = str(row.get("guard_id", ""))
        for semantic in row.get("applicability_semantics", []):
            semantics_to_guards.setdefault(str(semantic), []).append(guard_id)
    unmapped = sorted(semantic for semantic in semantics if semantic not in semantics_to_guards)
    if unmapped and selected_shape != "template_pack":
        findings.append({"code": "claim_semantics_unmapped", "semantics": unmapped})
    guards = tuple(
        dict.fromkeys(
            guard
            for semantic in semantics
            for guard in semantics_to_guards.get(semantic, [])
        )
    )
    if selected_shape in {"unit_contract", "model_mesh", "task_local_revision"} and not guards:
        findings.append({"code": "derived_guard_set_empty"})

    caller_guards_value = facts.get("target_guards", [])
    if isinstance(caller_guards_value, str):
        caller_guards_value = [caller_guards_value]
    caller_guards = {
        str(item) for item in caller_guards_value if isinstance(item, str) and item
    }
    omitted = sorted(set(guards) - caller_guards) if caller_guards else []

    bundle_paths: list[str] = ["SKILL.md", "references/entry-routing.md"]
    if selected_shape in shape_rows:
        bundle_paths.append(str(shape_rows[selected_shape].get("reference_path", "")))
    rows_by_guard = {str(row.get("guard_id", "")): row for row in routes}
    for guard in guards:
        row = rows_by_guard.get(guard, {})
        bundle_paths.append(str(row.get("reference_path", "")))

    predictive = bool(PREDICTIVE_SEMANTICS.intersection(semantics)) or bool(
        facts.get("predictive_intent")
    )
    if selected_shape == "task_local_revision" or predictive:
        bundle_paths.append("references/task-local-model-deepening.md")
    if selected_shape == "model_mesh" and facts.get("handoff_present"):
        bundle_paths.append("references/handoff-contracts.md")
    if facts.get("fact_revision_requested"):
        bundle_paths.append("references/fact-revision.md")
    if facts.get("model_authority_requested"):
        bundle_paths.append("references/model-authority.md")
    if facts.get("final_reporting_requested"):
        bundle_paths.append("references/closure-report.md")
    bundle_paths = list(dict.fromkeys(path for path in bundle_paths if path))

    bundle_characters = 0
    for relative in bundle_paths:
        path = skill_root / relative
        if not path.is_file():
            findings.append({"code": "mandatory_prompt_reference_missing", "path": relative})
            continue
        bundle_characters += len(path.read_text(encoding="utf-8"))
    budget = topology.get("prompt_budget", {})
    selected_max = budget.get("selected_bundle_max_characters")
    headroom = budget.get("minimum_reasoning_headroom_characters")
    if not isinstance(selected_max, int) or bundle_characters > selected_max:
        findings.append(
            {
                "code": "selected_prompt_bundle_budget_exceeded",
                "observed": bundle_characters,
                "maximum": selected_max,
            }
        )
    if not isinstance(headroom, int) or headroom < 12000:
        findings.append(
            {
                "code": "prompt_reasoning_headroom_too_small",
                "observed": headroom,
                "minimum": 12000,
            }
        )

    return {
        "schema_version": "worldguard.prompt_bundle_check.v1",
        "status": "pass" if not findings else "blocked",
        "ok": not findings,
        "selected_task_shape": selected_shape,
        "requested_semantics": list(semantics),
        "derived_guard_ids": list(guards),
        "caller_target_guard_omissions": omitted,
        "bundle_paths": bundle_paths,
        "bundle_characters": bundle_characters,
        "reasoning_headroom_characters": headroom,
        "findings": findings,
        "claim_boundary": (
            "This check proves only deterministic task-shape, complete claim-derived Guard, "
            "reference-load, and prompt-budget projection. It does not execute Guard semantics "
            "or prove factual truth, installation, Git, tag, or release."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-root", default="skills/worldguard")
    parser.add_argument("--facts", required=True)
    parser.add_argument("--topology")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = compose_prompt_bundle(
        Path(args.skill_root),
        _load_json(Path(args.facts)),
        topology_path=Path(args.topology) if args.topology else None,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"status={report['status']} findings={len(report['findings'])}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())


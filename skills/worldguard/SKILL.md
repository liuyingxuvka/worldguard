---
name: worldguard
description: Model-first world-claim and model-mesh guard checks for WorldGuard. Use when Codex needs to assess whether a claim about events, agents, spaces, resources, causality, conflicts, or norms is supported by an explicit model, contradicted by it, missing required inputs, or outside the modeled boundary; also use when creating or auditing GuardContract, ModelMeshContract, GuardResult, MeshReport, ledger, counterexample, handoff, authority, freshness, or toy-fixture replay artifacts.
---

# WorldGuard

Use this skill to keep world-claim analysis contract-first, mesh-aware, and evidence-preserving.

## Workflow

1. Decide the check shape before giving a conclusion:
   - Use `GuardContract` for one claim checked against one explicit world model.
   - Use `ModelMeshContract` when multiple models, versions, parent/child boundaries, handoffs, or downstream consumers are involved.
2. For a unit check, build or inspect a structured `GuardContract`, select only the Guards named by `claim.target_guards`, then run the local package when a contract file or packaged example is available:

   ```powershell
   python "$env:USERPROFILE\.codex\skills\worldguard\scripts\run_worldguard_check.py" --example fuel_cell
   ```

   or:

   ```powershell
   python "$env:USERPROFILE\.codex\skills\worldguard\scripts\run_worldguard_check.py" --contract <path>
   ```

3. For a mesh check, build or inspect a structured `ModelMeshContract`, then inspect:
   - model nodes and their authority boundaries;
   - model edges and handoff contracts;
   - stale/current source status;
   - forbidden downstream use;
   - dependency cycles;
   - child `GuardedReport` statuses and ledgers.
4. Run the local package when a mesh file is available:

   ```powershell
   python "$env:USERPROFILE\.codex\skills\worldguard\scripts\run_worldguard_check.py" --mesh <path>
   ```

5. Report `PASS`, `FAIL`, `GAP`, or `BOUNDARY_EXCEEDED` without collapsing non-pass statuses.
6. Preserve ledgers, missing slots, boundary traces, counterexamples, handoff findings, stale-source findings, authority findings, and cycle findings in the answer.

## Hard Rules

- Do not give a narrative-only PASS.
- Do not use a general prompt checklist in place of EventGuard, AgentGuard, SpaceGuard, ResourceGuard, CausalGuard, ConflictGuard, or NormGuard.
- Do not report a whole mesh as `PASS` merely because one child model or one Guard passed.
- Missing input means `GAP`, not low-confidence PASS.
- Unsupported semantics mean `BOUNDARY_EXCEEDED`, not ordinary FAIL.
- Non-pass results must include missing slots, errors, boundary traces, or counterexamples.
- Kernel handoff is read-only. Downstream Guards may not fill upstream missing slots, mutate upstream status, delete counterexamples, or convert GAP to PASS.
- Mesh handoff is read-only. Downstream model nodes may not mutate upstream node reports, fill upstream gaps, delete upstream counterexamples, or override upstream boundary findings.
- A model may only support claims inside its declared authority. Authority overreach means `BOUNDARY_EXCEEDED`.
- A stale source model cannot support a current downstream claim when the handoff requires current source evidence.
- Forbidden downstream use means `FAIL` with a concrete handoff finding.
- Dependency cycles must be reported as mesh `FAIL`.
- WorldGuard core must stay domain-neutral. Do not add chapter, scene, paragraph, quest, or other adapter-specific fields to core contracts.
- Fuel-cell examples are toy fixtures only. Never claim real fuel-cell physics, legal compliance, safety certification, deployment readiness, market truth, or strategy proof.

## References

- Read `references/worldguard-contracts.md` when constructing or validating contract/result/ledger fields.
- Read `references/guard-boundaries.md` when deciding which Guard owns a claim part.
- Read `references/model-mesh.md` when constructing or validating mesh nodes, edges, snapshots, and mesh reports.
- Read `references/model-authority.md` when deciding whether a model node is being used inside its authority.
- Read `references/handoff-contracts.md` when deciding whether one model may consume another model's output.
- Read `references/closure-report.md` before claiming a multi-model check is complete.

## Output Shape

Return:

- conclusion status;
- `GuardContract` or `ModelMeshContract` summary;
- per-Guard results;
- per-node mesh results, when applicable;
- non-pass evidence;
- ledger evidence;
- mesh findings, when applicable;
- missing model fields, if any;
- commands run or reason local runtime was not run.


<!-- BEGIN SKILLGUARD CONTRACT LAYER -->
## Purpose

Use this skill for its declared guard_investigation workflow while binding each run to a route, evidence, checks, and a bounded completion claim.

## Entrypoint Scope

The entrypoint covers the installed worldguard skill and the local materials explicitly routed by its instructions. It does not expand to unrelated repositories, private files, external services, publication, or release claims unless the user request and skill workflow explicitly include them.

## Local Material Routing

Resolve local materials from the active workspace, this skill directory, user-provided files, or explicitly configured project paths. Treat private machine paths as local-only inputs and keep public-facing instructions portable.

## Entrypoint Acceptance Map

A valid run selects one declared route, follows the phase order, records direct evidence, runs required checks, reports blockers and failures, and closes only inside the claim boundary. Available routes: claim or source intake, evidence model, gap review, closure.

## Use When

Use when the user request matches the worldguard activation boundary and needs this skill's governed workflow, source material, checks, or handoff behavior.

## Do Not Use When

Do not use when the task is outside this skill's domain, when required local materials are unavailable, when another more specific skill owns the request, or when the user asks only for a tiny direct answer.

## Required Workflow

Select the route, inspect local materials, perform the work in phase order, collect direct evidence, run the required checks, fix failures, and only then report progress or completion.

## Hard Gates

Do not skip phases, do not replace required evidence with prose, do not treat stale reports as current, do not weaken validation to pass, and do not claim completion when blockers remain.

## Output Requirements

When reporting, include evidence, failures, blockers, skipped_checks with reasons, residual_risk, and claim_boundary. State clearly what was checked, what was not checked, and what remains blocked or uncertain.

## SkillGuard Maintenance

Keep the `.skillguard` control root, work contract, check manifest, check scripts, evidence records, and progress ledger current. Re-run SkillGuard checks after changing this entrypoint, route behavior, evidence rules, or closure wording.

<!-- END SKILLGUARD CONTRACT LAYER -->

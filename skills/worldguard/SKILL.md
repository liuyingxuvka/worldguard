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
   python C:\Users\liu_y\.codex\skills\worldguard\scripts\run_worldguard_check.py --example fuel_cell
   ```

   or:

   ```powershell
   python C:\Users\liu_y\.codex\skills\worldguard\scripts\run_worldguard_check.py --contract <path>
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
   python C:\Users\liu_y\.codex\skills\worldguard\scripts\run_worldguard_check.py --mesh <path>
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

---
name: worldguard
description: Model-first world-claim guard checks for WorldGuard. Use when Codex needs to assess whether a claim about events, agents, spaces, resources, causality, conflicts, or norms is supported by an explicit model, contradicted by it, missing required inputs, or outside the modeled boundary; also use when creating or auditing GuardContract, GuardResult, ledger, counterexample, or toy-fixture replay artifacts.
---

# WorldGuard

Use this skill to keep world-claim analysis contract-first and evidence-preserving.

## Workflow

1. Build or inspect a structured `GuardContract` before giving a conclusion.
2. Select only the Guards named by `claim.target_guards`.
3. Run the local package when a contract file or packaged example is available:

   ```powershell
   python C:\Users\liu_y\.codex\skills\worldguard\scripts\run_worldguard_check.py --example fuel_cell
   ```

   or:

   ```powershell
   python C:\Users\liu_y\.codex\skills\worldguard\scripts\run_worldguard_check.py --contract <path>
   ```

4. Report `PASS`, `FAIL`, `GAP`, or `BOUNDARY_EXCEEDED` without collapsing non-pass statuses.
5. Preserve ledgers, missing slots, boundary traces, and counterexamples in the answer.

## Hard Rules

- Do not give a narrative-only PASS.
- Do not use a general prompt checklist in place of EventGuard, AgentGuard, SpaceGuard, ResourceGuard, CausalGuard, ConflictGuard, or NormGuard.
- Missing input means `GAP`, not low-confidence PASS.
- Unsupported semantics mean `BOUNDARY_EXCEEDED`, not ordinary FAIL.
- Non-pass results must include missing slots, errors, boundary traces, or counterexamples.
- Kernel handoff is read-only. Downstream Guards may not fill upstream missing slots, mutate upstream status, delete counterexamples, or convert GAP to PASS.
- Fuel-cell examples are toy fixtures only. Never claim real fuel-cell physics, legal compliance, safety certification, deployment readiness, market truth, or strategy proof.

## References

- Read `references/worldguard-contracts.md` when constructing or validating contract/result/ledger fields.
- Read `references/guard-boundaries.md` when deciding which Guard owns a claim part.

## Output Shape

Return:

- conclusion status;
- GuardContract summary;
- per-Guard results;
- non-pass evidence;
- ledger evidence;
- missing model fields, if any;
- commands run or reason local runtime was not run.

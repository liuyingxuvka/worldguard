---
name: worldguard
description: Model-first checks for claims about events, agents, space, resources, causality, conflicts, norms, predictions, model meshes, task-local reality revision, or WorldGuard template packs. Use when a conclusion must be licensed by an explicit world model and visible evidence boundary.
---

# WorldGuard

## Purpose

Use WorldGuard to turn a world claim into an explicit, executable, evidence-preserving model check. It keeps one public skill and console while retaining seven complete internal Guard routes.

WorldGuard does not ask the AI whether it understands. Understanding is demonstrated only by a model that makes bounded predictions, exposes missing inputs and counterexamples, survives native checks and independent revalidation, and produces the exact terminal licensed by current evidence.

## Public boundary

`worldguard` is the sole installed skill and console. EventGuard, AgentGuard, SpaceGuard, ResourceGuard, CausalGuard, ConflictGuard, and NormGuard are internal routes, not child skills, aliases, alternate consoles, or fallbacks.

An internal failure never triggers another Guard as a retry. A multi-semantic claim may legitimately require several Guards; WorldGuard derives the complete set from structured claim semantics.

## Use when

- A claim about events, agents, space, resources, causality, conflict, or norms needs an explicit model and bounded result.
- A prediction, forecast, what-if, intervention, or counterfactual needs temporal depth, scenarios, holdouts, and current evidence.
- Several world models need ownership, freshness, handoff, dependency, or closure analysis.
- A task asks whether the current model matches later observation and should be revised within a finite purpose.
- A WorldGuard-owned template pack, contract, result, ledger, receipt, authority, or closure artifact must be built or audited.

## Do not use when

- The request asks only for unmodeled narrative judgment with no explicit model/evidence boundary.
- Another Guard or writer is expected to repair missing WorldGuard inputs or reinterpret its result.
- A toy fixture, structural pass, prompt check, or repository test is being treated as factual truth or future accuracy.
- The request is ordinary use of some unrelated Guard family.

## Minimum task facts

Before selecting work, extract typed facts and preserve their source spans:

- task-shape facts: unit contract, model mesh, task-local revision, or template pack;
- claim id/text, structured atoms or requested semantics, and predictive intent;
- concrete inputs for the selected shape and every derived Guard;
- explicit unavailable providers, unsupported boundaries, and desired claim scope.

Missing facts remain missing. Do not invent them, use a keyword score as authority, trust `claim.target_guards` to shrink coverage, or record an understanding level.

## Entry route

1. Read [references/entry-routing.md](references/entry-routing.md).
2. Select exactly one public task shape from typed facts:
   - `unit_contract` for one claim and one explicit world-model boundary;
   - `model_mesh` for multi-node authority, freshness, handoff, coverage, or closure;
   - `task_local_revision` for prediction/observation comparison and finite model revision;
   - `template_pack` for reusable WorldGuard scaffolding.
3. For unit, mesh, or task-local work, derive the complete Guard set with structured claim semantics. Prediction semantics intentionally require EventGuard and CausalGuard together.
4. Read the selected shape and Guard capsules in [references/internal-guard-routes.json](references/internal-guard-routes.json). Verify positive and forbidden conditions, required inputs, first native actions, reference paths, deepening triggers, and claim boundaries.
5. Load only the mandatory selected material. Missing mandatory material blocks; unrelated deep references stay unloaded.

Zero matching task shapes, several matching task shapes, unmapped semantics, incomplete derived Guard coverage, forbidden conditions, and missing inputs remain visible. Do not guess or fall back.

## Conditional material

- Unit contract: [references/worldguard-contracts.md](references/worldguard-contracts.md).
- Each derived Guard purpose/proof: [references/guard-model-contract.md](references/guard-model-contract.md); ownership boundaries: [references/guard-boundaries.md](references/guard-boundaries.md).
- Model mesh: [references/model-mesh.md](references/model-mesh.md); load [references/handoff-contracts.md](references/handoff-contracts.md) only for handoffs.
- Predictive intent, current predictive gaps, or task-local reality revision: [references/task-local-model-deepening.md](references/task-local-model-deepening.md).
- Fact-level support revision: [references/fact-revision.md](references/fact-revision.md).
- Reusable scaffolding: [references/template-packs.md](references/template-packs.md).
- Model authority replacement/audit: [references/model-authority.md](references/model-authority.md).
- Final reporting: [references/closure-report.md](references/closure-report.md).

## First native actions

For a unit contract, construct or inspect a current `GuardContract`, derive the complete Guard set, freeze one task-local purpose declaration per Guard, then execute each registered native runner and semantic executor. Run an available contract with:

```powershell
python "$env:USERPROFILE\.codex\skills\worldguard\scripts\run_worldguard_check.py" --contract <path>
```

For a model mesh, inspect the complete nodes, edges, owners, freshness, handoffs, expected semantic children, and structural/semantic/provider/rollout statuses before execution:

```powershell
python "$env:USERPROFILE\.codex\skills\worldguard\scripts\run_worldguard_check.py" --mesh <path>
```

For task-local or predictive work, freeze the prediction before new observation and follow the evidence-derived loop in `task-local-model-deepening.md`.

For a template pack, ask the target for its current native route receipt before consulting its catalog. Reconcile exactly zero, one, or many candidates; do not rank or guess.

## Terminals

Preserve `PASS`, `FAIL`, `GAP`, and `BOUNDARY_EXCEEDED` exactly. Structural status, semantic status, provider status, rollout status, predictive license, and task-local terminal remain separate facts.

- `PASS` requires current native execution inside the declared boundary.
- `FAIL` preserves the contradicted invariant/expectation and evidence.
- `GAP` names missing required model inputs, coverage, evidence, or derived Guards.
- `BOUNDARY_EXCEEDED` names the unsupported semantics and affected claims.

For task-local revision, preserve `progress_stalled`, `iteration_limit`, and `external_input_required`; only the same task-local owner may emit `model_closed_for_task` from zero current gaps plus current native depth and independent original/holdout revalidation.

## Hard gates

- No narrative-only `PASS` and no model self-rating.
- No child Guard skill, alias, fallback, or retry replacement.
- No caller-authored Guard subset, remaining-gap list, progress boolean, or PASS string as authority.
- No family fixture in place of a fresh task-model purpose declaration with task-local native known-good and one known-bad per selected failure.
- No whole-mesh `PASS` from one child or structural-only evidence.
- No predictive license from field presence, a single event, clustered timepoints, aggregate coverage that hides a shallow node/variable, or incomplete scenarios/holdouts/interventions/counterfactuals.
- No semantic provider skip hidden as pass.
- No template zero-match fallback, ambiguous winner, overlapping field ownership, unresolved placeholder, stale registry, or construction without target-native validation.
- No fact activation as task closure; it returns to the same owner for revalidation.
- No stale model authority or release/install claim from source tests alone.

## Output

Report:

- selected task shape and typed fact sources;
- complete derived Guard set and any unmapped/omitted semantics;
- loaded references and skipped references with reasons;
- each native action and exact terminal/status;
- missing inputs, gaps, counterexamples, stale evidence, provider state, and boundary findings;
- preserved contracts, ledgers, receipts, fingerprints, task-local lineage, and template identities when used;
- what did not run and why;
- a claim boundary separating model evidence, factual truth, installation, Git/tag, and release.

Prompt routing proves only that WorldGuard loaded the right current instructions. Domain execution and current immutable evidence are still required for every substantive claim.

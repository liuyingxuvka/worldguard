---
name: worldguard
description: Model-first world-claim, what-if, prediction-boundary, model-mesh, and validating template-pack checks for WorldGuard. Use when Codex needs to construct, simulate, or assess whether a claim about events, agents, spaces, resources, causality, conflicts, or norms is supported by an explicit model, contradicted by it, missing required inputs, or outside the modeled boundary; also use when creating or auditing GuardContract, ModelMeshContract, template-pack manifests, deterministic 0/1/many template selection, field composition, instance fingerprints, GuardResult, MeshReport, semantic rollout status, native depth receipt, ledger, counterexample, handoff, authority, freshness, or toy-fixture replay artifacts.
---

# WorldGuard

## Purpose

Use this skill to keep world-claim analysis contract-first, mesh-aware, and evidence-preserving.

## Entrypoint Scope

Use `worldguard` as the sole installed skill and `worldguard` as the sole
console. EventGuard, AgentGuard, SpaceGuard, ResourceGuard, CausalGuard,
ConflictGuard, and NormGuard are seven complete internal routes. Do not install
or invoke them as child skills, aliases, alternate consoles, or fallbacks.

Each internal route preserves one claim-derived expectation boundary, its
native Guard runner, a `GuardResult` response, purpose-contract verification, a
WorldGuard semantic executor, and the visible terminal statuses `PASS`, `FAIL`,
`GAP`, and `BOUNDARY_EXCEEDED`. EventGuard and CausalGuard participate in
predictive closure only through the current predictive-depth gates. The other
five Guards provide bounded expectation and constraint evidence; their `PASS`
does not independently license a future forecast.

Read
[references/internal-guard-routes.json](references/internal-guard-routes.json)
when auditing route ownership or entrypoint topology. Do not use an internal
route failure as a trigger to try another Guard.

## Local Material Routing

Read `references/worldguard-contracts.md` for contract/result/ledger fields,
`references/guard-boundaries.md` for Guard ownership,
`references/model-mesh.md` and `references/handoff-contracts.md` for multi-model
work, and `references/template-packs.md` before creating reusable scaffolding.
Load only the reference needed for the current route.

## Entrypoint Acceptance Map

The public `worldguard` entry accepts a unit `GuardContract`, a
`ModelMeshContract`, a task-local prediction/observation/revision contract, or
an explicit template-pack construction request. It returns the selected
WorldGuard route with typed status and evidence. Missing required input,
unsupported semantics, or an incomplete predictive boundary remains a visible
non-pass result; it never triggers another Guard as a replacement route.

## Use When

- A claim about events, agents, space, resources, causality, conflict, or norms
  needs an explicit WorldGuard model and bounded result.
- A what-if or prediction request needs claim-derived Guard coverage, temporal
  depth, scenarios, holdouts, interventions, or counterfactual checks.
- A WorldGuard contract, model mesh, template pack, handoff, authority, receipt,
  ledger, or task-local revision needs construction or audit.

## Do Not Use When

- The task asks only for unmodeled narrative judgment with no WorldGuard
  contract or evidence boundary.
- A different Guard or downstream writer is expected to repair missing
  WorldGuard inputs or reinterpret a WorldGuard result.
- The request would treat a toy fixture, structural pass, or repository test as
  proof of factual truth or predictive accuracy.

## Required Workflow

1. Decide the check shape before giving a conclusion:
   - Use `GuardContract` for one claim checked against one explicit world model.
   - Use `ModelMeshContract` when multiple models, versions, parent/child boundaries, handoffs, or downstream consumers are involved.
2. When constructing a new contract, read `references/template-packs.md` and use the WorldGuard-owned template registry before assembling a dictionary from scratch. Feed only explicit WorldGuard/caller facts into selection. Zero matching candidates uses the unique base template and remains construction-only; one selects that exact candidate; many is `ambiguous` and blocks. Fill every task-owned slot, retain the selection and instance fingerprints, and run the bound WorldGuard-native validators. When another authoring tool needs a neutral catalog, emit WorldGuard's target-template interchange from the exact current registry fingerprint. Do not let a template or downstream tool infer Guard routes, purpose, applicability, selected failures, fixtures, oracles, semantic PASS, or predictive readiness.
3. Before trusting a Guard model, inspect `references/guard-model-contract.md`. First use the family baseline only to learn which WorldGuard-native oracle reactions are available. Then, before constructing each real Guard child, make the AI write a fresh task-model-instance declaration: exact task/run/model/Guard identity, the plain-language failure this particular model is intended to prevent, its unsupported boundary, and a non-empty one-or-many set of selected failure ids. Provide one task-local native known-good and exactly one task-local native known-bad for every selected failure. `GuardContract.for_guard` proves that declaration before construction; unit and semantic runtime verifiers rerun and fingerprint the exact proof. Missing, empty, unknown-oracle, incomplete, wrong-instance, post-construction, or stale declarations block. Run `python -m worldguard.guard_model_contract` to verify the family catalog itself; a family pass never substitutes for the fresh task declaration.
4. For a unit check, build or inspect a structured `GuardContract`. Decompose non-trivial or predictive claims into `claim.atoms` with stable ids, requested semantics, and `predictive_intent`. Let WorldGuard derive the required Guards from those atoms and compare them with `claim.target_guards`; a caller-selected subset is not authority to omit a required route. Then run the local package when a contract file or packaged example is available:

   ```powershell
   python "$env:USERPROFILE\.codex\skills\worldguard\scripts\run_worldguard_check.py" --example fuel_cell
   ```

   or:

   ```powershell
   python "$env:USERPROFILE\.codex\skills\worldguard\scripts\run_worldguard_check.py" --contract <path>
   ```

5. For a mesh check, build or inspect a structured `ModelMeshContract`, then inspect:
   - model nodes and their authority boundaries;
   - model edges and handoff contracts;
   - stale/current source status;
   - forbidden downstream use;
   - dependency cycles;
   - child `GuardedReport` statuses and ledgers.
   - `structural_status`, `semantic_status`, `provider_status`, and `rollout_status` separately;
   - every semantic executor's typed binding and unsupported boundary;
   - `semantic_coverage`: expected nodes and children, bounded/predictive profile, scenarios, holdouts, horizon, representative `timepoint_ids`, optional stricter target-authored `time_strata`, minimum timepoint count/coverage, optional `per_model_node` policies, states, transitions, branches, perturbations, interventions, and counterfactuals;
   - the native `depth_receipt`, including the mesh and coverage fingerprints, claim-derived required/missing Guards, quantitative executed/skipped coverage, predictive gaps, `predictive_claim_licensed`, and the aggregate claim boundary.
6. Run the local package when a mesh file is available:

   ```powershell
   python "$env:USERPROFILE\.codex\skills\worldguard\scripts\run_worldguard_check.py" --mesh <path>
   ```

7. For a non-trivial task that asks whether the world model matches reality, keep
   this WorldGuard task fully independent and run its native task-local loop:
   - freeze a `PredictionSnapshot` against the exact current model id, version,
     path, SHA-256, and sequence before reading the new observation;
   - preserve actual finite values and typed left/relation/right records in an
     `ObservedWorldSnapshot`, with a strictly later sequence and source;
   - compare only the declared expectations and retain every missing or
     contradicted expectation under its declared WorldGuard mismatch category;
   - create a separate candidate model rather than overwriting v1;
   - require both an original-scenario revalidation and a real-holdout-
     observation revalidation, with semantic rollout and empirical comparison
     passing in each, before accepting the candidate;
   - reject an unapplied failure or roll an applied failure back only to the
     exact still-current v1 identity.

   Native commands:

   ```powershell
   python "$env:USERPROFILE\.codex\skills\worldguard\scripts\run_worldguard.py" task-model freeze <prediction.yaml>
   python "$env:USERPROFILE\.codex\skills\worldguard\scripts\run_worldguard.py" task-model compare <prediction.yaml> <observation.yaml>
   python "$env:USERPROFILE\.codex\skills\worldguard\scripts\run_worldguard.py" task-model revision <candidate-revision.yaml>
   ```

8. Report `PASS`, `FAIL`, `GAP`, or `BOUNDARY_EXCEEDED` without collapsing non-pass statuses.
9. WorldGuard has one current closure behavior: semantic execution is required. The retired `closure_profile` field and `--closure-profile` selector are invalid; a caller cannot choose a shape-only path that skips required semantic checks.
10. Preserve template selection/instance receipts when used, plus ledgers, semantic receipts, task-local prediction/observation/revision receipts, missing slots, boundary traces, counterexamples, handoff findings, stale-source findings, authority findings, cycle findings, and the native depth receipt in the answer.

## Hard Gates

- Do not give a narrative-only PASS.
- Prefer a current WorldGuard-owned template pack over rebuilding a known contract scaffold. Selection must use explicit facts and expose the exact zero/one/many outcome; never rank or silently choose among multiple matches.
- Template fragments may compose only with exact disjoint leaf-field ownership. Reject stale manifests, undeclared writes, overlapping or ancestor/descendant fields, unresolved or unused slots, unknown validators, and last-writer-wins replacement.
- A template instance receipt proves construction integrity only. It never supplies a task purpose, protected failure, native good/bad evidence, semantic result, predictive license, installation identity, or maintenance closure.
- A target-template interchange must contain only the exact current root/catalog/template/result fields, bind the current WorldGuard route and native identities, and preserve native candidate equality. Unknown root fields, wrong routes, stale registry identities, and incomplete candidate rows block; a downstream authoring tool may seal transport identities but cannot change applicability.
- Do not use a general prompt checklist in place of EventGuard, AgentGuard, SpaceGuard, ResourceGuard, CausalGuard, ConflictGuard, or NormGuard.
- Merely connecting a shallow model is not Guard adequacy. The family baseline must still exhaust every Guard-owned runtime failure code, but a real child must independently declare the one or more failures relevant to this task. The entire family catalog is not automatically the child's purpose, and a Guard type is not permanently limited to one fixed failure. New failure semantics require a real WorldGuard-native code/oracle and family regression before a task may select them.
- A fixture-only family check cannot authorize a real Guard run. `GuardContract.for_guard` is the formal candidate constructor: it consumes exactly one explicit parent-task declaration for the selected Guard, proves its task-local known-good and per-failure known-bad reactions, freezes the declaration/proof fingerprints, and only then constructs the child. Missing, duplicate, empty, unknown-oracle, incomplete-proof, stale, post-construction, wrong-task, wrong-model, or wrong-Guard bindings are hard rejections. It never synthesizes a declaration from `GUARD_MODEL_PURPOSES`.
- Keep `SEM_EXECUTOR_UNREGISTERED` and `SEM_PROVIDER_UNAVAILABLE` under mesh/provider lifecycle ownership. Do not silently assign them to an individual Guard merely to make its failure inventory look complete.
- CausalGuard must return `GAP` when any declared endogenous variable lacks a structural equation; a non-empty but partial equation map is not a complete SCM.
- Do not report a whole mesh as `PASS` merely because one child model or one Guard passed.
- Do not trust `claim.target_guards` as the coverage denominator. Structured claim atoms and predictive intent determine the required routes; an omitted derived Guard is a concrete `GAP` with a skipped-child record.
- Structural `PASS` is not semantic `PASS`. A provider that did not run or an unsupported executor must remain visible and fail closed in the aggregate projection; no structural-only closure selector exists.
- Every expected semantic-rollout node needs a current `GuardContract`. A contractless expected node or expected-but-unexecuted semantic child reduces quantitative coverage and blocks aggregate pass.
- Discover every current semantic/predictive mesh node before evaluating `expected_model_node_ids`. Treat that list as a completeness assertion, never as authority to shrink the denominator. An exclusion must name a discovered non-critical node, include a reason and closed disposition, remain visible in reconciliation evidence, and contribute to neither execution coverage nor claim scope; unresolved, overlapping, critical, or still-connected exclusions block predictive closure.
- Do not claim predictive simulation from field presence, a single event, one or two convenient timepoints, or one parseable equation. A prediction claim requires structured claim atoms; claim-derived EventGuard and CausalGuard execution; a non-degenerate horizon; a target-owned representative timepoint floor and coverage ratio; non-replaceable native early/middle/late coverage; a bounded maximum gap between observations; normal and holdout scenarios; observed states and transitions; executed branches and perturbations; executed interventions and counterfactuals; complete expected child coverage; per-expected-model-node depth (so aggregate evidence cannot hide one shallow object); current mesh/coverage fingerprints; no predictive gaps; and `predictive_claim_licensed: true`. Target-authored strata may add stricter checks but cannot relabel clustered points as adequate temporal coverage. The native default scales with the square root of horizon length, so a 1,000-step horizon needs at least 32 distributed timepoints and a 10,000-step horizon needs at least 100 unless the target declares a stricter floor; exhaustive point-by-point execution is not the default. If the budget cannot meet the floor, downgrade the claim instead of shrinking the denominator.
- When a predictive node exposes variables or signals, derive a separate temporal child universe for every one. Each child must independently meet the same native count, early/middle/late, and maximum-gap gates; a deep node-level union cannot hide a shallow variable. Emit each per-object floor and exact selected timepoint identity as content-addressed WorldGuard evidence; do not add a competing weaker fixed-ratio floor.
- A node count, variable-name list, catalog expansion, whole-receipt hash, or ordinal time range is not proof of an individual WorldGuard obligation. Every satisfied governed obligation must retain its exact target-native semantic object, `evidence_ref`, and lowercase content hash. Missing, renamed, overlapping, mechanically generated, or summary-only mappings block predictive closure even when aggregate mesh coverage is green.
- A narrow executor may retain local `semantic_status: PASS` while predictive readiness remains false. When prediction was requested and predictive coverage is incomplete, `rollout_status` and aggregate closure remain `GAP` or `BOUNDARY_EXCEEDED`.
- Semantic rollout proves that the declared WorldGuard model executed under its
  native rules; it does not prove empirical accuracy. A task-local candidate
  cannot be accepted from model execution alone: the original scenario and a
  genuinely value-bearing real holdout observation must each have both semantic
  and empirical PASS.
- Freeze a prediction before its observation. A same-sequence or earlier
  observation is hindsight-invalid. Do not infer mismatch ownership from a
  variable name; each expectation must declare its WorldGuard-native category.
- Task-local revision may change only the separate current-task model candidate.
  It must not edit WorldGuard source, a Guard rule, a predictive-depth floor, an
  installed skill, or a reusable default. It must not call another Guard to
  supply or modify the task model.
- Repository FlowGuard/pytest regressions are engine-health calibration only. They never replace `python -m worldguard mesh-check --mesh <current-target-mesh>` and its current per-target native depth receipt.
- For every non-trivial or predictive conclusion, a current target-native WorldGuard receipt is required. A local executor PASS, one-off spot check, repository regression, or bounded single-event/equation check can support only a bounded conclusion. Author-side maintenance records may prove the skill was checked before installation, but ordinary WorldGuard use neither reads nor requires them.
- Treat the built-in event, BDI, RCC8, resource, causal, conflict, and norm executors as deliberately narrow. Their `PASS` licenses only the declared supported subset, never universal world understanding.
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

- Read `references/worldguard-contracts.md` when constructing or validating contract/result/ledger fields, frozen task-local predictions, real observations, or reversible candidate revisions.
- Read `references/template-packs.md` before constructing a GuardContract or ModelMeshContract from reusable scaffolding.
- Read `references/guard-model-contract.md` before accepting that any Guard model is meaningful or complete.
- Read `references/guard-boundaries.md` when deciding which Guard owns a claim part.
- Read `references/model-mesh.md` when constructing or validating mesh nodes, edges, snapshots, and mesh reports.
- Read `references/model-authority.md` when deciding whether a model node is being used inside its authority.
- Read `references/handoff-contracts.md` when deciding whether one model may consume another model's output.
- Read `references/closure-report.md` before claiming a multi-model check is complete.

## Output Requirements

Return:

- conclusion status;
- `GuardContract` or `ModelMeshContract` summary;
- template selection outcome and instance fingerprint/claim boundary, when a template pack was used;
- per-Guard results;
- per-node mesh results, when applicable;
- non-pass evidence;
- ledger evidence;
- mesh findings, when applicable;
- missing model fields, if any;
- commands run or reason local runtime was not run;
- `blockers` that prevent the requested conclusion;
- `skipped_checks` with a concrete reason for each check not run;
- `residual_risk` that remains inside the stated claim boundary.

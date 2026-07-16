---
name: worldguard
description: Model-first world-claim, what-if, prediction-boundary, and model-mesh checks for WorldGuard. Use when Codex needs to simulate or assess whether a claim about events, agents, spaces, resources, causality, conflicts, or norms is supported by an explicit model, contradicted by it, missing required inputs, or outside the modeled boundary; also use when creating or auditing GuardContract, ModelMeshContract, GuardResult, MeshReport, semantic rollout status, native depth receipt, ledger, counterexample, handoff, authority, freshness, or toy-fixture replay artifacts.
---

# WorldGuard

Use this skill to keep world-claim analysis contract-first, mesh-aware, and evidence-preserving.

## Workflow

1. Decide the check shape before giving a conclusion:
   - Use `GuardContract` for one claim checked against one explicit world model.
   - Use `ModelMeshContract` when multiple models, versions, parent/child boundaries, handoffs, or downstream consumers are involved.
2. Before trusting a Guard model, inspect `references/guard-model-contract.md`. First use the family baseline only to learn which WorldGuard-native oracle reactions are available. Then, before constructing each real Guard child, make the AI write a fresh task-model-instance declaration: exact task/run/model/Guard identity, the plain-language failure this particular model is intended to prevent, its unsupported boundary, and a non-empty one-or-many set of selected failure ids. Provide one task-local native known-good and exactly one task-local native known-bad for every selected failure. `GuardContract.for_guard` proves that declaration before construction; unit and semantic runtime verifiers rerun and fingerprint the exact proof. Missing, empty, unknown-oracle, incomplete, wrong-instance, post-construction, or stale declarations block. Run `python -m worldguard.guard_model_contract` to verify the family catalog itself; a family pass never substitutes for the fresh task declaration.
3. For a unit check, build or inspect a structured `GuardContract`. Decompose non-trivial or predictive claims into `claim.atoms` with stable ids, requested semantics, and `predictive_intent`. Let WorldGuard derive the required Guards from those atoms and compare them with `claim.target_guards`; a caller-selected subset is not authority to omit a required route. Then run the local package when a contract file or packaged example is available:

   ```powershell
   python "$env:USERPROFILE\.codex\skills\worldguard\scripts\run_worldguard_check.py" --example fuel_cell
   ```

   or:

   ```powershell
   python "$env:USERPROFILE\.codex\skills\worldguard\scripts\run_worldguard_check.py" --contract <path>
   ```

4. For a mesh check, build or inspect a structured `ModelMeshContract`, then inspect:
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
5. Run the local package when a mesh file is available:

   ```powershell
   python "$env:USERPROFILE\.codex\skills\worldguard\scripts\run_worldguard_check.py" --mesh <path>
   ```

6. Report `PASS`, `FAIL`, `GAP`, or `BOUNDARY_EXCEEDED` without collapsing non-pass statuses.
7. WorldGuard has one current closure behavior: semantic execution is required. The retired `closure_profile` field and `--closure-profile` selector are invalid; a caller cannot choose a shape-only path that skips required semantic checks.
8. Preserve ledgers, semantic receipts, missing slots, boundary traces, counterexamples, handoff findings, stale-source findings, authority findings, cycle findings, and the native depth receipt in the answer.

## Hard Rules

- Do not give a narrative-only PASS.
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
- When a predictive node exposes variables or signals, derive a separate temporal child universe for every one. Each child must independently meet the same native count, early/middle/late, and maximum-gap gates; a deep node-level union cannot hide a shallow variable. Emit each per-object floor and exact selected timepoint identity as content-addressed native evidence for SkillGuard to verify; do not add a competing weaker fixed-ratio SkillGuard floor.
- A node count, variable-name list, catalog expansion, whole-receipt hash, or ordinal time range is not proof of an individual WorldGuard obligation. Every satisfied governed obligation must retain its exact target-native semantic object, `evidence_ref`, and lowercase content hash. Missing, renamed, overlapping, mechanically generated, or summary-only mappings block predictive closure even when aggregate mesh coverage is green.
- A narrow executor may retain local `semantic_status: PASS` while predictive readiness remains false. When prediction was requested and predictive coverage is incomplete, `rollout_status` and aggregate closure remain `GAP` or `BOUNDARY_EXCEEDED`.
- Repository FlowGuard/pytest regressions are engine-health calibration only. They never replace `python -m worldguard mesh-check --mesh <current-target-mesh>` and its current per-target native depth receipt.
- For every non-trivial or predictive conclusion, that current target-native WorldGuard receipt is necessary but is not final closure by itself. The same exact target mesh/input set must close through the compiled current SkillGuard declared-check supervision contract. SkillGuard freezes and reconciles the exact WorldGuard-owned checks; it does not own Guard meanings, fixtures, failure universes, or predictive-depth semantics. A local executor PASS, one-off spot check, repository regression, or bounded single-event/equation check can support only a bounded conclusion. A repository `AGENTS.md` maintenance declaration or SkillGuard repository link selects the maintenance route; it is not runtime evidence and cannot replace the current native receipt or supervised closure.
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

- Read `references/worldguard-contracts.md` when constructing or validating contract/result/ledger fields.
- Read `references/guard-model-contract.md` before accepting that any Guard model is meaningful or complete.
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
Bind each guard_investigation run to the declared integration mode, evidence, blockers, residual_risk, and claim_boundary.
## Entrypoint Scope
Covers worldguard plus explicitly routed local materials; no unrelated repos, private files, external services, publication, or release claims unless requested and routed.
## Local Material Routing
Use workspace, skill directory, user files, or configured project paths; keep private machine paths local and public instructions portable.
## Entrypoint Acceptance Map
Use SkillGuard as the runtime contract executor for missing gates around the target workflow owned by Guard-family investigation workflow declared by the target skill. It enforces only the missing contract gates through the target workflow; duplicate SkillGuard-owned execution paths are invalid. Declared gates/routes: claim or source intake, evidence model, gap review, closure.

Treat `.skillguard/contract-source.json`, `.skillguard/compiled-contract.json`,
and the exact `.skillguard/check-manifest.json` as the only maintained runtime
authority. Former V1 manifests, work contracts, generic checkers, mutable
reports, evidence ledgers, caches, and fallback wording must be absent after
formal migration; OpenSpec history and immutable retirement receipts preserve
the migration record without leaving a second successful runtime route.
Preserve the existing Guard-investigation and `worldguard.semantic_rollout`
routes. SkillGuard supervises their evidence boundary and may not replace
WorldGuard's claim decomposition, semantic execution, simulation, per-object
depth judgment, or predictive/bounded decision.
## Use When
Use when the request matches worldguard and needs this governed workflow, materials, checks, or handoff behavior.
## Do Not Use When
Do not use outside the domain, without required materials, when a more specific skill owns the work, or for tiny direct answers.
## Required Workflow
Select the target workflow surface, fill missing SkillGuard gates around it, collect evidence, run native and SkillGuard checks, fix failures, then report.
## Hard Gates
Do not skip phases, do not replace required evidence with prose, do not treat stale reports as current, do not weaken validation to pass, and do not claim completion when blockers remain.
## Output Requirements
Report evidence, failures, blockers, skipped_checks with reasons, residual_risk, and claim_boundary; distinguish checked, unchecked, blocked, and uncertain.
## SkillGuard Maintenance
Keep only the current generic SkillGuard declared-check authority (`contract-source.json`, `compiled-contract.json`, and `check-manifest.json`); former authorities, optional closure profiles, calibration/depth policy fields owned by SkillGuard, ledgers, generic domain checkers, aliases, migration readers, and fallback success paths are invalid. The contract has exactly one `enforced` closure profile and `integration_mode: native-integrated`. WorldGuard alone defines Guard purposes, the finite failure universe, good/bad fixtures, reaction oracles, and predictive-depth policy.
Before validation, freeze the exact affected checks and assign each check one execution owner. Reuse only a current immutable terminal-success receipt whose governed inputs still match. A consumer must verify and project that receipt; it must not rerun the owner command or use `--resume` as a read-only audit. Run a full gate once only after source and tool identities freeze, never through a scheduled task, background resume, or unattended retry. After timeout or interruption, require confirmed descendant-process count zero before accepting evidence or starting another owner.

## Scheduled-production evidence boundary

The formal depth check is a `scheduled_production` target-native check over exactly one current input containing the WorldGuard mesh, `input_origin=target_native_scheduled_execution`, and the exact current `scheduled_production_identity` issued from the verified SkillGuard installation. The identity belongs in that target-owned mesh input, not in a generic SkillGuard run request. The native mesh evaluator derives semantic children, every modeled time step, scenario/holdout rows, predictive axes, and claim scope from that input. Repository fixtures cannot close a real world-model use; copying or relabeling them as production, shrinking the modeled denominator, or supplying generic placeholder evidence is invalid even when hashes match.

Formal supervision loads WorldGuard from the skill's bundled `.skillguard/runtime` tree. Every Python source in that tree is part of the current implementation authority, declared checks fingerprint their exact target inputs, and the installed bridge loads the bundled runtime before considering any editable checkout. A global import or external source checkout may help local development but cannot satisfy scheduled-production closure.

<!-- END SKILLGUARD CONTRACT LAYER -->

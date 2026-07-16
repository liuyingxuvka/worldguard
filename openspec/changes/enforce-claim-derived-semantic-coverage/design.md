## Context

WorldGuard's current mesh runner correctly distinguishes structure, provider availability, and semantic execution. Its semantic executors deliberately validate narrow subsets, but the aggregate has no machine-readable predictive readiness gate. Target Guards come from caller-declared lists, contractless nodes can be skipped, and the native receipt lacks an expected semantic universe, scenarios, horizon, branches, perturbations, or holdout evidence.

## Goals / Non-Goals

**Goals:**

- Derive required Guard routes from structured claim atoms and conservative predictive markers.
- Make every Guard declare the concrete invalid claim class it prevents and the boundary it does not license.
- Exhaust the finite source-discovered Guard-owned failure inventory with one native good per Guard, one native bad per failure class, and exact reaction oracles.
- Make every expected mesh node and semantic child visible as executed, skipped, missing, or bounded.
- Add target-owned predictive adequacy for horizon, state/transition rollout, interventions, counterfactuals, holdout scenarios, branches, and perturbations.
- Separate bounded semantic `PASS` from `predictive_claim_licensed`.
- Bind all quantitative coverage evidence to the current mesh fingerprint.
- Keep one target-native closure behavior: required semantic execution cannot be disabled by a caller-selected profile.
- Publish the existing target-native route/check bindings at the current contract top level for router visibility.

**Non-Goals:**

- Build a universal world simulator, solve arbitrary equations, or infer factual truth.
- Parse unrestricted natural language into a perfect ontology.
- Let SkillGuard own or reproduce WorldGuard semantic execution.

## Decisions

### 1. Guard model adequacy is target-owned and finite

WorldGuard owns a seven-Guard purpose registry. Each entry states the invalid
claim class the Guard prevents, the evidence boundary it does not license, and
one native good case that must pass both the unit runner and semantic executor.

The protected-failure universe is discovered from literal `error(...)` codes in
the Guard runners and per-Guard `_finding(...)` codes in the semantic executor.
Every discovered `(Guard, layer, code)` has exactly one native bad case and an
oracle requiring the exact expected status and single stable code. Duplicate,
missing, or extra cases block. Mesh registration and provider-lifecycle codes
remain separately owned and explicitly outside the individual-Guard universe.

Alternative considered: let each integration provide a few illustrative
fixtures. Rejected because a shallow connected model could pass while omitting
the failure class it is supposed to prevent.

### 2. Structured claim atoms drive route requirements

Extend claim contracts with generic atoms containing identity, text, requested semantics, and predictive intent. A WorldGuard-owned semantic-to-Guard registry derives required routes. Conservative prediction markers in legacy claim text/requested semantics can require the predictive route, but broad readiness still requires structured atoms.

Alternative considered: trust `target_guards` as the complete route set. Rejected because this lets the caller omit the very branch that could invalidate the claim.

### 3. Coverage contract lives on ModelMeshContract

Add a domain-neutral `SemanticCoverageContract` containing expected model-node ids, scenario ids, holdout ids, time horizon, branch ids, perturbation ids, and claim scope (`bounded` or `predictive`). Defaults derive expected nodes from the current mesh; predictive fields must be explicit and complete. This scope describes the claim being evaluated; it is not a quality selector and cannot disable semantic execution.

Alternative considered: infer adequate counts from input length. Rejected because adequate sampling depends on claim scope, not an arbitrary global number.

The current mesh inventory is the discovery authority. For every mesh, every model node is discovered before applying the declared expected-node list. The declared list is checked as a completeness assertion and cannot remove a discovered node. A target may exclude a genuinely inapplicable node only through an explicit reason plus closed disposition; excluded nodes remain in reconciliation evidence and cannot contribute receipts, aggregate coverage, or claim licensing.

### 4. Contractless required nodes fail closed

Every expected node must provide a contract. Missing contracts produce a concrete `GAP`, a skipped-child receipt, and reduced coverage. The former `structural_only` closure selector is retired and rejected; it cannot suppress the required semantic owner.

### 5. Predictive adequacy requires executed native semantics

A predictive route requires a non-degenerate horizon, at least one non-holdout and one holdout scenario, states, transitions, branch coverage, perturbations, interventions, counterfactual queries, and semantic receipts for every derived Guard. Event and causal executors emit executed rollout/intervention/counterfactual counts; field presence alone is insufficient.

Representative time depth uses a WorldGuard-owned lower bound: a non-zero count floor that grows as `ceil(sqrt(horizon_steps))` plus any stricter target-declared count or ratio. Native early/middle/late phases are derived from the declared horizon and cannot be replaced by arbitrary caller stratum names. A native maximum-normalized-gap gate prevents a count-complete sample from clustering around a few regions. Target-declared strata may add stricter checks only. If execution budget cannot meet these gates, WorldGuard downgrades the claim instead of shrinking the denominator.

WorldGuard emits the effective count, coverage, phase set, maximum-gap result, exact selected timepoint identities, eligible-count fingerprint, algorithm id/version, and precommit fingerprint as a native dynamic-floor receipt. Generic SkillGuard supervision verifies the exact declared target-native check and must not add, replace, or weaken that policy. This keeps one policy owner.

For nodes that expose variables or signals, WorldGuard derives a `(model node, variable/signal, horizon)` child universe. Each child uses the same native temporal algorithm against its own observations and phase distribution. Node-level union evidence does not repair a shallow variable/signal.

Predictive adequacy is also recomputed per expected model node. The shared coverage contract is the default object policy; an optional `per_model_node` override may make a target stricter or describe a genuinely different child denominator. Aggregate union coverage never repairs a shallow child.

Alternative considered: treat a valid event record or parseable equation as prediction. Rejected because those checks prove local evaluability, not forecast behavior.

Alternative considered: require every horizon point. Rejected because this would turn a general low-fidelity adequacy gate into project-grade full-resolution validation. The count/ratio/phase/object policy remains bounded and target-owned.

### 6. Receipt and aggregate carry separate decisions

The native receipt adds the coverage universe/fingerprint, claim atoms, required/missing Guards, expected/executed/skipped nodes and children, scenario/horizon/branch/perturbation counts, coverage ratio, predictive gaps, and `predictive_claim_licensed`. A narrow executor may still report semantic `PASS`; the receipt and claim boundary identify it as bounded, and a requested predictive route with gaps projects aggregate `GAP`.

### 7. SkillGuard binds declared target-native checks

Repository regression commands remain engine-health checks. SkillGuard supervision binds the exact declared WorldGuard checks and their current inputs; no parallel WorldGuard evaluator, Guard-purpose registry, failure universe, calibration policy, or oracle is added.

The maintained contract uses the current generic schema,
`integration_mode: native-integrated`, and exactly one `enforced` closure profile. Optional
routine/functional/release/highest-quality modes and SkillGuard-owned
calibration, coverage-universe, or dimension semantics are removed. Those
meanings remain in target-native WorldGuard checks.

The same contract also exposes `native_route_owner`, `default_route_id`, exact
top-level `native_route_bindings`, and exact `native_check_bindings`. These are
router projections of existing WorldGuard owners, not extra executors. The
top-level sets must equal the target-owned route/check sets in the compiled
depth profile.

The SkillGuard projection carries a complete object-scope attestation for discovered, declared, and excluded model nodes plus per-object native floor receipts for model-node and variable/signal temporal child universes. Exclusions never contribute to covered claim scope.

The projection preserves the exact native selected/evaluated/validated sets, including an empty set on a genuinely shallow branch. It never inserts a `bridge-health` witness, expands a catalog into executed evidence, or generates a mechanically ordinal span as a substitute for an exact native observation locator.

The WorldGuard-native receipt also preserves one content-addressed observation for each executed semantic child, each model-node and variable/signal temporal child, the scenario/holdout portfolio, predictive axes, native temporal policy, and each claim-derived route. Every observation names the semantic object and target obligation ids and carries the exact native content, evidence ref, and content hash. Aggregate counts and a whole-receipt digest remain summaries only.

### 8. Formal retirement covers every former SkillGuard authority

WorldGuard retains only the current generic contract source, compiled contract, exact check manifest, target-owned native checks, and final immutable retirement receipt. Former generic/domain checkers, optional profiles, policy files, mutable reports/evidence/ledgers, target-local run outputs, and caches are not history; they are alternate live surfaces and must be absent. The earlier narrow completion receipt remains invalid until the parent-owned source/install parity and installation-currentness replay close on the frozen current identity.

## Risks / Trade-offs

- [Legacy broad text is ambiguous] -> Use conservative predictive markers and require structured atoms before predictive licensing.
- [Existing topology-only meshes lack contracts] -> Require the missing contracts or keep the result as an explicit gap; do not preserve a structural-only bypass.
- [Safe scalar causal evaluation supports only a narrow subset] -> Keep AST restrictions and declare the unsupported boundary; arbitrary functions and external solvers remain `BOUNDARY_EXCEEDED`/`GAP`.
- [Predictive fixtures become verbose] -> Provide one compact canonical fixture and keep bounded checks lightweight.
- [Transport validation rejects an empty shallow result] -> Fix the transport contract to represent the block; never fabricate a successful observation.

## Migration Plan

1. Directly replace the current claim-atom and mesh coverage dataclasses without a compatibility reader or optional closure path.
2. Add route derivation, contractless-node findings, receipt coverage fields, and predictive adequacy aggregation.
3. Extend event/causal native executors for bounded deterministic rollout/intervention/counterfactual evidence.
4. Add focused shallow-negative and predictive-positive tests plus FlowGuard/model-test evidence.
5. Update skill references and directly replace the target-local SkillGuard contract with the current generic declared-check schema and sole `enforced` profile.
6. Run focused target-native tests, the existing FlowGuard owner, strict OpenSpec validation, and current generic SkillGuard authority/parity checks. Leave installation replay, the single parent-owned full regression/aggregation, OpenSpec verify receipt consumption, and archive to their declared owners.

## Open Questions

- Future adapters may add richer scenario generators, but core v1 remains domain-neutral and consumes only generic ids, states, transitions, interventions, counterfactuals, and expected outcomes.

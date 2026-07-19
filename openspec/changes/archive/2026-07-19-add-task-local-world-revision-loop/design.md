## Context

WorldGuard's semantic executors can run declared event and causal scenarios, including holdout scenarios, interventions, and counterfactuals. Its predictive-depth receipt proves that the declared axes and timepoints were executed for the current mesh. Current variable observations, however, are reduced to timepoint coverage, and causal holdouts are model inputs rather than real outputs against which predictions are scored.

The new layer must preserve the existing semantic rollout while adding an empirical, task-local comparison and reversible world-model candidate. WorldGuard remains one independent skill; no other Guard supplies models or changes WorldGuard state. Existing project-adoption edits are outside this change.

## Goals / Non-Goals

**Goals:**

- Freeze numeric and relationship predictions against an exact base world-model identity before observation.
- Preserve actual observed numeric values and relationships with provenance and monotonic ordering.
- Produce typed mismatch findings for initial state, transition, causal relation, resource, agent, observation mapping, and a bounded other category.
- Evaluate a distinct candidate world-model artifact against an original scenario and a real holdout observation.
- Accept, reject, or roll back the candidate while proving the base artifact remains current.

**Non-Goals:**

- Replace WorldGuard's structural or semantic rollout engines.
- Infer causal identification, agent beliefs, or observation mapping from raw data automatically.
- Change predictive-coverage floors, Guard rules, installed user skills, or reusable defaults.
- Add cross-Guard data exchange or meta-learning.

## Decisions

### 1. Add a separate empirical task-local contract

`worldguard.task_local_revision` owns immutable dataclasses and evaluation functions for predictions, observations, comparisons, and revision decisions. Existing `GuardContract`, `ModelMeshContract`, and semantic executors remain unchanged.

Alternative: reinterpret `holdout_scenarios` as actual observations. Rejected because those records currently supply exogenous inputs and changing their meaning would break existing semantic rollout.

### 2. Preserve values and relationships explicitly

A prediction contains expected numeric values with absolute tolerances and expected typed relationships. An observation contains actual numeric values and actual relationships plus source reference. Values must be finite. Relations are compared by stable ids and exact left/relation/right content.

### 3. Freeze by model hash and sequence

Prediction snapshots bind model id, version, path, and SHA-256 plus a prediction sequence. Observations name the prediction and require a strictly later observation sequence. Both fingerprints appear in the comparison receipt.

### 4. Make mismatch ownership explicit

Every expected value or relationship declares one WorldGuard-native mismatch category. The evaluator reports that category when the observation contradicts or omits the expectation. It does not guess which submodel to edit.

Alternative: infer mismatch type from variable names. Rejected because naming conventions are project-specific and could silently assign the wrong model owner.

### 5. Require two different candidate revalidation roles

A candidate revision must consume at least one `original_scenario` receipt and one `real_holdout_observation` receipt. Each receipt binds the candidate model identity, a WorldGuard semantic-rollout status, and a task-local prediction/observation comparison status. Both must pass before acceptance.

### 6. Never overwrite the base

Base and candidate world models are separate current artifacts. The evaluator is read-only. Failed unapplied candidates are rejected. Failed applied candidates are rolled back only when the rollback identity equals the verified base identity. The receipt always states whether v1 was preserved.

## Risks / Trade-offs

- [Typed observations cover only declared values and relationships] → Keep the claim boundary exact and report missing expectations; do not imply complete reality coverage.
- [A caller can assert an incorrect mismatch owner] → Preserve the declared category and evidence in the receipt; WorldGuard does not auto-edit the corresponding submodel.
- [A scenario can pass structurally but disagree with reality] → Require both semantic rollout and empirical comparison status in each revalidation receipt.
- [Bundled runtime drift] → Synchronize the repository-owned skill runtime and compare it with the package before closure.

## Migration Plan

1. Add task-local contracts, evaluator, native CLI commands, exports, and tests.
2. Update WorldGuard skill and reference guidance.
3. Refresh the repository-owned bundled runtime, including the package version identity.
4. Run focused and full tests plus OpenSpec, FlowGuard, and SkillGuard checks.

Rollback is removal of this unarchived capability. Existing `check` and `mesh-check` behavior remains unchanged.

## Open Questions

None. Domain-specific tolerances, observations, and revision contents remain task inputs.

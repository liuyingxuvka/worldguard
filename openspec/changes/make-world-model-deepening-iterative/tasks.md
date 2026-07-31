## 1. Current contract replacement

- [x] 1.1 Require task, purpose, independent coverage id/owner/source/fingerprint, assumptions, unknowns, iteration budget, and predecessor on every `PredictionSnapshot`.
- [x] 1.2 Require content-addressed observation evidence and exact external-input declarations; remove observation-authored gap transitions.
- [x] 1.3 Add a WorldGuard-owned task/candidate/coverage binding for current native execution-depth receipts and derive all predictive gaps from it.
- [x] 1.4 Replace semantic-rollout status strings with typed semantic and empirical original/holdout receipts and reject former shapes.

## 2. Single task-local runtime owner

- [x] 2.1 Compute input/resolved/persisted/introduced gaps and progress from comparison, depth, and revalidation receipts.
- [x] 2.2 Enforce exact task/candidate/coverage/predecessor identities, native predictive license, holdout independence, and candidate-construction separation.
- [x] 2.3 Implement exact `continue_iteration`, `progress_stalled`, `iteration_limit`, `external_input_required`, rollback/rejection, and `model_closed_for_task` decisions.
- [x] 2.4 Make fact activation emit only `task_local_revalidation_required` for the same task and sole task-local owner.
- [x] 2.5 Update the task-model CLI to expose current depth/revalidation bindings and strict terminal receipts.

## 3. Prompts, bundled runtime, and tests

- [x] 3.1 Update WorldGuard `SKILL.md`, task/fact references, and agent prompt to describe the one strict current route.
- [x] 3.2 Keep authoritative and bundled runtime byte-identical through the repository's existing single projection owner.
- [x] 3.3 Add exact known-bad tests for legacy/shallow inputs, tampered or stale receipts, self-reported gaps/progress, aliased holdout, new gaps, stalls, limits, incomplete external blockers, and fact-only closure.
- [x] 3.4 Add exact known-good tests for native-gap continuation, multi-iteration closure, independent holdout acceptance, external stop, rejection, rollback, and fact-to-task handoff.

## 4. Model and maintenance authority

- [x] 4.1 Extend existing task-local/fact FlowGuard behavior models and the observed implementation manifest to cover current schema, runtime, CLI, prompts, and tests.
- [x] 4.2 Add the target-owned task-local model-closure check to the WorldGuard SkillGuard contract and refresh compiled/check manifests with current project identity.
- [x] 4.3 Update source version, bundled version, README, CHANGELOG, topology expectations, and local release metadata to 0.7.0.

## 5. Affected verification and handoff

- [x] 5.1 Run focused task-local, fact, CLI, parity, and topology tests; fix every affected failure.
- [x] 5.2 Run affected FlowGuard task-local/fact checks and current project/model authority audits when the shared engine is callable.
- [x] 5.3 Run SkillGuard maintainer audit and affected-only plan/checks without starting the final frozen full validation.
- [x] 5.4 Leave installation, final full validation, commit, tag, push, and release to the root integration owner after all five repositories freeze.

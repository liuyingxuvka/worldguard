## Why

WorldGuard already owns task-local prediction snapshots, observations, fact-level revision, candidate revalidation, holdout checks, and rollback. The first iteration added the intended fields but left them optional, accepted caller-authored gap and progress claims, treated semantic `PASS` as an untyped string, allowed original and holdout evidence to alias, and let fact activation announce task closure. Those paths can still accept a shallow candidate while the current task's native predictive depth is absent or open.

## What Changes

- **BREAKING** Reject pre-0.7 task-local prediction, observation, revalidation, depth-binding, candidate-revision, and fact-activation shapes instead of preserving a compatibility success path.
- Require every prediction to bind one task/purpose, independently fingerprinted coverage universe, explicit assumptions and unknowns, and an exact predecessor iteration.
- Derive state, transition, branch, perturbation, intervention, counterfactual, and holdout gaps only from a content-addressed current native execution-depth receipt; derive gap transitions and progress instead of accepting caller declarations.
- Replace semantic-rollout strings and evidence references with typed, content-addressed original-scenario and real-holdout receipts, and prove their evidence independence from each other and from candidate construction.
- Make fact activation emit only a same-task, same-owner revalidation handoff. It cannot emit `model_closed_for_task`.
- Update WorldGuard prompts, CLI output, FlowGuard authority, SkillGuard declarations, version records, and exact known-good/known-bad tests.

## Capabilities

### New Capabilities
- None. This extends the existing task-local WorldGuard revision capability.

### Modified Capabilities
- `task-local-world-revision`: require iterative predictive-depth closure and explicit external blockers.

## Impact

- `worldguard/task_local_revision.py`, `worldguard/execution_depth.py`, `worldguard/fact_revision.py`, CLI, bundled runtime, skill prompts, tests, FlowGuard model authority, SkillGuard author contract, and release records.
- No new public Guard, global truth store, shared learner, or automatic cross-Guard handoff.

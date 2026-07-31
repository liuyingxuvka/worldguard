## Why

WorldGuard already owns task-local prediction snapshots, observations, fact-level revision, candidate revalidation, holdout checks, and rollback. A candidate can still be accepted while the current task's predictive depth reports addressable state, transition, branch, intervention, or counterfactual gaps.

## What Changes

- **BREAKING** Make WorldGuard continue task-local model revision while native predictive or fact-support gaps remain addressable.
- Extend prediction, observation, and candidate-revision records with purpose/coverage identity, assumptions/unknowns, gap transitions, iteration, and terminal reason.
- Make fact revision feed back into the same candidate model owner and rerun native depth.
- Update WorldGuard prompts, CLI output, and known-good/known-bad tests.

## Capabilities

### New Capabilities
- None. This extends the existing task-local WorldGuard revision capability.

### Modified Capabilities
- `task-local-world-revision`: require iterative predictive-depth closure and explicit external blockers.

## Impact

- `worldguard/task_local_revision.py`, `worldguard/execution_depth.py`, `worldguard/fact_revision.py`, CLI, skill prompts, tests, and local consumer projection.
- No new public Guard, global truth store, shared learner, or automatic cross-Guard handoff.

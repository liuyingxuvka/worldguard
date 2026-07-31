## 1. Contract and schema

- [x] 1.1 Extend the `task-local-world-revision` spec with iterative predictive closure requirements.
- [x] 1.2 Add task, purpose, coverage, assumptions, unknowns, and iteration fields to `PredictionSnapshot`.
- [x] 1.3 Add evidence identity and gap-transition fields to observations and candidate revisions.

## 2. Runtime owner

- [x] 2.1 Make candidate evaluation consume current `execution_depth.predictive_gaps`.
- [x] 2.2 Make fact-revision activation feed the same task-local candidate/depth loop.
- [x] 2.3 Add progress-stall, iteration-limit, external-blocker, and task-closure terminal reasons.
- [x] 2.4 Update existing task-model CLI output and preserve rollback behavior.

## 3. Prompts and tests

- [x] 3.1 Update WorldGuard SKILL.md and references with the no-level iterative rule.
- [x] 3.2 Add shallow, fact-only, missing-holdout, new-gap, stalled, and external-input known-bad tests.
- [x] 3.3 Add multi-iteration closure and rollback known-good tests.

## 4. Verification and local projection

- [x] 4.1 Complete affected WorldGuard validation/maintenance checks without overwriting peer evidence.
- [x] 4.2 Run focused task-local, fact, depth, and CLI tests.
- [x] 4.3 Refresh the local consumer installation and leave GitHub untouched.

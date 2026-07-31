## Context

WorldGuard's existing task-local revision owner already enforces current model identities, original-scenario and real-holdout revalidation, candidate acceptance/rejection, and rollback. Its fact-level transaction is subordinate to that owner. The change connects existing predictive gaps to the continuation decision.

## Goals / Non-Goals

**Goals:**

- Bind predictions to task purpose, independent coverage universe, assumptions, unknowns, and iteration history.
- Preserve fact support changes, prediction mismatches, candidate identity, native receipts, and rollback.
- Require state/transition, branch/perturbation, intervention/counterfactual, and holdout coverage when the task requests them.

**Non-Goals:**

- No global truth-maintenance service or permanent world learner.
- No conflation of TRUE_ONLY/FALSE_ONLY/BOTH/NEITHER with closure status.
- No automatic sibling Guard execution or online mutation of WorldGuard core rules.

## Decisions

1. Extend current dataclasses and evaluator; do not create a parallel deepening module.
2. Add prediction purpose/coverage/assumption/unknown fields and candidate gap transitions.
3. After fact-revision activation, rerun the same task-local prediction/depth owner before closure.
4. Return `model_closed_for_task` only when all current predictive gaps are closed or explicitly external with an exact boundary; stall and iteration limits are blocking.

## Risks / Trade-offs

- [Fact-only changes appear complete] -> require a new candidate/depth/holdout evaluation after fact activation.
- [A world model becomes unbounded] -> derive an explicit task universe and retain a safety iteration limit that blocks rather than passes.
- [Conflicting facts are hidden] -> preserve four-valued fact status and separate it from model closure.

## Migration Plan

Update current schemas and fixtures together, run task-local/fact/depth tests, regenerate local skills, then validate installation. Preserve existing revisions and rollback candidates.

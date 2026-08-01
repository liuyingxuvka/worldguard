## Context

WorldGuard's existing task-local revision owner already enforces current model identities, original-scenario and real-holdout roles, candidate acceptance/rejection, and rollback. The first implementation did not make the new task fields mandatory, accepted caller-authored gap/progress fields, represented semantic rollout as a status string, and allowed fact activation to become a second closure owner. This change replaces those successful paths in place.

## Goals / Non-Goals

**Goals:**

- Bind predictions to task purpose, independently owned coverage universe, assumptions, unknowns, and exact iteration history.
- Preserve fact support changes, prediction mismatches, candidate identity, current native receipts, evidence provenance, and rollback.
- Require state/transition, branch/perturbation, intervention/counterfactual, and holdout coverage from the native receipt rather than from caller gap lists.
- Make original and holdout evidence content-addressed, role-typed, and independent from each other and candidate construction.

**Non-Goals:**

- No global truth-maintenance service or permanent world learner.
- No conflation of TRUE_ONLY/FALSE_ONLY/BOTH/NEITHER with closure status.
- No automatic sibling Guard execution or online mutation of WorldGuard core rules.

## Decisions

1. Replace the current task-local dataclass shapes directly; do not add a legacy reader, converter, alias, fallback, or parallel deepening module.
2. `PredictionSnapshot` owns the task/coverage/assumption/unknown/predecessor binding. Later iterations carry exact prior gap ids plus a fingerprint of that set; observation evidence, content, and coverage fingerprints are recomputed from canonical payloads.
3. A WorldGuard-owned depth-binding function consumes the exact native depth receipt and binds it to the task, candidate, and independent coverage universe. Candidate evaluation classifies but never rewrites its native gap ids.
4. Candidate evaluation computes input, resolved, persisted, and introduced gaps. An unchanged/repeated gap fingerprint stalls; the finite iteration limit blocks.
5. Revalidation receipts contain typed semantic and empirical receipts. Exact role cardinality, task/candidate binding, source-result status/candidate/role binding, content fingerprints, source separation, and holdout construction-independence are enforced.
6. After fact-revision activation, emit a `task_local_revalidation_required` handoff to the sole `worldguard.task_local_world_revision` owner. Fact activation cannot decide closure.
7. Return `model_closed_for_task` only after the current native receipt licenses prediction, all derived gaps are closed, exactly one original and holdout revalidation pass, their evidence is independent, and all identities are current.

## Risks / Trade-offs

- [Fact-only changes appear complete] -> fact activation always emits a same-owner revalidation handoff and never a closure terminal.
- [A world model becomes unbounded] -> derive an explicit task universe and retain a safety iteration limit that blocks rather than passes.
- [Conflicting facts are hidden] -> preserve four-valued fact status and separate it from model closure.
- [Caller manufactures progress] -> remove transition/progress inputs and derive them from immutable before/after evidence.
- [A holdout is reused during fitting] -> retain candidate-construction evidence fingerprints and reject any holdout overlap.

## Migration Plan

This is a direct current-format replacement. Update authoritative and bundled runtime together, reject the former task-local shapes, update fixtures and CLI, extend the existing task-local/fact FlowGuard owners and manifest, refresh the SkillGuard declaration, then run affected checks. Preserve existing model files and rollback candidates as task data, but do not preserve a former runtime reader.

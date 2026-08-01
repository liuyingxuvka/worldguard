# Task-Local Model Deepening

Load this reference for the `task_local_revision` shape or when EventGuard/CausalGuard declares predictive intent, intervention/counterfactual work, or a current predictive gap. This is WorldGuard's existing evidence-derived loop, not an understanding questionnaire or level scale.

## Freeze before observing

Use only `worldguard.task_local_revision.v2`. Freeze a non-empty task id and purpose, independently owned coverage-universe id/source/inventory/fingerprint, non-empty assumptions and unknowns, finite iteration budget, and exact root or content-addressed predecessor. Later iterations bind exact prior gap ids and their set fingerprint.

Freeze `PredictionSnapshot` against the exact current model id, version, path, SHA-256, and sequence before reading the new observation. Preserve actual finite values and typed left/relation/right records in a strictly later `ObservedWorldSnapshot` with a content-addressed identity and source.

## Compare and revise

Compare only declared expectations. Keep every missing or contradicted expectation under its WorldGuard mismatch category. Create a separate candidate model; never overwrite the predecessor.

Bind one exact current native execution-depth receipt to the same task, coverage universe, and candidate. Derive state, transition, branch, perturbation, intervention, counterfactual, and holdout gaps from that receipt. A caller-authored remaining-gap list, progress boolean, PASS string, or understanding label has no authority.

Require exactly one typed original-scenario receipt and one typed real-holdout receipt. Each includes a content-addressed semantic result and empirical comparison. Their observation ids, sources, evidence fingerprints, content fingerprints, and semantic-result fingerprints must be independent; holdout evidence cannot appear in candidate construction.

## Continue or stop from evidence

The runtime computes input, resolved, persisted, introduced, and current gaps.

- Continue when a new addressable gap exists.
- Stop as `progress_stalled` when the gap fingerprint is unchanged or repeated.
- Stop as `iteration_limit` when the finite budget is exhausted.
- Return `external_input_required` only with the exact input, owner, reason, blocked gap ids, and affected claims.
- Emit `model_closed_for_task` only from the same task-local owner after native predictive license, zero current gaps, and both independent revalidations pass.

When fact-level support changes, load `fact-revision.md`. Fact activation ends at `task_local_revalidation_required` and returns to this same owner; it never closes the task.

## Native commands

```powershell
python "$env:USERPROFILE\.codex\skills\worldguard\scripts\run_worldguard.py" task-model freeze <prediction.yaml>
python "$env:USERPROFILE\.codex\skills\worldguard\scripts\run_worldguard.py" task-model compare <prediction.yaml> <observation.yaml>
python "$env:USERPROFILE\.codex\skills\worldguard\scripts\run_worldguard.py" task-model depth-bind <prediction.yaml> <candidate-identity.yaml> <native-depth.json> --binding-id <id>
python "$env:USERPROFILE\.codex\skills\worldguard\scripts\run_worldguard.py" task-model revalidation-bind <prediction.yaml> <candidate-identity.yaml> <role> <semantic-result.json> <comparison.json> --check-id <id> --semantic-receipt-id <id> --semantic-status <status> --evidence-ref <ref>
python "$env:USERPROFILE\.codex\skills\worldguard\scripts\run_worldguard.py" task-model revision <candidate-revision.yaml>
```

This loop proves only bounded task-local model closure under current declared evidence. It does not prove universal factual truth, future accuracy outside the boundary, installation, or release.

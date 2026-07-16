## Context

`worldguard.mesh` owns topology, authority, handoff, freshness, and child report aggregation. Existing child contracts can pass shape checks even when semantic relations are missing, contradictory, or unevaluable. Seven known negative probes currently pass, so mesh `PASS` can be misunderstood as semantic rollout success.

## Goals / Non-Goals

**Goals:** make structural and semantic results distinct, add minimal target-owned semantic executors and provider status, and prevent aggregate overclaim.

**Non-Goals:** build a universal world simulator, solve arbitrary equations, or let SkillGuard own world semantics.

## Decisions

- Extend `MeshReport` with `structural_status`, `semantic_status`, `provider_status`, `rollout_status`, and per-child semantic receipts.
- Aggregate fail-closed: structural pass plus semantic not-run is not semantic pass; provider unavailable remains visible.
- Add a small executor registry owned by WorldGuard. Each executor declares accepted input/output binding and supported semantic subset.
- Implement minimal evaluators for event axioms, BDI completeness, RCC8 consistency, resource conservation, causal evaluability, conflict completeness, and norm conditions.
- Use known passing negative probes as required regression failures.

## Risks / Trade-offs

- [Semantic scope expands without limit] -> Executors declare narrow supported subsets and return `PROVIDER_UNAVAILABLE` or `BOUNDARY_ONLY` outside them.
- [Existing clients expect `status`] -> Keep aggregate `status` as a conservative projection and add explicit component statuses.
- [Shape-only workflows become noisy] -> Allow an explicit structural-only closure profile with a visible boundary.

## Migration Plan

Add optional report fields and executor interfaces, preserve old contract loading, introduce negative probes, update CLI/skills, and graduate semantic rollout separately from structural checks.

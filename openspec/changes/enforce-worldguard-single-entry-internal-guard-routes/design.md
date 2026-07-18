## Context

WorldGuard currently publishes one `worldguard` console and one `skills/worldguard` consumer skill. Its runtime has exactly seven Guard runners and seven semantic executors, but the public skill and SkillGuard contract do not encode that topology as one verifiable authority. The change formalizes the existing architecture without creating new child entrypoints.

## Goals / Non-Goals

**Goals:**

- Prove `worldguard` is the sole installable skill and console.
- Preserve all seven Guards as independently complete internal routes.
- Bind each internal route to expectation/prediction boundaries, native response, semantic validation, and visible terminal states.
- Prove root runtime and bundled consumer runtime parity.
- Reject child skill directories, child consoles, aliases, and compatibility paths.

**Non-Goals:**

- Changing Guard algorithms or broadening their factual boundaries.
- Claiming every Guard independently performs future prediction.
- Installing, publishing, tagging, releasing, or changing global routing.
- Touching FlowPilot.

## Decisions

### Public root, internal complete routes

The only public skill id and console remain `worldguard`. EventGuard, AgentGuard, SpaceGuard, ResourceGuard, CausalGuard, ConflictGuard, and NormGuard remain callable inside the WorldGuard kernel through `GUARD_RUNNERS` and `EXECUTOR_REGISTRY`. They are modeled as complete internal routes, not direct Codex skills or project scripts.

### Topology contract is data plus executable validation

`skills/worldguard/references/internal-guard-routes.json` will declare the exact seven rows. Each row binds:

- internal route id and Guard id;
- native runner;
- claim-derived expectation owner;
- prediction mode and boundary;
- `GuardResult` response owner;
- semantic executor and purpose-contract validator;
- exact Guard terminal statuses.

The checker will compare this contract with the runtime registries, package scripts, skill inventory, status enum, and bundled-runtime bytes.

### Prediction remains bounded by current native semantics

EventGuard and CausalGuard participate in claim-derived predictive coverage when a predictive request is declared. The other five Guards preserve bounded model expectations and constraints but do not gain an invented future-forecast claim. Task-local prediction snapshots remain a WorldGuard suite capability, frozen before observation.

### Internal routes do not enter the global route registry

The SkillGuard contract will add one topology obligation and one target-native topology check. The seven internal routes may appear in the portable model as child functions, but `native_route_bindings` will continue to advertise only WorldGuard-owned public/current workflow routes. This prevents the global router from treating child Guards as installable skills.

## Risks / Trade-offs

- [Documentation drifts from code] → The checker compares exact registry keys, callable module names, statuses, scripts, and runtime mirror bytes.
- [A future Guard is added only to one registry] → Exact-set comparison blocks maintenance closure until the topology contract and both registries change together.
- [“Prediction” is overclaimed for non-predictive Guards] → Each row declares a bounded prediction mode; only current EventGuard/CausalGuard predictive gates can license predictive wording.
- [SkillGuard mistakes internal routes for public routes] → Keep child routes out of `native_route_bindings` and verify one consumer skill/project script.

## Migration Plan

1. Add the topology contract and checker.
2. Extend skill/reference text and FlowGuard model with exact internal route phases.
3. Add focused topology and negative tests.
4. Add one SkillGuard obligation/check and compile current contracts.
5. Run root/bundled parity, OpenSpec, FlowGuard, target-native, and full tests.

No compatibility route is created. Rollback is a source-level revert before any later installation.

## Open Questions

None. The exact seven-Guard inventory is frozen by the current runtime.

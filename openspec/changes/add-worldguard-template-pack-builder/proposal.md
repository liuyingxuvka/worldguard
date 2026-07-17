## Why

WorldGuard currently requires every `GuardContract` and `ModelMeshContract` instance to be assembled from scratch, which makes repeated field omissions and accidental semantic shortcuts likely even though the family already has validated native contracts and oracles. WorldGuard needs reusable, validated template packs that reduce construction error while keeping every Guard purpose, failure choice, fixture, and oracle under WorldGuard-native authority.

## What Changes

- Add a WorldGuard-owned template-pack manifest for `GuardContract` and `ModelMeshContract` construction, including applicability facts, owned fields, composition rules, native validator bindings, and a content-derived pack fingerprint.
- Add deterministic selection with explicit zero-, one-, and many-candidate outcomes. A unique candidate may be instantiated; no match falls back only to a declared WorldGuard base template; ambiguity blocks instead of letting AI guess.
- Add validated composition that rejects overlapping field ownership, incompatible fragments, undeclared writes, stale pack fingerprints, and missing native-validator bindings.
- Bind every produced instance to the exact selected template-pack fingerprint and then run the existing WorldGuard-native contract validators. Templates and SkillGuard do not choose Guard purposes, protected failures, task-local good/bad proofs, or predictive-depth semantics.
- Add positive, no-match/base-template, ambiguity, field-conflict, and stale-fingerprint regression coverage, plus FlowGuard artifacts for selection, lifecycle, and staged validation.
- Add a WorldGuard-owned, SkillGuard-neutral projection adapter that exports the current native catalog and one applicability row per native template under the exact central interchange schema. The target output stays unsealed; central SkillGuard may validate and seal identities but cannot infer applicability or alter the native candidate inventory.
- Bind the neutral projection to the exact WorldGuard route, request, registry, manifest, builder, and validator fingerprints; reject unknown root fields, wrong routes, incomplete candidate accounting, and stale native identities.

## Capabilities

### New Capabilities

- `worldguard-template-pack-builder`: Defines WorldGuard-owned validating template-pack manifests, deterministic candidate selection, safe composition, instance fingerprinting, and native validator handoff for GuardContract and ModelMeshContract construction.

### Modified Capabilities

- None.

## Impact

- Affected runtime: `worldguard` contract construction and a new WorldGuard-owned template-pack module.
- Affected skill surface: `skills/worldguard/SKILL.md`, WorldGuard references, bundled SkillGuard runtime projection, and current SkillGuard contract-source/compiled/check-manifest authority.
- Affected validation: focused pytest coverage, real FlowGuard model checks, OpenSpec verification contract, and the existing WorldGuard/SkillGuard native checks.
- The previously executed single full-suite owner is not rerun for the projection extension; completion is explicitly scoped to focused and affected checks plus read-only central schema compilation.
- No external dependency, installation, OpenSpec program, publication, commit, or push changes are required.

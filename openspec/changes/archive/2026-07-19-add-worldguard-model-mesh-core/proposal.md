## Why

WorldGuard can currently check one structured `GuardContract` at a time, but it cannot yet prove that several world models connect safely as a mesh. This leaves a gap for generic multi-model workflows where local Guard results are green but parent/child, version, authority, or downstream handoff relationships are stale, missing, cyclic, or overextended.

## What Changes

- Add a generic ModelMesh capability for model nodes, model edges, model authority boundaries, handoff contracts, world-state snapshots, and mesh-level closure reports.
- Keep `GuardContract` as the unit-level check surface; add a separate `ModelMeshContract` layer that can contain and run multiple Guard contracts without changing the single-contract API.
- Add mesh-level validation for missing nodes, stale sources, forbidden downstream use, model-authority overreach, dependency cycles, and preservation of all child Guard ledgers.
- Add a `worldguard mesh-check --mesh <path>` CLI surface and a Codex skill workflow branch for multi-model checks.
- Add repository and installed skill references for model mesh, model authority, handoff contracts, and closure reports.
- Exclude domain-specific concepts such as chapters, scenes, paragraphs, quests, or task arcs from the core capability; those belong in upper-layer adapters.

## Capabilities

### New Capabilities
- `worldguard-model-mesh`: Generic multi-model topology, handoff, authority, freshness, and closure checks for WorldGuard core.

### Modified Capabilities
- `worldguard-runtime`: Expose ModelMesh runtime APIs and CLI integration while preserving existing single-contract behavior.
- `worldguard-codex-skill`: Teach the local skill when to use `GuardContract` versus `ModelMeshContract`.

## Impact

- Adds `worldguard/mesh.py` and mesh tests.
- Updates `worldguard.cli` and public API exports.
- Adds WorldGuard skill reference documents for ModelMesh concepts.
- Updates repository and installed `worldguard` skill copies.
- Adds OpenSpec and FlowGuard records for field lifecycle, model mesh, development freshness, and model/test alignment.

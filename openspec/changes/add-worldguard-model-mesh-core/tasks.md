## 1. OpenSpec And FlowGuard Setup

- [x] 1.1 Create OpenSpec proposal, design, specs, and implementation checklist for generic WorldGuard ModelMesh core.
- [x] 1.2 Record FlowGuard existing-model, model-mesh, field-lifecycle, development-process, and model-test-alignment notes.

## 2. Skill And Reference Contracts

- [x] 2.1 Update repository `skills/worldguard/SKILL.md` with unit-check and mesh-check workflow branches.
- [x] 2.2 Add references for model mesh, model authority, handoff contracts, and closure reports.
- [x] 2.3 Update existing contract and boundary references to separate `GuardContract` from `ModelMeshContract`.

## 3. Runtime ModelMesh Core

- [x] 3.1 Add `worldguard.mesh` dataclasses for `ModelAuthority`, `ModelNode`, `ModelEdge`, `WorldStateSnapshot`, `ModelMeshContract`, `MeshFinding`, and `MeshReport`.
- [x] 3.2 Implement `run_model_mesh` with node contract execution, authority checks, handoff checks, freshness checks, cycle detection, child ledger preservation, and aggregate status.
- [x] 3.3 Export the mesh API from `worldguard.__init__`.

## 4. CLI, Examples, And Tests

- [x] 4.1 Add `worldguard mesh-check --mesh <path>` CLI support.
- [x] 4.2 Add generic mesh example fixture under `examples/model_mesh/`.
- [x] 4.3 Add tests for authority overreach, stale source gaps, forbidden and unallowed handoff failures, dependency cycles, child-gap preservation, API export, and CLI JSON output.
- [x] 4.4 Run existing and new validation commands.

## 5. Documentation And Skill Sync

- [x] 5.1 Update README and relevant docs to describe WorldGuard as unit-contract plus model-mesh core.
- [x] 5.2 Sync repository skill changes to `C:\Users\liu_y\.codex\skills\worldguard`.
- [x] 5.3 Validate repository and installed skill copies plus helper commands.

## 6. Local Git Sync And Completion Audit

- [x] 6.1 Review Git status without reverting unrelated peer work.
- [x] 6.2 Create a local commit for the ModelMesh core change.
- [x] 6.3 Run final requirement-by-requirement completion audit.

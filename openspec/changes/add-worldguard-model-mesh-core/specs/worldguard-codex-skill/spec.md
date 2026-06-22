## MODIFIED Requirements

### Requirement: Contract-first Prompt Contract
The WorldGuard skill SHALL instruct Codex to build or inspect a structured `GuardContract` for unit-level checks and a structured `ModelMeshContract` for multi-model checks before giving a PASS/FAIL/GAP/BOUNDARY_EXCEEDED conclusion.

#### Scenario: Multi-model pass is not inferred from child pass
- **WHEN** a user asks whether several related models jointly support a claim
- **THEN** the skill instructs Codex to inspect model nodes, authority, handoffs, freshness, and closure instead of reporting whole-mesh PASS from child-local PASS results alone.

### Requirement: Local Runtime Integration
The WorldGuard skill SHALL provide guidance for calling the installed runtime for both single-contract checks and mesh checks.

#### Scenario: Skill references mesh helper path
- **WHEN** the local skill is inspected
- **THEN** it includes a `mesh-check` command example and references for ModelMesh, authority, handoff, and closure concepts.

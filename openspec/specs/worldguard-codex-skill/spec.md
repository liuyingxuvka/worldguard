# worldguard-codex-skill Specification

## Purpose
TBD - created by archiving change productize-worldguard-mvp. Update Purpose after archive.
## Requirements
### Requirement: Local WorldGuard Skill
The system SHALL install a local Codex skill named `worldguard` under the user skill directory with valid `SKILL.md` frontmatter and concise usage instructions.

#### Scenario: Skill files exist
- **WHEN** the local skill directory is inspected
- **THEN** `SKILL.md`, references, and a runnable helper script exist under the local Codex skill directory, such as `$CODEX_HOME/skills/worldguard`.

### Requirement: Contract-first Prompt Contract
The WorldGuard skill SHALL instruct Codex to build or inspect a structured `GuardContract` for unit-level checks and a structured `ModelMeshContract` for multi-model checks before giving a PASS/FAIL/GAP/BOUNDARY_EXCEEDED conclusion.

#### Scenario: Narrative-only pass is forbidden
- **WHEN** a user asks whether a claim is valid but provides no model fields
- **THEN** the skill instructs Codex to return `GAP` or ask for missing model fields instead of narrative-only PASS.

#### Scenario: Multi-model pass is not inferred from child pass
- **WHEN** a user asks whether several related models jointly support a claim
- **THEN** the skill instructs Codex to inspect model nodes, authority, handoffs, freshness, and closure instead of reporting whole-mesh PASS from child-local PASS results alone.

### Requirement: Local Runtime Integration
The WorldGuard skill SHALL provide guidance for calling the installed runtime for both single-contract checks and mesh checks.

#### Scenario: Skill helper invokes package
- **WHEN** the skill helper script runs against the fuel-cell example
- **THEN** it imports `worldguard` and returns a JSON check result.

#### Scenario: Skill references mesh helper path
- **WHEN** the local skill is inspected
- **THEN** it includes a `mesh-check` command example and references for ModelMesh, authority, handoff, and closure concepts.

### Requirement: Codex entry is a thin executable shell
The `worldguard` Codex skill SHALL keep only purpose, use and do-not-use boundaries, minimum task facts, exact public task-shape selection, complete claim-derived internal Guard coverage, first actions, conditional reference loading, terminal statuses, and claim boundaries in its always-loaded shell. Detailed commands, examples, mesh rules, template rules, and task-local revision rules SHALL remain in shape- or Guard-selected references.

#### Scenario: Ordinary bounded check enters WorldGuard
- **WHEN** Codex receives enough typed facts for one bounded WorldGuard task shape and its structured claim semantics
- **THEN** it can select the shape, derive every required Guard, and start their native actions without loading unrelated mesh, template, or predictive protocols

#### Scenario: Deep route is selected
- **WHEN** the selected shape or any derived Guard declares a deepening trigger that is true
- **THEN** Codex loads the declared deep reference before making any closure claim

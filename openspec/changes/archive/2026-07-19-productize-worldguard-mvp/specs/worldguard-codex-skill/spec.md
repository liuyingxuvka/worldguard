## ADDED Requirements

### Requirement: Local WorldGuard Skill
The system SHALL install a local Codex skill named `worldguard` under the user skill directory with valid `SKILL.md` frontmatter and concise usage instructions.

#### Scenario: Skill files exist
- **WHEN** the local skill directory is inspected
- **THEN** `SKILL.md`, references, and a runnable helper script exist under the local Codex skill directory, such as `$CODEX_HOME/skills/worldguard`.

### Requirement: Contract-first Prompt Contract
The WorldGuard skill SHALL instruct Codex to build or inspect a structured `GuardContract` before giving a PASS/FAIL/GAP/BOUNDARY_EXCEEDED conclusion.

#### Scenario: Narrative-only pass is forbidden
- **WHEN** a user asks whether a claim is valid but provides no model fields
- **THEN** the skill instructs Codex to return `GAP` or ask for missing model fields instead of narrative-only PASS.

### Requirement: Local Runtime Integration
The WorldGuard skill SHALL provide a script that can call the installed `worldguard` runtime for local checks.

#### Scenario: Skill helper invokes package
- **WHEN** the skill helper script runs against the fuel-cell example
- **THEN** it imports `worldguard` and returns a JSON check result.

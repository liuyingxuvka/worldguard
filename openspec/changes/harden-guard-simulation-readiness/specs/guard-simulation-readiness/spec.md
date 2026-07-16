## ADDED Requirements

### Requirement: Module CLI Must Match Installed CLI

WorldGuard SHALL expose a module CLI entrypoint that delegates to the same implementation as the installed console script.

#### Scenario: Module help runs

- **WHEN** a maintainer runs `python -m worldguard --help`
- **THEN** the command exits successfully
- **AND** the available subcommands match the console-script CLI surface.

### Requirement: Skill Contract Must Block Parallel SkillGuard Paths

WorldGuard skill contracts SHALL declare that duplicate SkillGuard-owned execution paths are invalid.

#### Scenario: Contract route check runs

- **WHEN** the SkillGuard route checker inspects the source or installed WorldGuard skill contract
- **THEN** the route check passes
- **AND** the readiness claim does not rely on undocumented parallel routes.

### Requirement: Release Metadata Must Be Synchronized

WorldGuard SHALL keep source version, editable install metadata, local skill copy, git tag, and GitHub release version aligned for patch releases.

#### Scenario: Editable install is verified

- **WHEN** the package is reinstalled locally after a patch bump
- **THEN** `importlib.metadata.version("worldguard")` reports the release version
- **AND** the imported module path points at the active repository.

### Requirement: Verification Reuses The Frozen Parent Receipt

OpenSpec verification SHALL consume one current portable parent receipt whose
covered inputs include the WorldGuard suite, module CLI probes, readiness
audit, and release synchronization checks. It MUST NOT execute those owners
again or invoke `--resume` as an audit.

#### Scenario: Current parent evidence already exists

- **WHEN** the frozen validation owner has already completed the governed checks
- **THEN** OpenSpec reads and verifies the exact parent receipt
- **AND** does not launch pytest, CLI probes, the readiness script, FlowGuard audit, or another owner.

### Requirement: Formal Guard Candidates Bind A Fresh Task Purpose

WorldGuard SHALL require the AI to declare a fresh target-local purpose
contract before constructing each formal per-Guard child candidate. The
declaration SHALL identify the task and model instance, state in plain language
what this particular child is intended to prevent, state its unsupported
boundary, select a non-empty one-or-many set of concrete failures, and bind one
task-local known-good plus exactly one task-local known-bad and WorldGuard-native
oracle for every selected failure. The candidate SHALL carry the exact task
declaration and proof fingerprints. Both the unit kernel and semantic executor
SHALL verify that binding before proof.

#### Scenario: Invalid candidate purpose binding reaches a real proof entry

- **WHEN** a formal Guard candidate has a missing, empty, or stale task-purpose binding
- **OR** candidate construction precedes task-purpose declaration and native proof freeze
- **OR** its selected failure proof is incomplete, belongs to another Guard/model instance, or names an unknown native oracle
- **THEN** the runtime rejects the candidate before the Guard or semantic proof runs
- **AND** reports the stable missing, stale, order, proof, instance, or oracle rejection class.

#### Scenario: One Guard child declares several prevention targets

- **WHEN** the AI selects two or more failures for one formal Guard child
- **THEN** WorldGuard proves and preserves each failure independently
- **AND** one passing bad-case reaction cannot hide another unproved selected failure.

### Requirement: Family Inventory Is Baseline, Not Task Authority

WorldGuard SHALL treat `GUARD_MODEL_PURPOSES`, the native good cases, and the
protected failure-code inventory as family baseline and oracle-catalog evidence
only. It SHALL NOT automatically expand them into the purpose of every real
child.

#### Scenario: Only the family fingerprint is present

- **WHEN** a formal child carries the current family fingerprint but no fresh task-model-instance declaration and proof
- **THEN** WorldGuard blocks before child construction or execution
- **AND** does not infer a purpose from the Guard name or copy the entire catalog as a fallback.

#### Scenario: A task needs a new failure kind

- **WHEN** a task declares a failure with no WorldGuard-owned runtime code and native oracle
- **THEN** the declaration blocks until the family catalog and regression proof are extended
- **AND** SkillGuard does not define or reinterpret the missing domain semantics.

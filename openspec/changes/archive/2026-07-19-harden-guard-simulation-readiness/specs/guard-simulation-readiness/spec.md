## ADDED Requirements

### Requirement: Module CLI Must Match Installed CLI

WorldGuard SHALL expose a module CLI entrypoint that delegates to the same implementation as the installed console script.

#### Scenario: Module help runs

- **WHEN** a maintainer runs `python -m worldguard --help`
- **THEN** the command exits successfully
- **AND** the available subcommands match the console-script CLI surface.

### Requirement: Author Control Must Not Enter The Consumer

WorldGuard SHALL keep SkillGuard contracts, manifests, receipts, and runtime
control in the author source only. The installed WorldGuard consumer SHALL be
identified by one exact target-owned release manifest, SHALL match the
author-source consumer projection byte for byte, and SHALL contain zero
`.skillguard` paths.

#### Scenario: Source and installed boundaries are checked

- **WHEN** release readiness inspects the WorldGuard author source and installed consumer
- **THEN** the source has one current SkillGuard contract authority
- **AND** the installed tree matches one exact `consumer-release.json`
- **AND** no installed `.skillguard` path or alternate authority exists.

#### Scenario: Installed author control is present

- **WHEN** any `.skillguard` path appears in the installed consumer
- **OR** a source, manifest, or installed byte inventory differs
- **THEN** release readiness fails visibly
- **AND** does not read an alternate source, compatibility copy, or fallback route.

### Requirement: Release Metadata Must Be Synchronized

WorldGuard SHALL keep source version, editable install metadata, local skill copy, git tag, and GitHub release version aligned for patch releases.

#### Scenario: Editable install is verified

- **WHEN** the package is reinstalled locally after a patch bump
- **THEN** `importlib.metadata.version("worldguard")` reports the release version
- **AND** the imported module path points at the active repository.

### Requirement: Archive Gate Replays The Frozen Parent Aggregation

The WorldGuard archive gate SHALL replay one current immutable SkillGuard parent
aggregation whose covered inputs include the WorldGuard suite, module CLI
probes, readiness audit, and release synchronization checks. The replay MUST be
read-only and MUST NOT execute those owners again or invoke `--resume` as an
audit. Official OpenSpec validation SHALL remain limited to its proposal,
design, specifications, and tasks; it SHALL NOT register an external receipt
provider or adapter.

#### Scenario: Current parent evidence already exists

- **WHEN** the frozen validation owner has already completed the governed checks
- **THEN** the WorldGuard release gate read-only replays the exact parent aggregation
- **AND** official OpenSpec strictly validates its own change artifacts
- **AND** does not launch pytest, CLI probes, the readiness script, FlowGuard audit, or another owner.

### Requirement: Validation Is Affected-Only Until One Frozen Final Gate

WorldGuard SHALL bind every maintained input to an exact validation owner.
Current-input behavior and template-selection behavior SHALL have independent
shards and immutable receipts. A source change SHALL invalidate only owners
whose declared components, target-input roles, genuine receipt dependencies,
toolchain, or environment consume that change. Progress checkboxes, reports,
receipts, and publication state MUST NOT be validation freshness inputs.

#### Scenario: One behavior shard changes

- **WHEN** only current-input behavior or only template-selection behavior changes
- **THEN** only that shard's owner is scheduled
- **AND** the unchanged shard remains current by exact receipt identity
- **AND** no run-all fallback is selected.

#### Scenario: Final release gate is requested

- **WHEN** source, toolchain, impact plan, installation, environment, and target-input identities are frozen
- **THEN** exactly one foreground full owner may execute
- **AND** all later consumers replay its terminal receipt without invoking `--resume` or another owner.

### Requirement: Publication Is A Single Post-Archive Sequence

WorldGuard SHALL complete the SkillGuard read-only replay and official OpenSpec
strict validation, then archive the change before publication. It SHALL then
perform one commit, branch push, annotated tag, and GitHub Release sequence for
the frozen version. Publication itself SHALL NOT invalidate validation evidence
or trigger another full owner.

#### Scenario: Frozen release is published

- **WHEN** the archived source and installed projection have current terminal evidence
- **THEN** one commit is pushed, one annotated version tag is created, and one GitHub Release is published
- **AND** the post-publication check compares identities only
- **AND** no source edit, test owner, resume, or second release is started.

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

### Requirement: Guard Inputs Have One Current Authority

WorldGuard SHALL read each Guard input from one declared current `inputs.*`
location. Normal runtime MUST reject known former world-model fields, nested
aliases, alternate observation shapes, and renamed causal/event/norm fields.
It MUST NOT search multiple sources or select the first non-empty value.

#### Scenario: A current contract is supplied

- **WHEN** a caller provides the required Guard data at its current `inputs.*` location
- **THEN** the owning Guard and semantic executor consume that exact data
- **AND** no alternate source participates.

#### Scenario: An old contract is supplied

- **WHEN** a known former input path or renamed field is present
- **THEN** contract loading fails visibly with the retired path
- **AND** the caller must migrate the file directly before retrying.

### Requirement: Template No-Match Is A Blocker

WorldGuard SHALL compose the shared base fragment only after exactly one
current candidate matches. Zero candidates MUST block and MUST NOT activate the
base fragment as a bounded, structural, or semantic success path.

#### Scenario: No candidate matches

- **WHEN** the declared applicability facts match no candidate
- **THEN** selection reports `no_match`
- **AND** construction fails with `TEMPLATE_SELECTION_NO_MATCH`.

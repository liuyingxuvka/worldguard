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

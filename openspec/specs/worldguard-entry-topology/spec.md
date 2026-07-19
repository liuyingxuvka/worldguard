# worldguard-entry-topology Specification

## Purpose
TBD - created by archiving change enforce-worldguard-single-entry-internal-guard-routes. Update Purpose after archive.
## Requirements
### Requirement: WorldGuard has one public entrypoint
The project SHALL expose exactly one installable Codex skill named `worldguard` and exactly one package console named `worldguard`. EventGuard, AgentGuard, SpaceGuard, ResourceGuard, CausalGuard, ConflictGuard, and NormGuard MUST remain internal WorldGuard routes and MUST NOT be published as child skills, consoles, aliases, or compatibility entrypoints.

#### Scenario: Public entrypoint inventory is verified
- **WHEN** the target-native topology checker inspects project scripts and consumer skill directories
- **THEN** it SHALL find exactly `worldguard` and reject every direct child Guard surface

### Requirement: Seven internal Guards remain complete routes
WorldGuard SHALL retain exactly seven internal Guard routes. Each route MUST bind one claim-derived expectation/prediction boundary, one native Guard runner, one `GuardResult` response, one purpose-contract validation owner, one semantic executor, and the exact terminal Guard statuses `PASS`, `FAIL`, `GAP`, and `BOUNDARY_EXCEEDED`.

#### Scenario: Internal route contract matches runtime
- **WHEN** the topology checker compares the declared route contract with `GUARD_RUNNERS`, `EXECUTOR_REGISTRY`, the Guard status enum, and the Guard purpose inventory
- **THEN** every set and binding SHALL match exactly with no missing, duplicate, or extra Guard

#### Scenario: One internal route loses validation
- **WHEN** a route lacks its semantic executor or purpose-contract validator
- **THEN** the topology check SHALL fail instead of treating another Guard as a replacement

### Requirement: Predictive claims remain Guard-bounded
EventGuard and CausalGuard SHALL participate in predictive closure only through the existing claim-derived predictive-depth contract. AgentGuard, SpaceGuard, ResourceGuard, ConflictGuard, and NormGuard SHALL preserve bounded expectation and constraint checks without independently licensing future prediction.

#### Scenario: Non-predictive Guard returns pass
- **WHEN** a non-predictive internal Guard returns `PASS`
- **THEN** that result SHALL license only its declared bounded semantics and SHALL NOT become predictive evidence

#### Scenario: Predictive request lacks required depth
- **WHEN** prediction is requested and EventGuard or CausalGuard predictive coverage is incomplete
- **THEN** WorldGuard SHALL preserve `GAP` or `BOUNDARY_EXCEEDED` at aggregate closure and SHALL NOT retry through another Guard

### Requirement: Source and consumer runtime topology stay identical
The authoritative runtime and bundled consumer runtime SHALL contain identical internal Guard registry, semantic executor, validation, response, and terminal behavior for this topology.

#### Scenario: Bundled runtime drifts
- **WHEN** any governed runtime file differs between the repository package and `skills/worldguard/runtime/worldguard`
- **THEN** the topology checker SHALL fail before SkillGuard maintenance closure

### Requirement: Validation binds only the current runtime authority
FlowGuard alignment SHALL bind native depth obligations directly to `worldguard/execution_depth.py`. The retired `worldguard/skillguard_depth.py` path MUST have zero current authority and MUST NOT remain as a compatibility or fallback validation path.

#### Scenario: Retired validation path remains
- **WHEN** a current FlowGuard alignment file still names `worldguard/skillguard_depth.py`
- **THEN** the topology checker SHALL fail visibly instead of resolving or retrying through that retired path

### Requirement: The contracted entry topology has one version identity
The public child-entrypoint contraction SHALL be frozen as pre-1.0 source
version `0.3.0`. Root `VERSION`, package metadata, README source labels,
changelog, authoritative runtime `__version__`, and bundled consumer runtime
`__version__` SHALL agree before the candidate is published.

#### Scenario: Candidate is checked before installation
- **WHEN** the `0.3.0` candidate topology is validated on its review branch
- **THEN** the target-native version/topology check and recompiled SkillGuard
  contract SHALL pass on the exact candidate tree
- **AND** no installed projection, tag, or GitHub Release SHALL be claimed

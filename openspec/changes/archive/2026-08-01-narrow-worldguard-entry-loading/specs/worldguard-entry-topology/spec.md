## ADDED Requirements

### Requirement: Every internal route publishes a complete admission capsule
Each of the seven internal Guard routes SHALL declare positive applicability semantics, forbidden semantics, required input fields, one first native action, one primary reference path, an optional deepening trigger, and a claim boundary. The topology check SHALL compare those fields with current runtime ownership and reject missing, duplicate, or unresolvable bindings.

#### Scenario: Route capsule is complete
- **WHEN** the internal route registry is audited
- **THEN** every Guard has one complete admission capsule whose paths and owners resolve in the current consumer projection

#### Scenario: Route points to missing reference
- **WHEN** a route's primary or conditionally mandatory reference does not exist
- **THEN** the topology check fails before installation or release

## MODIFIED Requirements

### Requirement: The contracted entry topology has one version identity
The public entry-loading refinement SHALL be frozen as pre-1.0 source version `0.7.1`. Root `VERSION`, package metadata, README source labels, changelog, authoritative runtime `__version__`, and bundled consumer runtime `__version__` SHALL agree before the candidate is published.

#### Scenario: Candidate is checked before installation
- **WHEN** the `0.7.1` candidate topology is validated on its review branch
- **THEN** the target-native version/topology check and recompiled SkillGuard contract SHALL pass on the exact candidate tree
- **AND** installed projection, Git tag, and GitHub Release identities SHALL each be verified separately before they are claimed


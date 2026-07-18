## Why

WorldGuard already exposes one package and one skill, but its seven Guard implementations are not yet governed by one explicit topology contract that proves each internal route retains its full prediction, response, validation, and terminal behavior. Without that contract, future maintenance could accidentally publish child skills or collapse a Guard into a partial helper.

## What Changes

- Declare `worldguard` as the sole skill and console entrypoint.
- Declare EventGuard, AgentGuard, SpaceGuard, ResourceGuard, CausalGuard, ConflictGuard, and NormGuard as exact internal routes, not installable skills, aliases, or consoles.
- Bind every internal route to its existing runner, semantic executor, prediction/expectation boundary, `GuardResult` response, validation owner, and visible terminal statuses.
- Add a target-native topology checker that rejects missing routes, alternate public entrypoints, runtime/distribution drift, and incomplete internal route contracts.
- Extend the FlowGuard and SkillGuard models so the seven routes remain independently complete without becoming globally routed consumer skills.

## Capabilities

### New Capabilities

- `worldguard-entry-topology`: Defines and verifies the sole public entrypoint and seven complete internal Guard routes.

### Modified Capabilities

None.

## Impact

Affected surfaces include the WorldGuard skill instructions, a target-owned topology reference, bundled runtime parity, topology tests, FlowGuard topology modeling, and the WorldGuard SkillGuard contract. Guard algorithms, package installation, global routing, Git publication, tags, and releases remain outside this change.

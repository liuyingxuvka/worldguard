## Why

WorldGuard already has deep task-local modeling and seven complete internal Guard routes, but its public skill entry loads too much route-independent detail before the task shape is known. This makes ordinary bounded checks unnecessarily expensive and obscures the exact point where predictive work must deepen.

## What Changes

- Keep `worldguard` as the only public skill, select exactly one public task shape from typed facts, and derive the complete one-or-more internal Guard set from structured claim semantics through a compact seven-route capsule.
- Make every route expose positive applicability, forbidden conditions, required inputs, first native action, conditional reference, deepening trigger, and claim boundary.
- Keep bounded Event/Agent/Space/Resource/Conflict/Norm work light, while requiring Event/Causal predictive work to load and execute the existing task-local model-deepening protocol.
- Move detailed commands and long-form contracts out of the always-loaded entry shell without deleting or weakening existing semantics.
- Add prompt-bundle and load-graph checks that fail when a mandatory selected-shape/Guard reference is missing or an unrelated deep reference is loaded.
- Repair the archived OpenSpec input path in the model-regression manifest and renew the model-system authority after the final source is frozen.

## Capabilities

### New Capabilities

- `worldguard-route-loading`: Defines typed route admission, conditional reference loading, prompt-budget behavior, and mandatory deepening for predictive routes.

### Modified Capabilities

- `worldguard-codex-skill`: The public Codex entry becomes a thin shell whose selected task shape and complete claim-derived Guard set own the first actions and reference load.
- `worldguard-entry-topology`: The seven internal routes gain complete, machine-checkable admission and load metadata while remaining private implementation routes.
- `world-model-deepening`: Predictive deepening is reached by an explicit route trigger and remains the existing evidence-derived task-local loop rather than a self-reported understanding level.

## Impact

Affected surfaces include `skills/worldguard/SKILL.md`, the internal route registry, route/topology and prompt-load checks, the bundled prompt, SkillGuard maintenance contracts, FlowGuard model inputs and authority, documentation, and patch version metadata. Public package contracts, Guard terminal statuses, and the single public `worldguard` console remain compatible.

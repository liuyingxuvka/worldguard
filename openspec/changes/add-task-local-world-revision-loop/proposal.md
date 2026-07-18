## Why

WorldGuard can execute declared scenarios, holdouts, interventions, and counterfactuals, but its current observation handling mainly proves coverage and does not compare frozen predictions with real observed values or relationships. This change adds a reversible task-local world-model revision loop while leaving WorldGuard's core Guard rules and predictive-coverage thresholds unchanged.

## What Changes

- Add a versioned `PredictionSnapshot` that freezes the base world-model identity, initial state, intervention, expected values, expected relationships, and weakening conditions before observation.
- Add an `ObservedWorldSnapshot` that preserves actual numeric values and relationships instead of reducing observations to timepoint presence.
- Compare one frozen prediction with one real observation and classify mismatches including initial state, transition, causal relation, resource, agent, observation mapping, and other bounded WorldGuard-native categories.
- Add a task-local candidate world-model v2 contract with restricted revision operations and explicit original-scenario plus real-holdout-observation revalidation.
- Accept a candidate only when all declared checks pass; reject or roll back while preserving v1 when they fail.
- Add native CLI commands, WorldGuard skill guidance, bundled runtime projection, and focused regression tests.
- Keep task models independent and local. Do not share runtime or models with another Guard, alter core thresholds, perform meta-learning, or promote an episode into a reusable default.

## Capabilities

### New Capabilities

- `task-local-world-revision`: Frozen world predictions, value-bearing real observations, mismatch classification, and reversible candidate-world-model revision.

### Modified Capabilities

None.

## Impact

- New WorldGuard-native contracts and evaluation logic under `worldguard/`.
- Native CLI JSON commands and package exports.
- WorldGuard `SKILL.md`, references, and bundled runtime projection.
- Focused prediction, observation, mismatch, candidate acceptance, rejection, rollback, and real-holdout tests.
- Existing user changes in project adoption files remain untouched; no package release or user-skill installation is included.

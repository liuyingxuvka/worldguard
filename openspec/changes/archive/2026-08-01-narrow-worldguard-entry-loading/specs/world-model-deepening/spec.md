## ADDED Requirements

### Requirement: Predictive deepening is entered through route evidence
The task-local model-deepening loop SHALL be loaded when the selected EventGuard or CausalGuard capsule identifies predictive intent, causal intervention, unresolved predictive coverage, or a current counterexample. The selected route MUST load the full existing deepening protocol before evaluating closure and MUST NOT use a model-authored understanding label as evidence.

#### Scenario: Bounded event check has no predictive intent
- **WHEN** EventGuard checks only a bounded declared event and no predictive trigger is true
- **THEN** WorldGuard runs the bounded native action without loading the task-local predictive loop

#### Scenario: Current evidence exposes a predictive gap
- **WHEN** a bounded or predictive run exposes a state, transition, branch, intervention, counterfactual, or holdout gap
- **THEN** the selected route loads task-local deepening and preserves the gap until native evidence resolves it or returns an explicit terminal


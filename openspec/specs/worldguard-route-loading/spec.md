# worldguard-route-loading Specification

## Purpose
Define a small, deterministic WorldGuard entry load graph that selects exactly one public task shape, derives the complete internal Guard set from typed claim semantics, and loads deep material only when that shape or Guard set requires it.
## Requirements
### Requirement: Task shape and Guard coverage are fact-derived and exact
WorldGuard SHALL derive exactly one public task shape from typed request facts and SHALL derive the complete one-or-more internal Guard set from structured claim semantics and declared route predicates. It MUST preserve visible no-match, unmapped-semantic, ambiguity, missing-input, and forbidden-condition results; it MUST NOT choose by keyword score, trust a caller-selected subset, or retry through another Guard after a route failure.

#### Scenario: One task shape and several Guards are required
- **WHEN** typed request facts identify a unit contract and structured atoms require temporal and causal semantics
- **THEN** WorldGuard selects the unit task shape, derives both EventGuard and CausalGuard, and exposes each Guard's first native action

#### Scenario: Several public task shapes remain possible
- **WHEN** the supplied facts cannot distinguish a unit, mesh, task-local revision, or template-pack request
- **THEN** WorldGuard reports the shape ambiguity and the missing discriminating facts without guessing a winner

#### Scenario: Caller omits a derived Guard
- **WHEN** structured claim semantics require two Guards but `target_guards` names only one
- **THEN** WorldGuard preserves the complete derived set and reports the omitted route as a concrete gap

### Requirement: Selected route controls reference loading
The always-loaded entry SHALL contain only shared admission and terminal behavior. Each selected task shape and derived Guard SHALL identify its mandatory first reference and MAY identify additional references guarded by explicit deepening triggers; unrelated deep references MUST remain unloaded.

#### Scenario: Bounded route stays light
- **WHEN** a bounded non-predictive route has enough input for its native check
- **THEN** the prompt bundle contains the entry shell and that route's mandatory reference but excludes predictive deepening material

#### Scenario: Mandatory route reference is absent
- **WHEN** a selected shape or derived Guard's mandatory reference is missing from the prompt bundle
- **THEN** validation fails rather than treating the thin entry shell as complete guidance

### Requirement: Predictive routes deepen by evidence needs
When the request asks for prediction, what-if behavior over time, or causal intervention, the derived set SHALL include EventGuard and CausalGuard as required by current claim semantics, and SHALL load the existing task-local model-deepening protocol until current native evidence closes the modeled task or yields an explicit bounded terminal. It MUST NOT ask the model to declare an understanding level.

#### Scenario: Predictive request selects deepening
- **WHEN** typed facts declare predictive intent for events or causal relations
- **THEN** the selected Guard set loads task-local deepening and requires its prediction, depth, revalidation, gap, and terminal evidence

#### Scenario: Model cannot close the boundary
- **WHEN** required current evidence is missing, contradicted, stalled, or outside the task boundary
- **THEN** WorldGuard preserves the exact non-pass terminal and open gaps instead of self-reporting understanding

### Requirement: Prompt budget has mandatory headroom
The WorldGuard prompt bundle SHALL enforce a declared maximum for the entry shell, each route capsule, and the selected-route bundle while reserving headroom for task evidence and model reasoning. Budget validation MUST NOT permit deletion of mandatory route semantics merely to meet size limits.

#### Scenario: Entry exceeds its declared budget
- **WHEN** the always-loaded entry or a selected-route bundle exceeds its budget
- **THEN** validation fails and identifies the over-budget component


# world-model-deepening Specification

## ADDED Requirements

### Requirement: Predictions carry task and coverage identity

Every non-trivial `PredictionSnapshot` SHALL bind a task purpose, independent coverage-universe fingerprint, assumptions, declared unknowns, and iteration predecessor.

#### Scenario: Shallow prediction
- **GIVEN** a prediction has one expected value but no task coverage or unknown boundary
- **WHEN** task-local depth is evaluated
- **THEN** it is blocked as shallow and cannot license broad world claims

### Requirement: Predictive gaps force candidate continuation

Candidate evaluation SHALL continue when native `predictive_gaps` contain addressable state, transition, branch, perturbation, intervention, counterfactual, or holdout gaps.

#### Scenario: Fact revision without predictive revalidation
- **GIVEN** a fact transaction activates successfully
- **AND** the candidate has not passed the current predictive/depth/holdout checks
- **WHEN** revision closure is evaluated
- **THEN** the candidate is non-terminal and requires another iteration

### Requirement: Iterations preserve candidate identity and gap transitions

Every iteration SHALL record base/candidate identities, input/resolved/introduced gap ids, native receipt identities, and terminal reason.

#### Scenario: New gap after candidate
- **GIVEN** a candidate resolves one mismatch but exposes a new branch gap
- **WHEN** the candidate is evaluated
- **THEN** the new gap remains open and the next iteration is required

### Requirement: External blockers are exact and visible

If a required observation or world fact is unavailable outside the current tools, the result SHALL name the exact external input, why it is required, and which claim is limited.

#### Scenario: Missing external observation
- **GIVEN** a requested observation cannot be obtained locally
- **WHEN** WorldGuard evaluates the task model
- **THEN** it returns `external_input_required` with the input identity and affected claim boundary

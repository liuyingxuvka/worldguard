## MODIFIED Requirements

### Requirement: Fail-closed aggregate projection
WorldGuard MUST NOT project semantic or predictive pass from structural pass, provider availability, child-local pass, caller-selected Guard subsets, or an incomplete expected coverage universe.

#### Scenario: Provider unavailable
- **WHEN** a required semantic provider is unavailable
- **THEN** aggregate semantic closure SHALL remain unavailable and the provider status SHALL be visible

#### Scenario: Predictive coverage is incomplete
- **WHEN** local semantic checks pass but required nodes, Guards, scenarios, horizon, branches, perturbations, interventions, counterfactuals, or holdout evidence are missing
- **THEN** bounded local findings MAY remain visible but aggregate predictive closure SHALL remain `GAP` or `BOUNDARY_EXCEEDED`

### Requirement: Native WorldGuard depth receipt
WorldGuard SHALL emit a receipt containing structural checks, claim atoms, required and executed semantic children, provider states, bindings, findings, discovered/declared/excluded model-node reconciliation, expected/skipped nodes, scenario/horizon/branch/perturbation coverage, per-variable/signal temporal child coverage, native dynamic-floor receipts, predictive gaps, a predictive-license decision, and aggregate claim boundary bound to the current mesh fingerprint.

#### Scenario: Structural-only request
- **WHEN** the caller explicitly requests structural-only validation
- **THEN** the receipt SHALL identify every skipped semantic child and SHALL NOT claim semantic rollout or prediction

#### Scenario: Bounded semantic pass
- **WHEN** a narrow supported executor checks only its declared local subset
- **THEN** the receipt SHALL preserve semantic `PASS` if appropriate but SHALL distinguish it from predictive readiness

### Requirement: Installed portable native evaluator authority
Formal WorldGuard depth and calibration checks SHALL load the complete target-native Python runtime bundled under the installed skill's `.skillguard/runtime` tree. Every bundled source SHALL be part of the V2 implementation authority and every depth/calibration input fingerprint. A global package or editable source checkout SHALL NOT satisfy formal closure.

#### Scenario: Installed runtime file is absent from the contract
- **WHEN** a bundled native runtime source exists but is absent from implementation authority or any depth/calibration input set
- **THEN** compilation, source audit, installed parity, or formal closure SHALL fail closed

#### Scenario: External checkout can replace the installed evaluator
- **WHEN** the bundled runtime is missing or bypassed and an editable WorldGuard checkout remains importable
- **THEN** formal scheduled-production closure SHALL remain blocked rather than accepting the external import

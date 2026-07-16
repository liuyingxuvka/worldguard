## ADDED Requirements

### Requirement: Separate structural and semantic status
WorldGuard SHALL report structural contract status separately from semantic execution and provider availability.

#### Scenario: Shape passes but semantics do not run
- **WHEN** all required fields exist but no semantic executor runs
- **THEN** structural status MAY pass while semantic and rollout status SHALL be `NOT_RUN` or `BOUNDARY_ONLY`

### Requirement: Fail-closed aggregate projection
WorldGuard MUST NOT project semantic pass from structural pass, provider availability, or child-local pass alone.

#### Scenario: Provider unavailable
- **WHEN** a required semantic provider is unavailable
- **THEN** aggregate semantic closure SHALL remain unavailable and the provider status SHALL be visible

### Requirement: Typed semantic input/output binding
Every semantic executor MUST declare the input fields it reads, output fields it writes, supported semantics, and unsupported boundary.

#### Scenario: Unevaluable causal equation
- **WHEN** a causal rule uses an unsupported or incomplete equation
- **THEN** the executor SHALL return an unevaluable finding and SHALL NOT pass the causal model

### Requirement: Known negative semantic probes
WorldGuard SHALL reject missing event axioms, incomplete BDI, RCC8 conflict, resource double consumption, unevaluable causal equations, incomplete conflict, and missing norm conditions.

#### Scenario: Resource double consumption
- **WHEN** two transitions consume the same finite resource beyond the available quantity
- **THEN** resource semantic status SHALL fail with a conservation finding

### Requirement: Native WorldGuard depth receipt
WorldGuard SHALL emit a receipt containing structural checks, executed semantic children, provider states, bindings, findings, skipped children, and aggregate claim boundary.

#### Scenario: Structural-only request
- **WHEN** the caller explicitly requests structural-only validation
- **THEN** the receipt SHALL identify the boundary and SHALL NOT claim semantic rollout

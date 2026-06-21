## Why

WorldGuard currently exists as a technical specification plus route evidence, but not as an installable package, runnable test suite, example CLI, or Codex skill. This change turns the accepted roadmap into a working MVP while keeping FlowPilot process-debt repair explicitly out of scope.

## What Changes

- Add an installable `worldguard` Python package with contracts, ledgers, guard runners, kernel orchestration, CLI, and fuel-cell toy example replay.
- Add tests and fixtures that prove the required PASS, FAIL, GAP, and BOUNDARY_EXCEEDED semantics for every Guard plus read-only Kernel handoff.
- Add a local Codex `worldguard` skill with concise trigger metadata, references, and a script wrapper for local checks.
- Add productization boundaries so route-local `.flowpilot/`, root `evidence/`, stale repair-v4 material, and WG-13 repair checkers are not part of the public package surface.
- Initialize local OpenSpec and Git tracking for the productized project state.
- Exclude FlowPilot final-closure process-debt repair from this change.

## Capabilities

### New Capabilities
- `worldguard-runtime`: Installable Python MVP for GuardContract, GuardResult, ledgers, seven Guard runners, Kernel aggregation, CLI, examples, and tests.
- `worldguard-codex-skill`: Local Codex skill that guides agents to create structured WorldGuard contracts, run checks, and avoid narrative-only acceptance.
- `worldguard-productization`: Public-project packaging, documentation, examples, ignore rules, and cleanup boundaries for non-core route evidence.

### Modified Capabilities
- None.

## Impact

- Adds package files under `worldguard/`.
- Adds fixtures and tests under `tests/` and `examples/`.
- Adds OpenSpec artifacts under `openspec/`.
- Adds a local installable skill under `C:\Users\liu_y\.codex\skills\worldguard`.
- Adds packaging and Git hygiene files such as `pyproject.toml`, `README.md`, and `.gitignore`.

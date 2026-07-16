## 1. Runtime Entry

- [x] Add `worldguard.__main__` as a thin CLI wrapper.
- [x] Add focused regression coverage for module execution.

## 2. Skill Contract

- [x] Update source and installed WorldGuard skill contract anti-bypass wording.
- [x] Re-run SkillGuard contract checks.

## 3. Version And Sync

- [x] Bump package version for a patch release.
- [x] Reinstall editable package and verify metadata.
- [x] Sync installed skill folder.

## 4. Release

- [x] Run package tests and model smoke checks.
- [x] Commit, tag, push, and publish the release.

## Verification Evidence

- `python -m pytest tests -q`: 25 passed.
- `python -m worldguard --help`: passed.
- `python -m worldguard check --example fuel_cell`: passed.
- `openspec validate harden-guard-simulation-readiness --strict`: valid.
- Source and installed WorldGuard SkillGuard checks: passed.

## 5. Current Receipt-Only Closure

- [x] Replace direct validation commands with one fail-closed portable parent-receipt consumer.
- [ ] Consume the frozen final parent receipt and archive without rerunning any validation owner.

## 6. Formal Guard Candidate Task-Purpose Binding

- [x] Require and freeze a fresh task/model-instance purpose declaration and its native per-failure proof before every formal per-Guard child candidate is constructed.
- [x] Carry exact declaration/proof/family-catalog/candidate fingerprints, selected failure ids, task/run/model identity, and freeze/construction order in the candidate.
- [x] Reject missing, empty, unproved, stale, wrong-instance, and out-of-order bindings in both real unit and semantic proof entries.
- [x] Add focused runtime regressions and an executable FlowGuard ordering-hazard model.
- [x] Compile current SkillGuard authority and run focused tests, FlowGuard checks, project audits, and strict OpenSpec validation.
- [x] Install/synchronize the updated WorldGuard skill and refresh the global router after parent-level validation authorizes that separate step.

## 7. Per-Model Dynamic Purpose Correction

- [x] Reclassify `GUARD_MODEL_PURPOSES`, native good cases, and the protected failure inventory as family baseline/oracle-catalog regression authority only.
- [x] Add a required parent-task declaration for every formal Guard child with task/model-instance identity, plain-language purpose, boundary, and a non-empty one-or-many selected failure universe.
- [x] Require one task-local known-good and exactly one known-bad with a WorldGuard-native status/code oracle for every selected failure; reject unknown or incomplete proof.
- [x] Make `GuardContract.for_guard` consume the explicit declaration and remove automatic family-purpose synthesis/fallback.
- [x] Make unit and semantic proof entries independently verify exact task declaration, proof fingerprints, order, Guard/model identity, and selected failure completeness.
- [x] Update skill/reference guidance, real examples, fixtures, and focused one-failure/multi-failure/negative tests without adding an optional mode.
- [x] Recompile the affected SkillGuard projection after source freeze, then leave install and full-family validation to their single frozen owners.

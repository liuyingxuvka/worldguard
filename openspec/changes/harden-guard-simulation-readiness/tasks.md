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
- [ ] Commit, tag, push, and publish the release.

## Verification Evidence

- `python -m pytest tests -q`: 25 passed.
- `python -m worldguard --help`: passed.
- `python -m worldguard check --example fuel_cell`: passed.
- `openspec validate harden-guard-simulation-readiness --strict`: valid.
- Source and installed WorldGuard SkillGuard checks: passed.

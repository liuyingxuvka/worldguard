## Design

WorldGuard readiness is modeled as:

`Claim model + mesh contract + skill contract + installed package -> executable check result`

The fix is deliberately small. The package keeps the existing `worldguard.cli:main` implementation and exposes it through `worldguard.__main__`. This avoids a second CLI path.

Skill readiness is checked through the existing SkillGuard contract scripts. The contract text must state that duplicate SkillGuard-owned execution paths are invalid, because the route checker enforces that as the anti-bypass boundary.

## Validation

- Run package tests.
- Run `python -m worldguard --help`.
- Run fuel-cell example and model-mesh example.
- Reinstall editable package and verify import path plus metadata version.
- Re-run SkillGuard route checks on source and installed skill copies.

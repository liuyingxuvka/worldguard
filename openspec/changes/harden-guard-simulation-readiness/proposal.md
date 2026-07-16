## Why

WorldGuard already has model-mesh checks, but the local package entrypoint and installed metadata drift can make a skill look ready while the runnable model path is not synchronized.

## What Changes

- Add a direct module entrypoint so `python -m worldguard` runs the same CLI as the installed script.
- Keep source package version, editable install metadata, installed skill guidance, and release records aligned.
- Treat skill contract checks as part of readiness, not optional documentation.
- Require the AI to declare a fresh task-model-instance purpose for every
  formal Guard child before construction: what this particular model should
  prevent, one or more concrete failures, its unsupported boundary, and the
  WorldGuard-native good/bad proof for every selected failure.
- Keep the current family purpose/failure inventory as an extensible native
  oracle catalog and family regression baseline only. It must not silently
  choose one fixed purpose or the entire family failure universe for every
  real Guard child.

## Impact

Affected surfaces: `worldguard`, `skills/worldguard`, installed `worldguard` skill, package metadata, OpenSpec and FlowGuard adoption records.

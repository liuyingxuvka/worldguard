## Why

WorldGuard already has model-mesh checks, but the local package entrypoint and installed metadata drift can make a skill look ready while the runnable model path is not synchronized.

## What Changes

- Add a direct module entrypoint so `python -m worldguard` runs the same CLI as the installed script.
- Keep source package version, editable install metadata, installed skill guidance, and release records aligned.
- Treat skill contract checks as part of readiness, not optional documentation.

## Impact

Affected surfaces: `worldguard`, `skills/worldguard`, installed `worldguard` skill, package metadata, OpenSpec and FlowGuard adoption records.

## Why

WorldGuard already has model-mesh checks, but the local package entrypoint and installed metadata drift can make a skill look ready while the runnable model path is not synchronized.

## What Changes

- Add a direct module entrypoint so `python -m worldguard` runs the same CLI as the installed script.
- Keep source package version, editable install metadata, installed skill guidance, and release records aligned.
- Keep SkillGuard contracts and receipts in the author source only, while the
  installed consumer is verified from one exact target-owned release manifest
  and contains zero `.skillguard` paths.
- Require the AI to declare a fresh task-model-instance purpose for every
  formal Guard child before construction: what this particular model should
  prevent, one or more concrete failures, its unsupported boundary, and the
  WorldGuard-native good/bad proof for every selected failure.
- Keep the current family purpose/failure inventory as an extensible native
  oracle catalog and family regression baseline only. It must not silently
  choose one fixed purpose or the entire family failure universe for every
  real Guard child.
- Replace every retired Guard input alias and alternate data-source chain with
  one current `inputs.*` authority. Old files require direct AI migration
  before runtime.
- Make zero template candidates a visible blocker; the shared base fragment is
  never a selectable fallback.
- Split current-input authority and template-selection authority into separate
  affected-validation shards and immutable receipts. A changed shard reruns
  only its own exact owner; unchanged shards are consumed by identity.
- Remove progress checkboxes, runtime reports, and publication metadata from
  validation freshness. Freeze source, toolchain, impact plan, installation,
  and target inputs before one final foreground full owner.
- Replay the frozen parent aggregation through SkillGuard's read-only route,
  strictly validate the official OpenSpec artifacts, and archive the change
  before one commit/push/tag/GitHub Release sequence. OpenSpec does not register
  an external receipt provider or adapter. Post-publication work is a read-only
  identity audit and cannot start another validation owner.

## Impact

Affected surfaces: `worldguard`, `skills/worldguard`, installed `worldguard` skill, package metadata, OpenSpec and FlowGuard adoption records.

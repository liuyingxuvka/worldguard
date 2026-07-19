## Context

WorldGuard already owns canonical `GuardContract` and `ModelMeshContract` loaders, claim-derived Guard routing, task-model-instance purpose declarations, native good/bad proof, candidate freezing, semantic execution, and predictive-depth closure. Today callers still assemble the corresponding dictionaries manually. That repeated construction invites omitted fields, mismatched identities, stale copied fixtures, and accidental reliance on SkillGuard or AI judgment for domain meaning.

This change adds a reusable construction layer before the existing contract loaders. The layer is deliberately not a new Guard router or semantic executor: it can select and compose WorldGuard-authored scaffolding only from explicit applicability facts, resolve caller-supplied slots, fingerprint the resulting instance, and hand the instance to WorldGuard-native validators.

The existing model boundaries remain authoritative:

- `worldguard.contracts` owns canonical GuardContract fields and claim-derived Guard requirements.
- `worldguard.guard_model_contract` owns Guard purposes, protected failures, task-local good/bad proof, and candidate binding.
- `worldguard.mesh` owns ModelMesh fields, authority/handoff topology, semantic coverage, and mesh parsing.
- SkillGuard freezes and reconciles declared native checks only; it cannot select a purpose pack or interpret its semantics.

## Goals / Non-Goals

**Goals:**

- Provide WorldGuard-owned reusable base and purpose-specific template-pack manifests for GuardContract and ModelMeshContract construction.
- Make candidate selection deterministic and observable for zero, one, and many matches.
- Reject ambiguous selection, stale manifests, unknown validator ids, unresolved slots, and field ownership/composition conflicts before a runtime contract is accepted.
- Bind each built instance to the exact registry, selection, pack, binding, output, and native-validator identities through content fingerprints.
- Reuse the current WorldGuard contract and purpose-proof validators instead of recreating their meaning.

**Non-Goals:**

- Templates do not infer a claim's required Guards, select protected failure ids, author a task's purpose/boundary, generate task-local known-good/known-bad evidence, or license semantic/predictive PASS.
- SkillGuard does not become a template registry, template selector, or WorldGuard semantic validator.
- This change does not add compatibility readers, fallback authorities, external dependencies, installation, publication, or OpenSpec program changes.

## Decisions

### 1. Keep template packs inside the WorldGuard runtime

Add `worldguard.template_packs` as a WorldGuard-owned module and mirror it into the skill's bundled runtime projection. A manifest contains a stable schema/version, contract kind, base/candidate role, explicit required/excluded applicability facts, one or more field-owning fragments, native validator ids, and a declared content fingerprint.

Alternative considered: make SkillGuard own a generic Guard-family template catalog. Rejected because SkillGuard is target-neutral and must not infer Guard family meaning, purpose, failure classes, or validator semantics.

### 2. Select from explicit facts with typed 0/1/many outcomes

Selection compares normalized request facts with each candidate's `required_fact_ids` and `excluded_fact_ids`:

- zero candidates selects the one declared base template for the contract kind and records `base_template`;
- one candidate records `selected` and composes it after the base template;
- more than one candidate records `ambiguous`, exposes the exact candidate ids, and blocks building.

No score, priority, declaration order, filename order, or AI preference breaks a tie.

Alternative considered: rank candidates and choose the highest score. Rejected because a silent winner would turn incomplete applicability facts into hidden semantic policy.

### 3. Compose only disjoint field ownership

Each fragment declares the exact leaf field ids it writes, and the declaration must equal the fragment payload's discovered leaf set. Composition rejects any field owned by two fragments, any undeclared write, and any contract-kind mismatch. Slot values are resolved after composition; callers cannot overwrite template fields through a parallel override path.

Alternative considered: last-writer-wins overlays. Rejected because order-dependent replacement hides ownership conflicts and makes fingerprints difficult to interpret.

### 4. Use explicit slots for task-specific content

Templates may place an exact `{"$slot": "slot-id"}` object at a leaf. Build input supplies slot bindings. Missing slots and unused bindings fail closed. This lets reusable packs provide structure while requiring the caller/AI to supply task identity, claim/model content, purpose declarations, topology, and evidence-bearing inputs.

Alternative considered: auto-fill task purpose declarations from the family catalog. Rejected because the family catalog is calibration authority only and cannot become a real task's purpose.

### 5. Bind to existing WorldGuard-native validators

Validator ids resolve only through a WorldGuard-owned registry. GuardContract validation parses and round-trips the canonical contract and invokes the existing per-Guard candidate-purpose proof for every claim-derived Guard. ModelMesh validation parses and round-trips the canonical mesh and validates embedded Guard contracts through the same native boundary. Unknown or missing required validator ids block.

Validator success proves template/contract construction integrity only. It does not replace `run_worldguard`, `run_model_mesh`, native depth evaluation, or SkillGuard supervised closure.

### 6. Fingerprint every authority transition

Canonical SHA-256 fingerprints cover each manifest, the registry, normalized selection request and candidate set, resolved slot bindings, composed output, validator ids/results, and final instance receipt. Any manifest or binding mutation changes identity; a declared manifest fingerprint that no longer matches is rejected as stale.

### 7. Model and verify the workflow with existing governance

Add a real FlowGuard selection/composition/validation model, a full ExistingModelPreflight artifact, and a field lifecycle record. The OpenSpec verification contract freezes focused owners and reserves one full pytest owner for the stable integration snapshot. `tasks.md`, reports, logs, and receipts remain outputs and do not invalidate source checks.

### 8. Project one exact target-owned neutral catalog for SkillGuard

WorldGuard exposes a target-owned adapter for the existing `worldguard.template_pack_builder` route. One request names the exact contract kind, normalized fact ids, and current native registry fingerprint. The adapter must call the current registry validator and native selector; it cannot score words, infer a Guard, or synthesize another candidate list.

The adapter emits exactly these root fields and no others: `schema_version`, `target_id`, `native_owner_id`, `family_id`, `route_id`, `request_fingerprint`, `catalog`, `applicability_results`, and `claim_boundary`. The root schema is `skillguard.target_template_projection.v1`, and the request identity is `sha256:` followed by 64 lowercase hexadecimal characters.

The catalog is an unsealed `skillguard.template_catalog.v1` specification with exactly `schema_version`, `catalog_id`, `revision`, `native_owner_id`, `family_id`, `base_template_id`, `templates`, `harvest_policy`, and `claim_boundary`. Each contract kind is projected as its own family so the catalog has exactly one native base. Every native family manifest maps one-to-one to one unsealed central template specification, and every catalog template has exactly one applicability result derived from the same native selection receipt.

WorldGuard maps native ownership, slots, artifact content, builder source, and validator source into the central neutral fields. Native manifest fingerprints become artifact content-template hashes; native builder and validator implementation fingerprints become their `content_hash` values. The adapter emits neither `manifest_digest` nor `catalog_digest`; central SkillGuard owns only generic validation and canonical sealing. A supplied stale registry identity, an unknown/wrong route, any unknown root field, or any catalog/result inventory mismatch blocks before SkillGuard consumes the projection.

Alternative considered: teach SkillGuard how WorldGuard fact ids map to templates. Rejected because that would create a second applicability authority and make family evolution depend on central lexical policy.

## Risks / Trade-offs

- [Risk] A generic base template can be structurally valid while semantically incomplete. → Mitigation: report the `base_template` outcome explicitly, run native construction validators, and preserve later WorldGuard GAP/BOUNDARY outcomes; never describe base fallback as semantic PASS.
- [Risk] Purpose-specific packs could accidentally become a second Guard router. → Mitigation: selection consumes explicit WorldGuard-derived facts, ties block, and native claim derivation remains authoritative.
- [Risk] A broad template may conceal task-specific evidence. → Mitigation: task identity, purpose declarations, native cases, model content, and mesh topology remain required slots or caller-authored fields and are fingerprinted.
- [Risk] Duplicated source and bundled runtime could drift. → Mitigation: exact parity tests and SkillGuard compiler fingerprints cover both copies.
- [Trade-off] Disallowing implicit overrides requires more explicit fragments and slots. This is intentional because field ownership must remain reviewable and deterministic.
- [Risk] The neutral central interchange schema can evolve independently of WorldGuard. → Mitigation: keep the adapter output exact and unsealed, run the central compiler read-only as a cross-contract check, and treat any schema mismatch as a visible integration gap rather than adding compatibility fields.
- [Risk] Projected eligibility could drift from native selection. → Mitigation: emit exactly one row for every current native family manifest and derive each boolean from the same `TemplatePackRegistry.select` candidate set; candidate equality is a focused invariant.

## Migration Plan

1. Add the new WorldGuard module, built-in manifests, real FlowGuard artifacts, and focused tests without changing existing callers.
2. Export the builder API and document the construction-first workflow in the WorldGuard skill/reference layer.
3. Mirror the module into the bundled SkillGuard runtime and extend the current target-owned native check inputs/tests.
4. Compile the current SkillGuard source contract into its derived contract and manifest.
5. Run focused owners, then one frozen full-test owner, OpenSpec verification, FlowGuard project audit/model checks, and SkillGuard structural checks.
6. Extend the already-completed change with the target-owned neutral projection, update only the affected owners, and retain the earlier full-suite receipt as historical evidence rather than rerunning or treating it as current for the new projection fields.

Rollback is deletion of the new additive module, exports, templates, tests, references, and contract bindings. Existing direct `from_dict` construction remains unchanged.

## Open Questions

- None for this bounded change. Future Guard-family repositories can adopt the same pattern only by defining their own manifests, selection facts, field ownership, and native validators; this implementation does not claim a universal cross-Guard semantic catalog.

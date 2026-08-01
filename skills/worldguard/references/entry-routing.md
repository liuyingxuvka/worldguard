# WorldGuard Entry Routing

Use this reference immediately after the public `worldguard` entry admits a task. It owns prompt loading only; WorldGuard runtime contracts still own semantic behavior.

## 1. Extract typed task facts

Preserve a source span for every extracted fact. Do not treat a keyword as a route decision.

- `task_shape_facts`: whether the request supplies or asks for one unit contract, a model mesh, a task-local reality/revision loop, or a reusable template pack.
- `claim_facts`: claim id/text, structured atoms, requested semantics, predictive intent, and any caller-supplied `target_guards`.
- `input_facts`: concrete world-model fields, models/edges/handoffs, task/coverage/predecessor identities, or template parameters/validator identities.
- `boundary_facts`: explicit unavailable providers, unsupported semantics, missing evidence, and requested claim scope.

If a fact is absent, record it as missing. Do not invent it and do not ask the AI whether it understands.

## 2. Select exactly one public task shape

Read `task_shapes` in `internal-guard-routes.json` and evaluate its declared applicability, forbidden facts, and required inputs.

- `unit_contract`: one claim checked against one explicit world-model boundary.
- `model_mesh`: multi-node ownership, freshness, handoff, coverage, or closure.
- `task_local_revision`: compare a frozen prediction/model with later independent observation and revise within a finite task.
- `template_pack`: select and build reusable target-owned WorldGuard scaffolding.

Zero matching shapes is a visible no-match. Several matching shapes is an ambiguity naming the missing discriminators. Never use a score to choose.

## 3. Derive the complete internal Guard set

For unit, mesh, and task-local work, use structured claim semantics and `worldguard.contracts.derive_required_guards`. The result may contain one or several of EventGuard, AgentGuard, SpaceGuard, ResourceGuard, CausalGuard, ConflictGuard, and NormGuard.

`claim.target_guards` is a completeness assertion, not authority to shrink the denominator. Unmapped semantics, a missing derived Guard, missing required inputs, or a forbidden boundary remains visible. Do not retry through another Guard when one route fails.

Prediction semantics intentionally require EventGuard and CausalGuard together. A bounded Guard `PASS` licenses only that Guard's declared semantics.

## 4. Load only the selected material

Always load each selected shape's `reference_path` and each derived Guard's `reference_path`. Load a conditional reference only when its declared trigger is true.

- Unit shape: `worldguard-contracts.md`; each Guard: `guard-model-contract.md`.
- Mesh shape: `model-mesh.md`; add `handoff-contracts.md` only for handoffs.
- Task-local shape or predictive trigger: `task-local-model-deepening.md`; add `fact-revision.md` only for fact support revision.
- Template shape: `template-packs.md`.
- Final authority or reporting only: `model-authority.md` or `closure-report.md`.

Missing mandatory references block the route. Unrelated deep references stay unloaded so the task retains reasoning headroom.

## 5. Start the declared native action

Use the selected shape and Guard capsules' exact `first_native_action`. Preserve `PASS`, `FAIL`, `GAP`, and `BOUNDARY_EXCEEDED` without collapsing them. Prompt selection proves only that the correct instructions were loaded; it never proves semantic execution, factual truth, installation, or release.


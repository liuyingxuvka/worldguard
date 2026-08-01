## Context

See `proposal.md` for motivation. WorldGuard already has one public entry, seven internal routes, deep task-local revision, target-owned template selection, and current native checks. The problem is load shape rather than missing domain semantics. The current model authority is also stale because one governed input still names an archived OpenSpec path; the stable main spec is the direct current owner.

## Goals / Non-Goals

**Goals:**

- Make the public entry small while preserving every existing hard gate.
- Let typed task facts select exactly one public task shape and structured claim semantics derive the complete one-or-more internal Guard set with native first actions.
- Keep ordinary bounded routes cheap and make predictive routes capable of the existing maximum task-local depth.
- Make reference loading and prompt budgets executable maintenance obligations.
- Renew FlowGuard model authority once, after the full source candidate is frozen.

**Non-Goals:**

- Publishing seven child skills or introducing a new umbrella/runtime router.
- Adding understanding levels, model self-ratings, compatibility readers, or fallback routes.
- Changing public package contract schemas or terminal status meanings.
- Claiming empirical truth from prompt or repository validation.

## Decisions

### Task-shape selection and Guard derivation stay distinct

Add a four-shape admission table for unit, mesh, task-local revision, and template-pack work. Extend the existing `internal-guard-routes.json` instead of adding another Guard registry: each row gains semantic predicates, required fields, first action, references, deep trigger, and claim boundary. The public skill selects one shape, then reuses the existing `derive_required_guards` behavior to compute the complete Guard set. Predictive semantics intentionally map to EventGuard and CausalGuard together.

Alternative considered: force the seven internal Guards into exact-one admission. Rejected because multi-semantic claims legitimately require several Guards and caller subsets cannot shrink coverage.

### Admission uses typed facts and predicates

The AI extracts named request facts with source positions; target-owned checks evaluate one public shape plus the exact claim-derived Guard set. Text keywords may help extract candidate facts but never decide semantic applicability.

Alternative considered: weighted keyword routing. Rejected because equal or misleading wording can silently choose the wrong Guard.

### Thin entry does not weaken deep behavior

Detailed current material is moved, not deleted. Route selection first loads `entry-routing.md`; bounded routes then load their primary reference only. EventGuard/CausalGuard load `task-local-model-deepening.md` when predictive triggers are true. Existing contract, mesh, fact, template, authority, and closure references remain authoritative for their declared triggers.

Alternative considered: create a second simplified runtime. Rejected because it would create dual authority and semantic drift.

### Prompt bundle and load graph are target-owned checks

Add deterministic fixtures for bounded, predictive multi-Guard, template, mesh, no-match, unmapped, shape-ambiguous, forbidden, and missing-reference cases. Checks assert complete Guard coverage, required inclusion, unrelated exclusion, exact paths, and budget/headroom limits. These prove prompt composition only; native runtime/model checks still own domain behavior.

### Model authority renews after candidate freeze

Replace the archived path directly with `openspec/specs/world-model-deepening/spec.md`. After prompt, registry, contracts, tests, and version files stop changing, build one canonical candidate snapshot, derive its affected closure, run the exact current native owners, and activate one accepted `ModelRevisionSet`.

## Risks / Trade-offs

- [A moved rule is no longer loaded when required] -> Mandatory-reference fixtures fail on each route and deep trigger.
- [A smaller prompt is mistaken for shallower behavior] -> Deep-route fixtures require the full existing task-local protocol and native checks remain unchanged.
- [Admission predicates drift from runtime ownership] -> Topology validation compares the registry with runners, semantic executors, status enum, and reference inventory.
- [Budget pressure encourages semantic deletion] -> Separate mandatory-field assertions run before size checks and reserve reasoning headroom.
- [Authority is renewed from mutable inputs] -> Activation occurs only after source freeze and current regression evidence.

## Migration Plan

1. Extend the existing route registry and add references without changing public runtime schemas.
2. Rewrite the entry shell and bundled prompt to consume the registry conditionally.
3. Add target-owned topology, load-graph, and prompt-budget checks; update and compile the SkillGuard contract.
4. Run affected checks, freeze all governed inputs, renew the FlowGuard model authority, and run one final full maintenance validation.
5. Prepare and transactionally activate the clean consumer projection; verify installed currentness separately.
6. Commit, push, tag `v0.7.1`, create the GitHub Release, and verify every identity.

Rollback uses the previous Git/install projection plus the existing model-authority rollback transaction. No compatibility route remains active.

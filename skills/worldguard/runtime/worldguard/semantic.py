from __future__ import annotations

import ast
import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Callable, Mapping

from .contracts import GuardContract


class SemanticStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    GAP = "GAP"
    BOUNDARY_ONLY = "BOUNDARY_ONLY"
    NOT_RUN = "NOT_RUN"


class ProviderStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    NOT_REQUIRED = "NOT_REQUIRED"
    MIXED = "MIXED"


@dataclass(frozen=True)
class SemanticBinding:
    executor_id: str
    guard: str
    input_fields: tuple[str, ...]
    output_fields: tuple[str, ...]
    supported_semantics: tuple[str, ...]
    unsupported_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "executor_id": self.executor_id,
            "guard": self.guard,
            "input_fields": list(self.input_fields),
            "output_fields": list(self.output_fields),
            "supported_semantics": list(self.supported_semantics),
            "unsupported_boundary": self.unsupported_boundary,
        }


@dataclass(frozen=True)
class SemanticExecutionReceipt:
    node_id: str
    guard: str
    status: SemanticStatus
    provider_status: ProviderStatus
    binding: SemanticBinding
    findings: list[dict[str, Any]] = field(default_factory=list)
    consumed_inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    skipped_reason: str = ""
    guard_purpose_contract: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "guard": self.guard,
            "status": self.status.value,
            "provider_status": self.provider_status.value,
            "binding": self.binding.to_dict(),
            "findings": self.findings,
            "consumed_inputs": self.consumed_inputs,
            "outputs": self.outputs,
            "skipped_reason": self.skipped_reason,
            "guard_purpose_contract": self.guard_purpose_contract,
        }


@dataclass(frozen=True)
class NativeDepthReceipt:
    receipt_id: str
    mesh_id: str
    run_id: str
    mesh_fingerprint: str
    structural_checks: list[dict[str, Any]]
    executed_semantic_children: list[str]
    provider_states: dict[str, str]
    bindings: list[dict[str, Any]]
    findings: list[dict[str, Any]]
    skipped_children: list[dict[str, Any]]
    claim_boundary: str
    receipt_version: str = "worldguard.native_depth.v2"
    generated_at: str = ""
    coverage_fingerprint: str = ""
    predictive_profile: str = "bounded"
    claim_atoms: list[dict[str, Any]] = field(default_factory=list)
    required_guards: dict[str, list[str]] = field(default_factory=dict)
    declared_guards: dict[str, list[str]] = field(default_factory=dict)
    missing_guards: dict[str, list[str]] = field(default_factory=dict)
    expected_model_nodes: list[str] = field(default_factory=list)
    discovered_model_nodes: list[str] = field(default_factory=list)
    declared_model_nodes: list[str] = field(default_factory=list)
    excluded_model_nodes: list[dict[str, Any]] = field(default_factory=list)
    model_node_reconciliation_gaps: list[str] = field(default_factory=list)
    executed_model_nodes: list[str] = field(default_factory=list)
    skipped_model_nodes: list[dict[str, Any]] = field(default_factory=list)
    expected_semantic_children: list[str] = field(default_factory=list)
    quantitative_coverage: dict[str, Any] = field(default_factory=dict)
    predictive_gaps: list[str] = field(default_factory=list)
    native_obligation_evidence: list[dict[str, Any]] = field(default_factory=list)
    predictive_claim_licensed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "mesh_id": self.mesh_id,
            "run_id": self.run_id,
            "mesh_fingerprint": self.mesh_fingerprint,
            "structural_checks": self.structural_checks,
            "executed_semantic_children": self.executed_semantic_children,
            "provider_states": self.provider_states,
            "bindings": self.bindings,
            "findings": self.findings,
            "skipped_children": self.skipped_children,
            "claim_boundary": self.claim_boundary,
            "receipt_version": self.receipt_version,
            "generated_at": self.generated_at,
            "coverage_fingerprint": self.coverage_fingerprint,
            "predictive_profile": self.predictive_profile,
            "claim_atoms": self.claim_atoms,
            "required_guards": self.required_guards,
            "declared_guards": self.declared_guards,
            "missing_guards": self.missing_guards,
            "expected_model_nodes": self.expected_model_nodes,
            "discovered_model_nodes": self.discovered_model_nodes,
            "declared_model_nodes": self.declared_model_nodes,
            "excluded_model_nodes": self.excluded_model_nodes,
            "model_node_reconciliation_gaps": self.model_node_reconciliation_gaps,
            "executed_model_nodes": self.executed_model_nodes,
            "skipped_model_nodes": self.skipped_model_nodes,
            "expected_semantic_children": self.expected_semantic_children,
            "quantitative_coverage": self.quantitative_coverage,
            "predictive_gaps": self.predictive_gaps,
            "native_obligation_evidence": self.native_obligation_evidence,
            "predictive_claim_licensed": self.predictive_claim_licensed,
        }


Executor = Callable[[GuardContract], tuple[SemanticStatus, list[dict[str, Any]], dict[str, Any], dict[str, Any]]]


@dataclass(frozen=True)
class SemanticExecutor:
    binding: SemanticBinding
    execute: Executor


def _finding(code: str, message: str, *, evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"code": code, "message": message, "evidence": evidence or {}}


def _string_values(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [str(key) for key in value]
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value if str(item)]
    return [str(value)]


def _fluent_values(value: Any) -> list[str]:
    if isinstance(value, dict):
        return [str(key) for key, active in value.items() if active]
    return _string_values(value)


def _coverage_context(contract: GuardContract) -> dict[str, Any]:
    value = contract.inputs.get("_semantic_coverage") or {}
    return dict(value) if isinstance(value, dict) else {}


def _variable_timepoint_map(contract: GuardContract) -> dict[str, list[str]]:
    """Read explicit per-variable/signal observations without inventing samples."""

    rows: dict[str, set[str]] = {}

    def add(variable_id: object, timepoint_id: object) -> None:
        variable = str(variable_id or "").strip()
        timepoint = str(timepoint_id or "").strip()
        if variable and timepoint:
            rows.setdefault(variable, set()).add(timepoint)

    def consume(value: object) -> None:
        if isinstance(value, Mapping):
            variable = value.get(
                "variable_id",
                value.get("signal_id", value.get("variable", value.get("signal"))),
            )
            timepoint = value.get(
                "timepoint_id", value.get("at", value.get("time"))
            )
            if variable not in (None, "") and timepoint not in (None, ""):
                add(variable, timepoint)
            values = value.get("values")
            if timepoint not in (None, "") and isinstance(values, Mapping):
                for key in values:
                    add(key, timepoint)
            for key, item in value.items():
                if key in {
                    "variable_id",
                    "signal_id",
                    "variable",
                    "signal",
                    "timepoint_id",
                    "at",
                    "time",
                    "values",
                }:
                    continue
                if isinstance(item, (list, tuple, set)):
                    for point in item:
                        if isinstance(point, Mapping):
                            add(key, point.get("timepoint_id", point.get("at", point.get("time"))))
                        else:
                            add(key, point)
                elif isinstance(item, Mapping):
                    for point in item.get(
                        "timepoint_ids", item.get("observed_timepoints", [])
                    ):
                        add(key, point)
        elif isinstance(value, (list, tuple, set)):
            for item in value:
                consume(item)

    causal = contract.inputs.get("causal_model") or {}
    event_model = contract.inputs.get("event_model") or {}
    for source in (
        contract.inputs.get("variable_observations"),
        contract.inputs.get("signal_observations"),
        contract.inputs.get("time_series_observations"),
        causal.get("variable_observations") if isinstance(causal, Mapping) else None,
        causal.get("signal_observations") if isinstance(causal, Mapping) else None,
        event_model.get("variable_observations") if isinstance(event_model, Mapping) else None,
        event_model.get("signal_observations") if isinstance(event_model, Mapping) else None,
        contract.world_model.data.get("variable_observations"),
        contract.world_model.data.get("signal_observations"),
    ):
        consume(source)
    events = (
        contract.inputs.get("events")
        or (event_model.get("events") if isinstance(event_model, Mapping) else None)
        or contract.world_model.data.get("event_line")
        or []
    )
    consume(events)
    return {key: sorted(values) for key, values in sorted(rows.items())}


def _event(contract: GuardContract):
    event_model = contract.inputs.get("event_model") or {}
    events = contract.inputs.get("events") or event_model.get("events") or contract.world_model.data.get("event_line") or []
    variable_timepoints = _variable_timepoint_map(contract)
    consumed = {
        "event_model": event_model,
        "events": events,
        "variable_observations": variable_timepoints,
    }
    if not events:
        return SemanticStatus.GAP, [_finding("SEM_EVENT_MISSING_EVENTS", "No executable event records were supplied.")], consumed, {}
    contradictory = event_model.get("contradictory_fluents") or event_model.get("exclusive_violation")
    if contradictory:
        return SemanticStatus.FAIL, [_finding("SEM_EVENT_CONTRADICTION", "Declared event fluents are contradictory.", evidence={"contradiction": contradictory})], consumed, {}
    missing: list[dict[str, Any]] = []
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            missing.append({"index": index, "field": "event mapping"})
            continue
        for name in ("event_id", "at"):
            if not event.get(name):
                missing.append({"index": index, "field": name})
        if not any(event.get(name) for name in ("initiates", "terminates", "releases")):
            missing.append({"index": index, "field": "initiation/termination/release axiom"})
    for axiom in event_model.get("missing_axioms", []):
        missing.append({"field": str(axiom)})
    if missing:
        return SemanticStatus.GAP, [_finding("SEM_EVENT_MISSING_AXIOM", "Event records lack required temporal or fluent axioms.", evidence={"missing": missing})], consumed, {}

    coverage = _coverage_context(contract)
    scenario_ids = _string_values(coverage.get("scenario_ids"))
    holdout_ids = _string_values(coverage.get("holdout_scenario_ids"))
    rollout_scenarios = [*scenario_ids, *holdout_ids] or ["default"]
    initial_state = set(_fluent_values(event_model.get("initial_states", [])))
    executed_scenarios: list[str] = []
    executed_holdouts: list[str] = []
    observed_timepoints: set[str] = set()
    executed_state_ids: set[str] = set(initial_state)
    executed_transition_ids: set[str] = set()
    executed_branch_ids: set[str] = set()
    executed_perturbation_ids: set[str] = set()
    rollout_steps = 0
    final_states: dict[str, list[str]] = {}
    for scenario_id in rollout_scenarios:
        state = set(initial_state)
        applicable = [
            event
            for event in events
            if not event.get("scenario_id") or str(event.get("scenario_id")) == scenario_id
        ]
        if not applicable:
            continue
        for event in sorted(applicable, key=lambda item: str(item.get("at", ""))):
            rollout_steps += 1
            observed_timepoints.add(str(event.get("at")))
            event_id = str(event.get("event_id"))
            executed_transition_ids.add(event_id)
            executed_branch_ids.update(_string_values(event.get("branch_id", event.get("branch_ids"))))
            executed_perturbation_ids.update(
                _string_values(event.get("perturbation_id", event.get("perturbation_ids")))
            )
            for fluent in _fluent_values(event.get("terminates")):
                state.discard(fluent)
            for fluent in _fluent_values(event.get("releases")):
                state.discard(fluent)
            for fluent in _fluent_values(event.get("initiates")):
                state.add(fluent)
                executed_state_ids.add(fluent)
        final_states[scenario_id] = sorted(state)
        if scenario_id in holdout_ids:
            executed_holdouts.append(scenario_id)
        elif scenario_id != "default":
            executed_scenarios.append(scenario_id)
    return SemanticStatus.PASS, [], consumed, {
        "evaluated_events": len(events),
        "rollout_steps": rollout_steps,
        "observed_timepoints": sorted(observed_timepoints),
        "observed_variable_timepoints": variable_timepoints,
        "executed_scenario_ids": executed_scenarios,
        "executed_holdout_scenario_ids": executed_holdouts,
        "executed_state_ids": sorted(executed_state_ids),
        "executed_transition_ids": sorted(executed_transition_ids),
        "executed_branch_ids": sorted(executed_branch_ids),
        "executed_perturbation_ids": sorted(executed_perturbation_ids),
        "final_states": final_states,
    }


def _agent(contract: GuardContract):
    agent_model = contract.inputs.get("agent_model") or contract.world_model.data.get("agent_model") or {}
    agents = agent_model.get("agents") if isinstance(agent_model, dict) else None
    if agents is None:
        agents = contract.world_model.data.get("agents") or contract.inputs.get("agents") or contract.inputs.get("beliefs") or {}
    consumed = {"agent_model": agent_model, "agents": agents}
    if not agents:
        return SemanticStatus.GAP, [_finding("SEM_AGENT_MISSING_MODEL", "No BDI agent records were supplied.")], consumed, {}
    records = agents.values() if isinstance(agents, dict) else agents
    missing = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            missing.append({"agent": index, "fields": ["beliefs", "desires", "intentions"]})
            continue
        absent = [name for name in ("beliefs", "desires", "intentions") if not record.get(name)]
        if absent:
            missing.append({"agent": record.get("agent_id", index), "fields": absent})
    if missing:
        return SemanticStatus.GAP, [_finding("SEM_AGENT_INCOMPLETE_BDI", "One or more agents lack BDI state required for the claim.", evidence={"missing": missing})], consumed, {}
    conflicts = agent_model.get("conflicting_intentions", []) if isinstance(agent_model, dict) else []
    if conflicts:
        return SemanticStatus.FAIL, [_finding("SEM_AGENT_CONFLICTING_INTENTIONS", "The BDI model declares conflicting intentions.", evidence={"conflicts": conflicts})], consumed, {}
    return SemanticStatus.PASS, [], consumed, {"evaluated_agents": len(agents)}


_RCC8 = {"DC", "EC", "PO", "EQ", "TPP", "NTPP", "TPPI", "NTPPI"}


def _space(contract: GuardContract):
    relations = contract.inputs.get("spatial_relations") or contract.world_model.data.get("rcc8_relations") or contract.world_model.relations.get("rcc8_relations", [])
    consumed = {"spatial_relations": relations}
    if not relations:
        return SemanticStatus.GAP, [_finding("SEM_SPACE_MISSING_RCC8", "No RCC8 base relations were supplied.")], consumed, {}
    by_pair: dict[tuple[Any, Any, Any], set[str]] = defaultdict(set)
    ntpp: set[tuple[Any, Any, Any]] = set()
    malformed = []
    for index, relation in enumerate(relations):
        if not isinstance(relation, dict):
            malformed.append({"index": index, "reason": "not a mapping"})
            continue
        rel = str(relation.get("relation", "")).upper()
        x, y, at = relation.get("x"), relation.get("y"), relation.get("at")
        if rel not in _RCC8 or x is None or y is None:
            malformed.append({"index": index, "relation": rel, "x": x, "y": y})
            continue
        by_pair[(x, y, at)].add(rel)
        if rel == "NTPP":
            ntpp.add((x, y, at))
    if malformed:
        return SemanticStatus.GAP, [_finding("SEM_SPACE_UNEVALUABLE_RCC8", "Some RCC8 relations are incomplete or unsupported.", evidence={"relations": malformed})], consumed, {}
    conflicts = [{"pair": list(pair), "relations": sorted(values)} for pair, values in by_pair.items() if len(values) > 1]
    for a, b, at in ntpp:
        for b2, c, at2 in ntpp:
            if b2 != b or at2 != at:
                continue
            observed = by_pair.get((a, c, at), set())
            if observed and observed != {"NTPP"}:
                conflicts.append({"chain": [a, b, c], "at": at, "expected": "NTPP", "observed": sorted(observed)})
    if conflicts:
        return SemanticStatus.FAIL, [_finding("SEM_SPACE_RCC8_CONFLICT", "RCC8 base relations or NTPP composition are inconsistent.", evidence={"conflicts": conflicts})], consumed, {}
    return SemanticStatus.PASS, [], consumed, {"evaluated_relations": len(relations)}


def _resource(contract: GuardContract):
    resources = contract.inputs.get("resources") or contract.world_model.data.get("resources") or {}
    consumed = {"resources": resources}
    places = resources.get("places", {}) if isinstance(resources, dict) else {}
    transitions = resources.get("transitions", []) if isinstance(resources, dict) else []
    if not places or not transitions:
        return SemanticStatus.GAP, [_finding("SEM_RESOURCE_MISSING_MODEL", "Places and transitions are required for conservation rollout.")], consumed, {}
    available: dict[tuple[str, str], float] = defaultdict(float)
    demanded: dict[tuple[str, str], float] = defaultdict(float)
    for place, tokens in places.items():
        for token in tokens:
            available[(str(place), str(token.get("color", "")))] += float(token.get("qty", 0))
    for transition in transitions:
        for need in transition.get("consumes", []):
            demanded[(str(need.get("place", "")), str(need.get("color", "")))] += float(need.get("qty", 0))
    overspent = [
        {"place": key[0], "color": key[1], "available": available[key], "demanded": quantity}
        for key, quantity in demanded.items()
        if quantity > available[key]
    ]
    if overspent:
        return SemanticStatus.FAIL, [_finding("SEM_RESOURCE_DOUBLE_CONSUMPTION", "Combined transitions consume more finite resource than the initial marking provides.", evidence={"overspent": overspent})], consumed, {}
    return SemanticStatus.PASS, [], consumed, {"evaluated_transitions": len(transitions), "conserved_keys": len(demanded)}


_ALLOWED_AST = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Pow,
    ast.Mod,
    ast.USub,
    ast.UAdd,
)


def _equation_error(expression: Any, known_names: set[str]) -> str:
    if isinstance(expression, (int, float, bool)):
        return ""
    if not isinstance(expression, str) or not expression.strip():
        return "equation is empty or not a supported scalar expression"
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError:
        return "equation is not valid expression syntax"
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_AST):
            return f"unsupported expression node: {type(node).__name__}"
        if isinstance(node, ast.Name) and node.id not in known_names:
            return f"unknown variable: {node.id}"
    return ""


def _safe_scalar_eval(expression: Any, environment: dict[str, float]) -> float:
    if isinstance(expression, bool):
        return float(expression)
    if isinstance(expression, (int, float)):
        return float(expression)
    tree = ast.parse(str(expression), mode="eval")
    return float(eval(compile(tree, "<worldguard-causal>", "eval"), {"__builtins__": {}}, environment))


def _scenario_records(value: Any) -> dict[str, dict[str, float]]:
    records: dict[str, dict[str, float]] = {}
    if isinstance(value, dict):
        for scenario_id, raw in value.items():
            if isinstance(raw, dict):
                values = raw.get("values", raw)
                if isinstance(values, dict):
                    records[str(scenario_id)] = {
                        str(key): float(item) for key, item in values.items()
                    }
    elif isinstance(value, list):
        for index, raw in enumerate(value):
            if not isinstance(raw, dict):
                continue
            scenario_id = str(raw.get("scenario_id", raw.get("id", index)))
            values = raw.get("values", {})
            if isinstance(values, dict):
                records[scenario_id] = {str(key): float(item) for key, item in values.items()}
    return records


def _evaluate_equations(
    variables: list[str],
    equations: dict[str, Any],
    seed: dict[str, float],
    overrides: dict[str, float] | None = None,
) -> tuple[dict[str, float], list[str]]:
    environment = dict(seed)
    overrides = dict(overrides or {})
    environment.update(overrides)
    remaining = [variable for variable in variables if variable not in overrides]
    errors: list[str] = []
    for _ in range(max(1, len(remaining) + 1)):
        progressed = False
        for variable in list(remaining):
            try:
                environment[variable] = _safe_scalar_eval(equations[variable], environment)
            except (KeyError, NameError):
                continue
            except (TypeError, ValueError, ZeroDivisionError, OverflowError) as exc:
                errors.append(f"{variable}:{type(exc).__name__}")
                remaining.remove(variable)
            else:
                remaining.remove(variable)
                progressed = True
        if not remaining or not progressed:
            break
    errors.extend(f"{variable}:unresolved_dependencies" for variable in remaining)
    return environment, errors


def _causal(contract: GuardContract):
    causal = contract.inputs.get("causal_model") or {
        "variables": contract.world_model.data.get("causal_variables", []),
        "equations": contract.world_model.data.get("causal_equations", {}),
        "graph": contract.world_model.data.get("causal_graph", []),
    }
    variable_timepoints = _variable_timepoint_map(contract)
    consumed = {
        "causal_model": causal,
        "variable_observations": variable_timepoints,
    }
    variables = [str(item) for item in causal.get("variables", [])]
    equations = causal.get("equations", {})
    if not variables or not isinstance(equations, dict):
        return SemanticStatus.GAP, [_finding("SEM_CAUSAL_MISSING_EQUATIONS", "Variables and structural equations are required.")], consumed, {}
    missing = [variable for variable in variables if variable not in equations]
    errors = {variable: _equation_error(equations.get(variable), set(variables) | set(causal.get("exogenous", []))) for variable in variables if variable in equations}
    errors = {key: value for key, value in errors.items() if value}
    if missing or errors:
        return SemanticStatus.GAP, [_finding("SEM_CAUSAL_UNEVALUABLE_EQUATION", "At least one structural equation is missing or outside the supported scalar subset.", evidence={"missing": missing, "errors": errors})], consumed, {}

    coverage = _coverage_context(contract)
    scenario_ids = _string_values(coverage.get("scenario_ids"))
    holdout_ids = _string_values(coverage.get("holdout_scenario_ids"))
    scenarios = _scenario_records(causal.get("scenarios", contract.inputs.get("scenarios", {})))
    holdouts = _scenario_records(
        causal.get("holdout_scenarios", contract.inputs.get("holdout_scenarios", {}))
    )
    scenario_results: dict[str, dict[str, float]] = {}
    execution_errors: list[dict[str, Any]] = []
    executed_scenarios: list[str] = []
    executed_holdouts: list[str] = []
    for scenario_id in scenario_ids:
        if scenario_id not in scenarios:
            continue
        values, row_errors = _evaluate_equations(variables, equations, scenarios[scenario_id])
        if row_errors:
            execution_errors.append({"scenario_id": scenario_id, "errors": row_errors})
            continue
        scenario_results[scenario_id] = values
        executed_scenarios.append(scenario_id)
    for scenario_id in holdout_ids:
        if scenario_id not in holdouts:
            continue
        values, row_errors = _evaluate_equations(variables, equations, holdouts[scenario_id])
        if row_errors:
            execution_errors.append({"scenario_id": scenario_id, "errors": row_errors})
            continue
        scenario_results[scenario_id] = values
        executed_holdouts.append(scenario_id)

    interventions = causal.get("interventions", contract.inputs.get("interventions", []))
    intervention_results: dict[str, dict[str, float]] = {}
    executed_interventions: list[str] = []
    for index, intervention in enumerate(interventions or []):
        if not isinstance(intervention, dict):
            continue
        intervention_id = str(intervention.get("intervention_id", intervention.get("id", index)))
        scenario_id = str(intervention.get("scenario_id", ""))
        seed = scenarios.get(scenario_id, holdouts.get(scenario_id, {}))
        assignments = intervention.get("set", intervention.get("values", {}))
        if not isinstance(assignments, dict) or not seed:
            continue
        values, row_errors = _evaluate_equations(
            variables,
            equations,
            seed,
            {str(key): float(value) for key, value in assignments.items()},
        )
        if row_errors:
            execution_errors.append({"intervention_id": intervention_id, "errors": row_errors})
            continue
        intervention_results[intervention_id] = values
        executed_interventions.append(intervention_id)

    counterfactuals = causal.get("counterfactuals", contract.inputs.get("counterfactuals", []))
    counterfactual_results: dict[str, Any] = {}
    executed_counterfactuals: list[str] = []
    for index, counterfactual in enumerate(counterfactuals or []):
        if not isinstance(counterfactual, dict):
            continue
        counterfactual_id = str(
            counterfactual.get("counterfactual_id", counterfactual.get("id", index))
        )
        intervention_id = str(counterfactual.get("intervention_id", ""))
        query = str(counterfactual.get("query", counterfactual.get("variable", "")))
        result = intervention_results.get(intervention_id)
        if not result or query not in result:
            continue
        counterfactual_results[counterfactual_id] = result[query]
        executed_counterfactuals.append(counterfactual_id)

    if execution_errors:
        return SemanticStatus.GAP, [
            _finding(
                "SEM_CAUSAL_ROLLOUT_ERROR",
                "One or more declared causal scenarios could not be evaluated safely.",
                evidence={"errors": execution_errors},
            )
        ], consumed, {
            "evaluated_equations": len(variables),
            "executed_scenario_ids": executed_scenarios,
            "executed_holdout_scenario_ids": executed_holdouts,
            "executed_intervention_ids": executed_interventions,
            "executed_counterfactual_ids": executed_counterfactuals,
            "observed_variable_timepoints": variable_timepoints,
        }
    return SemanticStatus.PASS, [], consumed, {
        "evaluated_equations": len(variables),
        "executed_scenario_ids": executed_scenarios,
        "executed_holdout_scenario_ids": executed_holdouts,
        "executed_intervention_ids": executed_interventions,
        "executed_counterfactual_ids": executed_counterfactuals,
        "observed_variable_timepoints": variable_timepoints,
        "scenario_results": scenario_results,
        "intervention_results": intervention_results,
        "counterfactual_results": counterfactual_results,
    }


def _conflict(contract: GuardContract):
    game = contract.inputs.get("game_model") or {
        "players": contract.world_model.data.get("conflict_players", []),
        "actions": contract.world_model.data.get("conflict_actions", {}),
        "states": contract.world_model.data.get("conflict_states", []),
        "payoffs": contract.world_model.data.get("conflict_payoffs", []),
        "transitions": contract.world_model.data.get("conflict_transitions", []),
    }
    consumed = {"game_model": game}
    required = [name for name in ("players", "actions", "states", "transitions", "payoffs") if not game.get(name)]
    if required:
        return SemanticStatus.GAP, [_finding("SEM_CONFLICT_INCOMPLETE_GAME", "Conflict rollout requires players, actions, states, transitions, and payoffs.", evidence={"missing": required})], consumed, {}
    invalid = []
    for transition in game.get("transitions", []):
        probabilities = transition.get("probabilities")
        if probabilities and abs(sum(float(value) for value in probabilities) - 1.0) > 0.0001:
            invalid.append(transition)
    if invalid:
        return SemanticStatus.FAIL, [_finding("SEM_CONFLICT_INVALID_TRANSITION", "Conflict transition probabilities do not sum to one.", evidence={"transitions": invalid})], consumed, {}
    return SemanticStatus.PASS, [], consumed, {"evaluated_transitions": len(game.get("transitions", []))}


def _norm(contract: GuardContract):
    norm_model = contract.inputs.get("norm_model") or {
        "norms": contract.inputs.get("norms") or contract.world_model.data.get("norms", []),
        "facts": contract.inputs.get("facts") or contract.world_model.data.get("facts", []),
    }
    norms = norm_model.get("norms", [])
    facts = norm_model.get("facts", [])
    consumed = {"norm_model": norm_model}
    if not norms:
        return SemanticStatus.GAP, [_finding("SEM_NORM_MISSING_MODEL", "No norms were supplied.")], consumed, {}
    fact_ids = {str(item.get("fact_id", item.get("name", ""))) if isinstance(item, dict) else str(item) for item in facts}
    missing = []
    for index, norm in enumerate(norms):
        condition = norm.get("condition") if isinstance(norm, dict) else None
        if not condition:
            missing.append({"norm": index, "needed": "condition"})
        elif isinstance(condition, str) and condition not in fact_ids:
            missing.append({"norm": index, "needed_fact": condition})
        elif isinstance(condition, dict):
            needed = str(condition.get("fact", condition.get("fact_id", "")))
            if not needed or needed not in fact_ids:
                missing.append({"norm": index, "needed_fact": needed or "condition fact"})
    if missing:
        return SemanticStatus.GAP, [_finding("SEM_NORM_MISSING_CONDITION_FACT", "Norm applicability cannot be evaluated without declared condition facts.", evidence={"missing": missing})], consumed, {}
    return SemanticStatus.PASS, [], consumed, {"evaluated_norms": len(norms), "condition_facts": len(fact_ids)}


def _binding(guard: str, fields: tuple[str, ...], semantics: tuple[str, ...], boundary: str) -> SemanticBinding:
    return SemanticBinding(
        executor_id=f"worldguard.semantic.{guard.removesuffix('Guard').lower()}.v1",
        guard=guard,
        input_fields=fields,
        output_fields=("status", "findings", "consumed_inputs", "outputs"),
        supported_semantics=semantics,
        unsupported_boundary=boundary,
    )


EXECUTOR_REGISTRY: dict[str, SemanticExecutor] = {
    "EventGuard": SemanticExecutor(_binding("EventGuard", ("inputs.events", "inputs.event_model", "inputs.variable_observations", "inputs.signal_observations", "mesh.semantic_coverage"), ("event_axiom_completeness", "fluent_consistency", "bounded_state_rollout", "scenario_and_holdout_execution", "declared_variable_signal_timepoint_observation"), "arbitrary temporal theorem proving and continuous dynamics"), _event),
    "AgentGuard": SemanticExecutor(_binding("AgentGuard", ("inputs.agent_model", "world_model.data.agents"), ("bdi_completeness", "declared_intention_conflict"), "open-ended planning and belief revision"), _agent),
    "SpaceGuard": SemanticExecutor(_binding("SpaceGuard", ("inputs.spatial_relations", "world_model.rcc8_relations"), ("rcc8_base_consistency", "ntpp_transitivity"), "metric geometry and full RCC8 closure"), _space),
    "ResourceGuard": SemanticExecutor(_binding("ResourceGuard", ("inputs.resources.places", "inputs.resources.transitions"), ("finite_resource_conservation",), "unbounded colored Petri-net reachability"), _resource),
    "CausalGuard": SemanticExecutor(_binding("CausalGuard", ("inputs.causal_model.variables", "inputs.causal_model.equations", "inputs.causal_model.scenarios", "inputs.causal_model.interventions", "inputs.causal_model.counterfactuals", "inputs.variable_observations", "inputs.signal_observations", "mesh.semantic_coverage"), ("safe_scalar_equation_evaluability", "bounded_scenario_rollout", "declared_intervention_execution", "declared_counterfactual_query", "declared_variable_signal_timepoint_observation"), "arbitrary code, external solvers, and causal identification"), _causal),
    "ConflictGuard": SemanticExecutor(_binding("ConflictGuard", ("inputs.game_model.players", "inputs.game_model.actions", "inputs.game_model.states", "inputs.game_model.transitions", "inputs.game_model.payoffs"), ("finite_game_completeness", "transition_probability"), "equilibrium solving and open-ended strategy search"), _conflict),
    "NormGuard": SemanticExecutor(_binding("NormGuard", ("inputs.norm_model.norms", "inputs.norm_model.facts"), ("condition_fact_binding",), "general deontic theorem proving and legal interpretation"), _norm),
}


def execute_semantic(
    *,
    node_id: str,
    guard: str,
    contract: GuardContract,
    provider_available: bool,
    coverage_context: dict[str, Any] | None = None,
) -> SemanticExecutionReceipt:
    from .guard_model_contract import verify_guard_candidate_purpose_contract

    purpose_binding = verify_guard_candidate_purpose_contract(contract, guard)
    purpose_binding_payload = purpose_binding.to_dict()
    executor = EXECUTOR_REGISTRY.get(guard)
    if executor is None:
        binding = _binding(guard, (), (), "no WorldGuard-owned semantic executor is registered")
        return SemanticExecutionReceipt(
            node_id=node_id,
            guard=guard,
            status=SemanticStatus.BOUNDARY_ONLY,
            provider_status=ProviderStatus.UNAVAILABLE,
            binding=binding,
            findings=[_finding("SEM_EXECUTOR_UNREGISTERED", "No semantic executor is registered for this guard.")],
            skipped_reason="unregistered_executor",
            guard_purpose_contract=purpose_binding_payload,
        )
    if not provider_available:
        return SemanticExecutionReceipt(
            node_id=node_id,
            guard=guard,
            status=SemanticStatus.NOT_RUN,
            provider_status=ProviderStatus.UNAVAILABLE,
            binding=executor.binding,
            findings=[_finding("SEM_PROVIDER_UNAVAILABLE", "The required semantic provider was explicitly marked unavailable.")],
            skipped_reason="provider_unavailable",
            guard_purpose_contract=purpose_binding_payload,
        )
    if coverage_context:
        contract = replace(
            contract,
            inputs={**contract.inputs, "_semantic_coverage": dict(coverage_context)},
        )
    status, findings, consumed_inputs, outputs = executor.execute(contract)
    return SemanticExecutionReceipt(
        node_id=node_id,
        guard=guard,
        status=status,
        provider_status=ProviderStatus.AVAILABLE,
        binding=executor.binding,
        findings=findings,
        consumed_inputs=consumed_inputs,
        outputs=outputs,
        guard_purpose_contract=purpose_binding_payload,
    )


def aggregate_semantic_status(receipts: list[SemanticExecutionReceipt]) -> SemanticStatus:
    statuses = [receipt.status for receipt in receipts]
    if any(status == SemanticStatus.FAIL for status in statuses):
        return SemanticStatus.FAIL
    if any(status == SemanticStatus.GAP for status in statuses):
        return SemanticStatus.GAP
    if any(status == SemanticStatus.BOUNDARY_ONLY for status in statuses):
        return SemanticStatus.BOUNDARY_ONLY
    if any(status == SemanticStatus.NOT_RUN for status in statuses):
        return SemanticStatus.NOT_RUN
    if statuses and all(status == SemanticStatus.PASS for status in statuses):
        return SemanticStatus.PASS
    return SemanticStatus.NOT_RUN


def aggregate_provider_status(receipts: list[SemanticExecutionReceipt], *, required: bool) -> ProviderStatus:
    if not required:
        return ProviderStatus.NOT_REQUIRED
    statuses = {receipt.provider_status for receipt in receipts}
    if not statuses or statuses == {ProviderStatus.UNAVAILABLE}:
        return ProviderStatus.UNAVAILABLE
    if statuses == {ProviderStatus.AVAILABLE}:
        return ProviderStatus.AVAILABLE
    return ProviderStatus.MIXED


def fingerprint_mesh(data: dict[str, Any]) -> str:
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

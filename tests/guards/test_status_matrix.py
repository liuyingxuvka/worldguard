import pytest

from tests.helpers import make_contract
from worldguard.guards import GUARD_RUNNERS
from worldguard.status import GuardStatus


CASES = [
    (
        "EventGuard",
        {
            GuardStatus.PASS: {"inputs": {"events": [{"event_id": "e1", "initiates": "ready"}]}},
            GuardStatus.FAIL: {"inputs": {"event_model": {"contradictory_fluents": ["hot", "cold"]}}},
            GuardStatus.GAP: {"inputs": {}},
            GuardStatus.BOUNDARY_EXCEEDED: {"text": "numeric dynamics claim"},
        },
    ),
    (
        "AgentGuard",
        {
            GuardStatus.PASS: {"inputs": {"beliefs": {"agent": {"beliefs": ["b"]}}}},
            GuardStatus.FAIL: {"inputs": {"beliefs": {"agent": {}}, "agent_model": {"conflicting_intentions": ["i1", "i2"]}}},
            GuardStatus.GAP: {"inputs": {"agent_model": {"missing_beliefs": ["b_missing"]}}},
            GuardStatus.BOUNDARY_EXCEEDED: {"text": "payoff equilibrium claim"},
        },
    ),
    (
        "SpaceGuard",
        {
            GuardStatus.PASS: {"inputs": {"spatial_relations": [{"at": "t0", "x": "a", "y": "b", "relation": "DC"}]}},
            GuardStatus.FAIL: {
                "inputs": {
                    "spatial_relations": [
                        {"at": "t0", "x": "a", "y": "b", "relation": "DC"},
                        {"at": "t0", "x": "a", "y": "b", "relation": "EC"},
                    ]
                }
            },
            GuardStatus.GAP: {"inputs": {}},
            GuardStatus.BOUNDARY_EXCEEDED: {"text": "metric distance in meters"},
        },
    ),
    (
        "ResourceGuard",
        {
            GuardStatus.PASS: {
                "inputs": {
                    "resources": {
                        "places": {"tank": [{"color": "h2", "qty": 1}]},
                        "transitions": [{"id": "run", "consumes": [{"place": "tank", "color": "h2", "qty": 1}]}],
                    }
                }
            },
            GuardStatus.FAIL: {
                "inputs": {
                    "resources": {
                        "places": {"tank": [{"color": "h2", "qty": 2}]},
                        "capacities": {"out": 1},
                        "transitions": [
                            {
                                "id": "run",
                                "consumes": [{"place": "tank", "color": "h2", "qty": 1}],
                                "produces": [{"place": "out", "color": "kwh", "qty": 2}],
                            }
                        ],
                    }
                }
            },
            GuardStatus.GAP: {
                "inputs": {
                    "resources": {
                        "places": {"tank": [{"color": "h2", "qty": 0}]},
                        "transitions": [{"id": "run", "consumes": [{"place": "tank", "color": "h2", "qty": 1}]}],
                    }
                }
            },
            GuardStatus.BOUNDARY_EXCEEDED: {"text": "permission to run"},
        },
    ),
    (
        "CausalGuard",
        {
            GuardStatus.PASS: {"inputs": {"causal_model": {"variables": ["x"], "equations": {"x": "f(u)"}}}},
            GuardStatus.FAIL: {"inputs": {"causal_model": {"variables": ["x"], "equations": {"x": "f(y)"}, "graph": [["x", "y"], ["y", "x"]]}}},
            GuardStatus.GAP: {"inputs": {"causal_model": {"variables": ["x"], "equations": {}}}},
            GuardStatus.BOUNDARY_EXCEEDED: {"text": "temporal story only"},
        },
    ),
    (
        "ConflictGuard",
        {
            GuardStatus.PASS: {"inputs": {"game_model": {"payoffs": [{"state": "s", "reward": {"a": 1}}]}}},
            GuardStatus.FAIL: {"inputs": {"game_model": {"transitions": [{"probabilities": [0.7, 0.7]}], "payoffs": [{"state": "s"}]}}},
            GuardStatus.GAP: {"inputs": {"game_model": {"payoffs": []}}},
            GuardStatus.BOUNDARY_EXCEEDED: {"text": "deontic obligation"},
        },
    ),
    (
        "NormGuard",
        {
            GuardStatus.PASS: {"text": "operator may start", "inputs": {"norms": [{"modality": "permitted", "action": "start"}]}},
            GuardStatus.FAIL: {
                "text": "Company A may share the full membrane recipe",
                "inputs": {"norms": [{"modality": "forbidden", "action": "share_membrane_recipe"}]},
            },
            GuardStatus.GAP: {"text": "operator may vent", "inputs": {"norms": []}},
            GuardStatus.BOUNDARY_EXCEEDED: {"text": "physical enablement token claim"},
        },
    ),
]


@pytest.mark.parametrize("guard,cases", CASES)
def test_guard_status_matrix(guard, cases):
    runner = GUARD_RUNNERS[guard]
    for expected_status, kwargs in cases.items():
        contract = make_contract(guard, **kwargs)
        result = runner(contract)
        assert result.status == expected_status
        assert result.ledgers

"""
Ultron Response / Action Boundary Tests
Version: v0.78

Tests:
- ResponseActionBoundary initialization
- Valid DecisionRoute validation
- Response route handling
- Execution route handling
- Planning route handling
- Clarification route handling
- Continuation route handling
- Unknown route handling
- DecisionRoute preservation
- Invalid input validation
- Deterministic boundary behavior

The boundary does NOT:
- Select tools
- Create execution plans
- Execute agents
- Execute tools
"""

import pytest

from modules.intelligence.agent_decision import (
    AgentDecision,
    DecisionType,
)
from modules.intelligence.decision_route import (
    DecisionRoute,
    RouteType,
)
from modules.intelligence.intent import (
    Intent,
    IntentType,
)
from modules.intelligence.response_action_boundary import (
    ResponseActionBoundary,
)


def create_intent() -> Intent:
    return Intent(
        intent_type=IntentType.ACTION,
        query="Open my browser",
        confidence=0.95,
        metadata={
            "source": "test",
        },
    )


def create_decision(
    decision_type: DecisionType,
) -> AgentDecision:
    return AgentDecision(
        decision_type=decision_type,
        intent=create_intent(),
        confidence=0.92,
        metadata={
            "test": True,
        },
    )


def create_route(
    decision_type: DecisionType,
) -> DecisionRoute:
    decision = create_decision(
        decision_type
    )

    route_map = {
        DecisionType.RESPOND: RouteType.RESPONSE,
        DecisionType.EXECUTE: RouteType.EXECUTION,
        DecisionType.PLAN: RouteType.PLANNING,
        DecisionType.CLARIFY: RouteType.CLARIFICATION,
        DecisionType.CONTINUE: RouteType.CONTINUATION,
        DecisionType.UNKNOWN: RouteType.UNKNOWN,
    }

    return DecisionRoute(
        route_type=route_map[decision_type],
        decision=decision,
    )


class TestResponseActionBoundary:

    def test_boundary_initializes(self):
        boundary = ResponseActionBoundary()

        assert isinstance(
            boundary,
            ResponseActionBoundary,
        )

    @pytest.mark.parametrize(
        "route_type, expected",
        [
            (
                RouteType.RESPONSE,
                "response",
            ),
            (
                RouteType.EXECUTION,
                "action",
            ),
            (
                RouteType.PLANNING,
                "action",
            ),
            (
                RouteType.CLARIFICATION,
                "response",
            ),
            (
                RouteType.CONTINUATION,
                "response",
            ),
            (
                RouteType.UNKNOWN,
                "unknown",
            ),
        ],
    )
    def test_boundary_classifies_route(
        self,
        route_type,
        expected,
    ):
        boundary = ResponseActionBoundary()

        route = create_route(
            {
                RouteType.RESPONSE: DecisionType.RESPOND,
                RouteType.EXECUTION: DecisionType.EXECUTE,
                RouteType.PLANNING: DecisionType.PLAN,
                RouteType.CLARIFICATION: DecisionType.CLARIFY,
                RouteType.CONTINUATION: DecisionType.CONTINUE,
                RouteType.UNKNOWN: DecisionType.UNKNOWN,
            }[route_type]
        )

        result = boundary.process(route)

        assert result == expected

    def test_response_route_is_response_boundary(self):
        boundary = ResponseActionBoundary()
        route = create_route(
            DecisionType.RESPOND
        )

        result = boundary.process(route)

        assert result == "response"

    def test_execution_route_is_action_boundary(self):
        boundary = ResponseActionBoundary()
        route = create_route(
            DecisionType.EXECUTE
        )

        result = boundary.process(route)

        assert result == "action"

    def test_planning_route_is_action_boundary(self):
        boundary = ResponseActionBoundary()
        route = create_route(
            DecisionType.PLAN
        )

        result = boundary.process(route)

        assert result == "action"

    def test_clarification_route_is_response_boundary(self):
        boundary = ResponseActionBoundary()
        route = create_route(
            DecisionType.CLARIFY
        )

        result = boundary.process(route)

        assert result == "response"

    def test_continuation_route_is_response_boundary(self):
        boundary = ResponseActionBoundary()
        route = create_route(
            DecisionType.CONTINUE
        )

        result = boundary.process(route)

        assert result == "response"

    def test_unknown_route_is_unknown_boundary(self):
        boundary = ResponseActionBoundary()
        route = create_route(
            DecisionType.UNKNOWN
        )

        result = boundary.process(route)

        assert result == "unknown"

    def test_boundary_preserves_route(self):
        boundary = ResponseActionBoundary()
        route = create_route(
            DecisionType.EXECUTE
        )

        result = boundary.route(
            route
        )

        assert result is route

    def test_boundary_route_returns_decision_route(self):
        boundary = ResponseActionBoundary()
        route = create_route(
            DecisionType.RESPOND
        )

        result = boundary.route(
            route
        )

        assert isinstance(
            result,
            DecisionRoute,
        )

    def test_invalid_process_input_raises_type_error(self):
        boundary = ResponseActionBoundary()

        with pytest.raises(
            TypeError,
            match="route must be a DecisionRoute instance",
        ):
            boundary.process("invalid")

    def test_invalid_route_input_raises_type_error(self):
        boundary = ResponseActionBoundary()

        with pytest.raises(
            TypeError,
            match="route must be a DecisionRoute instance",
        ):
            boundary.route(None)

    def test_boundary_is_deterministic(self):
        boundary = ResponseActionBoundary()
        route = create_route(
            DecisionType.EXECUTE
        )

        first = boundary.process(
            route
        )
        second = boundary.process(
            route
        )

        assert first == second

    def test_boundary_does_not_modify_route(self):
        boundary = ResponseActionBoundary()
        route = create_route(
            DecisionType.EXECUTE
        )

        original_decision = route.decision
        original_metadata = route.metadata

        boundary.process(route)

        assert route.decision is original_decision
        assert route.metadata == original_metadata
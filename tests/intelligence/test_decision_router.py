"""
Ultron Decision Router Tests
Version: v0.77

Tests:
- DecisionRouter initialization
- DecisionType → RouteType mapping
- Structured DecisionRoute creation
- Process alias
- Route type lookup
- Invalid decision validation
- Decision preservation
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
from modules.intelligence.decision_router import (
    DecisionRouter,
)
from modules.intelligence.intent import (
    Intent,
    IntentType,
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


class TestDecisionRouter:
    def test_route_returns_decision_route(self):
        router = DecisionRouter()
        decision = create_decision(
            DecisionType.EXECUTE
        )

        result = router.route(decision)

        assert isinstance(
            result,
            DecisionRoute,
        )

    @pytest.mark.parametrize(
        "decision_type, expected_route",
        [
            (
                DecisionType.RESPOND,
                RouteType.RESPONSE,
            ),
            (
                DecisionType.EXECUTE,
                RouteType.EXECUTION,
            ),
            (
                DecisionType.PLAN,
                RouteType.PLANNING,
            ),
            (
                DecisionType.CLARIFY,
                RouteType.CLARIFICATION,
            ),
            (
                DecisionType.CONTINUE,
                RouteType.CONTINUATION,
            ),
            (
                DecisionType.UNKNOWN,
                RouteType.UNKNOWN,
            ),
        ],
    )
    def test_all_decision_types_map_to_correct_routes(
        self,
        decision_type,
        expected_route,
    ):
        router = DecisionRouter()
        decision = create_decision(
            decision_type
        )

        result = router.route(decision)

        assert result.route_type == expected_route

    def test_route_preserves_original_decision(self):
        router = DecisionRouter()
        decision = create_decision(
            DecisionType.EXECUTE
        )

        result = router.route(decision)

        assert result.decision is decision

    def test_route_metadata_is_empty_by_default(self):
        router = DecisionRouter()
        decision = create_decision(
            DecisionType.RESPOND
        )

        result = router.route(decision)

        assert result.metadata == {}

    def test_process_is_alias_for_route(self):
        router = DecisionRouter()
        decision = create_decision(
            DecisionType.PLAN
        )

        result = router.process(decision)

        assert isinstance(
            result,
            DecisionRoute,
        )
        assert result.route_type == RouteType.PLANNING
        assert result.decision is decision

    def test_get_route_type_returns_expected_route(self):
        router = DecisionRouter()
        decision = create_decision(
            DecisionType.CLARIFY
        )

        result = router.get_route_type(
            decision
        )

        assert result == RouteType.CLARIFICATION

    def test_get_route_type_does_not_create_route(self):
        router = DecisionRouter()
        decision = create_decision(
            DecisionType.CONTINUE
        )

        result = router.get_route_type(
            decision
        )

        assert isinstance(
            result,
            RouteType,
        )

    def test_invalid_decision_for_route_raises_type_error(self):
        router = DecisionRouter()

        with pytest.raises(
            TypeError,
            match="decision must be an AgentDecision instance",
        ):
            router.route("invalid")

    def test_invalid_decision_for_process_raises_type_error(self):
        router = DecisionRouter()

        with pytest.raises(
            TypeError,
            match="decision must be an AgentDecision instance",
        ):
            router.process(None)

    def test_invalid_decision_for_get_route_type_raises_type_error(
        self,
    ):
        router = DecisionRouter()

        with pytest.raises(
            TypeError,
            match="decision must be an AgentDecision instance",
        ):
            router.get_route_type(
                {}
            )

    def test_execute_routes_to_execution_boundary(self):
        router = DecisionRouter()
        decision = create_decision(
            DecisionType.EXECUTE
        )

        result = router.route(decision)

        assert result.route_type == RouteType.EXECUTION

    def test_plan_routes_to_planning_boundary(self):
        router = DecisionRouter()
        decision = create_decision(
            DecisionType.PLAN
        )

        result = router.route(decision)

        assert result.route_type == RouteType.PLANNING

    def test_respond_routes_to_response_boundary(self):
        router = DecisionRouter()
        decision = create_decision(
            DecisionType.RESPOND
        )

        result = router.route(decision)

        assert result.route_type == RouteType.RESPONSE

    def test_clarify_routes_to_clarification_boundary(self):
        router = DecisionRouter()
        decision = create_decision(
            DecisionType.CLARIFY
        )

        result = router.route(decision)

        assert result.route_type == RouteType.CLARIFICATION

    def test_continue_routes_to_continuation_boundary(self):
        router = DecisionRouter()
        decision = create_decision(
            DecisionType.CONTINUE
        )

        result = router.route(decision)

        assert result.route_type == RouteType.CONTINUATION

    def test_unknown_routes_to_unknown_boundary(self):
        router = DecisionRouter()
        decision = create_decision(
            DecisionType.UNKNOWN
        )

        result = router.route(decision)

        assert result.route_type == RouteType.UNKNOWN

    def test_router_is_deterministic(self):
        router = DecisionRouter()
        decision = create_decision(
            DecisionType.EXECUTE
        )

        first = router.route(decision)
        second = router.route(decision)

        assert first.route_type == second.route_type
        assert first.decision is second.decision
        assert first.metadata == second.metadata

    def test_route_result_serializes_correctly(self):
        router = DecisionRouter()
        decision = create_decision(
            DecisionType.EXECUTE
        )

        result = router.route(decision)
        payload = result.to_dict()

        assert payload["route_type"] == "execution"
        assert payload["decision"]["decision_type"] == "execute"
        assert payload["decision"]["intent"]["intent_type"] == "action"
        assert payload["decision"]["confidence"] == 0.92
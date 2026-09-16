"""
Ultron Decision Router
Version: v0.77

Routes high-level AgentDecision objects to stable
architectural destinations.

Responsibilities:
- Validate AgentDecision input
- Map DecisionType to RouteType
- Produce structured DecisionRoute objects
- Keep routing deterministic
- Preserve the originating decision

The DecisionRouter does NOT:
- Select tools
- Create execution plans
- Execute agents
- Execute tools
- Call AI providers
- Modify the AgentDecision
"""

from modules.intelligence.agent_decision import (
    AgentDecision,
    DecisionType,
)
from modules.intelligence.decision_route import (
    DecisionRoute,
    RouteType,
)


class DecisionRouter:
    """
    Deterministic routing boundary for AgentDecision objects.
    """

    _ROUTE_MAP = {
        DecisionType.RESPOND: RouteType.RESPONSE,
        DecisionType.EXECUTE: RouteType.EXECUTION,
        DecisionType.PLAN: RouteType.PLANNING,
        DecisionType.CLARIFY: RouteType.CLARIFICATION,
        DecisionType.CONTINUE: RouteType.CONTINUATION,
        DecisionType.UNKNOWN: RouteType.UNKNOWN,
    }

    def route(
        self,
        decision: AgentDecision,
    ) -> DecisionRoute:
        """
        Route an AgentDecision to its architectural destination.
        """

        if not isinstance(
            decision,
            AgentDecision,
        ):
            raise TypeError(
                "decision must be an AgentDecision instance"
            )

        route_type = self._ROUTE_MAP.get(
            decision.decision_type
        )

        if route_type is None:
            raise ValueError(
                f"Unsupported decision type: "
                f"{decision.decision_type}"
            )

        return DecisionRoute(
            route_type=route_type,
            decision=decision,
        )

    def process(
        self,
        decision: AgentDecision,
    ) -> DecisionRoute:
        """
        Process an AgentDecision through the routing boundary.
        """

        return self.route(
            decision
        )

    def get_route_type(
        self,
        decision: AgentDecision,
    ) -> RouteType:
        """
        Return the route type without creating a DecisionRoute.
        """

        if not isinstance(
            decision,
            AgentDecision,
        ):
            raise TypeError(
                "decision must be an AgentDecision instance"
            )

        route_type = self._ROUTE_MAP.get(
            decision.decision_type
        )

        if route_type is None:
            raise ValueError(
                f"Unsupported decision type: "
                f"{decision.decision_type}"
            )

        return route_type


__all__ = [
    "DecisionRouter",
]
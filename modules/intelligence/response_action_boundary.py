"""
Ultron Response / Action Boundary
Version: v0.78

Defines the architectural boundary between response-oriented
and action-oriented decision routes.

Responsibilities:
- Validate DecisionRoute input
- Preserve the original DecisionRoute
- Classify routed decisions into high-level boundaries
- Provide a stable response/action hand-off point

The ResponseActionBoundary does NOT:
- Select tools
- Create execution plans
- Execute agents
- Execute tools
- Call AI providers
- Modify DecisionRoute objects
"""

from modules.intelligence.decision_route import (
    DecisionRoute,
    RouteType,
)


class ResponseActionBoundary:
    """
    Stable architectural boundary for routed decisions.

    This class only identifies whether a DecisionRoute belongs
    to a response-oriented, action-oriented, or unknown boundary.
    """

    _BOUNDARY_MAP = {
        RouteType.RESPONSE: "response",
        RouteType.EXECUTION: "action",
        RouteType.PLANNING: "action",
        RouteType.CLARIFICATION: "response",
        RouteType.CONTINUATION: "response",
        RouteType.UNKNOWN: "unknown",
    }

    def route(
        self,
        route: DecisionRoute,
    ) -> DecisionRoute:
        """
        Preserve and return the original DecisionRoute.

        The boundary does not modify or replace the route.
        """

        if not isinstance(
            route,
            DecisionRoute,
        ):
            raise TypeError(
                "route must be a DecisionRoute instance"
            )

        return route

    def process(
        self,
        route: DecisionRoute,
    ) -> str:
        """
        Classify a DecisionRoute into a high-level boundary.
        """

        if not isinstance(
            route,
            DecisionRoute,
        ):
            raise TypeError(
                "route must be a DecisionRoute instance"
            )

        boundary = self._BOUNDARY_MAP.get(
            route.route_type
        )

        if boundary is None:
            raise ValueError(
                f"Unsupported route type: "
                f"{route.route_type}"
            )

        return boundary


__all__ = [
    "ResponseActionBoundary",
]
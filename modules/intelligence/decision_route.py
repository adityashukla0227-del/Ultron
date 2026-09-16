"""
Ultron Decision Route Model
Version: v0.77

Structured representation of a routed agent decision.

Responsibilities:
- Represent the destination of an AgentDecision
- Store the original AgentDecision
- Store routing metadata
- Validate route state
- Provide safe serialization

The DecisionRoute model does NOT:
- Select tools
- Create execution plans
- Execute agents
- Execute tools
- Perform routing logic

Routing logic belongs to DecisionRouter.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict

from modules.intelligence.agent_decision import AgentDecision


class DecisionRouteError(Exception):
    """Base exception for decision route errors."""


class RouteType(str, Enum):
    RESPONSE = "response"
    EXECUTION = "execution"
    PLANNING = "planning"
    CLARIFICATION = "clarification"
    CONTINUATION = "continuation"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class DecisionRoute:
    """
    Structured result of routing an AgentDecision.
    """

    route_type: RouteType
    decision: AgentDecision
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(
            self.route_type,
            RouteType,
        ):
            raise TypeError(
                "route_type must be a RouteType"
            )

        if not isinstance(
            self.decision,
            AgentDecision,
        ):
            raise TypeError(
                "decision must be an AgentDecision instance"
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise TypeError(
                "metadata must be a dictionary"
            )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the decision route into a dictionary.
        """

        return {
            "route_type": self.route_type.value,
            "decision": self.decision.to_dict(),
            "metadata": dict(self.metadata),
        }


__all__ = [
    "DecisionRoute",
    "DecisionRouteError",
    "RouteType",
]
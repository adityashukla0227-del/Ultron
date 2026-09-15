"""
Ultron Agent Decision Model
Version: v0.76

Structured representation of an autonomous agent decision.

Responsibilities:
- Represent a normalized decision type
- Store the originating intent
- Store decision confidence
- Store structured decision metadata
- Validate decision state
- Provide safe serialization

The AgentDecision model does NOT:
- Select tools
- Create execution plans
- Execute agents
- Execute tools
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict

from modules.intelligence.intent import Intent


class DecisionType(str, Enum):
    RESPOND = "respond"
    EXECUTE = "execute"
    PLAN = "plan"
    CLARIFY = "clarify"
    CONTINUE = "continue"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class AgentDecision:
    decision_type: DecisionType
    intent: Intent
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(
            self.decision_type,
            DecisionType,
        ):
            raise TypeError(
                "decision_type must be a DecisionType"
            )

        if not isinstance(
            self.intent,
            Intent,
        ):
            raise TypeError(
                "intent must be an Intent instance"
            )

        if not isinstance(
            self.confidence,
            (int, float),
        ):
            raise TypeError(
                "confidence must be a number"
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise TypeError(
                "metadata must be a dictionary"
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_type": self.decision_type.value,
            "intent": self.intent.to_dict(),
            "confidence": self.confidence,
            "metadata": dict(self.metadata),
        }


__all__ = [
    "AgentDecision",
    "DecisionType",
]
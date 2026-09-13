"""
Ultron Intent Model
Version: v0.75

Structured representation of a user's understood intent.

Responsibilities:
- Represent a normalized intent type
- Store the original normalized query
- Store intent confidence
- Store structured intent metadata
- Validate intent state
- Provide safe serialization

The Intent model does NOT:
- Select tools
- Determine execution actions
- Create execution plans
- Execute agents
- Execute tools
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict


class IntentType(str, Enum):
    """
    Supported intent categories for v0.75.
    """

    INFORMATION = "information"
    ACTION = "action"
    CREATION = "creation"
    CONTINUATION = "continuation"
    EXPLANATION = "explanation"
    CONVERSATION = "conversation"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Intent:
    """
    Immutable structured representation of user intent.
    """

    intent_type: IntentType
    query: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.intent_type, IntentType):
            raise TypeError(
                "intent_type must be an IntentType"
            )

        if not isinstance(self.query, str):
            raise TypeError(
                "query must be a string"
            )

        if not self.query.strip():
            raise ValueError(
                "query cannot be empty"
            )

        if not isinstance(self.confidence, (int, float)):
            raise TypeError(
                "confidence must be a number"
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )

        if not isinstance(self.metadata, dict):
            raise TypeError(
                "metadata must be a dictionary"
            )

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the intent into a dictionary.
        """
        return {
            "intent_type": self.intent_type.value,
            "query": self.query,
            "confidence": self.confidence,
            "metadata": dict(self.metadata),
        }


__all__ = [
    "Intent",
    "IntentType",
]
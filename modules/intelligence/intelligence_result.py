"""
Ultron Intelligence Result
Version: v0.70

Structured result contract for Ultron's AI Intelligence layer.

Responsibilities:
- Store intelligence execution status
- Store generated AI response
- Store future intent information
- Store future action information
- Store structured metadata
- Validate result state
- Provide safe serialization
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class IntelligenceResult:
    """
    Immutable result returned by the AI Intelligence layer.
    """

    success: bool
    response: Optional[str] = None
    intent: Optional[str] = None
    action: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.success, bool):
            raise TypeError("success must be a boolean")

        if self.response is not None and not isinstance(
            self.response, str
        ):
            raise TypeError("response must be a string or None")

        if self.intent is not None and not isinstance(
            self.intent, str
        ):
            raise TypeError("intent must be a string or None")

        if self.action is not None and not isinstance(
            self.action, str
        ):
            raise TypeError("action must be a string or None")

        if self.error is not None and not isinstance(
            self.error, str
        ):
            raise TypeError("error must be a string or None")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary")

    def is_successful(self) -> bool:
        """
        Return whether intelligence execution succeeded.
        """
        return self.success

    def is_failed(self) -> bool:
        """
        Return whether intelligence execution failed.
        """
        return not self.success

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the result into a dictionary.
        """
        return {
            "success": self.success,
            "response": self.response,
            "intent": self.intent,
            "action": self.action,
            "error": self.error,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def success_result(
        cls,
        response: str,
        intent: Optional[str] = None,
        action: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "IntelligenceResult":
        """
        Create a successful intelligence result.
        """
        return cls(
            success=True,
            response=response,
            intent=intent,
            action=action,
            error=None,
            metadata=dict(metadata or {}),
        )

    @classmethod
    def failure_result(
        cls,
        error: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "IntelligenceResult":
        """
        Create a failed intelligence result.
        """
        return cls(
            success=False,
            response=None,
            intent=None,
            action=None,
            error=error,
            metadata=dict(metadata or {}),
        )

    def __repr__(self) -> str:
        return (
            "IntelligenceResult("
            f"success={self.success!r}, "
            f"response={self.response!r}, "
            f"intent={self.intent!r}, "
            f"action={self.action!r}, "
            f"error={self.error!r}, "
            f"metadata={self.metadata!r}"
            ")"
        )


__all__ = ["IntelligenceResult"]
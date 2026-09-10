"""
Ultron AI Intelligence
Version: v0.70

Coordinates Ultron's AI intelligence foundation.

Responsibilities:
- Validate incoming user queries
- Reuse Ultron's existing AI context builder
- Reuse Ultron's existing AI engine
- Generate structured IntelligenceResult objects
- Preserve provider abstraction and existing AI behavior

The AI Intelligence layer does NOT:
- Select tools
- Create execution plans
- Execute agents
- Execute tools
- Determine final intent
- Determine final action

Those responsibilities belong to future intelligence and agent layers.
"""

from typing import Any, Dict, Optional

from core.ai_context import build_ai_context
from core.ai_engine import generate_ai_response

from modules.intelligence.intelligence_result import (
    IntelligenceResult,
)


class AIIntelligence:
    """
    Foundation-level coordinator for Ultron AI intelligence.
    """

    def __init__(
        self,
        context_builder=build_ai_context,
        response_generator=generate_ai_response,
    ):
        if not callable(context_builder):
            raise TypeError(
                "context_builder must be callable"
            )

        if not callable(response_generator):
            raise TypeError(
                "response_generator must be callable"
            )

        self._context_builder = context_builder
        self._response_generator = response_generator

    def validate_query(self, query: Any) -> str:
        """
        Validate and normalize an incoming user query.
        """
        if not isinstance(query, str):
            raise TypeError(
                "query must be a string"
            )

        normalized_query = query.strip()

        if not normalized_query:
            raise ValueError(
                "query cannot be empty"
            )

        return normalized_query

    def build_context(
        self,
        query: str,
        goal_context: Optional[Dict[str, Any]] = None,
        ranked_context: Optional[list] = None,
    ) -> str:
        """
        Build AI-ready context using Ultron's existing
        context builder.
        """
        return self._context_builder(
            user=query,
            goal_context=goal_context,
            ranked_context=ranked_context,
        )

    def generate(
        self,
        query: str,
        goal_context: Optional[Dict[str, Any]] = None,
        ranked_context: Optional[list] = None,
        max_tokens: int = 1024,
    ) -> IntelligenceResult:
        """
        Generate a structured intelligence result.
        """
        try:
            validated_query = self.validate_query(query)

            context = self.build_context(
                query=validated_query,
                goal_context=goal_context,
                ranked_context=ranked_context,
            )

            response = self._response_generator(
                prompt=validated_query,
                context=context or None,
                max_tokens=max_tokens,
            )

            if not isinstance(response, str):
                return IntelligenceResult.failure_result(
                    error="AI engine returned an invalid response",
                    metadata={
                        "query": validated_query,
                    },
                )

            if not response.strip():
                return IntelligenceResult.failure_result(
                    error="AI engine returned an empty response",
                    metadata={
                        "query": validated_query,
                    },
                )

            return IntelligenceResult.success_result(
                response=response,
                metadata={
                    "query": validated_query,
                    "context_used": bool(context),
                },
            )

        except (TypeError, ValueError) as exc:
            return IntelligenceResult.failure_result(
                error=str(exc),
            )

        except Exception as exc:
            return IntelligenceResult.failure_result(
                error=f"AI intelligence failed: {exc}",
            )

    def process(
        self,
        query: str,
        goal_context: Optional[Dict[str, Any]] = None,
        ranked_context: Optional[list] = None,
        max_tokens: int = 1024,
    ) -> IntelligenceResult:
        """
        Alias for generate() representing an intelligence
        processing operation.
        """
        return self.generate(
            query=query,
            goal_context=goal_context,
            ranked_context=ranked_context,
            max_tokens=max_tokens,
        )

    def is_available(self) -> bool:
        """
        Return whether the intelligence coordinator is configured
        with callable AI components.
        """
        return (
            callable(self._context_builder)
            and callable(self._response_generator)
        )


__all__ = ["AIIntelligence"]
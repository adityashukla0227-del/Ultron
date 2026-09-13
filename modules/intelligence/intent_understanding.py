"""
Ultron Intent Understanding
Version: v0.75

Understands the semantic intent of a user query using
Ultron's existing AI Engine.

Responsibilities:
- Validate user queries
- Build an intent-classification prompt
- Reuse the existing AI Engine
- Parse structured intent output
- Validate intent type and confidence
- Produce structured Intent objects
- Keep intent understanding separate from execution decisions

The IntentUnderstanding component does NOT:
- Select tools
- Determine concrete actions
- Create execution plans
- Execute agents
- Execute tools
"""

from __future__ import annotations

import json
from typing import Any, Callable, Optional

from core.ai_engine import generate_ai_response

from modules.intelligence.intent import Intent, IntentType


class IntentUnderstanding:
    """
    Understand the semantic intent of a user query.
    """

    _SUPPORTED_INTENTS = {
        intent_type.value
        for intent_type in IntentType
    }

    def __init__(
        self,
        response_generator: Callable[..., str] = generate_ai_response,
    ):
        if not callable(response_generator):
            raise TypeError(
                "response_generator must be callable"
            )

        self._response_generator = response_generator

    @staticmethod
    def validate_query(query: str) -> str:
        if not isinstance(query, str):
            raise TypeError(
                "query must be a string"
            )

        validated_query = query.strip()

        if not validated_query:
            raise ValueError(
                "query cannot be empty"
            )

        return validated_query

    @staticmethod
    def build_prompt(
        query: str,
        context: Optional[str] = None,
    ) -> str:
        context_section = ""

        if context:
            context_section = (
                "\nRelevant context:\n"
                f"{context.strip()}\n"
            )

        return (
            "Classify the semantic intent of the user query.\n\n"
            "Allowed intent types:\n"
            "- information\n"
            "- action\n"
            "- creation\n"
            "- continuation\n"
            "- explanation\n"
            "- conversation\n"
            "- unknown\n\n"
            "Return ONLY valid JSON using exactly this structure:\n"
            '{"intent_type": "information", '
            '"confidence": 0.95, "metadata": {}}\n\n'
            "Rules:\n"
            "- Determine only the user's intent category.\n"
            "- Do not select tools.\n"
            "- Do not determine concrete actions.\n"
            "- Do not create plans.\n"
            "- Do not execute anything.\n"
            "- Confidence must be between 0.0 and 1.0.\n"
            "- Use unknown when the intent is ambiguous.\n"
            f"{context_section}\n"
            "User query:\n"
            f"{query}"
        )

    @classmethod
    def parse_response(
        cls,
        response: str,
        query: str,
        context_used: bool,
    ) -> Intent:
        if not isinstance(response, str):
            raise TypeError(
                "AI response must be a string"
            )

        cleaned_response = response.strip()

        if not cleaned_response:
            raise ValueError(
                "AI response cannot be empty"
            )

        try:
            payload = json.loads(cleaned_response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "AI response must contain valid JSON"
            ) from exc

        if not isinstance(payload, dict):
            raise ValueError(
                "AI response must contain a JSON object"
            )

        raw_intent_type = payload.get("intent_type")
        raw_confidence = payload.get("confidence")
        metadata = payload.get("metadata", {})

        if not isinstance(raw_intent_type, str):
            raise ValueError(
                "intent_type must be a string"
            )

        normalized_intent_type = (
            raw_intent_type.strip().lower()
        )

        if (
            normalized_intent_type
            not in cls._SUPPORTED_INTENTS
        ):
            raise ValueError(
                f"Unsupported intent type: "
                f"{normalized_intent_type}"
            )

        if not isinstance(
            raw_confidence,
            (int, float),
        ):
            raise ValueError(
                "confidence must be a number"
            )

        confidence = float(raw_confidence)

        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )

        if not isinstance(metadata, dict):
            raise ValueError(
                "metadata must be a dictionary"
            )

        metadata = dict(metadata)
        metadata["context_used"] = context_used

        return Intent(
            intent_type=IntentType(
                normalized_intent_type
            ),
            query=query,
            confidence=confidence,
            metadata=metadata,
        )

    def understand(
        self,
        query: str,
        context: Optional[str] = None,
    ) -> Intent:
        validated_query = self.validate_query(query)

        if context is not None and not isinstance(
            context,
            str,
        ):
            raise TypeError(
                "context must be a string"
            )

        validated_context = (
            context.strip()
            if context is not None
            else None
        )

        prompt = self.build_prompt(
            query=validated_query,
            context=validated_context,
        )

        response = self._response_generator(
            prompt=prompt,
            context=None,
            max_tokens=256,
        )

        return self.parse_response(
            response=response,
            query=validated_query,
            context_used=bool(validated_context),
        )

    def process(
        self,
        query: str,
        context: Optional[str] = None,
    ) -> Intent:
        return self.understand(
            query=query,
            context=context,
        )


__all__ = ["IntentUnderstanding"]